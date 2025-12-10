import flet as ft
from core.config_manager import ConfigManager
from core.llm_client import LLMClient
from core.prompt_processor import PromptProcessor
from ui.main_window import AppViews

def main(page: ft.Page):
    page.title = "Ning_Prompt"
    
    # Core Logic
    config_manager = ConfigManager("config.json")
    
    # Initialize Theme
    saved_theme = config_manager.get_theme_mode()
    page.theme_mode = ft.ThemeMode.DARK if saved_theme == "dark" else ft.ThemeMode.LIGHT
    
    llm_client = LLMClient()
    processor = PromptProcessor(llm_client, config_manager.get_api_url(), config_manager.get_api_key())

    async def run_prompt_process(original_prompt, mode, intensity, view_instance):
        # Update processor with latest config
        processor.api_url = config_manager.get_api_url()
        processor.api_key = config_manager.get_api_key()

        if not processor.api_url or not processor.api_key or not original_prompt:
            view_instance.output_text.value = "Error: Please configure API Settings and enter a prompt."
            return

        try:
            if mode == "enhance":
                result = await processor.enhance_prompt(original_prompt, intensity)
            elif mode == "weaken":
                result = await processor.weaken_prompt(original_prompt, intensity)
            elif mode == "repair":
                result = await processor.repair_prompt(original_prompt, intensity)
            elif mode == "destroy":
                result = await processor.destroy_prompt(original_prompt, intensity)
            else:
                result = {"processed_prompt": "Error: Unknown Mode", "explanation": ""}
            
            view_instance.output_text.value = f"{result.get('processed_prompt')}\n\n--- Explanation ---\n{result.get('explanation')}"
            
        except Exception as ex:
            view_instance.output_text.value = f"Critical Error: {ex}"

    # Navigation Logic
    app_views = AppViews(page, config_manager, processor, run_prompt_process)

    def route_change(route):
        page.views.clear()
        if page.route == "/":
            page.views.append(app_views.get_main_view())
        elif page.route == "/settings":
            page.views.append(app_views.get_settings_view())
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # Start at home
    page.go("/")

if __name__ == "__main__":
    ft.app(target=main)
