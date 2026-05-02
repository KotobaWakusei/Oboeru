"""页面基类 - 所有页面的抽象基类"""
import tkinter as tk
from tkinter import ttk
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

from ui.customtinker import CTFrame, CTLabel, CTButton, CTCard

if TYPE_CHECKING:
    from .application import Application
    from .style_manager import StyleManager


class BasePage(ABC, CTFrame):
    """页面基类，所有页面都需要继承此类"""
    
    # 页面标识符
    page_id: str = "base"
    page_title: str = "基础页面"
    page_icon: str = ""
    
    def __init__(self, parent: tk.Widget, app: "Application"):
        super().__init__(parent, style_manager=app.style_manager)
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
        self._container = CTFrame(self, style_manager=self._style_manager, bg=self.colors["bg_primary"]) 
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

    def apply_translation(self):
        """在语言切换时调用，默认重建页面以刷新文本内容。"""
        if not self._is_initialized:
            return
        try:
            if hasattr(self, '_container') and self._container:
                self._container.destroy()
            self._setup_page()
            self.apply_theme()
        except Exception:
            pass

    def _t(self, key: str, default: str = "") -> str:
        """快捷翻译方法"""
        try:
            return self.app.language_manager.translate(key, default)
        except Exception:
            return default

    def create_card(self, parent: tk.Widget, title: str = "") -> tk.Frame:
        """创建卡片容器"""
        colors = self.colors
        card = CTCard(parent, style_manager=self._style_manager, title=title)
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
        btn = CTButton(parent, style_manager=self._style_manager, text=btn_text, command=command, style=style)
        return btn
    
    def create_label(
        self, 
        parent: tk.Widget, 
        text: str,
        style: str = "TLabel",
        **kwargs
    ) -> ttk.Label:
        """创建标签"""
        # 使用 CTLabel 以支持主题感知的 tk.Label
        return CTLabel(parent, style_manager=self._style_manager, text=text, **kwargs)
    
    def show_message(self, message: str, msg_type: str = "info"):
        """显示消息提示"""
        self._app.show_message(message, msg_type)
    
    def navigate_to(self, page_id: str, **kwargs):
        """导航到其他页面"""
        self._app.navigate_to(page_id, **kwargs)
    
    def go_back(self):
        """返回上一页"""
        self._app.go_back()
