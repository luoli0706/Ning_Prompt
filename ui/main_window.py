import flet as ft
import time
import threading

TRANSLATIONS = {
    "en": {
        "app_title": "Prompt Workshop",
        "input_label": "INPUT",
        "input_placeholder": "Type your prompt here...",
        "select_mode": "MODE",
        "mode_enhance": "Enhance",
        "mode_generalize": "Generalize",
        "mode_repair": "Repair",
        "mode_pruning": "Pruning",
        "mode_custom": "Custom Template",
        "select_template": "Select Template",
        "process_btn": "GENERATE",
        "temperature": "CREATIVITY (Temperature)",
        "output_label": "OUTPUT",
        "copy_btn": "Copy",
        "copied": "Copied!",
        "output_placeholder": "Result awaits...",
        "settings_title": "Settings",
        "api_config": "API Configuration",
        "api_url": "API URL",
        "api_key": "API Key",
        "api_model": "Model Name",
        "general_settings": "General Settings",
        "language": "Language",
        "response_lang": "Response Language",
        "output_fmt": "Output Format",
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
        "mode_generalize": "语义泛化",
        "mode_repair": "语义修复",
        "mode_pruning": "语义剪枝",
        "mode_custom": "自定义模板",
        "select_template": "选择模板文件",
        "process_btn": "立即生成",
        "temperature": "创造性 (温度)",
        "output_label": "输出结果",
        "copy_btn": "复制",
        "copied": "已复制!",
        "output_placeholder": "等待生成结果...",
        "settings_title": "设置",
        "api_config": "API 配置",
        "api_url": "API 地址 URL",
        "api_key": "API 密钥 Key",
        "api_model": "模型名称 (Model Name)",
        "general_settings": "通用设置",
        "language": "界面语言 / Interface Lang",
        "response_lang": "回答语言偏好",
        "output_fmt": "输出格式",
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
        
        # State
        self._init_components()

    def T(self, key):
        return TRANSLATIONS.get(self.lang, TRANSLATIONS["en"]).get(key, key)

    def _init_components(self):
        # 1. Input Field
        self.prompt_field = ft.TextField(
            hint_text=self.T("input_placeholder"),
            multiline=True,
            min_lines=15,
            border=ft.InputBorder.NONE, 
            text_size=14,
            cursor_color=ACCENT_CYAN,
        )

        # 2. Mode Dropdown
        self.mode_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("enhance", self.T("mode_enhance")),
                ft.dropdown.Option("generalize", self.T("mode_generalize")),
                ft.dropdown.Option("repair", self.T("mode_repair")),
                ft.dropdown.Option("pruning", self.T("mode_pruning")),
                ft.dropdown.Option("custom", self.T("mode_custom")),
            ],
            value="enhance",
            border_radius=10,
            border_color=ACCENT_CYAN,
            border_width=1,
            bgcolor=ft.colors.TRANSPARENT,
            text_size=14,
            height=45,
            content_padding=10,
            color=ACCENT_CYAN,
            on_change=self._on_mode_change
        )

        # 2.1 File Selector (Hidden by default)
        self.file_dropdown = ft.Dropdown(
            label=self.T("select_template"),
            options=[],
            visible=False,
            border_radius=10,
            border_color=ACCENT_CYAN,
            text_size=14,
            height=45,
            content_padding=10,
            color=ACCENT_CYAN,
        )

        # 3. Slider (Temperature)
        self.temp_slider = ft.Slider(
            min=0.0, max=1.0, value=0.7, 
            divisions=10,
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
        
        # 5. Copy Button & Output Header
        self.copy_btn = ft.IconButton(
            icon=ft.icons.COPY,
            tooltip=self.T("copy_btn"),
            icon_color=ACCENT_CYAN,
            on_click=self._on_copy_click
        )

        # 6. Run Button
        self.run_btn = ft.Container(
            content=ft.Text(self.T("process_btn"), weight="bold", color="white", size=16),
            alignment=ft.alignment.center,
            padding=ft.padding.symmetric(vertical=15, horizontal=30),
            border_radius=30,
            gradient=ft.LinearGradient(colors=ACCENT_GRADIENT),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.colors.with_opacity(0.4, ACCENT_CYAN), offset=ft.Offset(0, 4)),
            on_click=self._on_run_click_wrapper,
            animate_scale=ft.animation.Animation(100, ft.AnimationCurve.EASE_OUT),
            on_hover=self._on_btn_hover,
            ink=True,
        )
        
        # Settings inputs (same as before)
        self.api_url_field = ft.TextField(label=self.T("api_url"), value=self.config_manager.get_api_url(), border_color=ACCENT_CYAN)
        self.api_key_field = ft.TextField(label=self.T("api_key"), password=True, can_reveal_password=True, value=self.config_manager.get_api_key(), border_color=ACCENT_CYAN)
        self.model_field = ft.TextField(label=self.T("api_model"), value=self.config_manager.get_model(), border_color=ACCENT_CYAN)
        self.language_dropdown = ft.Dropdown(label=self.T("language"), options=[ft.dropdown.Option("en", "English"), ft.dropdown.Option("zh", "中文")], value=self.lang, on_change=self._on_language_change, border_color=ACCENT_CYAN)
        
        self.resp_lang_dropdown = ft.Dropdown(
            label=self.T("response_lang"),
            options=[
                ft.dropdown.Option("origin", "Same as Prompt (Origin)"),
                ft.dropdown.Option("en", "English"),
                ft.dropdown.Option("zh", "Chinese"),
            ],
            value=self.config_manager.get_response_language(),
            border_color=ACCENT_CYAN
        )
        
        self.fmt_dropdown = ft.Dropdown(
            label=self.T("output_fmt"),
            options=[
                ft.dropdown.Option("markdown", "Markdown"),
                ft.dropdown.Option("plain", "Plain Text"),
            ],
            value=self.config_manager.get_output_format(),
            border_color=ACCENT_CYAN
        )

        self.theme_switch = ft.Switch(label=self.T("theme"), value=(self.config_manager.get_theme_mode() == "dark"), on_change=self._on_theme_change, active_color=ACCENT_CYAN)

    def _refresh_ui_text(self):
        self.prompt_field.hint_text = self.T("input_placeholder")
        self.mode_dropdown.options = [
            ft.dropdown.Option("enhance", self.T("mode_enhance")),
            ft.dropdown.Option("generalize", self.T("mode_generalize")),
            ft.dropdown.Option("repair", self.T("mode_repair")),
            ft.dropdown.Option("pruning", self.T("mode_pruning")),
            ft.dropdown.Option("custom", self.T("mode_custom")),
        ]
        self.file_dropdown.label = self.T("select_template")
        self.run_btn.content.value = self.T("process_btn")
        self.output_text.value = self.T("output_placeholder")
        self.copy_btn.tooltip = self.T("copy_btn")
        self.api_url_field.label = self.T("api_url")
        self.api_key_field.label = self.T("api_key")
        self.model_field.label = self.T("api_model")
        self.language_dropdown.label = self.T("language")
        self.resp_lang_dropdown.label = self.T("response_lang")
        self.fmt_dropdown.label = self.T("output_fmt")
        self.theme_switch.label = self.T("theme")
        self.page.update()

    def _neu_container(self, content, is_dark, recessed=False):
        bg_color = NEU_BG_DARK if is_dark else NEU_BG_LIGHT
        shadow_light = ft.colors.with_opacity(0.1, "white") if is_dark else "white"
        shadow_dark = ft.colors.with_opacity(0.5, "black") if is_dark else ft.colors.with_opacity(0.2, "#a3b1c6")
        
        if recessed:
            return ft.Container(
                content=content,
                bgcolor=bg_color,
                border_radius=20,
                padding=20,
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color=shadow_dark, offset=ft.Offset(5, 5), blur_style=ft.ShadowBlurStyle.INNER),
                border=ft.border.all(1, ft.colors.with_opacity(0.05, "white")) if is_dark else None
            )
        else:
            return ft.Container(
                content=content,
                bgcolor=bg_color,
                border_radius=20,
                padding=20,
                shadow=ft.BoxShadow(spread_radius=1, blur_radius=20, color=shadow_dark, offset=ft.Offset(10, 10)),
            )

    def get_main_view(self):
        is_dark = self.page.theme_mode == ft.ThemeMode.DARK
        bg_color = NEU_BG_DARK if is_dark else NEU_BG_LIGHT
        text_color = "white" if is_dark else "#4a5568"
        self.page.bgcolor = bg_color

        main_layout_content = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(self.T("app_title").upper(), size=20, weight="bold", color=text_color),
                            ft.IconButton(ft.icons.SETTINGS, icon_color=text_color, on_click=lambda _: self.page.go("/settings"))
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Divider(color=ft.colors.TRANSPARENT, height=20),
                    ft.Row(
                        [
                            # COL 1: INPUT
                            ft.Column(
                                [
                                    ft.Text(self.T("input_label"), size=12, weight="bold", color=ft.colors.with_opacity(0.5, text_color)),
                                    ft.Container(content=self._neu_container(self.prompt_field, is_dark, recessed=True), expand=True)
                                ],
                                expand=4, spacing=10
                            ),
                            # COL 2: CONTROLS
                            ft.Column(
                                [
                                    ft.Container(expand=True), 
                                    
                                    # Mode Selector
                                    ft.Text(self.T("select_mode"), size=12, weight="bold", color=ACCENT_CYAN, text_align="center"),
                                    self.mode_dropdown,
                                    
                                    # File Selector (Conditional)
                                    self.file_dropdown,
                                    
                                    ft.Container(height=20),
                                    
                                    # Slider
                                    ft.Text(self.T("temperature"), size=12, weight="bold", color=ACCENT_CYAN, text_align="center"),
                                    self.temp_slider,
                                    
                                    ft.Container(height=40),
                                    
                                    # Run Button
                                    self.run_btn,
                                    
                                    ft.Container(expand=True), 
                                ],
                                expand=2, 
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=5
                            ),
                            # COL 3: OUTPUT
                            ft.Column(
                                [
                                    ft.Row([
                                        ft.Text(self.T("output_label"), size=12, weight="bold", color=ft.colors.with_opacity(0.5, text_color)),
                                        self.copy_btn
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                    
                                    ft.Container(content=self._neu_container(ft.Column([self.output_text], scroll=ft.ScrollMode.AUTO), is_dark, recessed=True), expand=True)
                                ],
                                expand=4, spacing=10
                            ),
                        ],
                        expand=True, spacing=30
                    )
                ],
            ),
            padding=40,
            expand=True,
            bgcolor=bg_color
        )
        return ft.View("/", [main_layout_content], padding=0, bgcolor=bg_color)

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
                                    ft.Container(width=40)
                                ], 
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            ft.Divider(color=ft.colors.TRANSPARENT, height=20),
                            
                            # Settings Content Wrapped in Neu Container
                            self._neu_container(
                                ft.Column([
                                    ft.Text(self.T("api_config").upper(), weight="bold", color=ACCENT_CYAN, size=14), 
                                    self.api_url_field, 
                                    self.api_key_field,
                                    self.model_field,
                                    
                                    ft.Divider(height=30, color=ft.colors.with_opacity(0.1, text_color)),
                                    
                                    ft.Text(self.T("general_settings").upper(), weight="bold", color=ACCENT_CYAN, size=14), 
                                    self.language_dropdown, 
                                    self.resp_lang_dropdown,
                                    self.fmt_dropdown,
                                    self.theme_switch,
                                    
                                    ft.Container(height=30),
                                    
                                    ft.ElevatedButton(
                                        self.T("save_return").upper(), 
                                        on_click=self._save_and_go_back,
                                        style=ft.ButtonStyle(
                                            color="white",
                                            bgcolor=ACCENT_CYAN,
                                            shape=ft.RoundedRectangleBorder(radius=10),
                                            padding=20
                                        )
                                    )
                                ], spacing=20), 
                                is_dark=is_dark # Pass is_dark to neu_container
                            )
                        ], 
                        alignment=ft.MainAxisAlignment.START,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True,
                        scroll=ft.ScrollMode.AUTO,
                    ), 
                    padding=40, 
                    expand=True, 
                    bgcolor=bg_color
                )
            ],
            padding=0, 
            bgcolor=bg_color
        )

    # --- Handlers ---
    def _on_btn_hover(self, e):
        e.control.scale = 1.05 if e.data == "true" else 1.0
        e.control.update()

    async def _on_run_click_wrapper(self, e):
        self.run_btn.scale = 0.95; self.run_btn.update()
        await self._on_run_click(e)
        self.run_btn.scale = 1.0; self.run_btn.update()

    def _on_language_change(self, e):
        if e.control.value != self.lang: 
            self.lang = e.control.value
            self._refresh_ui_text()
        # Force reload to update UI text in all views
        self.page.go(self.page.route)

    def _on_theme_change(self, e):
        new_mode = "dark" if e.control.value else "light"
        self.page.theme_mode = ft.ThemeMode.DARK if new_mode == "dark" else ft.ThemeMode.LIGHT
        # Force reload to apply theme colors to _neu_container
        self.page.go(self.page.route)

    def _save_and_go_back(self, e):
        self.config_manager.set_api_url(self.api_url_field.value)
        self.config_manager.set_api_key(self.api_key_field.value)
        self.config_manager.set_model(self.model_field.value)
        self.config_manager.set_language(self.lang) 
        
        # New Settings
        self.config_manager.set_response_language(self.resp_lang_dropdown.value)
        self.config_manager.set_output_format(self.fmt_dropdown.value)
        
        new_mode = "dark" if self.theme_switch.value else "light"
        self.config_manager.set_theme_mode(new_mode) 
        self.page.go("/")

    def _on_mode_change(self, e):
        # Handle Custom Mode Logic
        if self.mode_dropdown.value == "custom":
            self._load_custom_templates()
            self.file_dropdown.visible = True
        else:
            self.file_dropdown.visible = False
        self.page.update()

    def _load_custom_templates(self):
        templates = self.processor.loader.list_custom_templates()
        options = [ft.dropdown.Option(t["path"], t["name"]) for t in templates]
        self.file_dropdown.options = options
        if options:
            self.file_dropdown.value = options[0].key
        else:
            self.file_dropdown.value = None
            self.file_dropdown.hint_text = "No .md files found"

    def _on_copy_click(self, e):
        self.page.set_clipboard(self.output_text.value)
        self.copy_btn.icon = ft.icons.CHECK
        self.copy_btn.tooltip = self.T("copied")
        self.page.update()
        
        # Reset icon after 2 seconds
        import threading, time
        def reset_icon():
            time.sleep(2)
            self.copy_btn.icon = ft.icons.COPY
            self.copy_btn.tooltip = self.T("copy_btn")
            self.page.update()
        threading.Thread(target=reset_icon, daemon=True).start()

    async def _on_run_click(self, e):
        self.run_btn.opacity = 0.5
        self.output_text.value = self.T("processing")
        self.page.update()
        
        custom_path = self.file_dropdown.value if self.mode_dropdown.value == "custom" else None
        
        await self.on_run_callback(
            self.prompt_field.value, 
            self.mode_dropdown.value, 
            self.temp_slider.value, 
            self,
            custom_path=custom_path # Pass custom path
        )
        
        self.run_btn.opacity = 1.0
        self.page.update()