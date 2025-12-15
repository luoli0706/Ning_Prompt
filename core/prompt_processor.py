from .llm_client import LLMClient
from .prompt_loader import PromptLoader
from .mcp.protocol import MCPRequest, MCPResponse, MCPContext # Import MCP classes
import asyncio
import json

class PromptProcessor:
    def __init__(self, llm_client: LLMClient, api_url: str, api_key: str, model: str = "gpt-3.5-turbo"):
        self.llm_client = llm_client
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.loader = PromptLoader()

    async def _execute_mcp_request(self, request: MCPRequest) -> MCPResponse:
        """
        Core execution logic adhering to MCP.
        """
        if request.method != "process_prompt":
            return MCPResponse(error={"code": -32601, "message": "Method not found"})

        params = request.params
        mode = params.get("mode")
        prompt = params.get("prompt")
        temp = params.get("temperature", 0.7)
        lang = params.get("language", "en")
        fmt = params.get("output_format", "markdown")
        custom_path = params.get("custom_template_path")

        # Load Prompt
        system_prompt = self.loader.load_prompt(mode, prompt, lang, fmt, custom_path)
        
        # Prepare LLM Request
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Begin task."}
        ]

        # Call LLM (non-streaming for process_prompt's internal use)
        llm_response = await self.llm_client.send_request(
            self.api_url, self.api_key, messages, self.model, temp
        )

        if "error" in llm_response:
            return MCPResponse(error={"code": -32000, "message": llm_response["error"]})

        try:
            content = llm_response["choices"][0]["message"]["content"]
            return MCPResponse(result={
                "processed_prompt": content,
                "explanation": "Generated via MCP.",
                "meta": {
                    "model": self.model,
                    "mode": mode
                }
            })
        except (KeyError, IndexError) as e:
            return MCPResponse(error={"code": -32001, "message": f"Parse Error: {e}"})

    async def process_prompt(self, mode: str, original_prompt: str, temperature: float, language: str, output_format: str, custom_path: str = None) -> dict:
        """
        Bridge method for UI to call MCP execution (non-streaming).
        """
        # Create MCP Request
        req = MCPRequest(
            method="process_prompt",
            params={
                "mode": mode,
                "prompt": original_prompt,
                "temperature": temperature,
                "language": language,
                "output_format": output_format,
                "custom_template_path": custom_path
            },
            context=MCPContext(language=language)
        )

        # Execute
        resp = await self._execute_mcp_request(req)

        # Map back to dict for UI
        if resp.error:
            return {"processed_prompt": f"Error: {resp.error['message']}", "explanation": str(resp.error)}
        
        return resp.result

    async def stream_prompt(self, mode: str, original_prompt: str, temperature: float, language: str, output_format: str, custom_path: str = None):
        """
        Streaming version of process_prompt. Yields chunks of text.
        """
        full_prompt = self.loader.load_prompt(mode, original_prompt, language, output_format, custom_path)
        
        messages = [
            {"role": "system", "content": full_prompt},
            {"role": "user", "content": "Begin task."}
        ]

        async for chunk in self.llm_client.stream_request(
            self.api_url, self.api_key, messages, self.model, temperature
        ):
            yield chunk
