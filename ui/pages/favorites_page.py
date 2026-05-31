"""收藏页面 - 收藏管理"""
import tkinter as tk
from tkinter import ttk, filedialog
from ui.core.base_page import BasePage
from ui.customtinker import CTFrame, CTLabel


class FavoritesPage(BasePage):
    """收藏页面 - 支持滚动和自适应布局"""
    
    page_id = "favorites"
    page_title = "收藏"
    page_icon = "❤️"
    
    def create_widgets(self):
        """创建组件"""
        colors = self.colors
        
        # 配置页面网格
        self._container.columnconfigure(0, weight=1)
        self._container.rowconfigure(0, weight=1)
        
        self._create_header()
        self._create_favorites_list()
        self._create_actions()
        
        # 绑定滚轮事件
        self.after(100, self._rebind_mousewheel)
    
    def _rebind_mousewheel(self):
        """重新绑定滚轮事件"""
        self._bind_mousewheel_recursive(self._container)
    
    def _bind_mousewheel_recursive(self, widget):
        """递归绑定滚轮事件"""
        widget.bind("<MouseWheel>", self._on_mousewheel)
        widget.bind("<Button-4>", self._on_mousewheel)
        widget.bind("<Button-5>", self._on_mousewheel)
        
        for child in widget.winfo_children():
            self._bind_mousewheel_recursive(child)
    
    def _on_mousewheel(self, event):
        """鼠标滚轮滚动"""
        if event.num == 4:
            self._tree.yview_scroll(-1, "units")
        elif event.num == 5:
            self._tree.yview_scroll(1, "units")
        else:
            self._tree.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def setup_layout(self):
        """设置布局"""
        pass
    
    def _create_header(self):
        """创建标题区域"""
        colors = self.colors
        
        header = CTFrame(self._container, style_manager=self._style_manager, bg=colors["bg_primary"])
        header.pack(fill=tk.X, pady=(0, 12))
        header.columnconfigure(1, weight=1)
        
        # 左侧标题
        left = CTFrame(header, style_manager=self._style_manager, bg=colors["bg_primary"])
        left.grid(row=0, column=0, sticky="w")
        
        title = CTLabel(
            left,
            style_manager=self._style_manager,
            text=self._t('favorites.title', '❤️ 我的收藏'),
            font=self._style_manager.get_font("title"),
            bg=colors["bg_primary"],
            fg=colors["fg_primary"]
        )
        title.pack(anchor="w")
        
        # 数量统计
        self._count_label = CTLabel(
            left,
            style_manager=self._style_manager,
            text=self._t('favorites.count', '共 {count} 个单词').format(count=len(self.app.favorites_manager)),
            font=self._style_manager.get_font("caption"),
            bg=colors["bg_primary"],
            fg=colors["fg_secondary"]
        )
        self._count_label.pack(anchor="w", pady=(3, 0))
        
        # 右侧搜索
        right = CTFrame(header, style_manager=self._style_manager, bg=colors["bg_primary"])
        right.grid(row=0, column=1, sticky="e")
        
        self._search_var = tk.StringVar()
        self._search_entry = ttk.Entry(
            right,
            textvariable=self._search_var,
            width=20,
            font=self._style_manager.get_font("body")
        )
        self._search_entry.pack(side=tk.LEFT, padx=(0, 8))
        self._search_entry.bind("<KeyRelease>", self._on_search)
        
        ttk.Button(
            right,
            text="🔍",
            command=self._on_search,
            style="Secondary.TButton"
        ).pack(side=tk.LEFT)
    
    def _create_favorites_list(self):
        """创建收藏列表"""
        colors = self.colors
        
        # 列表卡片
        list_card = CTFrame(self._container, style_manager=self._style_manager, bg=colors["bg_card"])
        list_card.configure(highlightbackground=colors["border"], highlightthickness=1)
        list_card.pack(fill=tk.BOTH, expand=True, pady=(0, 12))
        
        # 配置网格
        list_card.columnconfigure(0, weight=1)
        list_card.rowconfigure(0, weight=1)
        
        # Treeview
        columns = ("word", "pos", "meaning")
        self._tree = ttk.Treeview(
            list_card,
            columns=columns,
            show="headings",
            selectmode="browse"
        )
        
        self._tree.heading("word", text=self._t('favorites.table.word', '单词'))
        self._tree.heading("pos", text=self._t('favorites.table.pos', '词性'))
        self._tree.heading("meaning", text=self._t('favorites.table.meaning', '中文意思'))
        
        self._tree.column("word", width=120, minwidth=80)
        self._tree.column("pos", width=60, minwidth=40)
        self._tree.column("meaning", width=300, minwidth=150)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(
            list_card,
            orient=tk.VERTICAL,
            command=self._tree.yview
        )
        self._tree.configure(yscrollcommand=scrollbar.set)
        
        self._tree.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=1)
        
        # 双击学习
        self._tree.bind("<Double-Button-1>", self._learn_selected)
        
        # 右键菜单
        self._context_menu = tk.Menu(self._tree, tearoff=0)
        self._context_menu.add_command(label=self._t('favorites.context.learn', '📚 学习'), command=self._learn_selected)
        self._context_menu.add_command(label=self._t('favorites.context.delete', '🗑️ 删除'), command=self._delete_selected)
        self._tree.bind("<Button-3>", self._show_context_menu)
        
        # 加载数据
        self._load_favorites()
    
    def _create_actions(self):
        """创建操作按钮"""
        colors = self.colors
        
        btn_frame = CTFrame(self._container, style_manager=self._style_manager, bg=colors["bg_primary"])
        btn_frame.pack(fill=tk.X)
        btn_frame.columnconfigure(1, weight=1)
        
        # 左侧
        left = CTFrame(btn_frame, style_manager=self._style_manager, bg=colors["bg_primary"])
        left.grid(row=0, column=0, sticky="w")
        
        ttk.Button(
            left,
            text=self._t('favorites.action.learn_selected', '📚 学习选中'),
            command=self._learn_selected,
            style="Primary.TButton"
        ).pack(side=tk.LEFT, padx=3)
        
        ttk.Button(
            left,
            text=self._t('favorites.action.learn_all', '📚 学习全部'),
            command=self._learn_all,
            style="Secondary.TButton"
        ).pack(side=tk.LEFT, padx=3)
        
        # 右侧
        right = CTFrame(btn_frame, style_manager=self._style_manager, bg=colors["bg_primary"])
        right.grid(row=0, column=2, sticky="e")
        
        ttk.Button(
            right,
            text=self._t('favorites.action.clear', '🧹 清空'),
            command=self._clear_all,
            style="Secondary.TButton"
        ).pack(side=tk.RIGHT, padx=3)
        
        ttk.Button(
            right,
            text=self._t('favorites.action.delete', '🗑️ 删除'),
            command=self._delete_selected,
            style="Secondary.TButton"
        ).pack(side=tk.RIGHT, padx=3)
        
        ttk.Button(
            right,
            text=self._t('favorites.action.export', '💾 导出'),
            command=self._export_favorites,
            style="Secondary.TButton"
        ).pack(side=tk.RIGHT, padx=3)
    
    def _load_favorites(self):
        """加载收藏数据"""
        for item in self._tree.get_children():
            self._tree.delete(item)
        
        query = self._search_var.get().lower()
        
        for word in self.app.favorites_manager.get_all_words():
            if query and query not in word.word.lower() and query not in word.meaning.lower():
                continue
            
            self._tree.insert(
                "",
                tk.END,
                values=(word.word, word.pos, word.meaning),
                iid=word.word
            )
        
        count = len(self._tree.get_children())
        self._count_label.configure(text=self._t('favorites.count', '共 {count} 个单词').format(count=count))
    
    def _on_search(self, event=None):
        """搜索"""
        self._load_favorites()
    
    def _show_context_menu(self, event):
        """显示右键菜单"""
        item = self._tree.identify_row(event.y)
        if item:
            self._tree.selection_set(item)
            self._context_menu.tk_popup(event.x_root, event.y_root)
    
    def _learn_selected(self, event=None):
        """学习选中的单词"""
        selected = self._tree.selection()
        if not selected:
            self.show_message(self._t('favorites.message.select_word', '请先选择一个单词'), "warning")
            return
        
        words = []
        for item in selected:
            word_text = item
            word = self.app.favorites_manager.get_word(word_text)
            if word:
                words.append(word)
        
        if not words:
            return
        
        self.app.today_words = words
        self.app.current_word_index = 0
        self.app.unknown_words = []
        self.app.stage = "recite"
        self.app.test_mode = False
        
        self.navigate_to("learning", mode="resume")
    
    def _learn_all(self):
        """学习全部收藏"""
        if len(self.app.favorites_manager) == 0:
            self.show_message(self._t('favorites.message.empty_list', '收藏列表为空'), "warning")
            return
        
        words = self.app.favorites_manager.get_all_words()
        
        if self.app.config.get_bool("shuffle_words", True):
            import random
            random.shuffle(words)
        
        self.app.today_words = words
        self.app.current_word_index = 0
        self.app.unknown_words = []
        self.app.stage = "recite"
        self.app.test_mode = False
        
        self.navigate_to("learning", mode="resume")
    
    def _delete_selected(self):
        """删除选中"""
        selected = self._tree.selection()
        if not selected:
            self.show_message(self._t('favorites.message.select_delete', '请先选择要删除的单词'), "warning")
            return
        
        for word_text in selected:
            self.app.favorites_manager.remove_word(word_text)
        # remove_word 已会标记为脏（DirtyTracker），不应直接赋值只读属性
        # 直接保存一次以持久化修改
        self.app.favorites_manager.save_favorites()
        
        self._load_favorites()
        self.app.update_favorites_count()
        
        self.show_message(self._t('favorites.message.deleted_count', '已删除 {count} 个单词').format(count=len(selected)), "success")
    
    def _export_favorites(self):
        """导出收藏"""
        if len(self.app.favorites_manager) == 0:
            self.show_message(self._t('favorites.message.empty_list', '收藏列表为空'), "warning")
            return
        
        file_path = filedialog.asksaveasfilename(
            title=self._t('favorites.export_title', '导出收藏词库'),
            defaultextension=".txt",
            initialfile="my_favorites.txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            parent=self.app.root
        )
        
        if file_path:
            if self.app.favorites_manager.export_to_file(file_path):
                self.show_message(self._t('favorites.message.export_success', '已导出到: {path}').format(path=file_path), "success")
            else:
                self.show_message(self._t('favorites.message.export_failed', '导出失败'), "error")
    
    def _clear_all(self):
        """清空收藏"""
        if len(self.app.favorites_manager) == 0:
            self.show_message(self._t('favorites.message.empty_already', '收藏列表已经是空的'), "info")
            return
        
        from tkinter import messagebox
        if not messagebox.askyesno(
            self._t('confirm.title', '确认'),
            self._t('favorites.confirm.clear_confirmation', '确定要清空所有收藏吗？此操作不可恢复！'),
            parent=self.app.root
        ):
            return
        
        if not messagebox.askyesno(
            self._t('confirm.title', '确认'),
            self._t('favorites.confirm.clear_confirmation_final', '您真的确定要清空所有收藏吗？'),
            parent=self.app.root
        ):
            return
        
        self.app.favorites_manager.clear_all()
        self.app.favorites_manager.save_favorites()
        
        self._load_favorites()
        self.app.update_favorites_count()
        
        self.show_message(self._t('favorites.message.cleared', '收藏已清空'), "success")
    
    def on_enter(self, **kwargs):
        """进入页面"""
        super().on_enter(**kwargs)
        self._load_favorites()
        self.app.update_status(self._t('favorites.status.manage', '管理您的收藏单词'))
        self.app.update_progress("")
    
    def refresh(self):
        """刷新"""
        self._load_favorites()
    
    def apply_theme(self):
        """应用主题"""
        super().apply_theme()
        self._load_favorites()
