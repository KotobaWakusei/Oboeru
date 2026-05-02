"""首页 - 应用入口页面（自适应布局）"""
import tkinter as tk
from tkinter import ttk
from ui.core.base_page import BasePage
from ui.customtinker import CTFrame, CTLabel, CTButton
import os


class HomePage(BasePage):
    """首页 - 支持窗口自适应和滚动"""
    
    page_id = "home"
    page_title = "首页"
    page_icon = "🏠"
    
    def create_widgets(self):
        """创建组件"""
        colors = self.colors
        
        # 配置页面网格
        self._container.columnconfigure(0, weight=1)
        self._container.rowconfigure(0, weight=1)
        
        # 创建可滚动区域
        self._create_scrollable_area()
        
        self._create_welcome_section()
        self._create_quick_actions()
        self._create_today_stats()
        self._create_recent_section()
        
        # 延迟绑定滚轮事件
        self.after(100, self._rebind_mousewheel)
    
    def _create_scrollable_area(self):
        """创建可滚动区域"""
        colors = self.colors
        
        # 外层容器
        self._outer_frame = CTFrame(self._container, style_manager=self._style_manager, bg=colors["bg_primary"])
        self._outer_frame.grid(row=0, column=0, sticky="nsew")
        self._outer_frame.columnconfigure(0, weight=1)
        self._outer_frame.rowconfigure(0, weight=1)
        
        # 创建 Canvas
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
        
        # 内层容器
        self._scroll_frame = CTFrame(self._canvas, style_manager=self._style_manager, bg=colors["bg_primary"])
        
        # 配置滚动
        self._canvas.configure(yscrollcommand=self._scrollbar.set)
        
        # 布局
        self._scrollbar.grid(row=0, column=1, sticky="ns")
        self._canvas.grid(row=0, column=0, sticky="nsew")
        
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
        
        # 设置内边距
        self._scroll_frame.configure(padx=20, pady=15)
    
    def _rebind_mousewheel(self):
        """重新绑定滚轮事件"""
        self._bind_mousewheel_recursive(self._scroll_frame)
    
    def _bind_mousewheel_recursive(self, widget):
        """递归绑定滚轮事件"""
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
    
    def _create_welcome_section(self):
        """创建欢迎区域"""
        colors = self.colors
        
        welcome_frame = CTFrame(self._scroll_frame, style_manager=self._style_manager, bg=colors["bg_primary"])
        welcome_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 主标题
        title = CTLabel(
            welcome_frame,
            style_manager=self._style_manager,
            text=self._t('home.welcome_title', '欢迎回来 👋'),
            font=self._style_manager.get_font("title"),
            bg=colors["bg_primary"],
            fg=colors["fg_primary"]
        )
        title.pack(anchor="w")
        
        # 副标题
        subtitle = CTLabel(
            welcome_frame,
            style_manager=self._style_manager,
            text=self._t('home.welcome_subtitle', '准备好今天的学习了吗？'),
            font=self._style_manager.get_font("body"),
            bg=colors["bg_primary"],
            fg=colors["fg_secondary"]
        )
        subtitle.pack(anchor="w", pady=(3, 0))
    
    def _create_quick_actions(self):
        """创建快捷操作区域"""
        colors = self.colors
        
        actions_frame = CTFrame(self._scroll_frame, style_manager=self._style_manager, bg=colors["bg_primary"])
        actions_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 配置列使其自适应
        for i in range(3):
            actions_frame.columnconfigure(i, weight=1)
        
        actions = [
            {"title": self._t('home.action.learn_title', '开始学习'), "icon": "📚", "desc": self._t('home.action.learn_desc', '学习新单词'), "command": self._start_learning, "color": colors["accent"]},
            {"title": self._t('home.action.review_title', '智能复习'), "icon": "🧠", "desc": self._t('home.action.review_desc', '基于遗忘曲线'), "command": self._start_review, "color": colors["success"]},
            {"title": self._t('home.action.search_title', '搜索单词'), "icon": "🔍", "desc": self._t('home.action.search_desc', '查找特定单词'), "command": self._search_words, "color": colors["warning"]},
        ]
        
        for i, action in enumerate(actions):
            card = self._create_action_card(actions_frame, action)
            card.grid(row=0, column=i, padx=(0 if i == 0 else 8, 0 if i == 2 else 8), sticky="nsew")
    
    def _create_action_card(self, parent: tk.Frame, action: dict) -> tk.Frame:
        """创建操作卡片"""
        colors = self.colors
        
        card = CTFrame(parent, style_manager=self._style_manager, bg=colors["bg_card"], cursor="hand2")
        card.configure(highlightbackground=colors["border"], highlightthickness=1)
        
        inner = CTFrame(card, style_manager=self._style_manager, bg=colors["bg_card"])
        inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        icon_label = CTLabel(inner, style_manager=self._style_manager, text=action["icon"], font=("Segoe UI", 20), bg=colors["bg_card"], fg=action["color"])
        icon_label.pack(anchor="w")
        
        title_label = CTLabel(inner, style_manager=self._style_manager, text=action["title"], font=self._style_manager.get_font("subheading"), bg=colors["bg_card"], fg=colors["fg_primary"])
        title_label.pack(anchor="w", pady=(6, 2))
        
        desc_label = CTLabel(inner, style_manager=self._style_manager, text=action["desc"], font=self._style_manager.get_font("caption"), bg=colors["bg_card"], fg=colors["fg_secondary"])
        desc_label.pack(anchor="w")
        
        def on_click(e):
            action["command"]()
        
        def on_enter(e):
            card.configure(highlightbackground=action["color"], highlightthickness=2)
            card.configure(bg=colors["bg_secondary"])
            inner.configure(bg=colors["bg_secondary"])
            for child in inner.winfo_children():
                try:
                    child.configure(bg=colors["bg_secondary"])
                except Exception:
                    pass
        
        def on_leave(e):
            card.configure(highlightbackground=colors["border"], highlightthickness=1)
            card.configure(bg=colors["bg_card"])
            inner.configure(bg=colors["bg_card"])
            for child in inner.winfo_children():
                try:
                    child.configure(bg=colors["bg_card"])
                except Exception:
                    pass
        
        card.bind("<Button-1>", on_click)
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        
        for child in card.winfo_children():
            child.bind("<Button-1>", on_click)
        
        for child in inner.winfo_children():
            child.bind("<Enter>", on_enter)
            child.bind("<Leave>", on_leave)
        
        return card
    
    def _create_today_stats(self):
        """创建今日统计"""
        colors = self.colors
        
        stats_card = CTFrame(self._scroll_frame, style_manager=self._style_manager, bg=colors["bg_card"])
        stats_card.configure(highlightbackground=colors["border"], highlightthickness=1)
        stats_card.pack(fill=tk.X, pady=(0, 15))
        
        header = CTFrame(stats_card, style_manager=self._style_manager, bg=colors["bg_secondary"])
        header.pack(fill=tk.X, padx=1, pady=1)
        
        title = CTLabel(header, style_manager=self._style_manager, text=self._t('home.today_overview', '📊 今日概览'), font=self._style_manager.get_font("subheading"), bg=colors["bg_secondary"], fg=colors["accent"], padx=10, pady=6)
        title.pack(anchor="w")
        
        content = CTFrame(stats_card, style_manager=self._style_manager, bg=colors["bg_card"])
        content.pack(fill=tk.X, padx=10, pady=10)
        
        for i in range(4):
            content.columnconfigure(i, weight=1)
        
        stats = self._get_today_stats()
        
        stat_items = [
            (self._t('home.stats.studied', '已学习'), f"{stats['studied']}", self._t('home.stats.unit_words', '词')),
            (self._t('home.stats.mastered', '已掌握'), f"{stats['mastered']}", self._t('home.stats.unit_words', '词')),
            (self._t('home.stats.review', '需复习'), f"{stats['review']}", self._t('home.stats.unit_words', '词')),
            (self._t('home.stats.accuracy', '准确率'), f"{stats['accuracy']}", "%"),
        ]
        
        for i, (label, value, unit) in enumerate(stat_items):
            stat_frame = CTFrame(content, style_manager=self._style_manager, bg=colors["bg_card"])
            stat_frame.grid(row=0, column=i, padx=5, pady=5)
            
            value_label = CTLabel(stat_frame, style_manager=self._style_manager, text=value, font=("Segoe UI", 18, "bold"), bg=colors["bg_card"], fg=colors["accent"])
            value_label.pack()
            
            unit_label = CTLabel(stat_frame, style_manager=self._style_manager, text=f"{label}{unit}", font=self._style_manager.get_font("caption"), bg=colors["bg_card"], fg=colors["fg_secondary"])
            unit_label.pack()
    
    def _create_recent_section(self):
        """创建最近学习区域"""
        colors = self.colors
        
        recent_card = CTFrame(self._scroll_frame, style_manager=self._style_manager, bg=colors["bg_card"])
        recent_card.configure(highlightbackground=colors["border"], highlightthickness=1)
        recent_card.pack(fill=tk.BOTH, expand=True)
        
        # 配置内部网格
        recent_card.columnconfigure(0, weight=1)
        recent_card.rowconfigure(1, weight=1)
        
        header = CTFrame(recent_card, style_manager=self._style_manager, bg=colors["bg_secondary"])
        header.grid(row=0, column=0, sticky="ew", padx=1, pady=1)
        
        title = CTLabel(header, style_manager=self._style_manager, text=self._t('home.recent_title', '📝 最近学习的单词'), font=self._style_manager.get_font("subheading"), bg=colors["bg_secondary"], fg=colors["accent"], padx=10, pady=6)
        title.pack(anchor="w")
        
        content = CTFrame(recent_card, style_manager=self._style_manager, bg=colors["bg_card"])
        content.grid(row=1, column=0, sticky="nsew", padx=10, pady=8)
        
        recent_words = self._get_recent_words()
        
        if recent_words:
            for word in recent_words[:5]:
                word_frame = CTFrame(content, style_manager=self._style_manager, bg=colors["bg_card"])
                word_frame.pack(fill=tk.X, pady=2)
                
                word_label = CTLabel(word_frame, style_manager=self._style_manager, text=word["word"], font=self._style_manager.get_font("body"), bg=colors["bg_card"], fg=colors["fg_primary"], width=10, anchor="w")
                word_label.pack(side=tk.LEFT)
                
                pos_label = CTLabel(word_frame, style_manager=self._style_manager, text=word["pos"], font=self._style_manager.get_font("caption"), bg=colors["bg_card"], fg=colors["warning"], width=5, anchor="w")
                pos_label.pack(side=tk.LEFT, padx=(0, 5))
                
                meaning_label = CTLabel(word_frame, style_manager=self._style_manager, text=word["meaning"], font=self._style_manager.get_font("body"), bg=colors["bg_card"], fg=colors["fg_secondary"], anchor="w")
                meaning_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        else:
            empty_label = CTLabel(content, style_manager=self._style_manager, text=self._t('home.recent_empty', '还没有学习记录，开始你的第一次学习吧！'), font=self._style_manager.get_font("body"), bg=colors["bg_card"], fg=colors["fg_secondary"])
            empty_label.pack(pady=15)
    
    def _get_today_stats(self) -> dict:
        """获取今日统计"""
        import datetime
        progress = self.app.progress_manager
        today = datetime.date.today().isoformat()
        sessions = [s for s in progress.study_sessions if s.date.startswith(today)]
        
        studied = sum(s.words_studied for s in sessions)
        mastered = sum(s.words_studied - s.words_reviewed for s in sessions)
        review = sum(s.words_reviewed for s in sessions)
        accuracy = sum(s.accuracy_rate for s in sessions) / len(sessions) * 100 if sessions else 0
        
        return {"studied": studied, "mastered": mastered, "review": review, "accuracy": int(accuracy)}
    
    def _get_recent_words(self) -> list:
        """获取最近学习的单词"""
        favorites = self.app.favorites_manager
        words = []
        
        for word in favorites.get_all_words()[:5]:
            words.append({
                "word": word.word,
                "pos": word.pos,
                "meaning": word.meaning[:20] + "..." if len(word.meaning) > 20 else word.meaning
            })
        
        return words
    
    def _start_learning(self):
        """开始学习"""
        vocab_file = self.app.config.get("vocab_file", "data/vocabulary.txt")
        
        if not os.path.exists(vocab_file):
            self.show_message(self._t('home.message.no_vocab_loaded', '请先在设置中加载词库'), "warning")
            return
        
        if len(self.app.vocabulary_manager) == 0:
            success, result = self.app.vocabulary_manager.load_from_file(vocab_file)
            if not success:
                self.show_message(self._t('home.message.load_vocab_failed', '加载词库失败: {error}').format(error=result), "error")
                return
        
        self.navigate_to("learning", mode="new")
    
    def _start_review(self):
        """开始复习"""
        # 自动加载词库
        if len(self.app.vocabulary_manager) == 0:
            vocab_file = self.app.config.get("vocab_file", "data/vocabulary.txt")
            if os.path.exists(vocab_file):
                success, result = self.app.vocabulary_manager.load_from_file(vocab_file)
                if not success:
                    self.show_message(f"加载词库失败: {result}", "error")
                    return
            else:
            self.show_message(self._t('home.message.no_vocab_loaded', '请先在设置中加载词库'), "warning")
        
        self.navigate_to("learning", mode="review")
    
    def _search_words(self):
        """搜索单词"""
        self.navigate_to("learning", mode="search")
    
    def on_enter(self, **kwargs):
        """进入页面"""
        super().on_enter(**kwargs)
        self.app.update_status(self._t('home.status.select_action', '选择一个操作开始学习'))
        self.app.update_progress("")
    
    def apply_theme(self):
        """应用主题"""
        super().apply_theme()
        colors = self.colors
        self._outer_frame.configure(bg=colors["bg_primary"])
        self._canvas.configure(bg=colors["bg_primary"])
        self._scroll_frame.configure(bg=colors["bg_primary"])
    
    def refresh(self):
        """刷新页面"""
        # 清除滚动框架中的所有内容
        for widget in self._scroll_frame.winfo_children():
            widget.destroy()
        
        # 重新创建组件
        self._create_welcome_section()
        self._create_quick_actions()
        self._create_today_stats()
        self._create_recent_section()
