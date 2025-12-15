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
    processor = PromptProcessor(llm_client, config_manager.get_api_url(), config_manager.get_api_key(), config_manager.get_model())

    async def run_prompt_process(original_prompt, mode, temperature, view_instance, custom_path=None):
        # Update processor with latest config
        processor.api_url = config_manager.get_api_url()
        processor.api_key = config_manager.get_api_key()
        processor.model = config_manager.get_model()
        
        # Get extra params from config
        lang = config_manager.get_response_language()
        output_format = config_manager.get_output_format()

        if not processor.api_url or not processor.api_key or not original_prompt:
            view_instance.output_text.value = "Error: Please configure API Settings and enter a prompt."
            view_instance.page.update()
            return

        try:
            view_instance.output_text.value = "" # Clear previous output
            current_text = ""
            
            # Use streaming
            async for chunk in processor.stream_prompt(mode, original_prompt, temperature, lang, output_format, custom_path):
                current_text += chunk
                view_instance.output_text.value = current_text
                # Update page periodically or on every chunk? 
                # Flet handles updates pretty well, but for very long streams, 
                # maybe verify if we need throttling. For now, direct update.
                view_instance.page.update()
            
            # Final touch
            view_instance.output_text.value += "\n\n--- End of Generation ---"
            view_instance.page.update()
            
        except Exception as ex:
            view_instance.output_text.value = f"Critical Error: {ex}"
            view_instance.page.update()

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
