"""页面管理器 - 管理页面切换和导航历史"""
import tkinter as tk
from typing import Dict, List, Optional, Type, TYPE_CHECKING
from collections import deque

if TYPE_CHECKING:
    from .base_page import BasePage
    from .application import Application


class PageManager:
    """页面管理器，负责页面的注册、创建和切换"""
    
    def __init__(self, app: "Application"):
        self._app = app
        self._pages: Dict[str, Type["BasePage"]] = {}
        self._instances: Dict[str, "BasePage"] = {}
        self._navigation_history: deque = deque(maxlen=20)
        self._current_page: Optional["BasePage"] = None
        self._page_kwargs: Dict[str, dict] = {}
    
    def register(self, page_class: Type["BasePage"]):
        """注册页面类"""
        page_id = page_class.page_id
        if page_id in self._pages:
            raise ValueError(f"页面 '{page_id}' 已经注册")
        self._pages[page_id] = page_class
    
    def register_all(self, page_classes: list):
        """批量注册页面类"""
        for page_class in page_classes:
            self.register(page_class)
    
    def get_page(self, page_id: str) -> Optional["BasePage"]:
        """获取页面实例（懒加载）"""
        if page_id not in self._pages:
            return None
        
        # 如果实例不存在，创建新实例
        if page_id not in self._instances:
            page_class = self._pages[page_id]
            self._instances[page_id] = page_class(self._app.page_container, self._app)
        
        return self._instances[page_id]
    
    def navigate_to(self, page_id: str, **kwargs) -> bool:
        """导航到指定页面"""
        if page_id not in self._pages:
            return False
        # 如果已经在目标页面，避免重复将当前页加入历史并仅刷新页面
        if self._current_page and self._current_page.page_id == page_id:
            # 保存页面参数并调用 on_enter 做刷新
            self._page_kwargs[page_id] = kwargs
            try:
                self._current_page.on_enter(**kwargs)
            except Exception:
                pass
            return True

        # 记录导航历史（仅当将要切换到不同页面时）
        if self._current_page:
            self._navigation_history.append(self._current_page.page_id)
            self._current_page.on_leave()
        
        # 获取目标页面
        target_page = self.get_page(page_id)
        if not target_page:
            return False
        
        # 保存页面参数
        self._page_kwargs[page_id] = kwargs
        
        # 隐藏当前页面
        if self._current_page:
            self._current_page.pack_forget()
        
        # 显示目标页面
        target_page.pack(fill=tk.BOTH, expand=True)
        target_page.on_enter(**kwargs)
        
        self._current_page = target_page
        return True
    
    def go_back(self) -> bool:
        """返回上一页"""
        if not self._navigation_history:
            return False
        
        previous_page_id = self._navigation_history.pop()
        return self._navigate_without_history(previous_page_id)
    
    def _navigate_without_history(self, page_id: str) -> bool:
        """导航但不记录历史（用于返回操作）"""
        if page_id not in self._pages:
            return False
        
        if self._current_page:
            self._current_page.on_leave()
            self._current_page.pack_forget()
        
        target_page = self.get_page(page_id)
        if not target_page:
            return False
        
        kwargs = self._page_kwargs.get(page_id, {})
        target_page.pack(fill=tk.BOTH, expand=True)
        target_page.on_enter(**kwargs)
        
        self._current_page = target_page
        return True
    
    @property
    def current_page(self) -> Optional["BasePage"]:
        return self._current_page
    
    @property
    def current_page_id(self) -> Optional[str]:
        return self._current_page.page_id if self._current_page else None
    
    def can_go_back(self) -> bool:
        """是否可以返回"""
        return len(self._navigation_history) > 0
    
    def get_history(self) -> List[str]:
        """获取导航历史"""
        return list(self._navigation_history)
    
    def clear_history(self):
        """清空导航历史"""
        self._navigation_history.clear()
    
    def apply_theme_to_all(self):
        """对所有已创建的页面应用主题"""
        for page in self._instances.values():
            page.apply_theme()

    def apply_translation_to_all(self):
        """对所有已创建的页面应用当前语言翻译"""
        for page in self._instances.values():
            try:
                page.apply_translation()
            except Exception:
                pass
