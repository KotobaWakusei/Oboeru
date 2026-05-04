"""学习页面 - 核心学习功能（自适应布局）"""
import tkinter as tk
from tkinter import ttk, simpledialog
from ui.core.base_page import BasePage
from ui.customtinker import CTFrame, CTLabel, CTProgressbar
import random
import os
from modules.logger import get_logger


class LearningPage(BasePage):
    """学习页面 - 支持窗口自适应"""
    
    page_id = "learning"
    page_title = "学习"
    page_icon = "📚"
    
    # 响应式断点配置
    BREAKPOINTS = {
        "xs": 400,    # 超小屏（手机）
        "sm": 568,    # 小屏（小平板）
        "md": 768,   # 中等（平板）
        "lg": 1024,  # 大屏（笔记本）
        "xl": 1366,  # 超大屏（桌面）
    }
    
    def create_widgets(self):
        """创建组件"""
        colors = self.colors
        
        # 初始化 AI 版本控制
        self._current_ai_version = 0
        self._logger = get_logger()
        
        # 防抖相关
        self._resize_timer = None
        self._last_width = 0
        
        # 快捷键冷却控制
        self._last_nav_time = 0
        self._nav_cooldown = 0.8  # 冷却时间（秒）
        self._nav_hint_shown = False  # 是否已显示"别急"提示
        
        # 配置页面网格
        self._container.columnconfigure(0, weight=1)
        self._container.rowconfigure(1, weight=1)  # 单词区域可扩展
        
        self._create_header()
        self._create_word_display()
        self._create_options()
        self._create_controls()
        
        # 绑定窗口大小变化事件（使用防抖）
        self.bind("<Configure>", self._on_resize_debounced)
    
    def setup_layout(self):
        """设置布局"""
        pass
    
    def bind_events(self):
        """绑定事件"""
        self.bind("<Return>", lambda e: self._next_word())
        self.bind("<Left>", lambda e: self._prev_word())
        self.bind("<Right>", lambda e: self._next_word())
        self.bind("<space>", lambda e: self._next_word())
        # 添加 Up/Down 快捷键支持
        self.bind("<Up>", lambda e: self._prev_word_with_cooldown())
        self.bind("<Down>", lambda e: self._next_word_with_cooldown())
    
    def _on_resize_debounced(self, event):
        """窗口大小变化时防抖处理"""
        if event.widget != self._container:
            return
        
        # 防抖：只在宽度变化超过50px或首次时触发
        width = event.width
        if abs(width - self._last_width) < 50 and self._last_width > 0:
            return
        
        self._last_width = width
        
        # 取消之前的定时器
        if self._resize_timer:
            self.after_cancel(self._resize_timer)
        
        # 延迟100ms后执行（防止频繁触发）
        self._resize_timer = self.after(100, lambda: self._apply_responsive_layout(event))
    
    def _apply_responsive_layout(self, event):
        """应用响应式布局"""
        width = event.width
        height = event.height
        
        # 确定当前断点
        if width < self.BREAKPOINTS["xs"]:
            size_key = "xs"
        elif width < self.BREAKPOINTS["sm"]:
            size_key = "sm"
        elif width < self.BREAKPOINTS["md"]:
            size_key = "md"
        elif width < self.BREAKPOINTS["lg"]:
            size_key = "lg"
        else:
            size_key = "xl"
        
        # 根据断点设置字体大小
        font_config = {
            "xs": {"word": 18, "meaning": 11, "option": 9, "heading": 14},
            "sm": {"word": 22, "meaning": 12, "option": 10, "heading": 16},
            "md": {"word": 26, "meaning": 14, "option": 11, "heading": 18},
            "lg": {"word": 30, "meaning": 16, "option": 12, "heading": 20},
            "xl": {"word": 34, "meaning": 18, "option": 13, "heading": 22},
        }
        
        config = font_config[size_key]
        
        try:
            # 更新字体
            self._word_label.configure(font=("Segoe UI", config["word"], "bold"))
            self._meaning_label.configure(
                font=("Segoe UI", config["meaning"], "bold"),
                wraplength=max(width - 120, 150)
            )
            
            for btn in self._option_buttons:
                btn.configure(font=("Segoe UI", config["option"]))
            
            # 更新例句区域
            wrap_length = max(width - 140, 180)
            self._sentence_label.configure(wraplength=wrap_length)
            
            # 根据屏幕宽度调整选项布局
            if width < self.BREAKPOINTS["sm"]:
                # 小屏：单列显示选项
                for i, btn in enumerate(self._option_buttons):
                    btn.grid(row=i, column=0, padx=5, pady=3, sticky="ew")
                # 隐藏第二列
                self._options_frame.columnconfigure(1, weight=0)
                self._options_frame.columnconfigure(0, weight=1)
            else:
                # 大屏：双列显示选项
                for i, btn in enumerate(self._option_buttons):
                    row = i // 2
                    col = i % 2
                    btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew", ipadx=10, ipady=8)
                self._options_frame.columnconfigure(0, weight=1)
                self._options_frame.columnconfigure(1, weight=1)
                
        except Exception as e:
            self._logger.debug(f"布局调整异常: {e}")
    
    def _create_header(self):
        """创建头部区域"""
        colors = self.colors
        
        header = CTFrame(self._container, style_manager=self._style_manager, bg=colors["bg_primary"])
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.columnconfigure(0, weight=1)
        
        # 阶段标签
        self._stage_label = CTLabel(
            header,
            style_manager=self._style_manager,
            text=self._t('learning.stage.ready', '准备开始'),
            font=self._style_manager.get_font("heading"),
            bg=colors["bg_primary"],
            fg=colors["fg_primary"]
        )
        self._stage_label.grid(row=0, column=0, sticky="w")
        
        # 进度区域
        progress_frame = CTFrame(header, style_manager=self._style_manager, bg=colors["bg_primary"])
        progress_frame.grid(row=0, column=1, sticky="e")
        
        # 进度条
        self._progress_bar = CTProgressbar(
            progress_frame,
            style_manager=self._style_manager,
            mode='determinate',
            length=120,
            maximum=100
        )
        self._progress_bar.pack(side=tk.RIGHT)
        
        # 进度百分比
        self._percent_label = CTLabel(
            progress_frame,
            style_manager=self._style_manager,
            text="0%",
            font=self._style_manager.get_font("body"),
            bg=colors["bg_primary"],
            fg=colors["accent"],
            width=5
        )
        self._percent_label.pack(side=tk.RIGHT, padx=(0, 5))
    
    def _create_word_display(self):
        """创建单词显示区域"""
        colors = self.colors
        
        # 主容器（包含单词卡片和最近单词）
        main_container = CTFrame(self._container, style_manager=self._style_manager, bg=colors["bg_primary"])
        main_container.grid(row=1, column=0, sticky="nsew", pady=10)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(0, weight=1)
        
        # 单词卡片
        self._word_card = CTFrame(
            main_container,
            style_manager=self._style_manager,
            bg=colors["bg_card"]
        )
        self._word_card.configure(highlightbackground=colors["border"], highlightthickness=1)
        self._word_card.grid(row=0, column=0, sticky="nsew")
        
        # 配置卡片内部网格
        self._word_card.columnconfigure(0, weight=1)
        self._word_card.rowconfigure(0, weight=1)
        
        # 单词容器
        word_container = CTFrame(self._word_card, style_manager=self._style_manager, bg=colors["bg_card"])
        word_container.grid(row=0, column=0, sticky="nsew")
        word_container.columnconfigure(0, weight=1)
        word_container.rowconfigure(1, weight=1)
        
        # 单词标签
        self._word_label = CTLabel(
            word_container,
            style_manager=self._style_manager,
            text=self._t('learning.placeholder', '点击「开始学习」开始'),
            font=("Segoe UI", 28, "bold"),
            bg=colors["bg_card"],
            fg=colors["accent"]
        )
        self._word_label.grid(row=0, column=0, pady=(20, 5))
        
        # 词性标签
        self._pos_label = CTLabel(
            word_container,
            style_manager=self._style_manager,
            text="",
            font=self._style_manager.get_font("subheading"),
            bg=colors["bg_card"],
            fg=colors["warning"]
        )
        self._pos_label.grid(row=1, column=0, pady=5)
        
        # 分隔线
        sep_frame = CTFrame(word_container, style_manager=self._style_manager, bg=colors["border"], height=1)
        sep_frame.grid(row=2, column=0, sticky="ew", padx=30, pady=10)
        
        # 意思标签
        self._meaning_label = CTLabel(
            word_container,
            style_manager=self._style_manager,
            text="",
            font=("Segoe UI", 16, "bold"),
            bg=colors["bg_card"],
            fg=colors["fg_primary"],
            wraplength=600,
            justify=tk.CENTER
        )
        self._meaning_label.grid(row=3, column=0, pady=10, padx=20)
        
        # AI 例句区域
        self._sentence_frame = CTFrame(word_container, style_manager=self._style_manager, bg=colors["bg_card"])
        self._sentence_frame.grid(row=4, column=0, pady=(5, 10), padx=20, sticky="ew")
        
        self._sentence_label = CTLabel(
            self._sentence_frame,
            style_manager=self._style_manager,
            text="",
            font=("Segoe UI", 11),
            bg=colors["bg_card"],
            fg=colors["success"],
            wraplength=550,
            justify=tk.LEFT
        )
        self._sentence_label.pack(anchor="w")
        
        self._sentence_loading = CTLabel(
            self._sentence_frame,
            style_manager=self._style_manager,
            text="",
            font=("Segoe UI", 10),
            bg=colors["bg_card"],
            fg=colors["fg_secondary"]
        )
        self._sentence_loading.pack(anchor="w")
        
        # 最近背诵单词回顾面板（背诵阶段显示）
        self._review_frame = CTFrame(main_container, style_manager=self._style_manager, bg=colors["bg_secondary"])
        self._review_frame.configure(highlightbackground=colors["border"], highlightthickness=1)
        # 初始隐藏，只在背诵阶段显示
        
        review_header = CTFrame(self._review_frame, style_manager=self._style_manager, bg=colors["bg_card"])
        review_header.pack(fill=tk.X, padx=1, pady=1)
        
        CTLabel(
            review_header,
            style_manager=self._style_manager,
            text=self._t('learning.recent_title', '📝 最近背诵'),
            font=self._style_manager.get_font("caption"),
            bg=colors["bg_card"],
            fg=colors["accent"],
            padx=10,
            pady=5
        ).pack(side=tk.LEFT)
        
        self._review_words_container = CTFrame(self._review_frame, style_manager=self._style_manager, bg=colors["bg_secondary"])
        self._review_words_container.pack(fill=tk.X, padx=10, pady=8)
        
        # 存储单词标签用于更新
        self._review_word_labels = []
    
    def _update_review_words(self):
        """更新最近背诵单词列表"""
        colors = self.colors
        
        # 彻底清除现有标签和框架中的所有子组件
        for child in self._review_words_container.winfo_children():
            try:
                child.destroy()
            except Exception:
                pass
        self._review_word_labels.clear()
        
        # 获取配置的回顾数量
        review_count = self.app.config.get_int("review_words_count", 3)
        
        # 如果设置为0或负数，禁用回顾功能
        if review_count <= 0:
            self._review_frame.grid_forget()
            return
        
        # 只在背诵阶段显示
        if self.app.stage != "recite" or not self.app.today_words:
            self._review_frame.grid_forget()
            return
        
        # 获取当前索引之前的单词（不包括当前单词）
        current_idx = self.app.current_word_index
        if current_idx == 0:
            self._review_frame.grid_forget()
            return
        
        # 使用双栈逻辑：获取最近N个单词
        start_idx = max(0, current_idx - review_count)
        review_words = self.app.today_words[start_idx:current_idx]
        
        if not review_words:
            self._review_frame.grid_forget()
            return
        
        # 显示回顾面板
        self._review_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        
        # 创建单词标签（严格限制数量）
        for word in review_words[-review_count:]:  # 确保不超过设定数量
            word_frame = CTFrame(self._review_words_container, style_manager=self._style_manager, bg=colors["bg_secondary"])
            word_frame.pack(side=tk.LEFT, padx=8)
            
            # 单词标签（默认只显示单词）
            word_label = CTLabel(
                word_frame,
                style_manager=self._style_manager,
                text=word.word,
                font=self._style_manager.get_font("body"),
                bg=colors["bg_secondary"],
                fg=colors["fg_primary"],
                cursor="hand2"
            )
            word_label.pack()
            
            # 存储单词信息用于显示意思
            word_label._word_data = word
            
            # 鼠标悬停显示意思
            def on_enter(event, lbl=word_label):
                lbl.configure(text=f"{word.word}: {word.meaning}", fg=colors["success"])
            
            def on_leave(event, lbl=word_label, w=word):
                lbl.configure(text=w.word, fg=colors["fg_primary"])
            
            # 点击切换显示/隐藏意思
            def on_click(event, lbl=word_label, w=word):
                current_text = lbl.cget("text")
                if ":" in current_text:
                    lbl.configure(text=w.word, fg=colors["fg_primary"])
                else:
                    lbl.configure(text=f"{w.word}: {w.meaning}", fg=colors["success"])
            
            word_label.bind("<Enter>", on_enter)
            word_label.bind("<Leave>", on_leave)
            word_label.bind("<Button-1>", on_click)
            
            self._review_word_labels.append(word_label)
    
    def _create_options(self):
        """创建选项区域"""
        colors = self.colors
        
        # 选项容器 - 初始状态不显示
        self._options_frame = tk.Frame(self._container, bg=colors["bg_primary"])
        # 不在这里grid，初始状态隐藏
        
        # 配置列使其自适应
        for i in range(2):
            self._options_frame.columnconfigure(i, weight=1)
        
        # 选项按钮
        self._option_buttons = []
        for i in range(4):
            row = i // 2
            col = i % 2
            
            btn = tk.Button(
                self._options_frame,
                text="",
                font=("Segoe UI", 12),
                bg=colors["bg_secondary"],
                fg=colors["fg_primary"],
                activebackground=colors["accent"],
                activeforeground=colors["fg_primary"],
                relief=tk.FLAT,
                cursor="hand2",
                state=tk.DISABLED,
                command=lambda idx=i: self._check_answer(idx)
            )
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew", ipadx=10, ipady=8)
            self._option_buttons.append(btn)
    
    def _create_controls(self):
        """创建控制按钮区域"""
        colors = self.colors
        
        controls_frame = tk.Frame(self._container, bg=colors["bg_primary"])
        controls_frame.grid(row=3, column=0, sticky="ew")
        controls_frame.columnconfigure(1, weight=1)
        
        # 左侧导航按钮
        left_frame = tk.Frame(controls_frame, bg=colors["bg_primary"])
        left_frame.grid(row=0, column=0, sticky="w")
        
        self._prev_btn = ttk.Button(
            left_frame,
            text=self._t('learning.action.previous', '◀ 上一个'),
            command=self._prev_word,
            style="Nav.TButton",
            state=tk.DISABLED
        )
        self._prev_btn.pack(side=tk.LEFT, padx=2)
        
        self._next_btn = ttk.Button(
            left_frame,
            text=self._t('learning.action.next', '下一个 ▶'),
            command=self._next_word,
            style="Nav.TButton",
            state=tk.DISABLED
        )
        self._next_btn.pack(side=tk.LEFT, padx=2)
        
        # 中间操作按钮
        center_frame = tk.Frame(controls_frame, bg=colors["bg_primary"])
        center_frame.grid(row=0, column=1)
        
        self._fav_btn = ttk.Button(
            center_frame,
            text=self._t('learning.action.favorite', '☆ 收藏'),
            command=self._toggle_favorite,
            style="Secondary.TButton",
            state=tk.DISABLED
        )
        self._fav_btn.pack(side=tk.LEFT, padx=2)
        
        self._pronounce_btn = ttk.Button(
            center_frame,
            text=self._t('learning.action.pronounce', '🔊 发音'),
            command=self._play_pronunciation,
            style="Secondary.TButton",
            state=tk.DISABLED
        )
        self._pronounce_btn.pack(side=tk.LEFT, padx=2)
        
        self._ai_btn = ttk.Button(
            center_frame,
            text=self._t('learning.action.ai_sentence', '🤖 例句'),
            command=self._generate_ai_sentence,
            style="Secondary.TButton",
            state=tk.DISABLED
        )
        self._ai_btn.pack(side=tk.LEFT, padx=2)
        
        # 右侧功能按钮
        self._controls_right_frame = tk.Frame(controls_frame, bg=colors["bg_primary"])
        self._controls_right_frame.grid(row=0, column=2, sticky="e")

        self._start_btn = ttk.Button(
            self._controls_right_frame,
            text=self._t('learning.action.start', '▶ 开始学习'),
            command=self._start_learning,
            style="Primary.TButton"
        )
        self._start_btn.pack(side=tk.LEFT, padx=2)
        
        self._review_btn = ttk.Button(
            self._controls_right_frame,
            text=self._t('learning.action.review', '🧠 复习'),
            command=self._start_review,
            style="Primary.TButton"
        )
        self._review_btn.pack(side=tk.LEFT, padx=2)
    
    def on_enter(self, **kwargs):
        """进入页面"""
        super().on_enter(**kwargs)
        
        mode = kwargs.get("mode", "new")
        
        if mode == "new":
            self._prepare_new_learning()
        elif mode == "review":
            self._start_review_mode()
        elif mode == "search":
            self._search_words()
    
    def _prepare_new_learning(self):
        """准备新学习"""
        self.app.update_status("点击「开始学习」开始今日学习")

    def on_leave(self):
        """离开页面时如果处于学习中，结束学习并恢复界面"""
        super().on_leave()
        # 如果开始按钮被隐藏，说明处于学习会话中或刚开始后未恢复
        if getattr(self, '_start_buttons_hidden', False):
            try:
                # 结束当前学习（保存会话）
                self._finish_learning()
            except Exception:
                pass
            try:
                self._show_start_review_buttons()
            except Exception:
                pass
            try:
                self.app.show_navbar()
            except Exception:
                pass
    
    def _start_learning(self):
        """开始学习 - 背诵模式"""
        if len(self.app.vocabulary_manager) == 0:
            self.show_message("请先加载词库", "warning")
            return
        
        daily_words = self.app.config.get_int("daily_words", 20)
        
        self.app.today_words = self.app.vocabulary_manager.get_words(
            count=daily_words,
            shuffle=self.app.config.get_bool("shuffle_words", True)
        )
        
        self.app.current_word_index = 0
        self.app.unknown_words = []
        self.app.stage = "recite"
        self.app.test_mode = False
        
        # 重置 AI 请求版本
        self._current_ai_version = self.app.ai_manager.increment_version()
        
        self.app.progress_manager.start_session()
        
        # 预加载 AI 例句（后台执行）
        if self.app.ai_manager.is_available() and self.app.config.get_bool("ai_show_sentence", True):
            self.app.ai_manager.preload_for_session(self.app.today_words)
        
        self._enable_controls()
        self._show_current_word()
        # 隐藏开始/复习按钮并隐藏导航栏，进入专注学习模式
        try:
            self._hide_start_review_buttons()
        except Exception:
            pass
        try:
            self.app.hide_navbar()
        except Exception:
            pass

        self.show_message(f"开始学习 {len(self.app.today_words)} 个单词", "success")
    
    def _start_review_mode(self):
        """开始复习模式"""
        # 自动加载词库
        if len(self.app.vocabulary_manager) == 0:
            vocab_file = self.app.config.get("vocab_file", "data/vocabulary.txt")
            if os.path.exists(vocab_file):
                success, result = self.app.vocabulary_manager.load_from_file(vocab_file)
                if not success:
                    self.show_message(f"加载词库失败: {result}", "error")
                    return
            else:
                self.show_message("请先在设置中加载词库", "warning")
                return
        
        all_words = [word.word for word in self.app.vocabulary_manager.vocabulary]
        due_words = self.app.progress_manager.get_due_words(all_words)
        
        if not due_words:
            self.show_message("暂时没有需要复习的单词", "info")
            return
        
        word_map = {word.word: word for word in self.app.vocabulary_manager.vocabulary}
        review_words = [word_map[w] for w in due_words if w in word_map]
        
        self.app.today_words = review_words
        self.app.current_word_index = 0
        self.app.unknown_words = []
        self.app.stage = "test"
        self.app.test_mode = True
        
        self.app.progress_manager.start_session()
        
        self._enable_controls()
        self._show_current_word()
        # 隐藏开始/复习按钮并隐藏导航栏，进入专注复习模式
        try:
            self._hide_start_review_buttons()
        except Exception:
            pass
        try:
            self.app.hide_navbar()
        except Exception:
            pass

        self.show_message(f"找到 {len(review_words)} 个需要复习的单词", "success")
    
    def _start_review(self):
        """智能复习按钮"""
        self._start_review_mode()
    
    def _search_words(self):
        """搜索单词"""
        # 自动加载词库
        if len(self.app.vocabulary_manager) == 0:
            vocab_file = self.app.config.get("vocab_file", "data/vocabulary.txt")
            if os.path.exists(vocab_file):
                success, result = self.app.vocabulary_manager.load_from_file(vocab_file)
                if not success:
                    self.show_message(f"加载词库失败: {result}", "error")
                    return
            else:
                self.show_message("请先在设置中加载词库", "warning")
                return
        
        query = simpledialog.askstring(
            "搜索单词",
            "请输入要搜索的单词或中文意思：",
            parent=self.app.root
        )
        
        if not query:
            return
        
        results = self.app.vocabulary_manager.search_words(query)
        
        if not results:
            self.show_message(f"没有找到包含 '{query}' 的单词", "info")
            return
        
        self._show_search_results(query, results)
    
    def _show_search_results(self, query: str, results: list):
        """显示搜索结果"""
        colors = self.colors
        
        dialog = tk.Toplevel(self.app.root)
        dialog.title(f"搜索结果: {query}")
        dialog.geometry("500x300")
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.configure(bg=colors["bg_primary"])
        
        frame = tk.Frame(dialog, bg=colors["bg_primary"], padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("word", "pos", "meaning")
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        
        tree.heading("word", text=self._t('learning.table.word', '单词'))
        tree.heading("pos", text=self._t('learning.table.pos', '词性'))
        tree.heading("meaning", text=self._t('learning.table.meaning', '中文意思'))
        
        tree.column("word", width=80)
        tree.column("pos", width=50)
        tree.column("meaning", width=250)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        for word in results:
            tree.insert("", tk.END, values=(word.word, word.pos, word.meaning))
        
        btn_frame = tk.Frame(dialog, bg=colors["bg_primary"])
        btn_frame.pack(fill=tk.X, padx=10, pady=8)
        
        def learn_selected():
            selected = tree.selection()
            if selected:
                item = tree.item(selected[0])
                word_text = item["values"][0]
                word = self.app.vocabulary_manager.get_word_by_text(word_text)
                if word:
                    dialog.destroy()
                    self.app.today_words = [word]
                    self.app.current_word_index = 0
                    self.app.unknown_words = []
                    self.app.stage = "recite"
                    self.app.test_mode = False
                    self._enable_controls()
                    self._show_current_word()
        
        ttk.Button(btn_frame, text=self._t('learning.dialog.learn_selected', '学习选中'), command=learn_selected, style="Primary.TButton").pack(side=tk.RIGHT, padx=3)
        ttk.Button(btn_frame, text=self._t('learning.dialog.close', '关闭'), command=dialog.destroy, style="Secondary.TButton").pack(side=tk.RIGHT, padx=3)
    
    def _show_current_word(self):
        """显示当前单词"""
        if not self.app.today_words:
            return
        
        idx = self.app.current_word_index
        if idx >= len(self.app.today_words):
            self._handle_stage_complete()
            return
        
        # 递增 AI 请求版本（防止竞态）
        self._current_ai_version = self.app.ai_manager.increment_version()
        
        current = self.app.today_words[idx]
        
        self._word_label.configure(text=current.word)
        self._pos_label.configure(text=current.pos)
        
        # 清除例句
        self._sentence_label.configure(text="")
        self._sentence_loading.configure(text="")
        
        if self.app.stage == "recite":
            self._stage_label.configure(text="📖 背诵阶段")
            self._meaning_label.configure(text=current.meaning)
            self._meaning_label.grid()
            self._hide_options()
            self._update_review_words()  # 更新最近单词回顾
            self.app.update_status("背诵：记忆单词和意思，按空格或「下一个」继续")
            
            # 自动生成 AI 例句（如果配置启用）
            if self.app.config.get_bool("ai_show_sentence", True):
                self._load_ai_sentence_async(current)
        else:
            self._stage_label.configure(text="📝 测试阶段")
            self._meaning_label.configure(text="")
            self._meaning_label.grid_remove()
            self._review_frame.grid_forget()  # 隐藏回顾面板
            options = self.app.vocabulary_manager.generate_options(current)
            self._update_options(options)
            self._show_options()
            self.app.update_status("测试：请选择正确答案")
        
        percent = (idx + 1) / len(self.app.today_words) * 100
        self._progress_bar["value"] = percent
        self._percent_label.configure(text=f"{int(percent)}%")
        
        stage_text = "背诵" if self.app.stage == "recite" else "测试"
        self.app.update_progress(f"{stage_text} {idx + 1}/{len(self.app.today_words)}")
        
        is_fav = self.app.favorites_manager.is_favorite(current.word)
        self._fav_btn.configure(text="★ 已收藏" if is_fav else "☆ 收藏")
    
    def _update_options(self, options: list):
        """更新选项"""
        colors = self.colors
        for i, btn in enumerate(self._option_buttons):
            if i < len(options):
                btn.configure(text=options[i], state=tk.NORMAL, bg=colors["bg_secondary"])
            else:
                btn.configure(text="", state=tk.DISABLED)
    
    def _show_options(self):
        """显示选项"""
        self._options_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        for btn in self._option_buttons:
            btn.configure(state=tk.NORMAL)
    
    def _hide_options(self):
        """隐藏选项"""
        self._options_frame.grid_forget()  # 完全隐藏选项框架
        for btn in self._option_buttons:
            btn.configure(state=tk.DISABLED, text="")
    
    def _enable_controls(self):
        """启用控制按钮"""
        self._prev_btn.configure(state=tk.NORMAL)
        self._next_btn.configure(state=tk.NORMAL)
        self._fav_btn.configure(state=tk.NORMAL)
        self._pronounce_btn.configure(state=tk.NORMAL)
        
        # 如果 AI 功能可用，启用 AI 按钮
        if self.app.ai_manager.is_available():
            self._ai_btn.configure(state=tk.NORMAL)
    
    def _disable_controls(self):
        """禁用控制按钮"""
        self._prev_btn.configure(state=tk.DISABLED)
        self._next_btn.configure(state=tk.DISABLED)
        self._fav_btn.configure(state=tk.DISABLED)
        self._pronounce_btn.configure(state=tk.DISABLED)
        self._ai_btn.configure(state=tk.DISABLED)
    
    def _check_answer(self, selected_index: int):
        """检查答案"""
        if not (self.app.stage == "test" and self.app.today_words):
            return
        
        current = self.app.today_words[self.app.current_word_index]
        options = [btn.cget("text") for btn in self._option_buttons]
        selected_meaning = options[selected_index]
        
        colors = self.colors
        
        # 禁用所有选项按钮，防止重复点击
        for btn in self._option_buttons:
            btn.configure(state=tk.DISABLED)

        if selected_meaning == current.meaning:
            self._option_buttons[selected_index].configure(bg=colors["success"])
            self.show_message(f"✓ 正确！ {current.word}", "success")
            self.app.progress_manager.record_answer(current.word, True)
            self.app.current_word_index += 1
            delay = self.app.config.get("test_delay", 800)
            self.after(delay, self._show_current_word)
        else:
            self._option_buttons[selected_index].configure(bg=colors["error"])
            self.show_message(f"✗ 错误！正确：{current.meaning}", "error")
            self.app.progress_manager.record_answer(current.word, False)
            self.app.unknown_words.append(current)
            
            for i, btn in enumerate(self._option_buttons):
                if btn.cget("text") == current.meaning:
                    btn.configure(bg=colors["success"])
            
            delay = self.app.config.get("wrong_delay", 1500)
            self.after(delay, self._show_current_word)
    
    def _prev_word(self):
        """上一个单词"""
        if self.app.today_words and self.app.current_word_index > 0:
            self.app.current_word_index -= 1
            self._show_current_word()
    
    def _next_word(self):
        """下一个单词"""
        if not self.app.today_words:
            return
        
        if self.app.current_word_index < len(self.app.today_words) - 1:
            self.app.current_word_index += 1
            self._show_current_word()
        else:
            self._handle_stage_complete()
    
    def _prev_word_with_cooldown(self):
        """带冷却时间的上一个单词（Up键）"""
        import time
        
        # 只在背诵阶段生效
        if self.app.stage != "recite":
            return
        
        if not self.app.today_words:
            return
        
        current_time = time.time()
        time_diff = current_time - self._last_nav_time
        
        if time_diff < self._nav_cooldown:
            # 冷却中，显示提示
            if not self._nav_hint_shown:
                self.show_message("别那么急嘛！好好背单词 📖", "warning")
                self._nav_hint_shown = True
            return
        
        # 重置提示状态
        self._nav_hint_shown = False
        self._last_nav_time = current_time
        
        # 执行切换
        if self.app.current_word_index > 0:
            self.app.current_word_index -= 1
            self._show_current_word()
    
    def _next_word_with_cooldown(self):
        """带冷却时间的下一个单词（Down键）"""
        import time
        
        # 只在背诵阶段生效
        if self.app.stage != "recite":
            return
        
        if not self.app.today_words:
            return
        
        current_time = time.time()
        time_diff = current_time - self._last_nav_time
        
        if time_diff < self._nav_cooldown:
            # 冷却中，显示提示
            if not self._nav_hint_shown:
                self.show_message("别那么急嘛！好好背单词 📖", "warning")
                self._nav_hint_shown = True
            return
        
        # 重置提示状态
        self._nav_hint_shown = False
        self._last_nav_time = current_time
        
        # 执行切换
        if self.app.current_word_index < len(self.app.today_words) - 1:
            self.app.current_word_index += 1
            self._show_current_word()
        else:
            self._handle_stage_complete()
    
    def _toggle_favorite(self):
        """切换收藏"""
        if not self.app.today_words:
            return
        
        idx = self.app.current_word_index
        if idx >= len(self.app.today_words):
            return
        
        current = self.app.today_words[idx]
        word_key = current.word
        
        if self.app.favorites_manager.is_favorite(word_key):
            self.app.favorites_manager.remove_word(word_key)
            self._fav_btn.configure(text="☆ 收藏")
            self.show_message(f"已取消收藏: {word_key}", "info")
        else:
            self.app.favorites_manager.add_from_vocabulary(current)
            self._fav_btn.configure(text="★ 已收藏")
            self.show_message(f"已收藏: {word_key}", "success")
        
        self.app.favorites_manager.save_favorites()
        self.app.update_favorites_count()
    
    def _play_pronunciation(self):
        """播放发音"""
        if not self.app.today_words:
            return
        
        idx = self.app.current_word_index
        if idx >= len(self.app.today_words):
            return
        
        if not self.app.tts_manager.is_available():
            self.show_message("发音功能不可用", "warning")
            return
        
        current = self.app.today_words[idx]
        success = self.app.tts_manager.speak_word(current.word)
        
        if success:
            self.app.update_status(f"正在播放: {current.word}")
        else:
            self.show_message("发音失败", "error")
    
    def _load_ai_sentence_async(self, word):
        """异步加载 AI 例句（带版本控制）"""
        if not self.app.ai_manager.is_available():
            return
        
        # 获取当前版本号
        request_version = getattr(self, '_current_ai_version', 0)
        
        self._sentence_loading.configure(text="正在生成例句...")
        
        def on_result(success, result):
            # 检查版本是否过期（防止快速切换时显示错误单词的例句）
            current_version = self.app.ai_manager.current_version
            if request_version < current_version:
                self._logger.debug(f"跳过过期例句: {word.word} (请求版本={request_version}, 当前={current_version})")
                return
            
            # 使用 after 确保在主线程中更新 UI
            self.after(0, lambda: self._on_ai_result(success, result))
        
        self.app.ai_manager.generate_sentence(
            word.word,
            word.meaning,
            callback=on_result,
            version=request_version
        )
    
    def _on_ai_result(self, success: bool, result: str):
        """AI 例句生成结果回调"""
        if success:
            self._sentence_label.configure(text=result)
            self._sentence_loading.configure(text="")
        else:
            self._sentence_loading.configure(text=f"生成失败: {result}")
    
    def _generate_ai_sentence(self):
        """手动生成 AI 例句"""
        if not self.app.today_words:
            return
        
        idx = self.app.current_word_index
        if idx >= len(self.app.today_words):
            return
        
        if not self.app.ai_manager.is_available():
            self.show_message("AI 功能未配置，请在设置中配置 API Key", "warning")
            return
        
        current = self.app.today_words[idx]
        self._load_ai_sentence_async(current)
    
    def _handle_stage_complete(self):
        """处理阶段完成"""
        from tkinter import messagebox
        
        if self.app.stage == "recite":
            if messagebox.askyesno("背诵完成", f"背诵完成！共 {len(self.app.today_words)} 个单词\n\n是否进入测试阶段？", parent=self.app.root):
                self.app.stage = "test"
                self.app.current_word_index = 0
                self._show_current_word()
            else:
                self._finish_learning()
        else:
            if self.app.unknown_words:
                if messagebox.askyesno("测试完成", f"有 {len(self.app.unknown_words)} 个单词需要复习\n\n是否继续复习？", parent=self.app.root):
                    self.app.today_words = self.app.unknown_words.copy()
                    self.app.unknown_words = []
                    self.app.current_word_index = 0
                    self.app.stage = "recite"
                    self._show_current_word()
                else:
                    self._finish_learning()
            else:
                self.show_message("🎉 恭喜！全部掌握！", "success")
                self._finish_learning()
    
    def _finish_learning(self):
        """完成学习"""
        if self.app.progress_manager.session_start_time is not None:
            self.app.progress_manager.end_session(
                words_studied=len(self.app.today_words),
                words_reviewed=len(self.app.unknown_words)
            )
        
        self.app.today_words = []
        self.app.current_word_index = 0
        self.app.unknown_words = []
        
        self._disable_controls()
        self._hide_options()
        
        self._word_label.configure(text="✅ 学习完成！")
        self._pos_label.configure(text="")
        self._meaning_label.configure(text="")
        self._stage_label.configure(text="学习完成")
        
        self.app.update_status("今日学习已完成")
        self.app.update_progress("")
        # 恢复开始/复习按钮和导航栏
        try:
            self._show_start_review_buttons()
        except Exception:
            pass
        try:
            self.app.show_navbar()
        except Exception:
            pass

    def _hide_start_review_buttons(self):
        """隐藏页面右侧的开始和复习按钮（进入专注模式）"""
        try:
            # 隐藏整个右侧控件容器，避免空白占位导致左侧按钮位置不变
            if getattr(self, '_controls_right_frame', None):
                try:
                    self._controls_right_frame.grid_remove()
                except Exception:
                    try:
                        self._controls_right_frame.pack_forget()
                    except Exception:
                        pass
            self._start_buttons_hidden = True
        except Exception:
            self._start_buttons_hidden = True

    def _show_start_review_buttons(self):
        """显示页面右侧的开始和复习按钮（离开专注模式）"""
        try:
            # 恢复整个右侧控件容器的布局
            if getattr(self, '_controls_right_frame', None) and getattr(self, '_start_buttons_hidden', False):
                try:
                    self._controls_right_frame.grid(row=0, column=2, sticky="e")
                except Exception:
                    try:
                        self._controls_right_frame.pack()
                    except Exception:
                        pass
            self._start_buttons_hidden = False
        except Exception:
            self._start_buttons_hidden = False

    def exit_learning(self):
        """供外部调用以退出学习，会结束会话并返回主页"""
        from tkinter import messagebox

        try:
            if messagebox.askyesno(self._t('learning.dialog.exit_confirm_title', '退出学习'), self._t('learning.dialog.exit_confirm', '确定要退出当前学习并结束本次会话吗？'), parent=self.app.root):
                try:
                    self._finish_learning()
                except Exception:
                    pass
                try:
                    self.app.show_navbar()
                except Exception:
                    pass
                try:
                    self.app.navigate_to('home')
                except Exception:
                    pass
        except Exception:
            # 默认直接结束
            try:
                self._finish_learning()
            except Exception:
                pass
            try:
                self.app.show_navbar()
            except Exception:
                pass
            try:
                self.app.navigate_to('home')
            except Exception:
                pass
    
    def apply_theme(self):
        """应用主题"""
        super().apply_theme()
        colors = self.colors
        
        self._word_card.configure(bg=colors["bg_card"], highlightbackground=colors["border"])
        
        for widget in self._word_card.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=colors["bg_card"])
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label):
                        try:
                            child.configure(bg=colors["bg_card"])
                        except Exception:
                            pass
        
        # 更新例句区域颜色
        self._sentence_frame.configure(bg=colors["bg_card"])
        self._sentence_label.configure(bg=colors["bg_card"], fg=colors["success"])
        self._sentence_loading.configure(bg=colors["bg_card"], fg=colors["fg_secondary"])
        
        for btn in self._option_buttons:
            if btn.cget("state") == tk.NORMAL:
                btn.configure(bg=colors["bg_secondary"])