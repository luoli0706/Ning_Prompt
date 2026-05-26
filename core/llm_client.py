import httpx
import json
import asyncio
import os

class LLMClient:
    DEFAULT_API_URLS = {
        "openai": "https://api.deepseek.com/v1/chat/completions",
        "anthropic": "https://api.anthropic.com/v1/messages",
    }

    def __init__(self):
        # httpx Client for persistent connections
        self._client = httpx.AsyncClient(timeout=60.0)

    def _resolve_api_url(self, api_url: str, protocol: str) -> str:
        if api_url:
            return api_url
        return self.DEFAULT_API_URLS.get(protocol, self.DEFAULT_API_URLS["openai"])

    def _build_request(self, protocol: str, api_key: str, messages: list, model: str, temperature: float, stream: bool = False):
        if protocol == "anthropic":
            system_parts = [m.get("content", "") for m in messages if m.get("role") == "system"]
            user_messages = [
                {"role": "user", "content": m.get("content", "")}
                for m in messages
                if m.get("role") != "system"
            ]
            headers = {
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            }
            payload = {
                "model": model,
                "messages": user_messages,
                "temperature": temperature,
                "max_tokens": 4096,
            }
            if system_parts:
                payload["system"] = "\n\n".join(system_parts)
            if stream:
                payload["stream"] = True
            return headers, payload

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        if stream:
            payload["stream"] = True
        return headers, payload

    async def send_request(self, api_url: str, api_key: str, messages: list,
                           model: str = "deepseek-v4-flash", temperature: float = 0.7, protocol: str = "openai") -> dict:
        protocol = (protocol or "openai").lower()
        resolved_api_url = self._resolve_api_url(api_url, protocol)
        headers, payload = self._build_request(protocol, api_key, messages, model, temperature)

        try:
            response = await self._client.post(resolved_api_url, headers=headers, json=payload)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            return response.json()
        except httpx.RequestError as exc:
            return {"error": f"An error occurred while requesting {exc.request.url!r}: {exc}"}
        except httpx.HTTPStatusError as exc:
            return {"error": f"Error response {exc.response.status_code} while requesting {exc.request.url!r}: {exc.response.text}"}
        except json.JSONDecodeError:
            return {"error": f"Failed to decode JSON response from {resolved_api_url}: {response.text}"}
        except Exception as exc:
            return {"error": f"An unexpected error occurred: {exc}"}

    async def stream_request(self, api_url: str, api_key: str, messages: list,
                             model: str = "deepseek-v4-flash", temperature: float = 0.7, protocol: str = "openai"):
        protocol = (protocol or "openai").lower()
        resolved_api_url = self._resolve_api_url(api_url, protocol)
        headers, payload = self._build_request(protocol, api_key, messages, model, temperature, stream=True)

        try:
            async with self._client.stream("POST", resolved_api_url, headers=headers, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        line = line[6:]  # Remove "data: " prefix
                        if line.strip() == "[DONE]":
                            break
                        try:
                            chunk = json.loads(line)
                            if protocol == "anthropic":
                                if chunk.get("type") == "content_block_delta":
                                    delta = chunk.get("delta", {})
                                    if "text" in delta:
                                        yield delta["text"]
                            else:
                                delta = chunk["choices"][0]["delta"]
                                if "content" in delta:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            continue
        except httpx.RequestError as exc:
            yield f"\n[Error: {exc}]\n"
        except httpx.HTTPStatusError as exc:
            yield f"\n[HTTP Error {exc.response.status_code}]\n"
        except Exception as exc:
            yield f"\n[Unexpected Error: {exc}]\n"

    async def close(self):
        await self._client.aclose()
