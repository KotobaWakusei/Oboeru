"""学习页面子组件（全翻译支持）"""
import tkinter as tk
from tkinter import ttk

from ui.customtinker import CTFrame, CTLabel


class WordDisplayCard(CTFrame):
    """单词展示卡片 — word + POS + meaning + AI 例句区"""

    def __init__(self, parent, style_manager, app):
        colors = style_manager.colors
        super().__init__(parent, style_manager=style_manager, bg=colors["bg_card"])
        self._app = app
        self._t = app.language_manager.translate
        self._style_manager = style_manager
        self.configure(highlightbackground=colors["border"], highlightthickness=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        container = CTFrame(self, style_manager=style_manager, bg=colors["bg_card"])
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        self._word_label = CTLabel(
            container, style_manager=style_manager,
            text="", font=("Segoe UI", 28, "bold"),
            bg=colors["bg_card"], fg=colors["accent"]
        )
        self._word_label.grid(row=0, column=0, pady=(20, 5))

        self._pos_label = CTLabel(
            container, style_manager=style_manager,
            text="", font=style_manager.get_font("subheading"),
            bg=colors["bg_card"], fg=colors["warning"]
        )
        self._pos_label.grid(row=1, column=0, pady=5)

        sep = CTFrame(container, style_manager=style_manager, bg=colors["border"], height=1)
        sep.grid(row=2, column=0, sticky="ew", padx=30, pady=10)

        self._meaning_label = CTLabel(
            container, style_manager=style_manager,
            text="", font=("Segoe UI", 16, "bold"),
            bg=colors["bg_card"], fg=colors["fg_primary"],
            wraplength=600, justify=tk.CENTER
        )
        self._meaning_label.grid(row=3, column=0, pady=10, padx=20)

        self._sentence_frame = CTFrame(container, style_manager=style_manager, bg=colors["bg_card"])
        self._sentence_frame.grid(row=4, column=0, pady=(5, 10), padx=20, sticky="ew")

        self._sentence_label = CTLabel(
            self._sentence_frame, style_manager=style_manager,
            text="", font=("Segoe UI", 11),
            bg=colors["bg_card"], fg=colors["success"],
            wraplength=550, justify=tk.LEFT
        )
        self._sentence_label.pack(anchor="w")

        self._sentence_loading = CTLabel(
            self._sentence_frame, style_manager=style_manager,
            text="", font=("Segoe UI", 10),
            bg=colors["bg_card"], fg=colors["fg_secondary"]
        )
        self._sentence_loading.pack(anchor="w")

    def show_word(self, word, meaning, pos=""):
        self._word_label.configure(text=word)
        self._pos_label.configure(text=pos)
        self._meaning_label.configure(text=meaning)
        self._meaning_label.grid()
        self._sentence_label.configure(text="")
        self._sentence_loading.configure(text="")
        self._animate_word_entry()

    def show_placeholder(self, text):
        self._word_label.configure(text=text)
        self._pos_label.configure(text="")
        self._meaning_label.configure(text="")
        self._sentence_label.configure(text="")
        self._sentence_loading.configure(text="")

    def hide_meaning(self):
        self._meaning_label.configure(text="")
        self._meaning_label.grid_remove()

    def set_sentence(self, text):
        self._sentence_label.configure(text=text)
        self._sentence_loading.configure(text="")

    def set_sentence_loading(self, text):
        self._sentence_loading.configure(text=text)

    def _animate_word_entry(self):
        colors = self._style_manager.colors
        start = colors.get("border", "#555")
        end = colors.get("accent", "#fff")
        steps = 12
        tag = object()
        self._entry_tag = tag

        def _lerp(c1, c2, t):
            def _h(hx):
                hx = hx.lstrip("#")
                return tuple(int(hx[i:i+2], 16) for i in (0, 2, 4))
            def _f(r, g, b):
                return f"#{int(r):02x}{int(g):02x}{int(b):02x}"
            r1, g1, b1 = _h(c1)
            r2, g2, b2 = _h(c2)
            return _f(r1 + (r2 - r1) * t, g1 + (g2 - g1) * t, b1 + (b2 - b1) * t)

        def tick(i):
            if getattr(self, '_entry_tag', None) is not tag:
                return
            if i < steps:
                t = (i + 1) / steps
                try:
                    self._word_label.configure(fg=_lerp(start, end, t))
                    self._pos_label.configure(fg=_lerp(start, colors.get("warning", start), t))
                except Exception:
                    pass
                self.after(20, tick, i + 1)
            else:
                try:
                    self._word_label.configure(fg=end)
                    self._pos_label.configure(fg=colors.get("warning", end))
                except Exception:
                    pass

        tick(0)

    def set_fonts(self, word_size, meaning_size, wrap_width):
        self._word_label.configure(font=("Segoe UI", word_size, "bold"))
        self._meaning_label.configure(font=("Segoe UI", meaning_size, "bold"), wraplength=wrap_width)
        self._sentence_label.configure(wraplength=wrap_width - 40)

    def apply_theme(self):
        colors = self._style_manager.colors
        self.configure(bg=colors["bg_card"], highlightbackground=colors["border"])
        for child in self.winfo_children():
            if isinstance(child, (CTFrame, tk.Frame)):
                child.configure(bg=colors["bg_card"])
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, (CTLabel, tk.Label)):
                        try:
                            grandchild.configure(bg=colors["bg_card"])
                        except Exception:
                            pass
        self._sentence_frame.configure(bg=colors["bg_card"])
        self._sentence_label.configure(bg=colors["bg_card"], fg=colors["success"])
        self._sentence_loading.configure(bg=colors["bg_card"], fg=colors["fg_secondary"])


class ReviewPanel(CTFrame):
    """最近背诵单词回顾面板"""

    def __init__(self, parent, style_manager, app):
        colors = style_manager.colors
        super().__init__(parent, style_manager=style_manager, bg=colors["bg_secondary"])
        self._app = app
        self._t = app.language_manager.translate
        self._style_manager = style_manager
        self._colors = colors
        self.configure(highlightbackground=colors["border"], highlightthickness=1)
        self._word_labels = []

        header = CTFrame(self, style_manager=style_manager, bg=colors["bg_card"])
        header.pack(fill=tk.X, padx=1, pady=1)
        CTLabel(
            header, style_manager=style_manager,
            text=self._t("learning.recent_title", "📝 最近背诵"), font=style_manager.get_font("caption"),
            bg=colors["bg_card"], fg=colors["accent"], padx=10, pady=5
        ).pack(side=tk.LEFT)

        self._words_container = CTFrame(self, style_manager=style_manager, bg=colors["bg_secondary"])
        self._words_container.pack(fill=tk.X, padx=10, pady=8)

    def update(self, today_words, current_index, review_count):
        for child in self._words_container.winfo_children():
            try:
                child.destroy()
            except Exception:
                pass
        self._word_labels.clear()

        if review_count <= 0 or current_index == 0 or not today_words:
            self.pack_forget()
            self.grid_forget()
            return

        start_idx = max(0, current_index - review_count)
        review_words = today_words[start_idx:current_index]
        if not review_words:
            self.pack_forget()
            self.grid_forget()
            return

        self.grid(row=1, column=0, sticky="ew", pady=(10, 0))

        for word in review_words[-review_count:]:
            frame = CTFrame(self._words_container, style_manager=self._style_manager, bg=self._colors["bg_secondary"])
            frame.pack(side=tk.LEFT, padx=8)

            lbl = CTLabel(
                frame, style_manager=self._style_manager,
                text=word.word, font=self._style_manager.get_font("body"),
                bg=self._colors["bg_secondary"], fg=self._colors["fg_primary"],
                cursor="hand2"
            )
            lbl.pack()
            lbl._word_data = word

            def _smooth_fg(label, target_color, steps=6):
                try:
                    current = label.cget("fg")
                except Exception:
                    return
                def _lerp(c1, c2, t):
                    def _h(hx):
                        hx = hx.lstrip("#")
                        return tuple(int(hx[i:i+2], 16) for i in (0, 2, 4))
                    def _f(r, g, b):
                        return f"#{int(r):02x}{int(g):02x}{int(b):02x}"
                    r1, g1, b1 = _h(c1)
                    r2, g2, b2 = _h(c2)
                    return _f(r1 + (r2 - r1) * t, g1 + (g2 - g1) * t, b1 + (b2 - b1) * t)
                tag = object()
                label._hover_tag = tag
                def tick(i):
                    if getattr(label, '_hover_tag', None) is not tag:
                        return
                    if i < steps:
                        t = (i + 1) / steps
                        try:
                            label.configure(fg=_lerp(current, target_color, t))
                        except Exception:
                            pass
                        label.after(20, tick, i + 1)
                    else:
                        try:
                            label.configure(fg=target_color)
                        except Exception:
                            pass
                tick(0)

            def on_enter(e, label=lbl, w=word):
                label.configure(text=f"{w.word}: {w.meaning}")
                _smooth_fg(label, self._colors["success"])

            def on_leave(e, label=lbl, w=word):
                label.configure(text=w.word)
                _smooth_fg(label, self._colors["fg_primary"])

            def on_click(e, label=lbl, w=word):
                if ":" in label.cget("text"):
                    label.configure(text=w.word)
                    _smooth_fg(label, self._colors["fg_primary"])
                else:
                    label.configure(text=f"{w.word}: {w.meaning}")
                    _smooth_fg(label, self._colors["success"])

            lbl.bind("<Enter>", on_enter)
            lbl.bind("<Leave>", on_leave)
            lbl.bind("<Button-1>", on_click)
            self._word_labels.append(lbl)

    def hide(self):
        self.grid_forget()

    def apply_theme(self):
        colors = self._style_manager.colors
        self._colors = colors
        self.configure(bg=colors["bg_secondary"], highlightbackground=colors["border"])


class OptionsPanel(CTFrame):
    """测试阶段选项面板 (4 按钮，带动画反馈)"""

    def __init__(self, parent, style_manager, on_answer, app=None):
        colors = style_manager.colors
        super().__init__(parent, style_manager=style_manager, bg=colors["bg_primary"])
        self._style_manager = style_manager
        self._on_answer = on_answer
        self._app = app
        self._colors = colors

        for i in range(2):
            self.columnconfigure(i, weight=1)

        self._buttons = []
        for i in range(4):
            row = i // 2
            col = i % 2
            btn = tk.Button(
                self,
                text="", font=("Segoe UI", 12),
                bg=colors["bg_secondary"], fg=colors["fg_primary"],
                activebackground=colors["accent"],
                activeforeground=colors["fg_primary"],
                relief=tk.FLAT, cursor="hand2",
                state=tk.DISABLED,
                command=lambda idx=i: on_answer(idx)
            )
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew", ipadx=10, ipady=8)
            self._buttons.append(btn)

    def show(self, options):
        self.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        for i, btn in enumerate(self._buttons):
            if i < len(options):
                btn.configure(text=options[i], state=tk.NORMAL, bg=self._colors["bg_secondary"])
            else:
                btn.configure(text="", state=tk.DISABLED)

    def hide(self):
        self.grid_forget()
        for btn in self._buttons:
            btn.configure(state=tk.DISABLED, text="")

    def mark_correct(self, index):
        animator = getattr(self._app, '_animator', None) if self._app else None
        btn = self._buttons[index]
        if animator:
            animator.flash_bg(btn, self._colors["success"], self._colors["bg_secondary"])
        else:
            btn.configure(bg=self._colors["success"])

    def mark_wrong(self, index, correct_text):
        animator = getattr(self._app, '_animator', None) if self._app else None
        btn = self._buttons[index]
        if animator:
            animator.flash_bg(btn, self._colors["error"], self._colors["bg_secondary"])
        else:
            btn.configure(bg=self._colors["error"])
        for i, btn in enumerate(self._buttons):
            if btn.cget("text") == correct_text:
                if animator:
                    animator.flash_bg(btn, self._colors["success"], self._colors["bg_secondary"])
                else:
                    btn.configure(bg=self._colors["success"])

    def disable_all(self):
        for btn in self._buttons:
            btn.configure(state=tk.DISABLED)

    def set_fonts(self, option_size, is_single_column):
        for btn in self._buttons:
            btn.configure(font=("Segoe UI", option_size))
        if is_single_column:
            for i, btn in enumerate(self._buttons):
                btn.grid(row=i, column=0, padx=5, pady=3, sticky="ew")
            self.columnconfigure(1, weight=0)
            self.columnconfigure(0, weight=1)
        else:
            for i, btn in enumerate(self._buttons):
                r, c = i // 2, i % 2
                btn.grid(row=r, column=c, padx=5, pady=5, sticky="ew", ipadx=10, ipady=8)
            self.columnconfigure(0, weight=1)
            self.columnconfigure(1, weight=1)

    def apply_theme(self):
        colors = self._style_manager.colors
        self._colors = colors
        self.configure(bg=colors["bg_primary"])
        for btn in self._buttons:
            if btn.cget("state") == tk.NORMAL:
                btn.configure(bg=colors["bg_secondary"])


class LearningControls(CTFrame):
    """学习页面控制按钮组（全翻译支持）"""

    def __init__(self, parent, style_manager, app):
        colors = style_manager.colors
        super().__init__(parent, style_manager=style_manager, bg=colors["bg_primary"])
        self._app = app
        self._t = app.language_manager.translate
        self._style_manager = style_manager
        self.columnconfigure(1, weight=1)

        left = CTFrame(self, style_manager=style_manager, bg=colors["bg_primary"])
        left.grid(row=0, column=0, sticky="w")

        self._prev_btn = ttk.Button(
            left, text=self._t("learning.action.previous", "◀ 上一个"),
            style="Nav.TButton", state=tk.DISABLED)
        self._prev_btn.pack(side=tk.LEFT, padx=2)

        self._next_btn = ttk.Button(
            left, text=self._t("learning.action.next", "下一个 ▶"),
            style="Nav.TButton", state=tk.DISABLED)
        self._next_btn.pack(side=tk.LEFT, padx=2)

        center = CTFrame(self, style_manager=style_manager, bg=colors["bg_primary"])
        center.grid(row=0, column=1)

        self._fav_btn = ttk.Button(
            center, text=self._t("learning.action.favorite", "☆ 收藏"),
            style="Secondary.TButton", state=tk.DISABLED)
        self._fav_btn.pack(side=tk.LEFT, padx=2)

        self._pronounce_btn = ttk.Button(
            center, text=self._t("learning.action.pronounce", "🔊 发音"),
            style="Secondary.TButton", state=tk.DISABLED)
        self._pronounce_btn.pack(side=tk.LEFT, padx=2)

        self._ai_btn = ttk.Button(
            center, text=self._t("learning.action.ai_sentence", "🤖 例句"),
            style="Secondary.TButton", state=tk.DISABLED)
        self._ai_btn.pack(side=tk.LEFT, padx=2)

        right = CTFrame(self, style_manager=style_manager, bg=colors["bg_primary"])
        right.grid(row=0, column=2, sticky="e")
        self._right_frame = right

        self._start_btn = ttk.Button(
            right, text=self._t("learning.action.start", "▶ 开始学习"),
            style="Primary.TButton")
        self._start_btn.pack(side=tk.LEFT, padx=2)

        self._review_btn = ttk.Button(
            right, text=self._t("learning.action.review", "🧠 复习"),
            style="Primary.TButton")
        self._review_btn.pack(side=tk.LEFT, padx=2)

        self._exit_btn = ttk.Button(
            right, text=self._t("learning.action.exit", "⏹ 退出学习"),
            style="Secondary.TButton", state=tk.DISABLED)
        self._exit_btn.pack(side=tk.LEFT, padx=2)
        self._exit_btn_visible = False
        self._start_buttons_hidden = False

    def set_prev_command(self, cmd):
        self._prev_btn.configure(command=cmd)

    def set_next_command(self, cmd):
        self._next_btn.configure(command=cmd)

    def set_fav_command(self, cmd):
        self._fav_btn.configure(command=cmd)

    def set_pronounce_command(self, cmd):
        self._pronounce_btn.configure(command=cmd)

    def set_ai_command(self, cmd):
        self._ai_btn.configure(command=cmd)

    def set_start_command(self, cmd):
        self._start_btn.configure(command=cmd)

    def set_review_command(self, cmd):
        self._review_btn.configure(command=cmd)

    def set_exit_command(self, cmd):
        self._exit_btn.configure(command=cmd)

    def enable_controls(self, ai_available=False):
        self._prev_btn.configure(state=tk.NORMAL)
        self._next_btn.configure(state=tk.NORMAL)
        self._fav_btn.configure(state=tk.NORMAL)
        self._pronounce_btn.configure(state=tk.NORMAL)
        self._ai_btn.configure(state=tk.NORMAL if ai_available else tk.DISABLED)
        if not self._exit_btn_visible:
            self._exit_btn.configure(state=tk.NORMAL)
            self._exit_btn_visible = True

    def disable_controls(self):
        for btn in (self._prev_btn, self._next_btn, self._fav_btn, self._pronounce_btn, self._ai_btn):
            btn.configure(state=tk.DISABLED)
        if self._exit_btn_visible:
            self._exit_btn.configure(state=tk.DISABLED)
            self._exit_btn_visible = False

    def update_fav_button(self, is_fav):
        t = self._t
        self._fav_btn.configure(text=t("learning.action.favored", "★ 已收藏") if is_fav else t("learning.action.unfavored", "☆ 收藏"))

    def hide_start_review_buttons(self):
        try:
            self._start_btn.pack_forget()
        except Exception:
            pass
        try:
            self._review_btn.pack_forget()
        except Exception:
            pass
        self._start_buttons_hidden = True

    def hide_nav_buttons(self):
        for btn in (self._prev_btn, self._next_btn):
            btn.pack_forget()

    def show_nav_buttons(self):
        self._prev_btn.pack(side=tk.LEFT, padx=2)
        self._next_btn.pack(side=tk.LEFT, padx=2)

    def show_start_review_buttons(self):
        if self._start_buttons_hidden:
            try:
                self._start_btn.pack(side=tk.LEFT, padx=2)
            except Exception:
                pass
            try:
                self._review_btn.pack(side=tk.LEFT, padx=2)
            except Exception:
                pass
            self._start_buttons_hidden = False

    def apply_theme(self):
        colors = self._style_manager.colors
        self.configure(bg=colors["bg_primary"])


class SearchResultsDialog:
    """搜索单词结果对话框"""

    def __init__(self, parent, app, query, results):
        self._app = app
        self._t = app.language_manager.translate
        self._style_manager = app.style_manager
        colors = self._style_manager.colors

        dialog = tk.Toplevel(app.root)
        dialog.title(self._t("learning.search.title", "搜索结果: {query}").format(query=query))
        dialog.geometry("500x300")
        dialog.transient(app.root)
        dialog.grab_set()
        dialog.configure(bg=colors["bg_primary"])
        self._dialog = dialog

        frame = CTFrame(dialog, style_manager=self._style_manager, bg=colors["bg_primary"], padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        columns = ("word", "pos", "meaning")
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        tree.heading("word", text=self._t("learning.table.word", "单词"))
        tree.heading("pos", text=self._t("learning.table.pos", "词性"))
        tree.heading("meaning", text=self._t("learning.table.meaning", "中文意思"))
        tree.column("word", width=80)
        tree.column("pos", width=50)
        tree.column("meaning", width=250)

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._tree = tree

        for w in results:
            tree.insert("", tk.END, values=(w.word, w.pos, w.meaning))

        btn_frame = CTFrame(dialog, style_manager=self._style_manager, bg=colors["bg_primary"])
        btn_frame.pack(fill=tk.X, padx=10, pady=8)

        ttk.Button(btn_frame, text=self._t("learning.search.learn_btn", "学习选中"), command=self._learn_selected, style="Primary.TButton").pack(side=tk.RIGHT, padx=3)
        ttk.Button(btn_frame, text=self._t("learning.search.close_btn", "关闭"), command=dialog.destroy, style="Secondary.TButton").pack(side=tk.RIGHT, padx=3)

    def _learn_selected(self):
        selected = self._tree.selection()
        if not selected:
            return
        item = self._tree.item(selected[0])
        word_text = item["values"][0]
        word = self._app.vocabulary_manager.get_word_by_text(word_text)
        if word:
            self._dialog.destroy()
            self._app.today_words = [word]
            self._app.current_word_index = 0
            self._app.unknown_words = []
            self._app.stage = "recite"
            self._app.test_mode = False
            from ui.pages.learning_page import LearningPage
            lp = self._app.page_manager.get_page("learning")
            if hasattr(lp, '_resume_existing_session'):
                lp._resume_existing_session()
