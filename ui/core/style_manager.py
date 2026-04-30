"""样式管理器 - 现代化主题系统"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional, Callable


class StyleManager:
    """现代化样式管理器，支持多主题切换"""
    
    # 预定义主题
    THEMES = {
        "default": {
            "name": "默认主题",
            "bg_primary": "#1a1a2e",
            "bg_secondary": "#16213e",
            "bg_card": "#0f3460",
            "fg_primary": "#e8e8e8",
            "fg_secondary": "#a0a0a0",
            "accent": "#e94560",
            "accent_hover": "#ff6b6b",
            "success": "#00d9a5",
            "warning": "#ffc107",
            "error": "#ff4757",
            "border": "#2d4263",
            "gradient_start": "#e94560",
            "gradient_end": "#0f3460",
        },
        "dark": {
            "name": "深邃夜空",
            "bg_primary": "#1a1a2e",
            "bg_secondary": "#16213e",
            "bg_card": "#0f3460",
            "fg_primary": "#e8e8e8",
            "fg_secondary": "#a0a0a0",
            "accent": "#e94560",
            "accent_hover": "#ff6b6b",
            "success": "#00d9a5",
            "warning": "#ffc107",
            "error": "#ff4757",
            "border": "#2d4263",
            "gradient_start": "#e94560",
            "gradient_end": "#0f3460",
        },
        "ocean": {
            "name": "海洋之心",
            "bg_primary": "#0a1628",
            "bg_secondary": "#1a2f4a",
            "bg_card": "#0d3b66",
            "fg_primary": "#f0f4f8",
            "fg_secondary": "#8ba4bc",
            "accent": "#00b4d8",
            "accent_hover": "#48cae4",
            "success": "#06d6a0",
            "warning": "#ffd60a",
            "error": "#ef476f",
            "border": "#1e4a6e",
            "gradient_start": "#00b4d8",
            "gradient_end": "#03045e",
        },
        "forest": {
            "name": "森林秘境",
            "bg_primary": "#1a1d1a",
            "bg_secondary": "#2d3a2d",
            "bg_card": "#3d5a3d",
            "fg_primary": "#e8f0e8",
            "fg_secondary": "#a0b8a0",
            "accent": "#7cb518",
            "accent_hover": "#9dd529",
            "success": "#00c896",
            "warning": "#fbbf24",
            "error": "#ef4444",
            "border": "#4a6b4a",
            "gradient_start": "#7cb518",
            "gradient_end": "#1a4d1a",
        },
        "sunset": {
            "name": "日落余晖",
            "bg_primary": "#1f1a24",
            "bg_secondary": "#2d2433",
            "bg_card": "#3d2d47",
            "fg_primary": "#faf0e6",
            "fg_secondary": "#c4aeb0",
            "accent": "#ff6b35",
            "accent_hover": "#ff8c5a",
            "success": "#4ade80",
            "warning": "#fbbf24",
            "error": "#f87171",
            "border": "#5d3d6b",
            "gradient_start": "#ff6b35",
            "gradient_end": "#4a1d6a",
        },
        "light": {
            "name": "简约白",
            "bg_primary": "#f8f9fa",
            "bg_secondary": "#ffffff",
            "bg_card": "#ffffff",
            "fg_primary": "#212529",
            "fg_secondary": "#6c757d",
            "accent": "#0d6efd",
            "accent_hover": "#0b5ed7",
            "success": "#198754",
            "warning": "#ffc107",
            "error": "#dc3545",
            "border": "#dee2e6",
            "gradient_start": "#0d6efd",
            "gradient_end": "#6610f2",
        },
        "mint": {
            "name": "薄荷清新",
            "bg_primary": "#e8f5e9",
            "bg_secondary": "#c8e6c9",
            "bg_card": "#a5d6a7",
            "fg_primary": "#1b5e20",
            "fg_secondary": "#4caf50",
            "accent": "#00897b",
            "accent_hover": "#00acc1",
            "success": "#2e7d32",
            "warning": "#ff8f00",
            "error": "#c62828",
            "border": "#81c784",
            "gradient_start": "#00897b",
            "gradient_end": "#1b5e20",
        },
    }
    
    def __init__(self, theme_name: str = "dark"):
        self._current_theme = theme_name
        self._theme_changed_callbacks: list[Callable] = []
        self._style: Optional[ttk.Style] = None
        # 优化后的字体大小，更适合中等窗口
        self._fonts = {
            "title": ("Segoe UI", 22, "bold"),
            "heading": ("Segoe UI", 16, "bold"),
            "subheading": ("Segoe UI", 13, "bold"),
            "body": ("Segoe UI", 11),
            "caption": ("Segoe UI", 10),
            "button": ("Segoe UI", 11, "bold"),
            "small": ("Segoe UI", 9),
            "word": ("Segoe UI", 28, "bold"),  # 单词专用字体
        }
    
    @property
    def current_theme(self) -> str:
        return self._current_theme
    
    @property
    def colors(self) -> Dict[str, str]:
        return self.THEMES[self._current_theme].copy()
    
    def get_theme_name(self) -> str:
        return self.THEMES[self._current_theme]["name"]
    
    def get_available_themes(self) -> list[str]:
        return list(self.THEMES.keys())
    
    def set_theme(self, theme_name: str) -> bool:
        if theme_name in self.THEMES:
            self._current_theme = theme_name
            self._notify_theme_changed()
            return True
        return False
    
    def on_theme_changed(self, callback: Callable):
        self._theme_changed_callbacks.append(callback)
    
    def _notify_theme_changed(self):
        for callback in self._theme_changed_callbacks:
            callback()
    
    def setup_styles(self, root: tk.Tk):
        """设置ttk样式"""
        self._style = ttk.Style()
        colors = self.colors
        
        # 基础设置
        self._style.theme_use('clam')
        
        # Frame样式
        self._style.configure(
            "TFrame",
            background=colors["bg_primary"]
        )
        self._style.configure(
            "Card.TFrame",
            background=colors["bg_card"]
        )
        self._style.configure(
            "Secondary.TFrame",
            background=colors["bg_secondary"]
        )
        
        # Label样式
        self._style.configure(
            "TLabel",
            background=colors["bg_primary"],
            foreground=colors["fg_primary"],
            font=self._fonts["body"]
        )
        self._style.configure(
            "Title.TLabel",
            background=colors["bg_primary"],
            foreground=colors["accent"],
            font=self._fonts["title"]
        )
        self._style.configure(
            "Heading.TLabel",
            background=colors["bg_primary"],
            foreground=colors["fg_primary"],
            font=self._fonts["heading"]
        )
        self._style.configure(
            "Subheading.TLabel",
            background=colors["bg_primary"],
            foreground=colors["fg_secondary"],
            font=self._fonts["subheading"]
        )
        self._style.configure(
            "Caption.TLabel",
            background=colors["bg_primary"],
            foreground=colors["fg_secondary"],
            font=self._fonts["caption"]
        )
        
        # Button样式
        self._style.configure(
            "TButton",
            background=colors["accent"],
            foreground=colors["fg_primary"],
            font=self._fonts["button"],
            padding=(20, 12),
            borderwidth=0,
            focuscolor='none'
        )
        self._style.map(
            "TButton",
            background=[
                ("active", colors["accent_hover"]),
                ("pressed", colors["accent"]),
                ("disabled", colors["bg_secondary"])
            ],
            foreground=[
                ("disabled", colors["fg_secondary"])
            ]
        )
        
        # 主要按钮
        self._style.configure(
            "Primary.TButton",
            background=colors["accent"],
            foreground="#ffffff",
            font=self._fonts["button"],
            padding=(24, 14),
            borderwidth=0
        )
        self._style.map(
            "Primary.TButton",
            background=[
                ("active", colors["accent_hover"]),
                ("pressed", colors["accent"])
            ],
            foreground=[
                ("active", "#ffffff"),
                ("pressed", "#ffffff")
            ]
        )
        
        # 次要按钮
        self._style.configure(
            "Secondary.TButton",
            background=colors["bg_secondary"],
            foreground=colors["fg_primary"],
            font=self._fonts["button"],
            padding=(20, 12),
            borderwidth=2,
            bordercolor=colors["border"]
        )
        self._style.map(
            "Secondary.TButton",
            background=[
                ("active", colors["bg_card"]),
                ("pressed", colors["bg_secondary"])
            ]
        )
        
        # 导航按钮
        self._style.configure(
            "Nav.TButton",
            background=colors["bg_secondary"],
            foreground=colors["fg_primary"],
            font=self._fonts["button"],
            padding=(16, 10),
            borderwidth=0
        )
        self._style.map(
            "Nav.TButton",
            background=[
                ("active", colors["bg_card"]),
                ("pressed", colors["accent"])
            ],
            foreground=[
                ("active", colors["fg_primary"]),
                ("pressed", "#ffffff")
            ]
        )
        
        # 收藏按钮
        self._style.configure(
            "Favorite.TButton",
            background=colors["warning"],
            foreground="#ffffff",
            font=self._fonts["button"],
            padding=(16, 10)
        )
        
        # 选项按钮
        self._style.configure(
            "Option.TButton",
            background=colors["bg_card"],
            foreground=colors["fg_primary"],
            font=self._fonts["body"],
            padding=(16, 14),
            borderwidth=1,
            bordercolor=colors["border"]
        )
        self._style.map(
            "Option.TButton",
            background=[
                ("active", colors["accent"]),
                ("selected", colors["success"])
            ]
        )
        
        # Entry样式
        self._style.configure(
            "TEntry",
            fieldbackground=colors["bg_secondary"],
            foreground=colors["fg_primary"],
            selectbackground=colors["accent"],
            selectforeground="#ffffff",
            insertcolor=colors["fg_primary"],
            insertwidth=1,
            bordercolor=colors["border"],
            lightcolor=colors["accent"],
            darkcolor=colors["border"],
            padding=8
        )
        self._style.map(
            "TEntry",
            fieldbackground=[
                ("focus", colors["bg_card"]),
                ("!focus", colors["bg_secondary"])
            ]
        )
        
        # LabelFrame样式
        self._style.configure(
            "TLabelframe",
            background=colors["bg_primary"],
            foreground=colors["fg_primary"],
            bordercolor=colors["border"]
        )
        self._style.configure(
            "TLabelframe.Label",
            background=colors["bg_primary"],
            foreground=colors["accent"],
            font=self._fonts["subheading"]
        )
        
        # Progressbar样式
        self._style.configure(
            "TProgressbar",
            background=colors["accent"],
            troughcolor=colors["bg_secondary"],
            borderwidth=0,
            lightcolor=colors["accent"],
            darkcolor=colors["accent"]
        )
        
        # Notebook样式 (用于标签页)
        self._style.configure(
            "TNotebook",
            background=colors["bg_primary"],
            borderwidth=0
        )
        self._style.configure(
            "TNotebook.Tab",
            background=colors["bg_secondary"],
            foreground=colors["fg_secondary"],
            padding=(20, 10),
            borderwidth=0
        )
        self._style.map(
            "TNotebook.Tab",
            background=[
                ("selected", colors["accent"]),
                ("active", colors["bg_card"])
            ],
            foreground=[
                ("selected", colors["fg_primary"]),
                ("active", colors["fg_primary"])
            ]
        )
        
        # Scrollbar样式
        self._style.configure(
            "TScrollbar",
            background=colors["bg_secondary"],
            troughcolor=colors["bg_primary"],
            borderwidth=0,
            arrowcolor=colors["fg_secondary"]
        )
        self._style.map(
            "TScrollbar",
            background=[
                ("active", colors["accent"])
            ]
        )
        
        # Treeview样式
        self._style.configure(
            "Treeview",
            background=colors["bg_secondary"],
            foreground=colors["fg_primary"],
            fieldbackground=colors["bg_secondary"],
            borderwidth=0
        )
        self._style.configure(
            "Treeview.Heading",
            background=colors["bg_card"],
            foreground=colors["fg_primary"],
            font=self._fonts["button"],
            borderwidth=0
        )
        self._style.map(
            "Treeview",
            background=[
                ("selected", colors["accent"])
            ],
            foreground=[
                ("selected", colors["fg_primary"])
            ]
        )
        
        # Checkbutton样式
        self._style.configure(
            "TCheckbutton",
            background=colors["bg_primary"],
            foreground=colors["fg_primary"],
            font=self._fonts["body"]
        )
        self._style.map(
            "TCheckbutton",
            background=[
                ("active", colors["bg_primary"])
            ]
        )
        
        # Combobox样式
        self._style.configure(
            "TCombobox",
            fieldbackground=colors["bg_secondary"],
            background=colors["bg_card"],
            foreground=colors["fg_primary"],
            arrowcolor=colors["fg_primary"],
            selectbackground=colors["accent"],
            selectforeground="#ffffff",
            insertcolor=colors["fg_primary"],
            insertwidth=1,
            borderwidth=1,
            bordercolor=colors["border"]
        )
        self._style.map(
            "TCombobox",
            fieldbackground=[
                ("focus", colors["bg_card"]),
                ("!focus", colors["bg_secondary"])
            ],
            background=[
                ("active", colors["accent"]),
                ("readonly", colors["bg_secondary"])
            ],
            foreground=[
                ("disabled", colors["fg_secondary"])
            ]
        )
        
        # 设置根窗口背景
        root.configure(bg=colors["bg_primary"])
    
    def get_font(self, font_type: str) -> tuple:
        return self._fonts.get(font_type, self._fonts["body"])
    
    def create_rounded_frame(self, parent: tk.Widget, **kwargs) -> tk.Frame:
        """创建圆角框架效果"""
        colors = self.colors
        frame = tk.Frame(
            parent,
            bg=colors["bg_card"],
            highlightbackground=colors["border"],
            highlightthickness=1,
            **kwargs
        )
        return frame
