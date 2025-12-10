from .llm_client import LLMClient
import asyncio

class PromptProcessor:
    def __init__(self, llm_client: LLMClient, api_url: str, api_key: str):
        self.llm_client = llm_client
        self.api_url = api_url
        self.api_key = api_key
        # Default model and temperature, can be made configurable later
        self.model = "gpt-3.5-turbo"
        self.temperature = 0.7

    async def _process_with_ai(self, system_prompt: str, user_prompt: str, intensity: float) -> dict:
        """
        Internal helper to send a meta-prompt to the AI and get a processed prompt.
        The intensity can be used by the meta-prompt to control the degree of transformation.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Original Prompt: {user_prompt}\nIntensity: {intensity}"}
        ]
        
        response = await self.llm_client.send_request(
            self.api_url, self.api_key, messages, self.model, self.temperature
        )
        
        if "error" in response:
            return {"processed_prompt": f"Error: {response['error']}", "explanation": response['error']}
        
        try:
            # Assuming the AI response is JSON with "processed_prompt" and "explanation"
            content = response["choices"][0]["message"]["content"]
            # Attempt to parse as JSON first, if not, treat as plain text
            try:
                parsed_content = json.loads(content)
                return {
                    "processed_prompt": parsed_content.get("processed_prompt", content),
                    "explanation": parsed_content.get("explanation", "")
                }
            except json.JSONDecodeError:
                return {"processed_prompt": content, "explanation": "AI returned plain text instead of JSON."}
        except (KeyError, IndexError) as e:
            return {"processed_prompt": f"Error parsing AI response: {e}. Full response: {response}", "explanation": f"Parsing error: {e}"}

    async def enhance_prompt(self, original_prompt: str, intensity: float) -> dict:
        system_prompt = f"""You are an expert prompt engineer specializing in semantic enhancement.
        Your task is to take an 'Original Prompt' and enhance it by adding descriptive details, positive and negative modifiers, and possibly suggesting optimal parameters like temperature and weight.
        The 'Intensity' parameter (0.0 to 1.0) dictates how aggressive the enhancement should be:
        - 0.0: Minimal, subtle additions.
        - 1.0: Maximal, highly detailed, and specific enhancements, including detailed negative prompts and parameter suggestions.
        Return the result in JSON format with 'processed_prompt' and 'explanation' fields.
        Example for intensity 0.7:
        {{
          "processed_prompt": "a fluffy Siamese cat, majestic, serene, sitting on a velvet cushion, highly detailed, photorealistic, 8k --neg low quality, blurry, cartoon, simple --temp 0.8 --w 0.9",
          "explanation": "Enhanced with descriptive details, positive aesthetic modifiers, and suggested negative prompts and parameters."
        }}
        """
        return await self._process_with_ai(system_prompt, original_prompt, intensity)

    async def weaken_prompt(self, original_prompt: str, intensity: float) -> dict:
        system_prompt = f"""You are an expert prompt engineer specializing in semantic weakening and generalization.
        Your task is to take an 'Original Prompt' and weaken its semantic specificity by generalizing its concepts, making it more abstract, and removing precise instructions.
        The 'Intensity' parameter (0.0 to 1.0) dictates how aggressive the weakening should be:
        - 0.0: Minimal, slight generalization.
        - 1.0: Maximal, highly abstract, leaving only core high-level concepts for maximum creative freedom.
        Return the result in JSON format with 'processed_prompt' and 'explanation' fields.
        Example for intensity 0.7:
        {{
          "processed_prompt": "An animal in an environment, conveying emotion.",
          "explanation": "Generalized specific elements into broader categories to expand creative possibilities."
        }}
        """
        return await self._process_with_ai(system_prompt, original_prompt, intensity)

    async def repair_prompt(self, original_prompt: str, intensity: float) -> dict:
        system_prompt = f"""You are an expert prompt engineer specializing in semantic repair and completion.
        Your task is to take an 'Original Prompt' and identify and fill in any semantic gaps, missing context, or ambiguities to ensure clarity, completeness, and a precise AI response.
        The 'Intensity' parameter (0.0 to 1.0) dictates how aggressive the repair should be:
        - 0.0: Minimal, fix obvious grammatical errors or typos.
        - 1.0: Maximal, thoroughly analyze for implicit assumptions, missing necessary details, and complete any logical gaps, potentially adding extensive context.
        Return the result in JSON format with 'processed_prompt' and 'explanation' fields.
        Example for intensity 0.7:
        {{
          "processed_prompt": "A serene landscape with a river flowing through a valley at sunrise, detailed reflections, vibrant colors, clear sky.",
          "explanation": "Repaired by adding missing details like time of day, specific features (river, valley), and atmospheric conditions."
        }}
        """
        return await self._process_with_ai(system_prompt, original_prompt, intensity)

    async def destroy_prompt(self, original_prompt: str, intensity: float) -> dict:
        system_prompt = f"""You are an expert prompt engineer specializing in semantic destruction for maximum creative exploration.
        Your task is to take an 'Original Prompt' and thoroughly break down its semantic meaning, fragmenting its concepts, removing logical connections, and leaving only disjointed, evocative fragments or keywords.
        The 'Intensity' parameter (0.0 to 1.0) dictates how aggressive the destruction should be:
        - 0.0: Minimal, slight rephrasing with minor fragmentation.
        - 1.0: Maximal, completely fragment the prompt into isolated, often abstract, keywords or short phrases, forcing the AI to interpret and generate with maximum imaginative freedom.
        Return the result in JSON format with 'processed_prompt' and 'explanation' fields.
        Example for intensity 0.7:
        {{
          "processed_prompt": "Cat. Fluffy. Blue. Sky. Fragment. Dream.",
          "explanation": "Destroyed the prompt by reducing it to abstract, disconnected keywords to inspire maximum creative interpretation."
        }}
        """
        return await self._process_with_ai(system_prompt, original_prompt, intensity)

# Example usage (for testing)
async def test_prompt_processor():
    # Placeholder LLMClient for testing purposes
    class MockLLMClient(LLMClient):
        async def send_request(self, api_url: str, api_key: str, messages: list,
                               model: str = "gpt-3.5-turbo", temperature: float = 0.7) -> dict:
            print(f"\n--- Mock LLM Call ---")
            print(f"System: {messages[0]['content']}")
            print(f"User: {messages[1]['content']}")
            print(f"API: {api_url}, Key: {'...' + api_key[-5:] if api_key else 'None'}")
            print(f"Model: {model}, Temp: {temperature}")
            # Simulate an AI response
            system_msg = messages[0]['content']
            user_msg = messages[1]['content']
            
            if "semantic enhancement" in system_msg:
                return {"choices": [{"message": {"content": json.dumps({"processed_prompt": f"Enhanced version of '{user_msg}' with intensity {temperature}", "explanation": "Mock enhancement"})}}]}
            elif "semantic weakening" in system_msg:
                return {"choices": [{"message": {"content": json.dumps({"processed_prompt": f"Weakened version of '{user_msg}' with intensity {temperature}", "explanation": "Mock weakening"})}}]}
            elif "semantic repair" in system_msg:
                return {"choices": [{"message": {"content": json.dumps({"processed_prompt": f"Repaired version of '{user_msg}' with intensity {temperature}", "explanation": "Mock repair"})}}]}
            elif "semantic destruction" in system_msg:
                return {"choices": [{"message": {"content": json.dumps({"processed_prompt": f"Destroyed version of '{user_msg}' with intensity {temperature}", "explanation": "Mock destruction"})}}]}
            else:
                return {"choices": [{"message": {"content": json.dumps({"processed_prompt": "Default processed prompt", "explanation": "Mock default"})}}]}

    mock_llm_client = MockLLMClient()
    processor = PromptProcessor(mock_llm_client, "http://mock-api.com", "mock-key")

    print("Testing Enhance:")
    result_enhance = await processor.enhance_prompt("A happy dog running in a field", 0.8)
    print("Processed:", result_enhance["processed_prompt"])

    print("\nTesting Weaken:")
    result_weaken = await processor.weaken_prompt("A detailed painting of a futuristic city with flying cars at sunset", 0.6)
    print("Processed:", result_weaken["processed_prompt"])
    
    print("\nTesting Repair:")
    result_repair = await processor.repair_prompt("show me a cat with some flowers", 0.9)
    print("Processed:", result_repair["processed_prompt"])
    
    print("\nTesting Destroy:")
    result_destroy = await processor.destroy_prompt("A majestic dragon guarding a treasure hoard in a dark cave", 0.7)
    print("Processed:", result_destroy["processed_prompt"])

if __name__ == "__main__":
    asyncio.run(test_prompt_processor())
