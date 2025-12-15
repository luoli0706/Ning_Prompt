import os
import logging
import glob
from typing import List, Dict

class PromptLoader:
    def __init__(self, prompts_dir=None, custom_dir=None):
        # Default internal prompts
        self.internal_dir = os.path.join(os.path.dirname(__file__), "prompts")
        if prompts_dir:
            self.internal_dir = prompts_dir
            
        # Directory for custom templates (now also core/prompts)
        self.custom_dir = self.internal_dir # Changed to point to internal prompts directory

    def list_custom_templates(self) -> List[Dict[str, str]]:
        """
        Scans the custom directory for .md files.
        Returns a list of dicts: {'name': 'filename', 'path': 'abs_path'}
        """
        templates = []
        try:
            # Use glob to find .md files in the custom directory (non-recursive for safety/simplicity)
            search_pattern = os.path.join(self.custom_dir, "*.md")
            files = glob.glob(search_pattern)
            
            for f in files:
                filename = os.path.basename(f)
                templates.append({
                    "name": filename,
                    "path": os.path.abspath(f)
                })
        except Exception as e:
            logging.error(f"Error scanning for templates: {e}")
        
        return templates

    def load_prompt(self, mode: str, original_prompt: str, language: str = "en", output_format: str = "markdown", custom_path: str = None) -> str:
        """
        Loads a prompt template.
        If mode is 'custom', it tries to load from 'custom_path'.
        Otherwise loads from internal directory.
        """
        if mode == "custom" and custom_path:
            file_path = custom_path
        else:
            file_path = os.path.join(self.internal_dir, f"{mode}.md")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                template = f.read()
        except FileNotFoundError:
            logging.error(f"Prompt template not found: {file_path}")
            return f"Error: Template not found at {file_path}"
        except Exception as e:
            return f"Error loading template: {e}"

        # Construct instructions based on parameters
        lang_instruction = self._get_language_instruction(language)
        format_instruction = self._get_format_instruction(output_format)

        # Replace placeholders
        filled_prompt = template.replace("{{original_prompt}}", original_prompt)
        filled_prompt = filled_prompt.replace("{{language_instruction}}", lang_instruction)
        filled_prompt = filled_prompt.replace("{{format_instruction}}", format_instruction)

        return filled_prompt

    def _get_language_instruction(self, language: str) -> str:
        if language == "zh":
            return "Ensure the final output is in Chinese (Simplified)."
        elif language == "en":
            return "Ensure the final output is in English."
        elif language == "origin":
            return "Keep the language of the output consistent with the Original Prompt."
        else:
            return f"Ensure the final output is in {language}."

    def _get_format_instruction(self, output_format: str) -> str:
        if output_format == "plain":
            return "Output as plain text only. Do NOT use markdown code blocks, bolding, or headers."
        else:
            return "Output in Markdown format. Use clear structure."
