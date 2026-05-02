"""导航栏组件"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Dict, TYPE_CHECKING
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
        
        self._create_widgets()
    
    def _create_widgets(self):
        """创建组件"""
        colors = self._style_manager.colors
        
        self.configure(
            bg=colors["bg_secondary"],
            height=60
        )
        self.pack_propagate(False)
        
        # 内部容器
        inner = CTFrame(self, style_manager=self._style_manager, bg=colors["bg_secondary"])
        inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 左侧 - Logo
        left_frame = CTFrame(inner, style_manager=self._style_manager, bg=colors["bg_secondary"])
        left_frame.pack(side=tk.LEFT)

        logo = CTLabel(
            left_frame,
            style_manager=self._style_manager,
            text="🎯",
            font=("Segoe UI", 24),
            bg=colors["bg_secondary"],
            fg=colors["accent"]
        )
        logo.pack(side=tk.LEFT, padx=(0, 10))
        
        title = CTLabel(
            left_frame,
            style_manager=self._style_manager,
            text="智能背单词",
            font=self._style_manager.get_font("heading"),
            bg=colors["bg_secondary"],
            fg=colors["fg_primary"]
        )
        title.pack(side=tk.LEFT)
        
        # 中间 - 导航按钮
        center_frame = CTFrame(inner, style_manager=self._style_manager, bg=colors["bg_secondary"])
        center_frame.pack(side=tk.LEFT, expand=True)
        
        for item in self._items:
            btn = CTButton(
                center_frame,
                style_manager=self._style_manager,
                text=f"{item['icon']} {item['title']}",
                command=lambda pid=item['id']: self._on_navigate(pid),
                style="Nav.TButton"
            )
            btn.pack(side=tk.LEFT, padx=5)
            self._nav_buttons[item['id']] = btn
        
        # 右侧 - 可扩展区域
        self._right_frame = CTFrame(inner, style_manager=self._style_manager, bg=colors["bg_secondary"])
        self._right_frame.pack(side=tk.RIGHT)
    
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
    
    def apply_theme(self):
        """应用主题"""
        colors = self._style_manager.colors
        
        self.configure(bg=colors["bg_secondary"])
        
        for child in self.winfo_children():
            self._update_colors(child, colors)
    
    def _update_colors(self, widget: tk.Widget, colors: dict):
        """递归更新颜色"""
        try:
            widget.configure(bg=colors["bg_secondary"])
        except Exception:
            pass
        
        for child in widget.winfo_children():
            if isinstance(child, tk.Label):
                try:
                    child.configure(bg=colors["bg_secondary"])
                except Exception:
                    pass
            elif isinstance(child, tk.Frame):
                self._update_colors(child, colors)
