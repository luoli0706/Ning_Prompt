import httpx
import json
import asyncio
import os

class LLMClient:
    def __init__(self):
        # httpx Client for persistent connections
        self._client = httpx.AsyncClient(timeout=60.0)

    async def send_request(self, api_url: str, api_key: str, messages: list,
                           model: str = "gpt-3.5-turbo", temperature: float = 0.7) -> dict:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }

        try:
            response = await self._client.post(api_url, headers=headers, json=payload)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            return response.json()
        except httpx.RequestError as exc:
            return {"error": f"An error occurred while requesting {exc.request.url!r}: {exc}"}
        except httpx.HTTPStatusError as exc:
            return {"error": f"Error response {exc.response.status_code} while requesting {exc.request.url!r}: {exc.response.text}"}
        except json.JSONDecodeError:
            return {"error": f"Failed to decode JSON response from {api_url}: {response.text}"}
        except Exception as exc:
            return {"error": f"An unexpected error occurred: {exc}"}

    async def stream_request(self, api_url: str, api_key: str, messages: list,
                             model: str = "gpt-3.5-turbo", temperature: float = 0.7):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": True
        }

        try:
            async with self._client.stream("POST", api_url, headers=headers, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        line = line[6:]  # Remove "data: " prefix
                        if line.strip() == "[DONE]":
                            break
                        try:
                            chunk = json.loads(line)
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
