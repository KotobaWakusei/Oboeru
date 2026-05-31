"""ui.customtinker
轻量级的 tkinter 封装，提供主题感知的基础组件，便于统一样式和后续扩展。
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Any, Callable


class CTFrame(tk.Frame):
    """主题感知的 Frame 包装器"""
    def __init__(self, parent, style_manager: Optional[Any] = None, bg: Optional[str] = None, **kwargs):
        self._style_manager = style_manager
        colors = style_manager.colors if style_manager else {}
        if bg is None and style_manager:
            bg = colors.get("bg_primary")
        super().__init__(parent, bg=bg, **kwargs)

    def apply_theme(self):
        if getattr(self, "_style_manager", None):
            try:
                self.configure(bg=self._style_manager.colors.get("bg_primary"))
            except Exception:
                pass


class CTLabel(tk.Label):
    """主题感知的 Label 包装器"""
    def __init__(
        self,
        parent,
        style_manager: Optional[Any] = None,
        text: str = "",
        font: Optional[Any] = None,
        fg: Optional[str] = None,
        bg: Optional[str] = None,
        **kwargs,
    ):
        self._style_manager = style_manager
        colors = style_manager.colors if style_manager else {}
        if bg is None and style_manager:
            bg = colors.get("bg_primary")
        if fg is None and style_manager:
            fg = colors.get("fg_primary")
        if font is None and style_manager and hasattr(style_manager, "_fonts"):
            font = style_manager._fonts.get("body")
        super().__init__(parent, text=text, font=font, bg=bg, fg=fg, **kwargs)

    def apply_theme(self):
        if getattr(self, "_style_manager", None):
            colors = self._style_manager.colors
            try:
                self.configure(bg=colors.get("bg_primary"), fg=colors.get("fg_primary"))
            except Exception:
                pass


class CTButton(tk.Frame):
    """自定义按钮：使用 Frame+Label 实现可控的背景、悬停和按下效果。

    API 尽量模仿 `ttk.Button` 的部分行为：支持 `text`, `command`, `state`, `style`。
    """
    def __init__(
        self,
        parent,
        style_manager: Optional[Any] = None,
        text: str = "",
        command: Optional[Callable] = None,
        style: Optional[str] = "Primary.TButton",
        padding: tuple[int, int] = (12, 8),
        **kwargs,
    ):
        super().__init__(parent)
        self._style_manager = style_manager
        self._command = command
        self._style_name = style or "Primary.TButton"
        self._state = "normal"

        # 初始颜色来自 style_manager
        colors = style_manager.colors if style_manager else {}
        self._colors = colors

        self._style_map = {}
        self._refresh_style_map()

        self._padding = padding

        # 内部 label
        self._label = CTLabel(self, style_manager=style_manager, text=text, cursor="hand2")
        self._label.pack(fill=tk.BOTH, expand=True)

        # 同步默认样式
        self._apply_style(self._style_name)

        # 事件绑定
        for widget in (self, self._label):
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
            widget.bind("<Button-1>", self._on_press)
            widget.bind("<ButtonRelease-1>", self._on_release)

    def _refresh_style_map(self):
        """Refresh style colors from the current theme."""
        colors = self._colors
        self._style_map = {
            "Primary.TButton": {
                "bg": colors.get("accent", "#0078d7"),
                "fg": "#ffffff",
                "hover": colors.get("accent_hover", colors.get("accent", "#005a9e")),
            },
            "Secondary.TButton": {
                "bg": colors.get("bg_secondary", "#333"),
                "fg": colors.get("fg_primary", "#fff"),
                "hover": colors.get("bg_card", "#444"),
            },
            "Nav.TButton": {
                "bg": colors.get("bg_secondary", "#222"),
                "fg": colors.get("fg_primary", "#fff"),
                "hover": colors.get("bg_card", "#333"),
            },
            "Option.TButton": {
                "bg": colors.get("bg_card", "#111"),
                "fg": colors.get("fg_primary", "#fff"),
                "hover": colors.get("accent", "#0078d7"),
            },
        }

    def _apply_style(self, style_name: str):
        cfg = self._style_map.get(style_name, {})
        bg = cfg.get("bg", self._colors.get("bg_secondary", "#333"))
        fg = cfg.get("fg", self._colors.get("fg_primary", "#fff"))

        self.configure(bg=bg)
        self._label.configure(
            bg=bg,
            fg=fg,
            font=(
                self._style_manager._fonts.get("button")
                if getattr(self._style_manager, "_fonts", None)
                else None
            ),
        )
        # 内部 padding
        padx, pady = self._padding
        self._label.configure(padx=padx, pady=pady)

    def _lerp_color(self, c1, c2, t):
        def _h(hx):
            hx = hx.lstrip("#")
            return tuple(int(hx[i:i+2], 16) for i in (0, 2, 4))
        def _f(r, g, b):
            return f"#{int(r):02x}{int(g):02x}{int(b):02x}"
        r1, g1, b1 = _h(c1)
        r2, g2, b2 = _h(c2)
        return _f(r1 + (r2 - r1) * t, g1 + (g2 - g1) * t, b1 + (b2 - b1) * t)

    def _smooth_bg(self, target_bg, steps=8):
        try:
            current = self._label.cget("bg") or self._colors.get("bg_secondary", "#333")
        except Exception:
            current = self._colors.get("bg_secondary", "#333")
        tag = object()
        self._hover_tag = tag

        def tick(i):
            if getattr(self, '_hover_tag', None) is not tag:
                return
            if i < steps:
                t = (i + 1) / steps
                color = self._lerp_color(current, target_bg, t)
                try:
                    self.configure(bg=color)
                    self._label.configure(bg=color)
                except Exception:
                    pass
                self.after(16, tick, i + 1)
            else:
                try:
                    self.configure(bg=target_bg)
                    self._label.configure(bg=target_bg)
                except Exception:
                    pass

        tick(0)

    def _on_enter(self, event=None):
        if self._state == "disabled":
            return
        cfg = self._style_map.get(self._style_name, {})
        hover = cfg.get("hover") or cfg.get("bg")
        self._smooth_bg(hover, steps=8)

    def _on_leave(self, event=None):
        if self._state == "disabled":
            return
        cfg = self._style_map.get(self._style_name, {})
        normal = cfg.get("bg", self._colors.get("bg_secondary", "#333"))
        self._smooth_bg(normal, steps=6)

    def _on_press(self, event=None):
        if self._state == "disabled":
            return
        try:
            # 按下的微调效果
            self._label.configure(relief=tk.SUNKEN)
        except Exception:
            pass

    def _on_release(self, event=None):
        if self._state == "disabled":
            return
        try:
            self._label.configure(relief=tk.FLAT)
            if self._command:
                self._command()
        except Exception:
            pass

    def _smooth_style_transition(self, old_style, new_style, steps=12):
        old_cfg = self._style_map.get(old_style, {})
        new_cfg = self._style_map.get(new_style, {})
        start_bg = old_cfg.get("bg", self._colors.get("bg_secondary", "#333"))
        end_bg = new_cfg.get("bg", start_bg)
        start_fg = old_cfg.get("fg", self._colors.get("fg_primary", "#fff"))
        end_fg = new_cfg.get("fg", start_fg)
        tag = object()
        self._style_tag = tag

        def _lerp(c1, c2, t):
            def _h(hx):
                hx = hx.lstrip("#")
                return tuple(int(hx[i:i+2], 16) for i in (0, 2, 4))
            def _f(r, g, b):
                return f"#{int(r):02x}{int(g):02x}{int(b):02x}"
            r1, g1, b1 = _h(c1)
            r2, g2, b2 = _h(c2)
            return _f(r1 + (r2 - r1) * t, g1 + (g2 - g1) * t, b1 + (b2 - b1) * t)

        def tick(i):
            if getattr(self, '_style_tag', None) is not tag:
                return
            if i < steps:
                t = (i + 1) / steps
                bg = _lerp(start_bg, end_bg, t)
                fg = _lerp(start_fg, end_fg, t)
                try:
                    self.configure(bg=bg)
                    self._label.configure(bg=bg, fg=fg)
                except Exception:
                    pass
                self.after(16, tick, i + 1)
            else:
                self._apply_style(new_style)

        tick(0)

    def configure(self, **kwargs):
        # 支持 text, command, state, style
        if "text" in kwargs:
            self._label.configure(text=kwargs.pop("text"))
        if "command" in kwargs:
            self._command = kwargs.pop("command")
        if "state" in kwargs:
            state = kwargs.pop("state")
            self._state = state
            if state in ("disabled", tk.DISABLED):
                # 变灰
                try:
                    self._label.configure(fg=self._colors.get("fg_secondary", "#888"))
                    self._label.configure(cursor="")
                except Exception:
                    pass
            else:
                try:
                    self._label.configure(fg=self._style_map.get(self._style_name, {}).get("fg", self._colors.get("fg_primary")))
                    self._label.configure(cursor="hand2")
                except Exception:
                    pass
        if "style" in kwargs:
            style = kwargs.pop("style")
            old_style = self._style_name
            self._style_name = style
            if old_style and old_style != style:
                self._smooth_style_transition(old_style, style)
            else:
                self._apply_style(style)

        # 处理其余 Frame 属性
        try:
            super().configure(**kwargs)
        except Exception:
            pass

    # 兼容 cget
    def cget(self, key):
        if key == "text":
            return self._label.cget("text")
        if key == "state":
            return self._state
        return super().cget(key)

    def apply_theme(self):
        # 在主题切换时重新应用风格
        if getattr(self, "_style_manager", None):
            self._colors = self._style_manager.colors
            self._refresh_style_map()
            self._apply_style(self._style_name)


class CTCard(CTFrame):
    """卡片容器：带边框和可选标题，支持轻量悬停效果（带动画）"""
    def __init__(self, parent, style_manager: Optional[Any] = None, title: str = "", **kwargs):
        colors = style_manager.colors if style_manager else {}
        super().__init__(parent, style_manager=style_manager, bg=colors.get("bg_card") if style_manager else None, **kwargs)
        self._style_manager = style_manager
        self._border_default = colors.get("border")
        self.configure(highlightbackground=self._border_default, highlightthickness=1)
        if title:
            title_frame = CTFrame(self, style_manager=style_manager, bg=colors.get("bg_secondary"))
            title_frame.pack(fill=tk.X, padx=1, pady=1)
            title_label = CTLabel(title_frame, style_manager=style_manager, text=title, fg=colors.get("accent"))
            title_label.pack(fill=tk.X)

        self._hover_tag = None
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _smooth_border(self, target_color, steps=8):
        try:
            current = self.cget("highlightbackground") or self._border_default
        except Exception:
            current = self._border_default
        tag = object()
        self._hover_tag = tag

        def _lerp(c1, c2, t):
            def _h(hx):
                hx = hx.lstrip("#")
                return tuple(int(hx[i:i+2], 16) for i in (0, 2, 4))
            def _f(r, g, b):
                return f"#{int(r):02x}{int(g):02x}{int(b):02x}"
            r1, g1, b1 = _h(c1)
            r2, g2, b2 = _h(c2)
            return _f(r1 + (r2 - r1) * t, g1 + (g2 - g1) * t, b1 + (b2 - b1) * t)

        def tick(i):
            if getattr(self, '_hover_tag', None) is not tag:
                return
            if i < steps:
                t = (i + 1) / steps
                color = _lerp(current, target_color, t)
                try:
                    self.configure(highlightbackground=color)
                except Exception:
                    pass
                self.after(16, tick, i + 1)
            else:
                try:
                    self.configure(highlightbackground=target_color)
                except Exception:
                    pass

        tick(0)

    def _on_enter(self, event=None):
        try:
            colors = self._style_manager.colors
            self._smooth_border(colors.get("accent"), steps=8)
        except Exception:
            pass

    def _on_leave(self, event=None):
        try:
            colors = self._style_manager.colors
            self._smooth_border(colors.get("border"), steps=6)
        except Exception:
            pass


class CTProgressbar(ttk.Progressbar):
    """进度条封装，用以统一扩展点"""
    def __init__(self, parent, style_manager: Optional[Any] = None, **kwargs):
        self._style_manager = style_manager
        super().__init__(parent, **kwargs)

    def apply_theme(self):
        return


class CTEntry(ttk.Entry):
    """主题感知的 Entry（基于 ttk.Entry）"""
    def __init__(self, parent, style_manager: Optional[Any] = None, textvariable=None, font: Optional[Any] = None, width: Optional[int] = None, show: Optional[str] = None, **kwargs):
        self._style_manager = style_manager
        if font is None and getattr(style_manager, "_fonts", None):
            font = style_manager._fonts.get("body")
        cfg = {}
        if show is not None:
            cfg['show'] = show
        super().__init__(parent, textvariable=textvariable, width=width, font=font, style="TEntry", **cfg, **kwargs)


class CTCombobox(ttk.Combobox):
    """主题感知的 Combobox（基于 ttk.Combobox）"""
    def __init__(self, parent, style_manager: Optional[Any] = None, values=None, textvariable=None, font: Optional[Any] = None, width: Optional[int] = None, state: str = "readonly", **kwargs):
        self._style_manager = style_manager
        if font is None and getattr(style_manager, "_fonts", None):
            font = style_manager._fonts.get("body")
        super().__init__(parent, values=values or [], textvariable=textvariable, font=font, width=width, state=state, style="TCombobox", **kwargs)


class CTScrollableFrame(CTFrame):
    """可滚动的容器：内部使用 Canvas + 内层 Frame + 垂直滚动条。

    创建后可以通过属性访问内部对象：
    - `_canvas`：底层 Canvas
    - `_scrollbar`：垂直滚动条
    - `_scroll_frame`：内层用于放置内容的 CTFrame
    - `_canvas_window`：Canvas 中创建的窗口 id
    """
    def __init__(self, parent, style_manager: Optional[Any] = None, bg: Optional[str] = None, padx: int = 0, pady: int = 0, **kwargs):
        super().__init__(parent, style_manager=style_manager, bg=bg, **kwargs)
        colors = style_manager.colors if style_manager else {}

        # Canvas
        self._canvas = tk.Canvas(self, bg=bg or colors.get("bg_primary"), highlightthickness=0)

        # 内层 frame（使用 CTFrame 以保持主题感知）
        self._scroll_frame = CTFrame(self._canvas, style_manager=style_manager, bg=bg or colors.get("bg_primary"))

        # 垂直滚动条
        self._scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        # 布局
        self._scrollbar.grid(row=0, column=1, sticky="ns")
        self._canvas.grid(row=0, column=0, sticky="nsew")

        # 在 Canvas 中创建窗口
        self._canvas_window = self._canvas.create_window((0, 0), window=self._scroll_frame, anchor="nw", width=self._canvas.winfo_reqwidth())

        # 配置 grid 扩展
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # 内边距
        try:
            self._scroll_frame.configure(padx=padx, pady=pady)
        except Exception:
            pass

        # 绑定事件
        self._scroll_frame.bind("<Configure>", self._on_frame_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)

        # 鼠标滚轮支持（绑定到 canvas）
        self._canvas.bind("<MouseWheel>", self._on_mousewheel)
        self._canvas.bind("<Button-4>", self._on_mousewheel)
        self._canvas.bind("<Button-5>", self._on_mousewheel)

    def _on_frame_configure(self, event=None):
        try:
            self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        except Exception:
            pass

    def _on_canvas_configure(self, event=None):
        try:
            self._canvas.itemconfig(self._canvas_window, width=event.width)
        except Exception:
            pass

    def _on_mousewheel(self, event):
        try:
            if event.num == 4:
                self._canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self._canvas.yview_scroll(1, "units")
            else:
                self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass


__all__ = ["CTFrame", "CTLabel", "CTButton", "CTCard", "CTProgressbar", "CTEntry", "CTCombobox", "CTScrollableFrame"]
