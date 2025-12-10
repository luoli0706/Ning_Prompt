import flet as ft

# --- Color Palette & Constants ---
NEON_BLUE = "#00F3FF"
NEON_PURPLE = "#BC13FE"
GLASS_BG = ft.colors.with_opacity(0.1, ft.colors.WHITE)
GLASS_BORDER = ft.colors.with_opacity(0.3, ft.colors.WHITE)
TEXT_COLOR = "#E0E0E0"

class NeonInput(ft.UserControl):
    """
    An input field wrapped in a glowing neon container.
    """
    def __init__(self, label, value="", password=False, can_reveal_password=False, on_change=None, multiline=False, min_lines=1, max_lines=1):
        super().__init__()
        self.label = label
        self.initial_value = value
        self.password = password
        self.can_reveal_password = can_reveal_password
        self.on_change = on_change
        self.multiline = multiline
        self.min_lines = min_lines
        self.max_lines = max_lines
        self.field = ft.TextField(
            label=self.label,
            value=self.initial_value,
            password=self.password,
            can_reveal_password=self.can_reveal_password,
            on_change=self.on_change,
            multiline=self.multiline,
            min_lines=self.min_lines,
            max_lines=self.max_lines,
            border=ft.InputBorder.NONE, # Remove default border
            color=TEXT_COLOR,
            cursor_color=NEON_BLUE,
            label_style=ft.TextStyle(color=ft.colors.with_opacity(0.7, NEON_BLUE)),
            text_size=14,
            expand=True
        )

    def build(self):
        return ft.Container(
            content=self.field,
            padding=ft.padding.only(left=15, right=15, top=5, bottom=5),
            border=ft.border.all(1, NEON_BLUE),
            border_radius=10,
            bgcolor=ft.colors.with_opacity(0.05, NEON_BLUE),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=10,
                color=ft.colors.with_opacity(0.3, NEON_BLUE),
                offset=ft.Offset(0, 0),
                blur_style=ft.ShadowBlurStyle.OUTER,
            ),
            animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
            on_hover=self._on_hover
        )
    
    def _on_hover(self, e):
        e.control.shadow.spread_radius = 2 if e.data == "true" else 0
        e.control.shadow.blur_radius = 15 if e.data == "true" else 10
        e.control.border = ft.border.all(1, NEON_PURPLE) if e.data == "true" else ft.border.all(1, NEON_BLUE)
        e.control.update()
        
    def get_value(self):
        return self.field.value
    
    def set_value(self, val):
        self.field.value = val
        self.field.update()

class PromptInputControl(ft.UserControl):
    def __init__(self, on_change=None):
        super().__init__()
        self.input_control = NeonInput(
            label="Enter your original prompt here...",
            multiline=True,
            min_lines=8,
            max_lines=12,
            on_change=on_change
        )

    def build(self):
        return ft.Column(
            [
                ft.Text("ORIGINAL PROMPT", size=12, weight=ft.FontWeight.BOLD, color=NEON_BLUE, font_family="Roboto Mono"),
                self.input_control,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.START,
            spacing=5
        )
    
    def get_value(self):
        return self.input_control.get_value()

class ModeSelectionControl(ft.UserControl):
    def __init__(self, on_change=None):
        super().__init__()
        self.on_change_callback = on_change
        self.modes = ["enhance", "weaken", "repair", "destroy"]
        self.buttons = []
        self.selected_index = 0
        
        # Define mode specific colors/icons
        self.mode_data = {
            "enhance": {"icon": ft.icons.AUTO_FIX_HIGH, "color": NEON_BLUE},
            "weaken": {"icon": ft.icons.BLUR_ON, "color": ft.colors.CYAN_200},
            "repair": {"icon": ft.icons.BUILD_CIRCLE, "color": ft.colors.GREEN_400},
            "destroy": {"icon": ft.icons.DELETE_FOREVER, "color": ft.colors.RED_ACCENT},
        }

    def _create_button(self, index, mode):
        is_selected = index == self.selected_index
        color = self.mode_data[mode]["color"]
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(
                        self.mode_data[mode]["icon"], 
                        color=color if is_selected else ft.colors.with_opacity(0.5, color),
                        size=24 if is_selected else 20,
                        animate_size=300
                    ),
                    ft.Text(
                        mode.upper(), 
                        color=color if is_selected else ft.colors.with_opacity(0.5, color),
                        size=12 if is_selected else 10,
                        weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL,
                        animate_size=300
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=5
            ),
            data=index,
            on_click=self._handle_click,
            padding=10,
            border_radius=10,
            bgcolor=ft.colors.with_opacity(0.1, color) if is_selected else ft.colors.TRANSPARENT,
            border=ft.border.all(1, color if is_selected else ft.colors.TRANSPARENT),
            animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
            expand=True,
            ink=True
        )

    def _handle_click(self, e):
        self.selected_index = e.control.data
        self.update()
        if self.on_change_callback:
            self.on_change_callback(self.modes[self.selected_index])

    def build(self):
        self.buttons = [self._create_button(i, mode) for i, mode in enumerate(self.modes)]
        
        # Glassmorphic container for the toggle bar
        return ft.Column(
            [
                 ft.Text("OPERATION MODE", size=12, weight=ft.FontWeight.BOLD, color=NEON_PURPLE, font_family="Roboto Mono"),
                 ft.Container(
                    content=ft.Row(self.buttons, spacing=5),
                    padding=5,
                    border_radius=15,
                    bgcolor=ft.colors.with_opacity(0.1, ft.colors.BLACK),
                    border=ft.border.all(1, ft.colors.with_opacity(0.2, ft.colors.WHITE)),
                )
            ],
            spacing=5
        )
    
    def update(self):
        # Rebuild buttons to reflect state change
        new_buttons = [self._create_button(i, mode) for i, mode in enumerate(self.modes)]
        self.controls[0].controls[1].content.controls = new_buttons
        super().update()

    def get_selected_mode(self):
        return self.modes[self.selected_index]

class ModeParameterControl(ft.UserControl):
    def __init__(self, on_intensity_change=None):
        super().__init__()
        self.on_change = on_intensity_change
        self.slider = ft.Slider(
            min=0,
            max=1,
            divisions=10,
            value=0.5,
            label="{value}",
            on_change=self.on_change,
            active_color=NEON_PURPLE,
            thumb_color=NEON_BLUE,
        )

    def build(self):
        return ft.Column(
            [
                ft.Row([
                    ft.Text("INTENSITY", size=12, weight=ft.FontWeight.BOLD, color=NEON_PURPLE, font_family="Roboto Mono"),
                    ft.Container(width=10),
                    ft.Icon(ft.icons.BOLT, color=NEON_PURPLE, size=16),
                ]),
                ft.Container(
                    content=self.slider,
                    padding=ft.padding.symmetric(horizontal=10),
                    bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
                    border_radius=15,
                ),
                ft.Row(
                    [
                        ft.Text("Subtle", size=10, color=ft.colors.GREY_500),
                        ft.Text("Extreme", size=10, color=ft.colors.GREY_500),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            ],
            spacing=5
        )
    
    def get_intensity(self):
        return self.slider.value

class ProcessedPromptOutput(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.processed_prompt_text = ft.Markdown(
            "Ready to process...",
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            code_theme="atom-one-dark",
            code_style=ft.TextStyle(font_family="Roboto Mono", color=NEON_BLUE),
        )
        self.explanation_text = ft.Text(
            "",
            selectable=True,
            size=12,
            italic=True,
            color=ft.colors.GREY_400
        )

    def build(self):
        return ft.Column(
            [
                ft.Text("PROCESSED RESULT", size=12, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_ACCENT, font_family="Roboto Mono"),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(
                                content=self.processed_prompt_text,
                                expand=True,
                            ),
                            ft.Divider(color=ft.colors.with_opacity(0.2, ft.colors.WHITE)),
                            self.explanation_text
                        ],
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    padding=20,
                    border_radius=15,
                    bgcolor=ft.colors.with_opacity(0.1, ft.colors.BLACK),
                    border=ft.border.all(1, ft.colors.with_opacity(0.3, ft.colors.GREEN_ACCENT)),
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=20,
                        color=ft.colors.with_opacity(0.1, ft.colors.GREEN_ACCENT),
                        blur_style=ft.ShadowBlurStyle.OUTER,
                    ),
                    expand=True,
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.START,
            expand=True
        )
    
    def set_output(self, processed_prompt: str, explanation: str = ""):
        self.processed_prompt_text.value = processed_prompt
        self.explanation_text.value = f"💡 AI Insight: {explanation}" if explanation else ""
        self.update()

class GlowingButton(ft.UserControl):
    def __init__(self, text, on_click):
        super().__init__()
        self.text = text
        self.on_click = on_click

    def build(self):
        return ft.Container(
            content=ft.Text(self.text, size=16, weight=ft.FontWeight.BOLD, color="white"),
            padding=ft.padding.all(15),
            alignment=ft.alignment.center,
            border_radius=10,
            gradient=ft.LinearGradient(
                colors=[NEON_PURPLE, NEON_BLUE],
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
            ),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.colors.with_opacity(0.5, NEON_PURPLE),
            ),
            on_click=self.on_click,
            animate=ft.animation.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
            on_hover=self._on_hover,
            ink=True
        )

    def _on_hover(self, e):
        e.control.scale = 1.05 if e.data == "true" else 1.0
        e.control.shadow.blur_radius = 25 if e.data == "true" else 15
        e.control.update()