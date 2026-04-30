"""页面基类 - 所有页面的抽象基类"""
import tkinter as tk
from tkinter import ttk
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .application import Application
    from .style_manager import StyleManager


class BasePage(ABC, tk.Frame):
    """页面基类，所有页面都需要继承此类"""
    
    # 页面标识符
    page_id: str = "base"
    page_title: str = "基础页面"
    page_icon: str = ""
    
    def __init__(self, parent: tk.Widget, app: "Application"):
        super().__init__(parent)
        self._app = app
        self._style_manager: "StyleManager" = app.style_manager
        self._is_initialized = False
        self._is_visible = False
        
        # 配置页面框架
        self.configure(bg=self._style_manager.colors["bg_primary"])
        self._setup_page()
        self._is_initialized = True
    
    @property
    def app(self) -> "Application":
        return self._app
    
    @property
    def colors(self) -> dict:
        return self._style_manager.colors
    
    def _setup_page(self):
        """设置页面结构"""
        # 创建主容器
        self._container = tk.Frame(self, bg=self.colors["bg_primary"])
        self._container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # 子类实现具体内容
        self.create_widgets()
        self.setup_layout()
        self.bind_events()
    
    @abstractmethod
    def create_widgets(self):
        """创建页面组件 - 子类必须实现"""
        pass
    
    @abstractmethod
    def setup_layout(self):
        """设置布局 - 子类必须实现"""
        pass
    
    def bind_events(self):
        """绑定事件 - 子类可选实现"""
        pass
    
    def on_enter(self, **kwargs):
        """页面进入时调用"""
        self._is_visible = True
        self.refresh()
    
    def on_leave(self):
        """页面离开时调用"""
        self._is_visible = False
    
    def refresh(self):
        """刷新页面内容 - 子类可选实现"""
        pass
    
    def apply_theme(self):
        """应用主题 - 子类可选实现"""
        self.configure(bg=self.colors["bg_primary"])
        self._container.configure(bg=self.colors["bg_primary"])
    
    def create_card(self, parent: tk.Widget, title: str = "") -> tk.Frame:
        """创建卡片容器"""
        colors = self.colors
        
        card = tk.Frame(
            parent,
            bg=colors["bg_card"],
            highlightbackground=colors["border"],
            highlightthickness=1
        )
        
        if title:
            title_frame = tk.Frame(card, bg=colors["bg_secondary"])
            title_frame.pack(fill=tk.X, padx=1, pady=1)
            
            title_label = tk.Label(
                title_frame,
                text=title,
                font=self._style_manager.get_font("subheading"),
                bg=colors["bg_secondary"],
                fg=colors["accent"],
                anchor="w",
                padx=15,
                pady=10
            )
            title_label.pack(fill=tk.X)
        
        return card
    
    def create_button(
        self, 
        parent: tk.Widget, 
        text: str, 
        command: callable,
        style: str = "Primary.TButton",
        icon: str = ""
    ) -> ttk.Button:
        """创建按钮"""
        btn_text = f"{icon} {text}" if icon else text
        btn = ttk.Button(
            parent,
            text=btn_text,
            command=command,
            style=style
        )
        return btn
    
    def create_label(
        self, 
        parent: tk.Widget, 
        text: str,
        style: str = "TLabel",
        **kwargs
    ) -> ttk.Label:
        """创建标签"""
        return ttk.Label(parent, text=text, style=style, **kwargs)
    
    def show_message(self, message: str, msg_type: str = "info"):
        """显示消息提示"""
        self._app.show_message(message, msg_type)
    
    def navigate_to(self, page_id: str, **kwargs):
        """导航到其他页面"""
        self._app.navigate_to(page_id, **kwargs)
    
    def go_back(self):
        """返回上一页"""
        self._app.go_back()
