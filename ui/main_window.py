import flet as ft

TRANSLATIONS = {
    "en": {
        "app_title": "Prompt Workshop",
        "input_label": "INPUT",
        "input_placeholder": "Type your prompt here...",
        "select_mode": "MODE",
        "mode_enhance": "Enhance",
        "mode_weaken": "Weaken",
        "mode_repair": "Repair",
        "mode_destroy": "Destroy",
        "process_btn": "GENERATE",
        "intensity": "INTENSITY",
        "output_label": "OUTPUT",
        "output_placeholder": "Result awaits...",
        "settings_title": "Settings",
        "api_config": "API Configuration",
        "api_url": "API URL",
        "api_key": "API Key",
        "general_settings": "General Settings",
        "language": "Language",
        "theme": "Dark Mode",
        "save_return": "Save & Return",
        "processing": "Processing...",
    },
    "zh": {
        "app_title": "提示词工坊",
        "input_label": "输入区域",
        "input_placeholder": "在此输入您的原始提示词...",
        "select_mode": "处理模式",
        "mode_enhance": "语义增强",
        "mode_weaken": "语义弱化",
        "mode_repair": "语义修复",
        "mode_destroy": "语义破坏",
        "process_btn": "立即生成",
        "intensity": "处理强度",
        "output_label": "输出结果",
        "output_placeholder": "等待生成结果...",
        "settings_title": "设置",
        "api_config": "API 配置",
        "api_url": "API 地址 URL",
        "api_key": "API 密钥 Key",
        "general_settings": "通用设置",
        "language": "语言 / Language",
        "theme": "深色模式",
        "save_return": "保存并返回",
        "processing": "正在处理中...",
    }
}

# --- Neumorphism Constants ---
NEU_BG_LIGHT = "#e0e5ec"
NEU_BG_DARK = "#2b2e33"

ACCENT_CYAN = "#00e5ff"
ACCENT_GRADIENT = ["#00e5ff", "#00b8d4"]

class AppViews:
    def __init__(self, page: ft.Page, config_manager, processor, on_run_callback):
        self.page = page
        self.config_manager = config_manager
        self.processor = processor
        self.on_run_callback = on_run_callback
        
        self.lang = self.config_manager.get_language()
        self._init_components()

    def T(self, key):
        return TRANSLATIONS.get(self.lang, TRANSLATIONS["en"]).get(key, key)

    def _init_components(self):
        # 1. Input Field (Transparent to let container style show)
        self.prompt_field = ft.TextField(
            hint_text=self.T("input_placeholder"),
            multiline=True,
            min_lines=15,
            border=ft.InputBorder.NONE, # Remove default border
            text_size=14,
            cursor_color=ACCENT_CYAN,
        )

        # 2. Mode Dropdown - Styled directly to avoid ghosting
        self.mode_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("enhance", self.T("mode_enhance")),
                ft.dropdown.Option("weaken", self.T("mode_weaken")),
                ft.dropdown.Option("repair", self.T("mode_repair")),
                ft.dropdown.Option("destroy", self.T("mode_destroy")),
            ],
            value="enhance",
            border_radius=10,
            border_color=ACCENT_CYAN,
            border_width=1,
            bgcolor=ft.colors.with_opacity(0.05, ACCENT_CYAN), # Subtle background
            text_size=14,
            height=45,
            content_padding=10,
        )

        # 3. Slider
        self.intensity_slider = ft.Slider(
            min=0, max=1, value=0.5, 
            label="{value}", 
            active_color=ACCENT_CYAN,
            thumb_color=ACCENT_CYAN,
        )
        
        # 4. Output Text
        self.output_text = ft.Markdown(
            value=self.T("output_placeholder"), 
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            code_theme="atom-one-dark",
        )
        
        # 5. Run Button (Elevated)
        self.run_btn = ft.Container(
            content=ft.Text(self.T("process_btn"), weight="bold", color="white", size=16),
            alignment=ft.alignment.center,
            padding=ft.padding.symmetric(vertical=15, horizontal=30),
            border_radius=30,
            gradient=ft.LinearGradient(colors=ACCENT_GRADIENT),
            shadow=ft.BoxShadow(
                spread_radius=1, blur_radius=10, color=ft.colors.with_opacity(0.4, ACCENT_CYAN), offset=ft.Offset(0, 4)
            ),
            on_click=self._on_run_click_wrapper,
            animate_scale=ft.animation.Animation(100, ft.AnimationCurve.EASE_OUT),
            on_hover=self._on_btn_hover,
            ink=True,
        )
        
        # Settings
        self.api_url_field = ft.TextField(label=self.T("api_url"), value=self.config_manager.get_api_url(), border_color=ACCENT_CYAN)
        self.api_key_field = ft.TextField(label=self.T("api_key"), password=True, can_reveal_password=True, value=self.config_manager.get_api_key(), border_color=ACCENT_CYAN)
        self.language_dropdown = ft.Dropdown(
            label=self.T("language"), options=[ft.dropdown.Option("en", "English"), ft.dropdown.Option("zh", "中文")],
            value=self.lang, on_change=self._on_language_change, border_color=ACCENT_CYAN
        )
        self.theme_switch = ft.Switch(
            label=self.T("theme"), value=(self.config_manager.get_theme_mode() == "dark"), on_change=self._on_theme_change, active_color=ACCENT_CYAN
        )

    def _refresh_ui_text(self):
        self.prompt_field.hint_text = self.T("input_placeholder")
        self.mode_dropdown.options = [
            ft.dropdown.Option("enhance", self.T("mode_enhance")),
            ft.dropdown.Option("weaken", self.T("mode_weaken")),
            ft.dropdown.Option("repair", self.T("mode_repair")),
            ft.dropdown.Option("destroy", self.T("mode_destroy")),
        ]
        self.run_btn.content.value = self.T("process_btn")
        self.output_text.value = self.T("output_placeholder")
        self.api_url_field.label = self.T("api_url")
        self.api_key_field.label = self.T("api_key")
        self.language_dropdown.label = self.T("language")
        self.theme_switch.label = self.T("theme")
        self.page.update()

    # --- UI Helpers for Neumorphism ---
    def _neu_container(self, content, is_dark, recessed=False):
        bg_color = NEU_BG_DARK if is_dark else NEU_BG_LIGHT
        shadow_light = ft.colors.with_opacity(0.1, "white") if is_dark else "white"
        shadow_dark = ft.colors.with_opacity(0.5, "black") if is_dark else ft.colors.with_opacity(0.2, "#a3b1c6")
        
        if recessed:
            # Inner Shadow for Input/Output areas
            return ft.Container(
                content=content,
                bgcolor=bg_color,
                border_radius=20,
                padding=20,
                shadow=ft.BoxShadow(
                    spread_radius=1, blur_radius=15, color=shadow_dark, offset=ft.Offset(5, 5), blur_style=ft.ShadowBlurStyle.INNER
                ),
                # Note: Flet only supports one BoxShadow per container. 
                # For full Neu effect we ideally need two (light & dark). 
                # We compromise with one main inner shadow for depth.
                border=ft.border.all(1, ft.colors.with_opacity(0.05, "white")) if is_dark else None
            )
        else:
            # Raised Container (Flat)
            return ft.Container(
                content=content,
                bgcolor=bg_color,
                border_radius=20,
                padding=20,
                shadow=ft.BoxShadow(
                    spread_radius=1, blur_radius=20, color=shadow_dark, offset=ft.Offset(10, 10)
                ),
            )

    def get_main_view(self):
        is_dark = self.page.theme_mode == ft.ThemeMode.DARK
        bg_color = NEU_BG_DARK if is_dark else NEU_BG_LIGHT
        text_color = "white" if is_dark else "#4a5568"
        
        self.page.bgcolor = bg_color

        return ft.View(
            "/",
            [
                ft.Container(
                    content=ft.Column(
                        [
                            # Header
                            ft.Row(
                                [
                                    ft.Text(self.T("app_title").upper(), size=20, weight="bold", color=text_color),
                                    ft.IconButton(
                                        ft.icons.SETTINGS, 
                                        icon_color=text_color,
                                        on_click=lambda _: self.page.go("/settings")
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            ft.Divider(color=ft.colors.TRANSPARENT, height=20),
                            
                            # 3-Column Layout
                            ft.Row(
                                [
                                    # COL 1: INPUT (Recessed)
                                    ft.Column(
                                        [
                                            ft.Text(self.T("input_label"), size=12, weight="bold", color=ft.colors.with_opacity(0.5, text_color)),
                                            ft.Container(
                                                content=self._neu_container(self.prompt_field, is_dark, recessed=True),
                                                expand=True
                                            )
                                        ],
                                        expand=4, spacing=10
                                    ),
                                    
                                    # COL 2: CONTROLS (Center)
                                    ft.Column(
                                        [
                                            ft.Container(expand=True), # Spacer top
                                            
                                            # Mode Selector
                                            ft.Text(self.T("select_mode"), size=12, weight="bold", color=ACCENT_CYAN, text_align="center"),
                                            
                                            # Dropdown directly placed, no wrapping container
                                            self.mode_dropdown,
                                            
                                            ft.Container(height=30),
                                            
                                            # Slider
                                            ft.Text(self.T("intensity"), size=12, weight="bold", color=ACCENT_CYAN, text_align="center"),
                                            self.intensity_slider,
                                            
                                            ft.Container(height=40),
                                            
                                            # Run Button
                                            self.run_btn,
                                            
                                            ft.Container(expand=True), # Spacer bottom
                                        ],
                                        expand=2, 
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=5
                                    ),
                                    
                                    # COL 3: OUTPUT (Recessed)
                                    ft.Column(
                                        [
                                            ft.Text(self.T("output_label"), size=12, weight="bold", color=ft.colors.with_opacity(0.5, text_color)),
                                            ft.Container(
                                                content=self._neu_container(
                                                    ft.Column([self.output_text], scroll=ft.ScrollMode.AUTO), 
                                                    is_dark, 
                                                    recessed=True
                                                ),
                                                expand=True
                                            )
                                        ],
                                        expand=4, spacing=10
                                    ),
                                ],
                                expand=True,
                                spacing=30
                            )
                        ],
                    ),
                    padding=40,
                    expand=True,
                    bgcolor=bg_color
                )
            ],
            padding=0,
            bgcolor=bg_color
        )

    # --- Settings View (Styled) ---
    def get_settings_view(self):
        is_dark = self.page.theme_mode == ft.ThemeMode.DARK
        bg_color = NEU_BG_DARK if is_dark else NEU_BG_LIGHT
        text_color = "white" if is_dark else "#4a5568"
        
        return ft.View(
            "/settings",
            [
                ft.Container(
                    content=ft.Column(
                        [
                             # Header
                            ft.Row(
                                [
                                    ft.IconButton(ft.icons.ARROW_BACK, icon_color=text_color, on_click=self._save_and_go_back),
                                    ft.Text(self.T("settings_title").upper(), size=20, weight="bold", color=text_color),
                                    ft.Container(width=40), # Balance space
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            ft.Divider(color=ft.colors.TRANSPARENT, height=20),
                            
                            # Settings Content
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(self.T("api_config"), weight="bold", color=ACCENT_CYAN), 
                                    self.api_url_field, 
                                    self.api_key_field,
                                    
                                    ft.Divider(height=30, color=ft.colors.with_opacity(0.1, text_color)),
                                    
                                    ft.Text(self.T("general_settings"), weight="bold", color=ACCENT_CYAN), 
                                    self.language_dropdown, 
                                    self.theme_switch,
                                    
                                    ft.Container(height=30),
                                    
                                    ft.ElevatedButton(
                                        self.T("save_return"), 
                                        on_click=self._save_and_go_back,
                                        style=ft.ButtonStyle(
                                            color="white",
                                            bgcolor=ACCENT_CYAN,
                                            shape=ft.RoundedRectangleBorder(radius=10),
                                            padding=20
                                        )
                                    )
                                ], spacing=20), 
                                padding=30,
                                bgcolor=bg_color, # Same bg to blend in or slightly different? Let's use neu container logic if needed, but simple is clean.
                                # Let's actually put it in a raised neu container
                            ),
                            
                        ],
                    ),
                    padding=40,
                    expand=True,
                    bgcolor=bg_color
                )
            ],
            padding=0,
            bgcolor=bg_color
        )

    # ... Event Handlers ...
    def _on_btn_hover(self, e):
        e.control.scale = 1.05 if e.data == "true" else 1.0
        e.control.update()

    async def _on_run_click_wrapper(self, e):
        # UI animation
        self.run_btn.scale = 0.95
        self.run_btn.update()
        await self._on_run_click(e)
        self.run_btn.scale = 1.0
        self.run_btn.update()

    # ... (Keep existing handlers: _on_language_change, _on_theme_change, _save_and_go_back, _on_run_click) ...
    def _on_language_change(self, e):
        new_lang = e.control.value
        if new_lang != self.lang:
            self.lang = new_lang
            self._refresh_ui_text()
        self.page.update()

    def _on_theme_change(self, e):
        new_mode = "dark" if e.control.value else "light"
        self.page.theme_mode = ft.ThemeMode.DARK if new_mode == "dark" else ft.ThemeMode.LIGHT
        self.page.update()

    def _save_and_go_back(self, e):
        self.config_manager.set_api_url(self.api_url_field.value)
        self.config_manager.set_api_key(self.api_key_field.value)
        self.config_manager.set_language(self.lang) 
        new_mode = "dark" if self.theme_switch.value else "light"
        self.config_manager.set_theme_mode(new_mode) 
        self.page.go("/")

    async def _on_run_click(self, e):
        # self.run_btn.disabled = True # Container doesn't have disabled prop
        self.run_btn.opacity = 0.5
        self.output_text.value = self.T("processing")
        self.page.update()
        
        await self.on_run_callback(
            self.prompt_field.value,
            self.mode_dropdown.value,
            self.intensity_slider.value,
            self
        )
        
        self.run_btn.opacity = 1.0
        self.page.update()