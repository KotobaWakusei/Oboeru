"""导航栏组件"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Dict, Optional, TYPE_CHECKING
from ui.customtinker import CTFrame, CTLabel, CTButton

if TYPE_CHECKING:
    from ui.core.style_manager import StyleManager


class NavBar(CTFrame):
    """顶部导航栏组件"""
    
    def __init__(
        self,
        parent: tk.Widget,
        style_manager: "StyleManager",
        on_navigate: Callable[[str], None],
        items: List[Dict[str, str]],
        **kwargs
    ):
        super().__init__(parent, style_manager=style_manager, **kwargs)
        
        self._style_manager = style_manager
        self._on_navigate = on_navigate
        self._items = items
        self._nav_buttons: Dict[str, ttk.Button] = {}
        self._center_frame: CTFrame
        self._left_frame: CTFrame
        self._right_frame: CTFrame
        
        self._create_widgets()
    
    def _create_widgets(self):
        """创建组件"""
        colors = self._style_manager.colors
        
        self.configure(
            bg=colors["bg_secondary"],
            height=60
        )
        self.grid_propagate(False)
        
        # 内部容器
        inner = CTFrame(self, style_manager=self._style_manager, bg=colors["bg_secondary"])
        inner.grid(row=0, column=0, sticky="nsew", padx=16, pady=9)
        inner.columnconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # 左侧 - Logo
        self._left_frame = CTFrame(
            inner, style_manager=self._style_manager, bg=colors["bg_secondary"]
        )
        self._left_frame.grid(row=0, column=0, sticky="w")

        logo = CTLabel(
            self._left_frame,
            style_manager=self._style_manager,
            text="🎯",
            font=("Segoe UI", 24),
            bg=colors["bg_secondary"],
            fg=colors["accent"]
        )
        logo.pack(side=tk.LEFT, padx=(0, 10))
        
        self._title_label = CTLabel(
            self._left_frame,
            style_manager=self._style_manager,
            text="智能背单词",
            font=self._style_manager.get_font("heading"),
            bg=colors["bg_secondary"],
            fg=colors["fg_primary"]
        )
        self._title_label.pack(side=tk.LEFT)
        
        # 中间 - 导航按钮
        self._center_frame = CTFrame(
            inner, style_manager=self._style_manager, bg=colors["bg_secondary"]
        )
        self._center_frame.grid(row=0, column=1)
        
        for item in self._items:
            btn = CTButton(
                self._center_frame,
                style_manager=self._style_manager,
                text=f"{item['icon']} {item.get('title', '')}",
                command=lambda pid=item['id']: self._on_navigate(pid),
                style="Nav.TButton",
                padding=(10, 7),
            )
            btn.pack(side=tk.LEFT, padx=5)
            self._nav_buttons[item['id']] = btn
        
        # 右侧 - 可扩展区域
        self._right_frame = CTFrame(inner, style_manager=self._style_manager, bg=colors["bg_secondary"])
        self._right_frame.grid(row=0, column=2, sticky="e")
        self.bind("<Configure>", self._on_resize)

    def refresh_layout(self, width: Optional[int] = None):
        """Refresh title and button labels for the current width."""
        if width is None:
            width = self.winfo_width()
        if width <= 1:
            width = self.winfo_toplevel().winfo_width()

        title_text = "智能背单词"
        if width < 780:
            title_text = "Oboeru"
        self._title_label.configure(text=title_text)

        compact = width < 700
        for item in self._items:
            pid = item["id"]
            icon = item.get("icon", "")
            title = item.get("title", "")
            if pid in self._nav_buttons:
                self._nav_buttons[pid].configure(
                    text=icon if compact else f"{icon} {title}"
                )

    def _on_resize(self, event):
        """Keep the navbar readable on narrow windows."""
        self.refresh_layout(event.width)
    
    def set_active(self, page_id: str):
        """设置当前激活的导航项"""
        for pid, btn in self._nav_buttons.items():
            if pid == page_id:
                btn.configure(style="Primary.TButton")
            else:
                btn.configure(style="Nav.TButton")
    
    def add_right_widget(self, widget: tk.Widget):
        """在右侧添加组件"""
        widget.pack(in_=self._right_frame, side=tk.RIGHT, padx=5)

    def apply_translation(self, translate_func: Callable[[str, str], str]):
        """应用翻译：更新标题和按钮文本（由 Application 提供 translate 方法）"""
        try:
            # 更新应用标题
            try:
                if getattr(self, '_title_label', None):
                    self._title_label.configure(text=translate_func('app.title', '智能背单词'))
            except Exception:
                pass

            # 更新导航按钮文本
            for item in self._items:
                pid = item.get('id')
                icon = item.get('icon', '')
                default = item.get('title', '')
                try:
                    translated = translate_func(f'nav.{pid}', default)
                    item['title'] = translated
                except Exception:
                    pass
            self.refresh_layout()
        except Exception:
            pass
    
    def apply_theme(self):
        """应用主题"""
        colors = self._style_manager.colors
        self.configure(bg=colors["bg_secondary"])
        try:
            self._left_frame.configure(bg=colors["bg_secondary"])
            self._center_frame.configure(bg=colors["bg_secondary"])
            self._right_frame.configure(bg=colors["bg_secondary"])
            self._title_label.configure(fg=colors["fg_primary"], bg=colors["bg_secondary"])
        except Exception:
            pass
        for button in self._nav_buttons.values():
            try:
                button.apply_theme()
            except Exception:
                pass
