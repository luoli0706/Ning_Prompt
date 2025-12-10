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

    async def close(self):
        await self._client.aclose()

# Example usage (for testing)
async def test_llm_client():
    client = LLMClient()
    
    # Placeholder values - replace with actual API URL and Key for real test
    api_url = os.environ.get("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")
    api_key = os.environ.get("OPENAI_API_KEY", "YOUR_API_KEY_HERE") # !!! Replace with your actual key or set env var

    if api_key == "YOUR_API_KEY_HERE":
        print("Please set OPENAI_API_KEY environment variable or replace 'YOUR_API_KEY_HERE' for a real test.")
        await client.close()
        return

    test_messages = [
        {"role": "system", "content": "You are a helpful assistant."}, 
        {"role": "user", "content": "Hello, how are you?"}
    ]

    print(f"Sending test request to {api_url}...")
    response = await client.send_request(api_url, api_key, test_messages)
    print("Response:", json.dumps(response, indent=2, ensure_ascii=False))

    await client.close()

if __name__ == "__main__":
    print("This is a test run for LLMClient. If you want to test with a real API,")
    print("please set OPENAI_API_KEY environment variable and potentially OPENAI_API_URL.")
    
    # Ensure httpx is installed
    try:
        import httpx
    except ImportError:
        print("\nError: 'httpx' library not found.")
        print("Please install it using: pip install httpx")
        exit(1)

    asyncio.run(test_llm_client())
