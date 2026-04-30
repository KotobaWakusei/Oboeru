"""应用程序核心类 - 应用入口和主控制"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any
import os

from .style_manager import StyleManager
from .page_manager import PageManager
from modules.config_manager import ConfigManager
from modules.vocabulary_manager import VocabularyManager
from modules.favorites_manager import FavoritesManager
from modules.ai_manager import AIManager
from modules.logger import get_logger


class Application:
    """应用程序核心类"""
    
    def __init__(self, root: Optional[tk.Tk] = None):
        # 初始化根窗口
        self._root = root or tk.Tk()
        
        # 核心组件
        self._config = ConfigManager()
        self._style_manager = StyleManager(
            self._config.get("theme", "dark")
        )
        self._page_manager = PageManager(self)
        
        # 业务管理器
        self._vocabulary_manager = VocabularyManager()
        self._favorites_manager = FavoritesManager()
        
        # 日志
        self._logger = get_logger()
        
        # 学习状态
        self._today_words = []
        self._current_word_index = 0
        self._unknown_words = []
        self._stage = "recite"
        self._test_mode = False
        
        # 初始化TTS
        from modules.tts_manager import TTSManager
        self._tts_manager = TTSManager()
        
        # 初始化进度管理器
        from modules.progress_manager import ProgressManager
        self._progress_manager = ProgressManager()
        
        # 初始化 AI 管理器
        self._ai_manager = AIManager()
        self._ai_manager.configure(
            api_key=self._config.get("ai_api_key", ""),
            provider=self._config.get("ai_provider", "xunfei_lite"),
            custom_url=self._config.get("ai_custom_url", ""),
            custom_model=self._config.get("ai_custom_model", ""),
            difficulty=self._config.get("ai_difficulty", "junior"),
            enabled=self._config.get_bool("ai_enabled", False),
            timeout=self._config.get_int("ai_timeout", 30)
        )
        
        # 消息提示
        self._message_label: Optional[tk.Label] = None
        self._message_timer: Optional[str] = None
        
        # 初始化应用
        self._setup_window()
        self._create_layout()
        self._register_pages()
        self._setup_bindings()
        
        # 启动自动保存
        self._favorites_manager.start_auto_save()
        
        # 导航到首页
        self.navigate_to("home")
        
        self._logger.info("应用程序初始化完成")
    
    @property
    def root(self) -> tk.Tk:
        return self._root
    
    @property
    def config(self) -> ConfigManager:
        return self._config
    
    @property
    def style_manager(self) -> StyleManager:
        return self._style_manager
    
    @property
    def page_manager(self) -> PageManager:
        return self._page_manager
    
    @property
    def vocabulary_manager(self) -> VocabularyManager:
        return self._vocabulary_manager
    
    @property
    def favorites_manager(self) -> FavoritesManager:
        return self._favorites_manager
    
    @property
    def tts_manager(self):
        return self._tts_manager
    
    @property
    def progress_manager(self):
        return self._progress_manager
    
    @property
    def ai_manager(self) -> AIManager:
        return self._ai_manager
    
    @property
    def page_container(self) -> tk.Frame:
        return self._page_container
    
    @property
    def today_words(self) -> list:
        return self._today_words
    
    @today_words.setter
    def today_words(self, value: list):
        self._today_words = value
    
    @property
    def current_word_index(self) -> int:
        return self._current_word_index
    
    @current_word_index.setter
    def current_word_index(self, value: int):
        self._current_word_index = value
    
    @property
    def unknown_words(self) -> list:
        return self._unknown_words
    
    @unknown_words.setter
    def unknown_words(self, value: list):
        self._unknown_words = value
    
    @property
    def stage(self) -> str:
        return self._stage
    
    @stage.setter
    def stage(self, value: str):
        self._stage = value
    
    @property
    def test_mode(self) -> bool:
        return self._test_mode
    
    @test_mode.setter
    def test_mode(self, value: bool):
        self._test_mode = value
    
    def _setup_window(self):
        """设置窗口属性"""
        self._root.title("智能背单词系统")
        self._root.geometry("950x720")
        self._root.minsize(900, 650)  # 增加最小尺寸，确保所有控件可见
        
        # 居中显示
        self._center_window()
        
        # 设置样式
        self._style_manager.setup_styles(self._root)
        
        # 监听主题变化
        self._style_manager.on_theme_changed(self._on_theme_changed)
        
        # 设置窗口图标（如果存在）
        self._set_window_icon()
    
    def _set_window_icon(self):
        """设置窗口图标（任务栏图标）"""
        try:
            # 尝试使用 PIL 动态生成图标
            from PIL import Image, ImageDraw, ImageTk
            
            # 创建图标
            icon_size = 64
            image = Image.new('RGBA', (icon_size, icon_size), color=(0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # 绘制圆角背景
            draw.rounded_rectangle([4, 4, 60, 60], radius=12, fill='#e94560')
            
            # 绘制书本图标
            # 左页
            draw.rectangle([12, 14, 30, 50], fill='#ffffff', outline='#ffffff')
            # 右页
            draw.rectangle([34, 14, 52, 50], fill='#ffffff', outline='#ffffff')
            # 中缝
            draw.line([(32, 14), (32, 50)], fill='#1a1a2e', width=2)
            # 文字线条（左页）
            draw.line([(16, 22), (26, 22)], fill='#e94560', width=2)
            draw.line([(16, 30), (26, 30)], fill='#e94560', width=2)
            draw.line([(16, 38), (26, 38)], fill='#e94560', width=2)
            # 文字线条（右页）
            draw.line([(38, 22), (48, 22)], fill='#e94560', width=2)
            draw.line([(38, 30), (48, 30)], fill='#e94560', width=2)
            draw.line([(38, 38), (48, 38)], fill='#e94560', width=2)
            
            # 转换为 Tkinter PhotoImage
            self._icon_image = ImageTk.PhotoImage(image)
            self._root.iconphoto(True, self._icon_image)
            
            self._logger.debug("窗口图标已设置（动态生成）")
            
        except ImportError:
            self._logger.debug("PIL 未安装，使用默认图标")
        except Exception as e:
            self._logger.debug(f"设置窗口图标失败: {e}")
    
    def _center_window(self):
        """居中显示窗口"""
        self._root.update_idletasks()
        # 尝试使用实际窗口尺寸，若尚未计算则回退到默认值
        width = self._root.winfo_width()
        height = self._root.winfo_height()
        if width <= 1:
            width = 950
        if height <= 1:
            height = 720
        x = (self._root.winfo_screenwidth() // 2) - (width // 2)
        y = (self._root.winfo_screenheight() // 2) - (height // 2)
        self._root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_layout(self):
        """创建主布局"""
        colors = self._style_manager.colors
        
        # 主容器
        self._main_container = tk.Frame(
            self._root, 
            bg=colors["bg_primary"]
        )
        self._main_container.pack(fill=tk.BOTH, expand=True)
        
        # 配置网格
        self._main_container.columnconfigure(0, weight=1)
        self._main_container.rowconfigure(1, weight=1)
        
        # 顶部导航栏
        self._create_navbar()
        
        # 页面容器
        self._page_container = tk.Frame(
            self._main_container,
            bg=colors["bg_primary"]
        )
        self._page_container.grid(row=1, column=0, sticky="nsew")
        self._page_container.columnconfigure(0, weight=1)
        self._page_container.rowconfigure(0, weight=1)
        
        # 底部状态栏
        self._create_status_bar()
    
    def _create_navbar(self):
        """创建导航栏 - 响应式设计"""
        colors = self._style_manager.colors
        
        navbar = tk.Frame(
            self._main_container,
            bg=colors["bg_secondary"],
            height=50
        )
        navbar.grid(row=0, column=0, sticky="ew")
        navbar.grid_propagate(False)
        
        # 配置网格
        navbar.columnconfigure(0, weight=0)  # Logo区域
        navbar.columnconfigure(1, weight=1)  # 导航按钮区域（可扩展）
        navbar.columnconfigure(2, weight=0)  # 右侧信息区域
        
        # 左侧 - Logo和标题（紧凑）
        left_frame = tk.Frame(navbar, bg=colors["bg_secondary"])
        left_frame.grid(row=0, column=0, sticky="w", padx=15, pady=8)
        
        logo_label = tk.Label(
            left_frame,
            text="🎯",
            font=("Segoe UI", 16),
            bg=colors["bg_secondary"],
            fg=colors["accent"]
        )
        logo_label.pack(side=tk.LEFT, padx=(0, 6))
        
        title_label = tk.Label(
            left_frame,
            text="智能背单词",
            font=self._style_manager.get_font("subheading"),
            bg=colors["bg_secondary"],
            fg=colors["fg_primary"]
        )
        title_label.pack(side=tk.LEFT)
        
        # 中间 - 导航按钮（居中）
        center_frame = tk.Frame(navbar, bg=colors["bg_secondary"])
        center_frame.grid(row=0, column=1, sticky="", pady=8)
        
        self._nav_buttons = {}
        nav_items = [
            ("home", "🏠 首页"),
            ("learning", "📚 学习"),
            ("favorites", "❤️ 收藏"),
            ("statistics", "📊 统计"),
            ("settings", "⚙️ 设置"),
        ]
        
        for page_id, text in nav_items:
            btn = ttk.Button(
                center_frame,
                text=text,
                command=lambda pid=page_id: self.navigate_to(pid),
                style="Nav.TButton"
            )
            btn.pack(side=tk.LEFT, padx=2)
            self._nav_buttons[page_id] = btn
        
        # 右侧 - 收藏数
        right_frame = tk.Frame(navbar, bg=colors["bg_secondary"])
        right_frame.grid(row=0, column=2, sticky="e", padx=15, pady=8)
        
        self._favorites_count_label = tk.Label(
            right_frame,
            text=f"❤️ {len(self._favorites_manager)}",
            font=self._style_manager.get_font("caption"),
            bg=colors["bg_secondary"],
            fg=colors["accent"]
        )
        self._favorites_count_label.pack(side=tk.RIGHT)
        
        # 导航栏响应式状态
        self._navbar_resize_timer = None
        self._last_navbar_width = 0
    
    def _on_navbar_resize(self, event):
        """导航栏响应式调整（带防抖）"""
        if event.widget != self._root:
            return
        
        # 获取窗口宽度
        width = self._root.winfo_width()
        
        # 宽度变化小于50px时不触发
        if abs(width - self._last_navbar_width) < 50:
            return
        
        self._last_navbar_width = width
        
        # 取消之前的定时器
        if self._navbar_resize_timer:
            self._root.after_cancel(self._navbar_resize_timer)
        
        # 延迟100ms后执行
        self._navbar_resize_timer = self._root.after(100, lambda: self._apply_navbar_layout(width))
    
    def _apply_navbar_layout(self, width: int):
        """应用导航栏布局"""
        try:
            if width < 700:
                # 小窗口：只显示图标
                short_labels = {
                    "home": "🏠",
                    "learning": "📚",
                    "favorites": "❤️",
                    "statistics": "📊",
                    "settings": "⚙️",
                }
                for page_id, text in short_labels.items():
                    if page_id in self._nav_buttons:
                        self._nav_buttons[page_id].configure(text=text)
            else:
                # 大窗口：显示完整文字
                full_labels = {
                    "home": "🏠 首页",
                    "learning": "📚 学习",
                    "favorites": "❤️ 收藏",
                    "statistics": "📊 统计",
                    "settings": "⚙️ 设置",
                }
                for page_id, text in full_labels.items():
                    if page_id in self._nav_buttons:
                        self._nav_buttons[page_id].configure(text=text)
        except Exception:
            pass
    
    def _create_status_bar(self):
        """创建状态栏"""
        colors = self._style_manager.colors
        
        status_bar = tk.Frame(
            self._main_container,
            bg=colors["bg_secondary"],
            height=35
        )
        status_bar.grid(row=2, column=0, sticky="ew")
        status_bar.grid_propagate(False)
        
        status_inner = tk.Frame(status_bar, bg=colors["bg_secondary"])
        status_inner.pack(fill=tk.BOTH, expand=True, padx=15)
        
        # 状态文本
        self._status_label = tk.Label(
            status_inner,
            text="准备就绪",
            font=self._style_manager.get_font("caption"),
            bg=colors["bg_secondary"],
            fg=colors["fg_secondary"]
        )
        self._status_label.pack(side=tk.LEFT, pady=8)
        
        # 进度文本
        self._progress_label = tk.Label(
            status_inner,
            text="",
            font=self._style_manager.get_font("caption"),
            bg=colors["bg_secondary"],
            fg=colors["accent"]
        )
        self._progress_label.pack(side=tk.RIGHT, pady=8)
    
    def _register_pages(self):
        """注册所有页面"""
        from ui.pages import (
            HomePage, LearningPage, SettingsPage,
            FavoritesPage, StatisticsPage
        )
        
        self._page_manager.register_all([
            HomePage,
            LearningPage,
            SettingsPage,
            FavoritesPage,
            StatisticsPage,
        ])
    
    def _setup_bindings(self):
        """设置全局绑定"""
        self._root.bind("<Escape>", lambda e: self.go_back())
        self._root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # 键盘快捷键
        self._root.bind("<Control-h>", lambda e: self.navigate_to("home"))
        self._root.bind("<Control-l>", lambda e: self.navigate_to("learning"))
        self._root.bind("<Control-f>", lambda e: self.navigate_to("favorites"))
        self._root.bind("<Control-s>", lambda e: self.navigate_to("settings"))
        
        # 导航栏响应式调整
        self._root.bind("<Configure>", self._on_navbar_resize)
    
    def _on_theme_changed(self):
        """主题变化回调"""
        colors = self._style_manager.colors
        
        # 更新主容器
        self._main_container.configure(bg=colors["bg_primary"])
        self._page_container.configure(bg=colors["bg_primary"])
        
        # 更新导航栏
        for widget in self._main_container.winfo_children():
            if isinstance(widget, tk.Frame):
                self._update_frame_colors(widget, colors)
        
        # 更新所有页面
        self._page_manager.apply_theme_to_all()
    
    def _update_frame_colors(self, frame: tk.Frame, colors: dict):
        """递归更新框架颜色"""
        try:
            frame.configure(bg=colors.get("bg_secondary", colors["bg_primary"]))
        except Exception:
            pass
        
        for child in frame.winfo_children():
            if isinstance(child, tk.Label):
                try:
                    bg = child.cget("bg")
                    if bg in [self._style_manager.THEMES.get(self._style_manager.current_theme, {}).get("bg_secondary"),
                              self._style_manager.THEMES.get(self._style_manager.current_theme, {}).get("bg_primary")]:
                        child.configure(bg=colors.get("bg_secondary", colors["bg_primary"]))
                except Exception:
                    pass
            elif isinstance(child, tk.Frame):
                self._update_frame_colors(child, colors)
    
    def navigate_to(self, page_id: str, **kwargs):
        """导航到指定页面"""
        success = self._page_manager.navigate_to(page_id, **kwargs)
        if success:
            self._update_nav_buttons(page_id)
            self._logger.info(f"导航到页面: {page_id}")
        return success
    
    def go_back(self):
        """返回上一页"""
        if self._page_manager.can_go_back():
            self._page_manager.go_back()
            self._update_nav_buttons(self._page_manager.current_page_id)
    
    def _update_nav_buttons(self, current_page_id: str):
        """更新导航按钮状态"""
        for page_id, btn in self._nav_buttons.items():
            if page_id == current_page_id:
                btn.configure(style="Primary.TButton")
            else:
                btn.configure(style="Nav.TButton")
    
    def update_status(self, message: str):
        """更新状态栏"""
        self._status_label.configure(text=message)
    
    def update_progress(self, progress: str):
        """更新进度显示"""
        self._progress_label.configure(text=progress)
    
    def update_favorites_count(self, count: int = None):
        """更新收藏数量"""
        if count is None:
            try:
                count = len(self._favorites_manager)
            except Exception:
                count = 0
        self._favorites_count_label.configure(text=f"❤️ {count}")
    
    def show_message(self, message: str, msg_type: str = "info"):
        """显示消息提示"""
        colors = self._style_manager.colors
        
        if self._message_timer is not None:
            try:
                self._root.after_cancel(self._message_timer)
            except Exception:
                pass
        
        # 创建消息标签（如果没有）
        if not self._message_label:
            self._message_label = tk.Label(
                self._page_container,
                font=self._style_manager.get_font("body"),
                padx=20,
                pady=10
            )
        
        # 设置颜色
        if msg_type == "success":
            bg_color = colors["success"]
        elif msg_type == "error":
            bg_color = colors["error"]
        elif msg_type == "warning":
            bg_color = colors["warning"]
        else:
            bg_color = colors["accent"]
        
        self._message_label.configure(
            text=message,
            bg=bg_color,
            fg="#ffffff"
        )
        self._message_label.place(relx=0.5, rely=0.05, anchor="n")
        
        # 3秒后自动隐藏
        self._message_timer = self._root.after(
            3000, 
            lambda: self._message_label.place_forget() if self._message_label else None
        )
    
    def save_config(self):
        """保存配置"""
        self._config.save_config()
    
    def _on_closing(self):
        """关闭应用"""
        # 防止重复关闭
        if not hasattr(self, '_closing'):
            self._closing = False
        
        if self._closing:
            return
        
        self._closing = True
        self._logger.info("应用程序正在关闭")
        
        # 停止TTS
        self._tts_manager.stop()
        
        # 确认退出
        if self._config.get_bool("confirm_before_exit", True):
            message = "确定要退出程序吗？"
            if self._today_words:
                message = "学习尚未完成，确定要退出吗？"
            
            try:
                if not messagebox.askyesno("确认", message):
                    self._closing = False
                    return
            except tk.TclError:
                pass
        
        # 清理资源
        try:
            if self._favorites_manager.dirty_flag:
                self._favorites_manager.save_favorites()
            
            if self._progress_manager.session_start_time is not None:
                self._progress_manager.end_session(
                    words_studied=len(self._today_words),
                    words_reviewed=len(self._unknown_words)
                )
            
            self._logger.info("应用程序正常退出")
            self._root.destroy()
        except Exception as e:
            self._logger.exception(f"退出时发生错误: {e}")
            try:
                self._root.destroy()
            except:
                pass
    
    def run(self):
        """运行应用"""
        self._logger.info("应用程序启动")
        self._root.mainloop()
