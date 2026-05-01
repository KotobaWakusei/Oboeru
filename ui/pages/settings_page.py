"""设置页面 - 应用配置（优化版本）"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ui.core.base_page import BasePage
import os


class SettingsPage(BasePage):
    """设置页面 - 支持滚动"""
    
    page_id = "settings"
    page_title = "设置"
    page_icon = "⚙️"
    
    def create_widgets(self):
        """创建组件"""
        colors = self.colors
        
        # 创建滚动区域
        self._create_scrollable_area()
        
        # 添加设置项
        self._create_header()
        self._create_learning_settings()
        self._create_display_settings()
        self._create_behavior_settings()
        self._create_theme_settings()
        self._create_ai_settings()
        self._create_ai_debug()
        self._create_data_settings()
        self._create_action_buttons()
        
        # 延迟绑定滚轮事件到所有子组件
        self.after(100, self._rebind_mousewheel)
    
    def _rebind_mousewheel(self):
        """重新绑定滚轮事件到所有子组件"""
        self._bind_mousewheel_recursive(self._scroll_frame)
    
    def _create_scrollable_area(self):
        """创建滚动区域"""
        colors = self.colors
        
        # 外层容器
        self._outer_frame = tk.Frame(self._container, bg=colors["bg_primary"])
        self._outer_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建 Canvas 和滚动条
        self._canvas = tk.Canvas(
            self._outer_frame,
            bg=colors["bg_primary"],
            highlightthickness=0
        )
        
        self._scrollbar = ttk.Scrollbar(
            self._outer_frame,
            orient=tk.VERTICAL,
            command=self._canvas.yview
        )
        
        # 内层容器（放置内容）
        self._scroll_frame = tk.Frame(self._canvas, bg=colors["bg_primary"])
        
        # 配置滚动
        self._canvas.configure(yscrollcommand=self._scrollbar.set)
        
        # 布局
        self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 在 Canvas 中创建窗口
        self._canvas_window = self._canvas.create_window(
            (0, 0),
            window=self._scroll_frame,
            anchor="nw",
            width=self._canvas.winfo_reqwidth()
        )
        
        # 绑定事件
        self._scroll_frame.bind("<Configure>", self._on_frame_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)
        
        # 鼠标滚轮支持 - 绑定到 canvas
        self._canvas.bind("<MouseWheel>", self._on_mousewheel)
        self._canvas.bind("<Button-4>", self._on_mousewheel)
        self._canvas.bind("<Button-5>", self._on_mousewheel)
        
        # 鼠标滚轮支持 - 绑定到 scroll_frame 及其子组件
        self._bind_mousewheel_recursive(self._scroll_frame)
        
        # 设置内边距
        self._scroll_frame.configure(padx=15, pady=15)
    
    def _bind_mousewheel_recursive(self, widget):
        """递归绑定滚轮事件到所有子组件"""
        widget.bind("<MouseWheel>", self._on_mousewheel)
        widget.bind("<Button-4>", self._on_mousewheel)
        widget.bind("<Button-5>", self._on_mousewheel)
        
        for child in widget.winfo_children():
            self._bind_mousewheel_recursive(child)
    
    def _on_frame_configure(self, event=None):
        """更新滚动区域"""
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))
    
    def _on_canvas_configure(self, event=None):
        """调整内层窗口宽度"""
        self._canvas.itemconfig(self._canvas_window, width=event.width)
    
    def _on_mousewheel(self, event):
        """鼠标滚轮滚动"""
        if event.num == 4:
            self._canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self._canvas.yview_scroll(1, "units")
        else:
            self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def setup_layout(self):
        """设置布局"""
        pass
    
    def _create_header(self):
        """创建标题"""
        colors = self.colors
        
        header = tk.Frame(self._scroll_frame, bg=colors["bg_primary"])
        header.pack(fill=tk.X, pady=(0, 15))
        
        title = tk.Label(
            header,
            text="⚙️ 应用设置",
            font=self._style_manager.get_font("title"),
            bg=colors["bg_primary"],
            fg=colors["fg_primary"]
        )
        title.pack(anchor="w")
        
        subtitle = tk.Label(
            header,
            text="自定义您的学习体验",
            font=self._style_manager.get_font("caption"),
            bg=colors["bg_primary"],
            fg=colors["fg_secondary"]
        )
        subtitle.pack(anchor="w", pady=(3, 0))
    
    def _create_setting_row(self, parent, label: str, widget, label_width: int = 12):
        """创建设置行"""
        colors = self.colors
        
        row = tk.Frame(parent, bg=colors["bg_card"])
        row.pack(fill=tk.X, pady=5)
        
        tk.Label(
            row,
            text=label,
            font=self._style_manager.get_font("body"),
            bg=colors["bg_card"],
            fg=colors["fg_primary"],
            width=label_width,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        widget.pack(side=tk.LEFT, padx=(0, 8))
        
        return row
    
    def _create_learning_settings(self):
        """创建学习设置"""
        colors = self.colors
        
        card = self._create_card("📚 学习设置")
        
        # 每日单词量
        row1 = tk.Frame(card, bg=colors["bg_card"])
        row1.pack(fill=tk.X, pady=5)
        
        tk.Label(
            row1,
            text="每日单词量：",
            font=self._style_manager.get_font("body"),
            bg=colors["bg_card"],
            fg=colors["fg_primary"],
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self._daily_words_var = tk.StringVar(
            value=str(self.app.config.get("daily_words", 20))
        )
        
        daily_entry = ttk.Entry(
            row1,
            textvariable=self._daily_words_var,
            width=8,
            font=self._style_manager.get_font("body")
        )
        daily_entry.pack(side=tk.LEFT, padx=(0, 8))
        
        daily_min = self.app.config.get("daily_words_min", 1)
        daily_max = self.app.config.get("daily_words_max", 100)
        
        tk.Label(
            row1,
            text=f"({daily_min}-{daily_max})",
            font=self._style_manager.get_font("caption"),
            bg=colors["bg_card"],
            fg=colors["fg_secondary"]
        ).pack(side=tk.LEFT)
        
        # 词库文件
        row2 = tk.Frame(card, bg=colors["bg_card"])
        row2.pack(fill=tk.X, pady=5)
        
        tk.Label(
            row2,
            text="词库文件：",
            font=self._style_manager.get_font("body"),
            bg=colors["bg_card"],
            fg=colors["fg_primary"],
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self._vocab_file_var = tk.StringVar(
            value=self.app.config.get("vocab_file", "data/vocabulary.txt")
        )
        
        vocab_entry = ttk.Entry(
            row2,
            textvariable=self._vocab_file_var,
            width=30,
            font=self._style_manager.get_font("body")
        )
        vocab_entry.pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True)
        
        ttk.Button(
            row2,
            text="浏览",
            command=self._browse_vocab,
            style="Secondary.TButton"
        ).pack(side=tk.LEFT)
        
        # 随机顺序
        row3 = tk.Frame(card, bg=colors["bg_card"])
        row3.pack(fill=tk.X, pady=5)
        
        self._shuffle_var = tk.BooleanVar(
            value=self.app.config.get_bool("shuffle_words", True)
        )
        
        ttk.Checkbutton(
            row3,
            text="随机打乱单词顺序",
            variable=self._shuffle_var,
            style="TCheckbutton"
        ).pack(side=tk.LEFT)
        
        # 显示拼音
        row4 = tk.Frame(card, bg=colors["bg_card"])
        row4.pack(fill=tk.X, pady=5)
        
        self._show_pinyin_var = tk.BooleanVar(
            value=self.app.config.get_bool("show_pinyin", True)
        )
        
        ttk.Checkbutton(
            row4,
            text="显示拼音/词性标注",
            variable=self._show_pinyin_var,
            style="TCheckbutton"
        ).pack(side=tk.LEFT)
        
        # 自动播放发音
        row5 = tk.Frame(card, bg=colors["bg_card"])
        row5.pack(fill=tk.X, pady=5)
        
        self._auto_play_sound_var = tk.BooleanVar(
            value=self.app.config.get_bool("auto_play_sound", False)
        )
        
        ttk.Checkbutton(
            row5,
            text="学习时自动播放发音",
            variable=self._auto_play_sound_var,
            style="TCheckbutton"
        ).pack(side=tk.LEFT)
        
        # 回顾单词数量
        row6 = tk.Frame(card, bg=colors["bg_card"])
        row6.pack(fill=tk.X, pady=5)
        
        tk.Label(
            row6,
            text="回顾单词数：",
            font=self._style_manager.get_font("body"),
            bg=colors["bg_card"],
            fg=colors["fg_primary"],
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self._review_words_count_var = tk.StringVar(
            value=str(self.app.config.get("review_words_count", 3))
        )
        
        review_entry = ttk.Entry(
            row6,
            textvariable=self._review_words_count_var,
            width=8,
            font=self._style_manager.get_font("body")
        )
        review_entry.pack(side=tk.LEFT, padx=(0, 8))
        
        tk.Label(
            row6,
            text="(1-10) 背诵时显示最近N个单词",
            font=self._style_manager.get_font("caption"),
            bg=colors["bg_card"],
            fg=colors["fg_secondary"]
        ).pack(side=tk.LEFT)
    
    def _create_display_settings(self):
        """创建显示设置"""
        colors = self.colors
        
        card = self._create_card("🖥️ 显示设置")
        
        # 字体大小
        row1 = tk.Frame(card, bg=colors["bg_card"])
        row1.pack(fill=tk.X, pady=5)
        
        tk.Label(
            row1,
            text="字体大小：",
            font=self._style_manager.get_font("body"),
            bg=colors["bg_card"],
            fg=colors["fg_primary"],
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self._font_size_var = tk.StringVar(
            value=str(self.app.config.get("font_size", 14))
        )
        
        font_entry = ttk.Entry(
            row1,
            textvariable=self._font_size_var,
            width=8,
            font=self._style_manager.get_font("body")
        )
        font_entry.pack(side=tk.LEFT, padx=(0, 8))
        
        font_min = self.app.config.get("font_size_min", 12)
        font_max = self.app.config.get("font_size_max", 24)
        
        tk.Label(
            row1,
            text=f"({font_min}-{font_max})",
            font=self._style_manager.get_font("caption"),
            bg=colors["bg_card"],
            fg=colors["fg_secondary"]
        ).pack(side=tk.LEFT)
        
        # 显示进度条
        row2 = tk.Frame(card, bg=colors["bg_card"])
        row2.pack(fill=tk.X, pady=5)
        
        self._progress_var = tk.BooleanVar(
            value=self.app.config.get_bool("show_progress_bar", True)
        )
        
        ttk.Checkbutton(
            row2,
            text="显示学习进度条",
            variable=self._progress_var,
            style="TCheckbutton"
        ).pack(side=tk.LEFT)
        
        # 记住窗口大小
        row3 = tk.Frame(card, bg=colors["bg_card"])
        row3.pack(fill=tk.X, pady=5)
        
        self._remember_size_var = tk.BooleanVar(
            value=self.app.config.get_bool("remember_window_size", True)
        )
        
        ttk.Checkbutton(
            row3,
            text="记住窗口大小和位置",
            variable=self._remember_size_var,
            style="TCheckbutton"
        ).pack(side=tk.LEFT)
    
    def _create_behavior_settings(self):
        """创建行为设置"""
        colors = self.colors
        
        card = self._create_card("⚡ 行为设置")
        
        # 测试延迟
        row1 = tk.Frame(card, bg=colors["bg_card"])
        row1.pack(fill=tk.X, pady=5)
        
        tk.Label(
            row1,
            text="答对延迟：",
            font=self._style_manager.get_font("body"),
            bg=colors["bg_card"],
            fg=colors["fg_primary"],
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self._test_delay_var = tk.StringVar(
            value=str(self.app.config.get_int("test_delay", 1500))
        )
        
        ttk.Entry(
            row1,
            textvariable=self._test_delay_var,
            width=8,
            font=self._style_manager.get_font("body")
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Label(
            row1,
            text="毫秒",
            font=self._style_manager.get_font("caption"),
            bg=colors["bg_card"],
            fg=colors["fg_secondary"]
        ).pack(side=tk.LEFT)
        
        # 错误延迟
        row2 = tk.Frame(card, bg=colors["bg_card"])
        row2.pack(fill=tk.X, pady=5)
        
        tk.Label(
            row2,
            text="答错延迟：",
            font=self._style_manager.get_font("body"),
            bg=colors["bg_card"],
            fg=colors["fg_primary"],
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self._wrong_delay_var = tk.StringVar(
            value=str(self.app.config.get_int("wrong_delay", 2000))
        )
        
        ttk.Entry(
            row2,
            textvariable=self._wrong_delay_var,
            width=8,
            font=self._style_manager.get_font("body")
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Label(
            row2,
            text="毫秒",
            font=self._style_manager.get_font("caption"),
            bg=colors["bg_card"],
            fg=colors["fg_secondary"]
        ).pack(side=tk.LEFT)
        
        # 退出确认
        row3 = tk.Frame(card, bg=colors["bg_card"])
        row3.pack(fill=tk.X, pady=5)
        
        self._confirm_exit_var = tk.BooleanVar(
            value=self.app.config.get_bool("confirm_before_exit", True)
        )
        
        ttk.Checkbutton(
            row3,
            text="退出前确认",
            variable=self._confirm_exit_var,
            style="TCheckbutton"
        ).pack(side=tk.LEFT)
        
        # 自动保存
        row4 = tk.Frame(card, bg=colors["bg_card"])
        row4.pack(fill=tk.X, pady=5)
        
        self._auto_save_var = tk.BooleanVar(
            value=self.app.config.get_bool("auto_save_config", True)
        )
        
        ttk.Checkbutton(
            row4,
            text="自动保存配置",
            variable=self._auto_save_var,
            style="TCheckbutton"
        ).pack(side=tk.LEFT)
    
    def _create_theme_settings(self):
        """创建主题设置"""
        colors = self.colors
        
        card = self._create_card("🎨 主题设置")
        
        row1 = tk.Frame(card, bg=colors["bg_card"])
        row1.pack(fill=tk.X, pady=5)
        
        tk.Label(
            row1,
            text="选择主题：",
            font=self._style_manager.get_font("body"),
            bg=colors["bg_card"],
            fg=colors["fg_primary"],
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self._theme_var = tk.StringVar(
            value=self._style_manager.current_theme
        )
        
        themes = self._style_manager.get_available_themes()
        
        theme_combo = ttk.Combobox(
            row1,
            textvariable=self._theme_var,
            values=themes,
            state="readonly",
            width=15,
            font=self._style_manager.get_font("body")
        )
        theme_combo.pack(side=tk.LEFT)
        theme_combo.bind("<<ComboboxSelected>>", self._on_theme_change)
        
        # 主题预览
        self._theme_preview = tk.Frame(card, bg=colors["bg_card"])
        self._theme_preview.pack(fill=tk.X, pady=10)
        
        self._update_theme_preview()
    
    def _create_ai_settings(self):
        """创建 AI 例句设置"""
        colors = self.colors
        from modules.utils.constants import Constants
        
        card = self._create_card("🤖 AI 例句设置")
        
        # 启用 AI 和基本说明
        row0 = tk.Frame(card, bg=colors["bg_card"])
        row0.pack(fill=tk.X, pady=5)
        
        self._ai_enabled_var = tk.BooleanVar(
            value=self.app.config.get_bool("ai_enabled", False)
        )
        
        ttk.Checkbutton(
            row0,
            text="启用 AI 例句生成",
            variable=self._ai_enabled_var,
            style="TCheckbutton"
        ).pack(side=tk.LEFT)
        
        # 添加说明标签
        tk.Label(
            row0,
            text="(使用 AI 为单词生成例句，需要 API Key)",
            font=self._style_manager.get_font("small"),
            bg=colors["bg_card"],
            fg=colors["fg_secondary"]
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # API 提供商选择
        row_provider = tk.Frame(card, bg=colors["bg_card"])
        row_provider.pack(fill=tk.X, pady=5)
        
        tk.Label(
            row_provider,
            text="API 提供商：",
            font=self._style_manager.get_font("body"),
            bg=colors["bg_card"],
            fg=colors["fg_primary"],
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self._ai_provider_var = tk.StringVar(
            value=self.app.config.get("ai_provider", "xunfei_lite")
        )
        
        providers = Constants.AI_PROVIDERS
        provider_names = [(k, v["name"]) for k, v in providers.items()]
        
        provider_combo = ttk.Combobox(
            row_provider,
            textvariable=self._ai_provider_var,
            values=[f"{v[1]}" for v in provider_names],
            state="readonly",
            width=18,
            font=self._style_manager.get_font("body")
        )
        provider_combo.pack(side=tk.LEFT)
        provider_combo.bind("<<ComboboxSelected>>", self._on_provider_change)
        
        # 保存 provider_names 供后续使用
        self._provider_names = provider_names
        
        # 提示文字（根据提供商变化）
        self._provider_hint = tk.Label(
            row_provider,
            text="",
            font=self._style_manager.get_font("small"),
            bg=colors["bg_card"],
            fg=colors["fg_secondary"]
        )
        self._provider_hint.pack(side=tk.LEFT, padx=(5, 0))
        
        # 自定义 URL（仅当选择自定义时显示）
        self._custom_url_frame = tk.Frame(card, bg=colors["bg_card"])
        
        tk.Label(
            self._custom_url_frame,
            text="自定义 URL：",
            font=self._style_manager.get_font("body"),
            bg=colors["bg_card"],
            fg=colors["fg_primary"],
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self._ai_custom_url_var = tk.StringVar(
            value=self.app.config.get("ai_custom_url", "")
        )
        
        ttk.Entry(
            self._custom_url_frame,
            textvariable=self._ai_custom_url_var,
            width=40,
            font=self._style_manager.get_font("body")
        ).pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True)
        
        # 自定义模型（仅当选择自定义时显示）
        self._custom_model_frame = tk.Frame(card, bg=colors["bg_card"])
        
        tk.Label(
            self._custom_model_frame,
            text="模型名称：",
            font=self._style_manager.get_font("body"),
            bg=colors["bg_card"],
            fg=colors["fg_primary"],
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self._ai_custom_model_var = tk.StringVar(
            value=self.app.config.get("ai_custom_model", "")
        )
        
        ttk.Entry(
            self._custom_model_frame,
            textvariable=self._ai_custom_model_var,
            width=25,
            font=self._style_manager.get_font("body")
        ).pack(side=tk.LEFT)
        
        # API Key 输入区域
        row1 = tk.Frame(card, bg=colors["bg_card"])
        row1.pack(fill=tk.X, pady=5)
        
        tk.Label(
            row1,
            text="API Key：",
            font=self._style_manager.get_font("body"),
            bg=colors["bg_card"],
            fg=colors["fg_primary"],
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self._ai_key_var = tk.StringVar(
            value=self.app.config.get("ai_api_key", "")
        )
        
        self._api_entry = ttk.Entry(
            row1,
            textvariable=self._ai_key_var,
            width=35,
            font=self._style_manager.get_font("body"),
            show="*"
        )
        self._api_entry.pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True)
        
        # 显示/隐藏密钥
        self._show_key_var = tk.BooleanVar(value=False)
        
        def toggle_key_visibility():
            if self._show_key_var.get():
                self._api_entry.configure(show="")
            else:
                self._api_entry.configure(show="*")
        
        ttk.Checkbutton(
            row1,
            text="显示",
            variable=self._show_key_var,
            command=toggle_key_visibility,
            style="TCheckbutton"
        ).pack(side=tk.LEFT)
        
        # 添加测试连接按钮
        test_btn = ttk.Button(
            row1,
            text="测试连接",
            command=self._test_ai_connection,
            style="Secondary.TButton"
        )
        test_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # 难度等级选择
        row_diff = tk.Frame(card, bg=colors["bg_card"])
        row_diff.pack(fill=tk.X, pady=5)
        
        tk.Label(
            row_diff,
            text="例句难度：",
            font=self._style_manager.get_font("body"),
            bg=colors["bg_card"],
            fg=colors["fg_primary"],
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self._ai_difficulty_var = tk.StringVar(
            value=self.app.config.get("ai_difficulty", "junior")
        )
        
        difficulties = Constants.AI_DIFFICULTY_LEVELS
        diff_options = [(k, v["name"]) for k, v in difficulties.items()]
        
        diff_combo = ttk.Combobox(
            row_diff,
            textvariable=self._ai_difficulty_var,
            values=[f"{v[1]}" for v in diff_options],
            state="readonly",
            width=12,
            font=self._style_manager.get_font("body")
        )
        diff_combo.pack(side=tk.LEFT)
        
        self._diff_options = diff_options
        
        # 难度说明
        self._diff_hint = tk.Label(
            row_diff,
            text="",
            font=self._style_manager.get_font("small"),
            bg=colors["bg_card"],
            fg=colors["fg_secondary"]
        )
        self._diff_hint.pack(side=tk.LEFT, padx=(5, 0))
        
        # 超时设置
        row3 = tk.Frame(card, bg=colors["bg_card"])
        row3.pack(fill=tk.X, pady=5)
        
        tk.Label(
            row3,
            text="超时(秒)：",
            font=self._style_manager.get_font("body"),
            bg=colors["bg_card"],
            fg=colors["fg_primary"],
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self._ai_timeout_var = tk.StringVar(
            value=str(self.app.config.get_int("ai_timeout", 30))
        )
        
        ttk.Entry(
            row3,
            textvariable=self._ai_timeout_var,
            width=8,
            font=self._style_manager.get_font("body")
        ).pack(side=tk.LEFT)
        
        # 添加超时说明
        tk.Label(
            row3,
            text="(网络请求超时时间，建议 10-60 秒)",
            font=self._style_manager.get_font("small"),
            bg=colors["bg_card"],
            fg=colors["fg_secondary"]
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # 显示例句选项
        row4 = tk.Frame(card, bg=colors["bg_card"])
        row4.pack(fill=tk.X, pady=5)
        
        self._ai_show_sentence_var = tk.BooleanVar(
            value=self.app.config.get_bool("ai_show_sentence", True)
        )
        
        ttk.Checkbutton(
            row4,
            text="学习时自动显示 AI 例句",
            variable=self._ai_show_sentence_var,
            style="TCheckbutton"
        ).pack(side=tk.LEFT)
        
        # 初始化显示状态
        self.after(100, self._update_ai_settings_display)
    
    def _on_provider_change(self, event=None):
        """提供商变更时更新界面"""
        self._update_ai_settings_display()
    
    def _update_ai_settings_display(self):
        """更新 AI 设置界面显示"""
        from modules.utils.constants import Constants
        
        colors = self.colors
        
        # 获取当前选中的提供商
        current_name = self._ai_provider_var.get()
        provider_key = None
        for k, v in self._provider_names:
            if v == current_name:
                provider_key = k
                break
        
        if provider_key:
            provider_config = Constants.AI_PROVIDERS.get(provider_key, {})
            hint_text = provider_config.get("api_key_hint", "")
            self._provider_hint.configure(text=hint_text)
            
            # 显示/隐藏自定义配置
            if provider_key == "custom":
                self._custom_url_frame.pack(fill=tk.X, pady=5)
                self._custom_model_frame.pack(fill=tk.X, pady=5)
            else:
                self._custom_url_frame.pack_forget()
                self._custom_model_frame.pack_forget()
        
        # 更新难度说明
        current_diff = self._ai_difficulty_var.get()
        for k, v in self._diff_options:
            if v == current_diff:
                diff_config = Constants.AI_DIFFICULTY_LEVELS.get(k, {})
                self._diff_hint.configure(text=diff_config.get("description", ""))
                break
    
    def _create_ai_debug(self):
        """创建 AI 对话调试区域"""
        colors = self.colors
        
        card = self._create_card("🐛 AI 对话调试")
        
        # 对话历史区域
        history_frame = tk.Frame(card, bg=colors["bg_card"])
        history_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建带滚动条的文本框
        self._debug_history = tk.Text(
            history_frame,
            height=8,
            font=self._style_manager.get_font("body"),
            bg=colors["bg_secondary"],
            fg=colors["fg_primary"],
            wrap=tk.WORD,
            state=tk.DISABLED,
            padx=8,
            pady=8
        )
        
        debug_scrollbar = ttk.Scrollbar(
            history_frame,
            orient=tk.VERTICAL,
            command=self._debug_history.yview
        )
        self._debug_history.configure(yscrollcommand=debug_scrollbar.set)
        
        debug_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._debug_history.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 输入区域
        input_frame = tk.Frame(card, bg=colors["bg_card"])
        input_frame.pack(fill=tk.X, pady=(0, 8))
        
        self._debug_input = ttk.Entry(
            input_frame,
            font=self._style_manager.get_font("body"),
            width=50
        )
        self._debug_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self._debug_input.bind("<Return>", lambda e: self._send_debug_message())
        
        ttk.Button(
            input_frame,
            text="发送",
            command=self._send_debug_message,
            style="Primary.TButton"
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            input_frame,
            text="清除",
            command=self._clear_debug_history,
            style="Secondary.TButton"
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            input_frame,
            text="测试连接",
            command=self._test_ai_connection,
            style="Secondary.TButton"
        ).pack(side=tk.LEFT, padx=2)
        
        # 状态显示
        self._debug_status = tk.Label(
            card,
            text="准备就绪",
            font=self._style_manager.get_font("caption"),
            bg=colors["bg_card"],
            fg=colors["fg_secondary"]
        )
        self._debug_status.pack(anchor="w")
    
    def _send_debug_message(self):
        """发送调试消息"""
        message = self._debug_input.get().strip()
        if not message:
            return
        
        if not self.app.ai_manager.is_available():
            self._add_debug_message("系统", "AI 功能未配置，请先配置 API Key", "error")
            return
        
        self._debug_input.delete(0, tk.END)
        self._add_debug_message("用户", message)
        self._debug_status.configure(text="AI 正在思考...")
        
        def on_response(success, result):
            self.after(0, lambda: self._on_debug_response(success, result))
        
        # 构建对话 prompt
        prompt = f"""请回复以下问题或请求，回复要简洁有用：
{message}"""
        
        # 直接调用 API
        self._call_ai_api(prompt, on_response)
    
    def _call_ai_api(self, prompt: str, callback):
        """调用 AI API"""
        import threading
        import json
        import urllib.request
        import urllib.error
        
        def call_in_thread():
            try:
                api_key = self.app.config.get("ai_api_key", "")
                model = self.app.config.get("ai_model", "generalv3.5")
                timeout = self.app.config.get_int("ai_timeout", 30)
                
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
                
                data = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 500,
                    "temperature": 0.7
                }
                
                request = urllib.request.Request(
                    "https://spark-api-open.xf-yun.com/v1/chat/completions",
                    data=json.dumps(data).encode("utf-8"),
                    headers=headers,
                    method="POST"
                )
                
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    result = json.loads(response.read().decode("utf-8"))
                    if "choices" in result:
                        content = result["choices"][0]["message"]["content"]
                        callback(True, content)
                    else:
                        callback(False, result.get("error", "解析响应失败"))
                        
            except urllib.error.HTTPError as e:
                error_body = e.read().decode("utf-8") if e.fp else ""
                callback(False, f"HTTP {e.code}: {error_body}")
            except urllib.error.URLError as e:
                callback(False, f"网络错误: {str(e.reason)}")
            except Exception as e:
                callback(False, f"错误: {str(e)}")
        
        thread = threading.Thread(target=call_in_thread, daemon=True)
        thread.start()
    
    def _on_debug_response(self, success: bool, result: str):
        """处理 AI 响应"""
        if success:
            self._add_debug_message("AI", result)
            self._debug_status.configure(text="回复完成")
        else:
            self._add_debug_message("系统", f"错误: {result}", "error")
            self._debug_status.configure(text="请求失败")
    
    def _add_debug_message(self, sender: str, message: str, msg_type: str = "normal"):
        """添加消息到调试历史"""
        colors = self.colors
        
        self._debug_history.configure(state=tk.NORMAL)
        
        # 添加时间戳
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # 设置标签样式
        tag_name = f"msg_{msg_type}"
        if msg_type == "error":
            self._debug_history.tag_configure(tag_name, foreground=colors["error"])
        elif sender == "AI":
            self._debug_history.tag_configure(tag_name, foreground=colors["success"])
        elif sender == "用户":
            self._debug_history.tag_configure(tag_name, foreground=colors["accent"])
        
        self._debug_history.insert(tk.END, f"[{timestamp}] {sender}: ", tag_name)
        self._debug_history.insert(tk.END, f"{message}\n\n")
        
        self._debug_history.configure(state=tk.DISABLED)
        self._debug_history.see(tk.END)
    
    def _clear_debug_history(self):
        """清除调试历史"""
        self._debug_history.configure(state=tk.NORMAL)
        self._debug_history.delete(1.0, tk.END)
        self._debug_history.configure(state=tk.DISABLED)
        self._debug_status.configure(text="历史已清除")
    
    def _test_ai_connection(self):
        """测试 AI 连接"""
        if not self.app.ai_manager.is_available():
            self._add_debug_message("系统", "AI 功能未配置，请先配置 API Key", "error")
            return
        
        self._add_debug_message("系统", "正在测试连接...")
        self._debug_status.configure(text="测试连接中...")
        
        def on_response(success, result):
            self.after(0, lambda: self._on_test_response(success, result))
        
        self._call_ai_api("回复'连接成功'两个词", on_response)
    
    def _on_test_response(self, success: bool, result: str):
        """处理测试响应"""
        if success:
            self._add_debug_message("系统", f"✓ 连接成功！AI 响应: {result}")
            self._debug_status.configure(text="连接正常")
        else:
            self._add_debug_message("系统", f"✗ 连接失败: {result}", "error")
            self._debug_status.configure(text="连接失败")
    
    def _create_data_settings(self):
        """创建数据管理设置"""
        colors = self.colors
        
        card = self._create_card("📁 数据管理")
        
        # 收藏自动备份
        row1 = tk.Frame(card, bg=colors["bg_card"])
        row1.pack(fill=tk.X, pady=5)
        
        self._fav_backup_var = tk.BooleanVar(
            value=self.app.config.get_bool("favorites_auto_backup", True)
        )
        
        ttk.Checkbutton(
            row1,
            text="收藏自动备份",
            variable=self._fav_backup_var,
            style="TCheckbutton"
        ).pack(side=tk.LEFT)
        
        # 收藏排序方式
        row2 = tk.Frame(card, bg=colors["bg_card"])
        row2.pack(fill=tk.X, pady=5)
        
        tk.Label(
            row2,
            text="收藏排序：",
            font=self._style_manager.get_font("body"),
            bg=colors["bg_card"],
            fg=colors["fg_primary"],
            width=12,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self._fav_sort_var = tk.StringVar(
            value=self.app.config.get("favorites_sort", "time")
        )
        
        sort_combo = ttk.Combobox(
            row2,
            textvariable=self._fav_sort_var,
            values=["time", "word", "learn_count"],
            state="readonly",
            width=15,
            font=self._style_manager.get_font("body")
        )
        sort_combo.pack(side=tk.LEFT)
        
        tk.Label(
            row2,
            text="(时间/字母/学习次数)",
            font=self._style_manager.get_font("caption"),
            bg=colors["bg_card"],
            fg=colors["fg_secondary"]
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # 操作按钮
        btn_row = tk.Frame(card, bg=colors["bg_card"])
        btn_row.pack(fill=tk.X, pady=(10, 5))
        
        ttk.Button(
            btn_row,
            text="🗑️ 清除学习进度",
            command=self._clear_progress,
            style="Secondary.TButton"
        ).pack(side=tk.LEFT, padx=3)
        
        ttk.Button(
            btn_row,
            text="📤 导出所有数据",
            command=self._export_all_data,
            style="Secondary.TButton"
        ).pack(side=tk.LEFT, padx=3)
    
    def _create_card(self, title: str) -> tk.Frame:
        """创建设置卡片"""
        colors = self.colors
        
        card = tk.Frame(self._scroll_frame, bg=colors["bg_card"])
        card.configure(highlightbackground=colors["border"], highlightthickness=1)
        card.pack(fill=tk.X, pady=(0, 12))
        
        header = tk.Frame(card, bg=colors["bg_secondary"])
        header.pack(fill=tk.X, padx=1, pady=1)
        
        tk.Label(
            header,
            text=title,
            font=self._style_manager.get_font("subheading"),
            bg=colors["bg_secondary"],
            fg=colors["accent"],
            padx=12,
            pady=8
        ).pack(anchor="w")
        
        content = tk.Frame(card, bg=colors["bg_card"])
        content.pack(fill=tk.X, padx=15, pady=12)
        
        return content
    
    def _update_theme_preview(self):
        """更新主题预览"""
        colors = self.colors
        
        for widget in self._theme_preview.winfo_children():
            widget.destroy()
        
        preview_items = [
            ("主背景", colors["bg_primary"]),
            ("次背景", colors["bg_secondary"]),
            ("卡片", colors["bg_card"]),
            ("主文字", colors["fg_primary"]),
            ("强调色", colors["accent"]),
            ("成功", colors["success"]),
        ]
        
        for i, (name, color) in enumerate(preview_items):
            frame = tk.Frame(self._theme_preview, bg=self.colors["bg_card"])
            frame.pack(side=tk.LEFT, padx=4)
            
            color_box = tk.Frame(
                frame,
                bg=color,
                width=30,
                height=30
            )
            color_box.pack()
            color_box.pack_propagate(False)
            
            tk.Label(
                frame,
                text=name,
                font=self._style_manager.get_font("small"),
                bg=self.colors["bg_card"],
                fg=self.colors["fg_secondary"]
            ).pack(pady=(3, 0))
    
    def _create_action_buttons(self):
        """创建操作按钮"""
        colors = self.colors
        
        btn_frame = tk.Frame(self._scroll_frame, bg=colors["bg_primary"])
        btn_frame.pack(fill=tk.X, pady=(8, 0))
        
        ttk.Button(
            btn_frame,
            text="💾 保存设置",
            command=self._save_settings,
            style="Primary.TButton"
        ).pack(side=tk.RIGHT, padx=3)
        
        ttk.Button(
            btn_frame,
            text="🔄 重置",
            command=self._reset_settings,
            style="Secondary.TButton"
        ).pack(side=tk.RIGHT, padx=3)
        
        ttk.Button(
            btn_frame,
            text="📁 加载词库",
            command=self._load_vocabulary,
            style="Secondary.TButton"
        ).pack(side=tk.RIGHT, padx=3)
    
    def _browse_vocab(self):
        """浏览词库文件"""
        file_path = filedialog.askopenfilename(
            title="选择词库文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            parent=self.app.root
        )
        
        if file_path:
            self._vocab_file_var.set(file_path)
    
    def _on_theme_change(self, event=None):
        """主题变更"""
        theme = self._theme_var.get()
        self._style_manager.set_theme(theme)
        self._style_manager.setup_styles(self.app.root)
        self._update_theme_preview()
        self.show_message(f"已切换到 {self._style_manager.get_theme_name()} 主题", "success")
    
    def _save_settings(self):
        """保存设置"""
        try:
            # 验证数值
            daily_words = int(self._daily_words_var.get())
            daily_min = self.app.config.get("daily_words_min", 1)
            daily_max = self.app.config.get("daily_words_max", 100)
            
            if not (daily_min <= daily_words <= daily_max):
                self.show_message(f"每日单词量必须在 {daily_min}-{daily_max} 之间", "warning")
                return
            
            font_size = int(self._font_size_var.get())
            font_min = self.app.config.get("font_size_min", 12)
            font_max = self.app.config.get("font_size_max", 24)
            
            if not (font_min <= font_size <= font_max):
                self.show_message(f"字体大小必须在 {font_min}-{font_max} 之间", "warning")
                return
            
            # 验证 AI 设置
            ai_enabled = self._ai_enabled_var.get()
            ai_timeout = int(self._ai_timeout_var.get())
            
            if ai_enabled:
                # 验证 API Key
                api_key = self._ai_key_var.get().strip()
                if not api_key:
                    self.show_message("启用 AI 功能需要填写 API Key", "warning")
                    return
                
                # 验证超时时间
                if not (5 <= ai_timeout <= 120):
                    self.show_message("超时时间必须在 5-120 秒之间", "warning")
                    return
                
                # 验证自定义提供商
                provider_key = "xunfei_lite"
                current_name = self._ai_provider_var.get()
                for k, v in self._provider_names:
                    if v == current_name:
                        provider_key = k
                        break
                
                if provider_key == "custom":
                    custom_url = self._ai_custom_url_var.get().strip()
                    if not custom_url:
                        self.show_message("自定义提供商需要填写 API URL", "warning")
                        return
                    if not custom_url.startswith(("http://", "https://")):
                        self.show_message("API URL 必须以 http:// 或 https:// 开头", "warning")
                        return
            
            # 保存学习设置
            self.app.config.set("daily_words", daily_words)
            self.app.config.set("vocab_file", self._vocab_file_var.get())
            self.app.config.set("shuffle_words", self._shuffle_var.get())
            self.app.config.set("show_pinyin", self._show_pinyin_var.get())
            self.app.config.set("auto_play_sound", self._auto_play_sound_var.get())
            
            # 保存回顾单词数量
            review_count = int(self._review_words_count_var.get())
            if not (1 <= review_count <= 10):
                review_count = 3
            self.app.config.set("review_words_count", review_count)
            
            # 保存显示设置
            self.app.config.set("font_size", font_size)
            self.app.config.set("show_progress_bar", self._progress_var.get())
            self.app.config.set("remember_window_size", self._remember_size_var.get())
            
            # 保存行为设置
            self.app.config.set("test_delay", int(self._test_delay_var.get()))
            self.app.config.set("wrong_delay", int(self._wrong_delay_var.get()))
            self.app.config.set("confirm_before_exit", self._confirm_exit_var.get())
            self.app.config.set("auto_save_config", self._auto_save_var.get())
            
            # 保存主题
            self.app.config.set("theme", self._theme_var.get())
            
            # 保存 AI 配置
            self.app.config.set("ai_enabled", ai_enabled)
            self.app.config.set("ai_api_key", self._ai_key_var.get())
            self.app.config.set("ai_timeout", ai_timeout)
            self.app.config.set("ai_show_sentence", self._ai_show_sentence_var.get())
            
            # 获取 provider key
            provider_key = "xunfei_lite"
            current_name = self._ai_provider_var.get()
            for k, v in self._provider_names:
                if v == current_name:
                    provider_key = k
                    break
            self.app.config.set("ai_provider", provider_key)
            self.app.config.set("ai_custom_url", self._ai_custom_url_var.get())
            self.app.config.set("ai_custom_model", self._ai_custom_model_var.get())
            
            # 获取 difficulty key
            difficulty_key = "junior"
            current_diff = self._ai_difficulty_var.get()
            for k, v in self._diff_options:
                if v == current_diff:
                    difficulty_key = k
                    break
            self.app.config.set("ai_difficulty", difficulty_key)
            
            # 保存数据设置
            self.app.config.set("favorites_auto_backup", self._fav_backup_var.get())
            self.app.config.set("favorites_sort", self._fav_sort_var.get())
            
            # 更新 AI 管理器配置
            self.app.ai_manager.configure(
                api_key=self._ai_key_var.get(),
                provider=provider_key,
                custom_url=self._ai_custom_url_var.get(),
                custom_model=self._ai_custom_model_var.get(),
                difficulty=difficulty_key,
                enabled=ai_enabled,
                timeout=ai_timeout
            )
            
            self.app.config.save_config()
            
            self.show_message("设置已保存", "success")
            
        except ValueError as e:
            self.show_message(f"请输入有效的数值: {e}", "error")
    
    def _reset_settings(self):
        """重置设置"""
        if not messagebox.askyesno("确认", "确定要重置所有设置为默认值吗？", parent=self.app.root):
            return
        
        self._daily_words_var.set("20")
        self._vocab_file_var.set("data/vocabulary.txt")
        self._shuffle_var.set(True)
        self._show_pinyin_var.set(True)
        self._auto_play_sound_var.set(False)
        
        self._font_size_var.set("14")
        self._progress_var.set(True)
        self._remember_size_var.set(True)
        
        self._test_delay_var.set("1500")
        self._wrong_delay_var.set("2000")
        self._confirm_exit_var.set(True)
        self._auto_save_var.set(True)
        
        self._theme_var.set("dark")
        
        self._ai_enabled_var.set(False)
        self._ai_key_var.set("")
        self._ai_timeout_var.set("30")
        self._ai_show_sentence_var.set(True)
        self._ai_provider_var.set("讯飞星火 Lite")
        self._ai_custom_url_var.set("")
        self._ai_custom_model_var.set("")
        self._ai_difficulty_var.set("初中")
        
        self._fav_backup_var.set(True)
        self._fav_sort_var.set("time")
        
        self._on_theme_change()
        self._update_ai_settings_display()
        self._save_settings()
        
        self.show_message("已重置为默认设置", "info")
    
    def _load_vocabulary(self):
        """加载词库"""
        vocab_file = self._vocab_file_var.get()
        
        if not os.path.exists(vocab_file):
            self.show_message(f"词库文件不存在: {vocab_file}", "error")
            return
        
        success, result = self.app.vocabulary_manager.load_from_file(vocab_file)
        
        if success:
            self.show_message(f"词库加载成功，共 {result} 个单词", "success")
            self.app.update_status(f"词库已加载: {result} 个单词")
        else:
            self.show_message(f"加载词库失败: {result}", "error")
    
    def _clear_progress(self):
        """清除学习进度"""
        if not messagebox.askyesno(
            "确认",
            "确定要清除所有学习进度吗？\n此操作不可恢复！",
            parent=self.app.root
        ):
            return
        
        self.app.progress_manager.clear_all_progress()
        self.show_message("学习进度已清除", "success")
    
    def _export_all_data(self):
        """导出所有数据"""
        dir_path = filedialog.askdirectory(
            title="选择导出目录",
            parent=self.app.root
        )
        
        if not dir_path:
            return
        
        import datetime
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 导出配置
        config_path = os.path.join(dir_path, f"config_{timestamp}.json")
        self.app.config.save_config()
        import shutil
        if os.path.exists(self.app.config._config_file):
            shutil.copy2(self.app.config._config_file, config_path)
        
        # 导出收藏
        fav_path = os.path.join(dir_path, f"favorites_{timestamp}.txt")
        self.app.favorites_manager.export_to_file(fav_path)
        
        # 导出进度
        progress_path = os.path.join(dir_path, f"progress_{timestamp}.txt")
        self.app.progress_manager.export_progress(progress_path)
        
        self.show_message(f"数据已导出到: {dir_path}", "success")
    
    def on_enter(self, **kwargs):
        """进入页面"""
        super().on_enter(**kwargs)
        self.app.update_status("配置您的学习偏好")
        self.app.update_progress("")
        
        # 滚动到顶部
        self._canvas.yview_moveto(0)
    
    def apply_theme(self):
        """应用主题"""
        super().apply_theme()
        colors = self.colors
        
        # 更新 Canvas 颜色
        self._canvas.configure(bg=colors["bg_primary"])
        self._outer_frame.configure(bg=colors["bg_primary"])
        self._scroll_frame.configure(bg=colors["bg_primary"])
