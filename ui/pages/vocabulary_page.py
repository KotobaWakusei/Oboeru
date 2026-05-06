"""词汇表页面 - 显示全部/已复习/未复习/未学习单词"""
import tkinter as tk
from tkinter import ttk, messagebox
from ui.core.base_page import BasePage
from ui.customtinker import CTFrame, CTLabel, CTEntry, CTCombobox


class VocabularyPage(BasePage):
    """词汇表页面"""
    page_id = "vocabulary"
    page_title = "词汇表"
    page_icon = "📖"

    def create_widgets(self):
        colors = self.colors

        header = CTFrame(self._container, style_manager=self._style_manager, bg=colors["bg_primary"]) 
        header.pack(fill=tk.X, pady=(0, 8))

        title = CTLabel(header, style_manager=self._style_manager, text=self._t('vocab.title', '词汇表'), font=self._style_manager.get_font('heading'), bg=colors['bg_primary'], fg=colors['accent'])
        title.pack(side=tk.LEFT)

        # 控件区：搜索 + 过滤
        ctrl = CTFrame(self._container, style_manager=self._style_manager, bg=colors['bg_primary'])
        ctrl.pack(fill=tk.X, pady=(0, 8))

        self._search_var = tk.StringVar()
        self._search_entry = CTEntry(ctrl, style_manager=self._style_manager, textvariable=self._search_var, width=30)
        self._search_entry.pack(side=tk.LEFT, padx=(0, 8))

        # 过滤器：使用友好名称展示，内部通过映射获取 key
        self._filter_var = tk.StringVar(value=self._t('vocab.filter.all', '全部'))
        options = [
            ('all', self._t('vocab.filter.all', '全部')),
            ('reviewed', self._t('vocab.filter.reviewed', '已复习')),
            ('unreviewed', self._t('vocab.filter.unreviewed', '未复习')),
            ('unlearned', self._t('vocab.filter.unlearned', '未学习')),
        ]

        # Combobox 绑定变量以便读取当前选择
        self._filter_combo = CTCombobox(ctrl, style_manager=self._style_manager, textvariable=self._filter_var, values=[v for _, v in options], width=18)
        self._filter_combo.pack(side=tk.LEFT, padx=(0, 8))
        self._filter_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh())

        ttk.Button(ctrl, text=self._t('vocab.action.search', '搜索'), command=self.refresh).pack(side=tk.LEFT, padx=4)
        ttk.Button(ctrl, text=self._t('vocab.action.refresh', '刷新'), command=self.refresh).pack(side=tk.LEFT, padx=4)

        # 列表区域
        frame = CTFrame(self._container, style_manager=self._style_manager, bg=colors['bg_primary'])
        frame.pack(fill=tk.BOTH, expand=True)

        columns = ("word", "pos", "meaning", "status", "last_study")
        self._tree = ttk.Treeview(frame, columns=columns, show='headings')
        self._tree.heading('word', text=self._t('vocab.table.word', '单词'))
        self._tree.heading('pos', text=self._t('vocab.table.pos', '词性'))
        self._tree.heading('meaning', text=self._t('vocab.table.meaning', '中文意思'))
        self._tree.heading('status', text=self._t('vocab.table.status', '状态'))
        self._tree.heading('last_study', text=self._t('vocab.table.last_study', '最后学习'))

        self._tree.column('word', width=120)
        self._tree.column('pos', width=80)
        self._tree.column('meaning', width=360)
        self._tree.column('status', width=120)
        self._tree.column('last_study', width=140)

        vsb = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._tree.pack(fill=tk.BOTH, expand=True)

        # 事件
        self._tree.bind('<Double-1>', self._on_row_double)

    def setup_layout(self):
        pass

    def bind_events(self):
        self._search_entry.bind('<Return>', lambda e: self.refresh())

    def on_enter(self, **kwargs):
        super().on_enter(**kwargs)
        # 确保词库已加载
        if len(self.app.vocabulary_manager) == 0:
            vocab_file = self.app.config.get('vocab_file')
            try:
                if vocab_file and __import__('os').path.exists(vocab_file):
                    self.app.vocabulary_manager.load_from_file(vocab_file)
            except Exception:
                pass
        self.refresh()

    def refresh(self):
        """刷新表格数据"""
        # 读取当前筛选（按显示文本映射为内部 key）
        sel = self._filter_var.get()
        options = [
            ('all', self._t('vocab.filter.all', '全部')),
            ('reviewed', self._t('vocab.filter.reviewed', '已复习')),
            ('unreviewed', self._t('vocab.filter.unreviewed', '未复习')),
            ('unlearned', self._t('vocab.filter.unlearned', '未学习')),
        ]
        display_to_key = {display: key for key, display in options}
        key = display_to_key.get(sel, 'all')

        query = (self._search_var.get() or '').strip().lower()

        words = self.app.vocabulary_manager.get_words()
        # 清空
        for item in self._tree.get_children():
            self._tree.delete(item)

        for w in sorted(words, key=lambda x: x.word.lower()):
            prog = self.app.progress_manager.word_progress.get(w.word)
            status_key = 'unlearned'
            last_study = ''
            if prog:
                last_study = getattr(prog, 'last_study_date', '')[:19]
                if prog.is_mastered:
                    status_key = 'mastered'
                elif getattr(prog, 'review_count', 0) > 0:
                    status_key = 'reviewed'
                elif getattr(prog, 'total_study_count', 0) > 0:
                    status_key = 'in_progress'
            else:
                status_key = 'unlearned'

            # 过滤
            if key == 'reviewed' and status_key not in ('reviewed', 'mastered'):
                continue
            if key == 'unreviewed' and status_key != 'in_progress':
                continue
            if key == 'unlearned' and status_key != 'unlearned':
                continue

            # 搜索过滤
            if query:
                if query not in w.word.lower() and query not in w.meaning.lower():
                    continue

            status_text = self._t(f'vocab.status.{status_key}', {
                'mastered': self._t('vocab.status.mastered', '已掌握'),
                'reviewed': self._t('vocab.status.reviewed', '已复习'),
                'in_progress': self._t('vocab.status.in_progress', '学习中'),
                'unlearned': self._t('vocab.status.unlearned', '未学习')
            }[status_key])

            self._tree.insert('', tk.END, values=(w.word, w.pos, w.meaning, status_text, last_study))

    def _on_row_double(self, event):
        item = self._tree.selection()
        if not item:
            return
        vals = self._tree.item(item[0])['values']
        word = vals[0]
        prog = self.app.progress_manager.word_progress.get(word)
        detail = f"{vals[0]} [{vals[1]}]\n{vals[2]}\n状态: {vals[3]}"
        if prog:
            detail += f"\n掌握等级: {getattr(prog, 'mastery_level', 0)}/5"
            detail += f"\n学习次数: {getattr(prog, 'total_study_count', 0)}"
            detail += f"\n最后学习: {getattr(prog, 'last_study_date', '')}"
            detail += f"\n下次复习: {getattr(prog, 'next_review_date', '')}"

        messagebox.showinfo(self._t('vocab.dialog.title', '单词详情'), detail, parent=self.app.root)
