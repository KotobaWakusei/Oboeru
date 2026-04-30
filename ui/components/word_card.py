"""单词卡片组件"""
import tkinter as tk
from tkinter import ttk
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ui.core.style_manager import StyleManager


class WordCard(tk.Frame):
    """单词显示卡片组件"""
    
    def __init__(
        self,
        parent: tk.Widget,
        style_manager: "StyleManager",
        on_click: Optional[callable] = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        
        self._style_manager = style_manager
        self._on_click = on_click
        self._is_interactive = False
        
        self._create_widgets()
    
    def _create_widgets(self):
        """创建组件"""
        colors = self._style_manager.colors
        
        self.configure(
            bg=colors["bg_card"],
            highlightbackground=colors["border"],
            highlightthickness=1
        )
        
        # 内容容器
        self._content = tk.Frame(self, bg=colors["bg_card"])
        self._content.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        # 单词标签
        self._word_label = tk.Label(
            self._content,
            text="",
            font=("Segoe UI", 36, "bold"),
            bg=colors["bg_card"],
            fg=colors["accent"]
        )
        self._word_label.pack(expand=True)
        
        # 词性标签
        self._pos_label = tk.Label(
            self._content,
            text="",
            font=self._style_manager.get_font("subheading"),
            bg=colors["bg_card"],
            fg=colors["warning"]
        )
        self._pos_label.pack(pady=(10, 0))
    
    def set_word(self, word: str, pos: str = ""):
        """设置单词"""
        self._word_label.configure(text=word)
        self._pos_label.configure(text=pos)
    
    def set_interactive(self, interactive: bool = True):
        """设置是否可交互"""
        self._is_interactive = interactive
        
        if interactive:
            self._word_label.configure(cursor="hand2")
            self._word_label.bind("<Button-1>", self._handle_click)
            self._word_label.bind("<Double-Button-1>", self._handle_click)
        else:
            self._word_label.configure(cursor="")
            self._word_label.unbind("<Button-1>")
            self._word_label.unbind("<Double-Button-1>")
    
    def _handle_click(self, event):
        """处理点击"""
        if self._on_click and self._is_interactive:
            self._on_click()
    
    def set_font_size(self, size: int):
        """设置字体大小"""
        self._word_label.configure(font=("Segoe UI", size, "bold"))
    
    def clear(self):
        """清空"""
        self._word_label.configure(text="")
        self._pos_label.configure(text="")
    
    def set_placeholder(self, text: str = "点击「开始学习」开始"):
        """设置占位文本"""
        self._word_label.configure(text=text)
        self._pos_label.configure(text="")
    
    def apply_theme(self):
        """应用主题"""
        colors = self._style_manager.colors
        
        self.configure(
            bg=colors["bg_card"],
            highlightbackground=colors["border"]
        )
        
        self._content.configure(bg=colors["bg_card"])
        self._word_label.configure(bg=colors["bg_card"], fg=colors["accent"])
        self._pos_label.configure(bg=colors["bg_card"], fg=colors["warning"])
