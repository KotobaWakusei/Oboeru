"""进度指示器组件"""
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ui.core.style_manager import StyleManager

from ui.customtinker import CTFrame, CTLabel, CTProgressbar


class ProgressIndicator(CTFrame):
    """进度指示器组件"""
    
    def __init__(
        self,
        parent: tk.Widget,
        style_manager: "StyleManager",
        **kwargs
    ):
        super().__init__(parent, style_manager=style_manager, **kwargs)
        
        self._style_manager = style_manager
        self._current = 0
        self._total = 0
        
        self._create_widgets()
    
    def _create_widgets(self):
        """创建组件"""
        colors = self._style_manager.colors
        
        self.configure(bg=colors["bg_primary"])

        # 阶段标签
        self._stage_label = CTLabel(
            self,
            style_manager=self._style_manager,
            text="准备开始",
            font=self._style_manager.get_font("heading"),
            bg=colors["bg_primary"],
            fg=colors["fg_primary"]
        )
        self._stage_label.pack(side=tk.LEFT)

        # 右侧容器
        right_frame = CTFrame(self, style_manager=self._style_manager, bg=colors["bg_primary"])
        right_frame.pack(side=tk.RIGHT)

        # 百分比标签
        self._percent_label = CTLabel(
            right_frame,
            style_manager=self._style_manager,
            text="0%",
            font=self._style_manager.get_font("body"),
            bg=colors["bg_primary"],
            fg=colors["accent"]
        )
        self._percent_label.pack(side=tk.RIGHT, padx=(10, 0))

        # 进度条
        self._progress_bar = CTProgressbar(
            right_frame,
            style_manager=self._style_manager,
            mode='determinate',
            length=200,
            maximum=100
        )
        self._progress_bar.pack(side=tk.RIGHT)
    
    def set_stage(self, stage: str):
        """设置阶段"""
        self._stage_label.configure(text=stage)
    
    def update_progress(self, current: int, total: int):
        """更新进度"""
        self._current = current
        self._total = total
        
        if total > 0:
            percent = (current / total) * 100
            self._progress_bar["value"] = percent
            self._percent_label.configure(text=f"{int(percent)}%")
        else:
            self._progress_bar["value"] = 0
            self._percent_label.configure(text="0%")
    
    def reset(self):
        """重置"""
        self._current = 0
        self._total = 0
        self._stage_label.configure(text="准备开始")
        self._progress_bar["value"] = 0
        self._percent_label.configure(text="0%")
    
    def get_progress_text(self) -> str:
        """获取进度文本"""
        if self._total > 0:
            return f"{self._current}/{self._total}"
        return ""
    
    def apply_theme(self):
        """应用主题"""
        colors = self._style_manager.colors
        
        self.configure(bg=colors["bg_primary"])
        self._stage_label.configure(bg=colors["bg_primary"], fg=colors["fg_primary"])
        self._percent_label.configure(bg=colors["bg_primary"], fg=colors["accent"])
        
        # 更新右侧框架
        for child in self.winfo_children():
            if isinstance(child, tk.Frame):
                child.configure(bg=colors["bg_primary"])
                for subchild in child.winfo_children():
                    if isinstance(subchild, tk.Label):
                        subchild.configure(bg=colors["bg_primary"])
