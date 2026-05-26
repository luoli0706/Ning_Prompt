import os
import tempfile
import unittest
import asyncio

from core.config_manager import ConfigManager
from core.llm_client import LLMClient
from core.prompt_processor import PromptProcessor


class ProtocolSupportTests(unittest.TestCase):
    def test_config_defaults_include_protocol_and_latest_model(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager(os.path.join(tmpdir, "config.json"))
            self.assertEqual(manager.get_protocol(), "openai")
            self.assertEqual(manager.get_model(), "deepseek-v4-flash")

    def test_openai_default_url_resolution(self):
        client = LLMClient()
        self.assertEqual(
            client._resolve_api_url("", "openai"),
            "https://api.deepseek.com/v1/chat/completions",
        )
        asyncio.run(client.close())

    def test_anthropic_payload_conversion(self):
        client = LLMClient()
        headers, payload = client._build_request(
            "anthropic",
            "test-key",
            [
                {"role": "system", "content": "sys"},
                {"role": "user", "content": "hello"},
            ],
            "claude-3-5-sonnet",
            0.5,
            stream=True,
        )
        self.assertEqual(headers["x-api-key"], "test-key")
        self.assertEqual(payload["system"], "sys")
        self.assertEqual(payload["messages"][0]["role"], "user")
        self.assertTrue(payload["stream"])
        asyncio.run(client.close())

    def test_prompt_processor_extracts_openai_and_anthropic(self):
        llm_client = LLMClient()
        processor = PromptProcessor(llm_client, "", "", "deepseek-v4-flash", "openai")
        self.assertEqual(
            processor._extract_content({"choices": [{"message": {"content": "ok"}}]}),
            "ok",
        )
        self.assertEqual(
            processor._extract_content(
                {"content": [{"type": "text", "text": "hello "}, {"type": "text", "text": "world"}]}
            ),
            "hello world",
        )
        asyncio.run(llm_client.close())


if __name__ == "__main__":
    unittest.main()
