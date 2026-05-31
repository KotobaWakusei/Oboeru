"""学习页面 - 核心学习功能（自适应布局）"""
import os
import time
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from modules.logger import get_logger
from ui.core.base_page import BasePage
from ui.customtinker import CTFrame, CTLabel, CTProgressbar
from ui.components.learning_components import (
    WordDisplayCard, ReviewPanel, OptionsPanel, LearningControls, SearchResultsDialog
)


class LearningPage(BasePage):
    """学习页面 - 支持窗口自适应"""

    page_id = "learning"
    page_title = "学习"
    page_icon = "📚"

    BREAKPOINTS = {"xs": 400, "sm": 568, "md": 768, "lg": 1024, "xl": 1366}

    def create_widgets(self):
        self._current_ai_version = 0
        self._logger = get_logger()
        self._resize_timer = None
        self._last_width = 0
        self._last_nav_time = 0
        self._nav_cooldown = 0.8
        self._nav_hint_shown = False
        self._shortcuts_bound = False

        self._container.columnconfigure(0, weight=1)
        self._container.rowconfigure(1, weight=1)

        self._create_header()
        self._create_word_display()
        self._create_options()
        self._create_controls()

    def setup_layout(self):
        pass

    def bind_events(self):
        self.bind("<Configure>", self._on_resize_debounced)

    def _bind_learning_shortcuts(self):
        if self._shortcuts_bound:
            return
        root = self.app.root
        root.bind("<Return>", lambda e: self._next_word())
        root.bind("<Left>", lambda e: self._prev_word())
        root.bind("<Right>", lambda e: self._next_word())
        root.bind("<space>", lambda e: self._next_word())
        root.bind("<Up>", lambda e: self._prev_word_with_cooldown())
        root.bind("<Down>", lambda e: self._next_word_with_cooldown())
        self._shortcuts_bound = True

    def _unbind_learning_shortcuts(self):
        if not self._shortcuts_bound:
            return
        root = self.app.root
        for seq in ("<Return>", "<Left>", "<Right>", "<space>", "<Up>", "<Down>"):
            root.unbind(seq)
        self._shortcuts_bound = False

    def _on_resize_debounced(self, event):
        if event.widget != self._container:
            return
        width = event.width
        if abs(width - self._last_width) < 50 and self._last_width > 0:
            return
        self._last_width = width
        if self._resize_timer:
            self.after_cancel(self._resize_timer)
        self._resize_timer = self.after(100, lambda: self._apply_responsive_layout(event))

    def _apply_responsive_layout(self, event):
        width = event.width
        if width < self.BREAKPOINTS["xs"]:
            sk = "xs"
        elif width < self.BREAKPOINTS["sm"]:
            sk = "sm"
        elif width < self.BREAKPOINTS["md"]:
            sk = "md"
        elif width < self.BREAKPOINTS["lg"]:
            sk = "lg"
        else:
            sk = "xl"

        fc = {
            "xs": {"word": 18, "meaning": 11, "option": 9, "heading": 14},
            "sm": {"word": 22, "meaning": 12, "option": 10, "heading": 16},
            "md": {"word": 26, "meaning": 14, "option": 11, "heading": 18},
            "lg": {"word": 30, "meaning": 16, "option": 12, "heading": 20},
            "xl": {"word": 34, "meaning": 18, "option": 13, "heading": 22},
        }[sk]

        try:
            wrap = max(width - 120, 150)
            self._word_display.set_fonts(fc["word"], fc["meaning"], wrap)
            self._options_panel.set_fonts(fc["option"], width < self.BREAKPOINTS["sm"])
        except Exception:
            pass

    def _create_header(self):
        colors = self.colors
        header = CTFrame(self._container, style_manager=self._style_manager, bg=colors["bg_primary"])
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.columnconfigure(0, weight=1)

        self._stage_label = CTLabel(
            header, style_manager=self._style_manager,
            text=self._t('learning.stage.ready', '准备开始'),
            font=self._style_manager.get_font("heading"),
            bg=colors["bg_primary"], fg=colors["fg_primary"]
        )
        self._stage_label.grid(row=0, column=0, sticky="w")

        progress_frame = CTFrame(header, style_manager=self._style_manager, bg=colors["bg_primary"])
        progress_frame.grid(row=0, column=1, sticky="e")

        self._progress_bar = CTProgressbar(
            progress_frame, style_manager=self._style_manager,
            mode='determinate', length=120, maximum=100
        )
        self._progress_bar.pack(side=tk.RIGHT)

        self._percent_label = CTLabel(
            progress_frame, style_manager=self._style_manager,
            text="0%", font=self._style_manager.get_font("body"),
            bg=colors["bg_primary"], fg=colors["accent"], width=5
        )
        self._percent_label.pack(side=tk.RIGHT, padx=(0, 5))

    def _create_word_display(self):
        colors = self.colors
        main_container = CTFrame(self._container, style_manager=self._style_manager, bg=colors["bg_primary"])
        main_container.grid(row=1, column=0, sticky="nsew", pady=10)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(0, weight=1)

        self._word_display = WordDisplayCard(main_container, self._style_manager, self.app)
        self._word_display.grid(row=0, column=0, sticky="nsew")
        self._word_display.show_placeholder(self._t('learning.placeholder', '点击「开始学习」开始'))

        self._review_panel = ReviewPanel(main_container, self._style_manager, self.app)

    def _create_options(self):
        self._options_panel = OptionsPanel(self._container, self._style_manager, self._check_answer, app=self.app)

    def _create_controls(self):
        self._controls = LearningControls(self._container, self._style_manager, self.app)
        self._controls.grid(row=3, column=0, sticky="ew")

        self._controls.set_prev_command(self._prev_word)
        self._controls.set_next_command(self._next_word)
        self._controls.set_fav_command(self._toggle_favorite)
        self._controls.set_pronounce_command(self._play_pronunciation)
        self._controls.set_ai_command(self._generate_ai_sentence)
        self._controls.set_start_command(self._start_learning)
        self._controls.set_review_command(self._start_review)
        self._controls.set_exit_command(self.exit_learning)

    def on_enter(self, **kwargs):
        super().on_enter(**kwargs)
        self._bind_learning_shortcuts()
        mode = kwargs.get("mode", "new")

        if mode in ("new", "resume"):
            if not self._resume_existing_session():
                self._prepare_new_learning()
        elif mode == "review":
            self._start_review_mode()
        elif mode == "search":
            self._search_words()

    def _resume_existing_session(self):
        if not self.app.today_words:
            return False
        if self.app.current_word_index >= len(self.app.today_words):
            self.app.current_word_index = 0
        if self.app.progress_manager.session_start_time is None:
            self.app.progress_manager.start_session()
        self._controls.enable_controls(self.app.ai_manager.is_available())
        self._show_current_word()
        try:
            self._controls.hide_start_review_buttons()
        except Exception:
            pass
        try:
            self.app.hide_navbar()
        except Exception:
            pass
        return True

    def _prepare_new_learning(self):
        self.app.update_status(self._t("learning.status.click_to_start", "点击「开始学习」开始今日学习"))

    def on_leave(self):
        super().on_leave()
        self._unbind_learning_shortcuts()
        if getattr(self._controls, '_start_buttons_hidden', False):
            try:
                self._finish_learning()
            except Exception:
                pass
            try:
                self._controls.show_start_review_buttons()
            except Exception:
                pass
            try:
                self.app.show_navbar()
            except Exception:
                pass

    def _start_learning(self):
        if len(self.app.vocabulary_manager) == 0:
            self.show_message(self._t("learning.msg.load_vocab_first", "请先加载词库"), "warning")
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
        self._current_ai_version = self.app.ai_manager.increment_version()
        self.app.progress_manager.start_session()

        if self.app.ai_manager.is_available() and self.app.config.get_bool("ai_show_sentence", True):
            self.app.ai_manager.preload_for_session(self.app.today_words)

        self._controls.enable_controls(self.app.ai_manager.is_available())
        self._show_current_word()
        try:
            self._controls.hide_start_review_buttons()
        except Exception:
            pass
        try:
            self.app.hide_navbar()
        except Exception:
            pass
        self.show_message(self._t("learning.msg.start_learning", "开始学习 {count} 个单词").format(count=len(self.app.today_words)), "success")

    def _start_review_mode(self):
        if len(self.app.vocabulary_manager) == 0:
            vocab_file = self.app.config.get("vocab_file", "data/vocabulary.txt")
            if os.path.exists(vocab_file):
                success, result = self.app.vocabulary_manager.load_from_file(vocab_file)
                if not success:
                    self.show_message(self._t("learning.msg.load_failed", "加载词库失败: {msg}").format(msg=result), "error")
                    return
            else:
                self.show_message(self._t("learning.msg.load_vocab_in_settings", "请先在设置中加载词库"), "warning")
                return

        all_words = [w.word for w in self.app.vocabulary_manager.get_words()]
        review_count = self.app.config.get_int("review_words_count", 3)
        due_words = self.app.progress_manager.get_due_words(all_words, include_last_n=review_count)

        if not due_words:
            self.show_message(self._t("learning.msg.no_due_words", "暂时没有需要复习的单词"), "info")
            return

        word_map = {w.word: w for w in self.app.vocabulary_manager.get_words()}
        review_words = [word_map[w] for w in due_words if w in word_map]

        self.app.today_words = review_words
        self.app.current_word_index = 0
        self.app.unknown_words = []
        self.app.stage = "test"
        self.app.test_mode = True
        self.app.progress_manager.start_session()
        self._controls.enable_controls(self.app.ai_manager.is_available())
        self._show_current_word()
        try:
            self._controls.hide_start_review_buttons()
        except Exception:
            pass
        try:
            self.app.hide_navbar()
        except Exception:
            pass
        self.show_message(self._t("learning.msg.review_found", "找到 {count} 个需要复习的单词").format(count=len(review_words)), "success")

    def _start_review(self):
        self._start_review_mode()

    def _search_words(self):
        if len(self.app.vocabulary_manager) == 0:
            vocab_file = self.app.config.get("vocab_file", "data/vocabulary.txt")
            if os.path.exists(vocab_file):
                success, result = self.app.vocabulary_manager.load_from_file(vocab_file)
                if not success:
                    self.show_message(self._t("learning.msg.load_failed", "加载词库失败: {msg}").format(msg=result), "error")
                    return
            else:
                self.show_message(self._t("learning.msg.load_vocab_in_settings", "请先在设置中加载词库"), "warning")
                return

        query = simpledialog.askstring(
            self._t("learning.search.dialog_title", "搜索单词"),
            self._t("learning.search.dialog_prompt", "请输入要搜索的单词或中文意思："),
            parent=self.app.root)
        if not query:
            return
        results = self.app.vocabulary_manager.search_words(query)
        if not results:
            self.show_message(self._t("learning.msg.search_no_results", "没有找到包含 '{query}' 的单词").format(query=query), "info")
            return
        SearchResultsDialog(self, self.app, query, results)

    def _show_current_word(self):
        if not self.app.today_words:
            return
        idx = self.app.current_word_index
        if idx >= len(self.app.today_words):
            self._handle_stage_complete()
            return

        self._current_ai_version = self.app.ai_manager.increment_version()
        current = self.app.today_words[idx]
        total = len(self.app.today_words)
        stage = self.app.stage

        self._word_display.show_word(current.word, current.meaning if stage == "recite" else "", current.pos)

        if stage == "recite":
            self._stage_label.configure(text=self._t("learning.stage.recite", "📖 背诵阶段"))
            self._review_panel.update(
                self.app.today_words, idx, self.app.config.get_int("review_words_count", 3)
            )
            self._options_panel.hide()
            self._word_display._meaning_label.grid()
            self._controls.show_nav_buttons()
            self.app.update_status(self._t("learning.status.recite_hint", "背诵：记忆单词和意思，按空格或「下一个」继续"))
            if self.app.config.get_bool("ai_show_sentence", True):
                self._load_ai_sentence_async(current)
        else:
            self._stage_label.configure(text=self._t("learning.stage.test", "📝 测试阶段"))
            self._word_display.hide_meaning()
            self._review_panel.hide()
            self._controls.hide_nav_buttons()
            options = self.app.vocabulary_manager.generate_options(current)
            self._options_panel.show(options)
            self.app.update_status(self._t("learning.status.test_hint", "测试：请选择正确答案"))

        pct = (idx + 1) / total * 100
        self.app._animator.animate_progress(self._progress_bar, pct, steps=15)
        self._percent_label.configure(text=f"{int(pct)}%")
        stage_name = self._t("learning.stage.recite_short", "背诵") if stage == "recite" else self._t("learning.stage.test_short", "测试")
        self.app.update_progress(self._t("learning.progress.format", "{stage} {current}/{total}").format(stage=stage_name, current=idx + 1, total=total))

        is_fav = self.app.favorites_manager.is_favorite(current.word)
        self._controls.update_fav_button(is_fav)

    def _check_answer(self, selected_index):
        if not (self.app.stage == "test" and self.app.today_words):
            return

        current = self.app.today_words[self.app.current_word_index]
        options = [b.cget("text") for b in self._options_panel._buttons]
        selected_meaning = options[selected_index]
        self._options_panel.disable_all()

        if selected_meaning == current.meaning:
            self._options_panel.mark_correct(selected_index)
            self.show_message(self._t("learning.msg.correct", "✓ 正确！ {word}").format(word=current.word), "success")
            self.app.progress_manager.record_answer(current.word, True)
            self.app.current_word_index += 1
            self.after(self.app.config.get("test_delay", 800), self._show_current_word)
        else:
            self._options_panel.mark_wrong(selected_index, current.meaning)
            self.show_message(self._t("learning.msg.wrong", "✗ 错误！正确：{meaning}").format(meaning=current.meaning), "error")
            self.app.progress_manager.record_answer(current.word, False)
            self.app.unknown_words.append(current)
            self.app.current_word_index += 1
            self.after(self.app.config.get("wrong_delay", 1500), self._show_current_word)

    def _prev_word(self):
        if self.app.stage != "recite" or not self.app.today_words:
            return
        if self.app.current_word_index > 0:
            self.app.current_word_index -= 1
            self._show_current_word()

    def _next_word(self):
        if self.app.stage != "recite" or not self.app.today_words:
            return
        if self.app.current_word_index < len(self.app.today_words) - 1:
            self.app.current_word_index += 1
            self._show_current_word()
        else:
            self._handle_stage_complete()

    def _prev_word_with_cooldown(self):
        if self.app.stage != "recite" or not self.app.today_words:
            return
        now = time.time()
        if now - self._last_nav_time < self._nav_cooldown:
            if not self._nav_hint_shown:
                self.show_message(self._t("learning.msg.cooldown", "别那么急嘛！好好背单词 📖"), "warning")
                self._nav_hint_shown = True
            return
        self._nav_hint_shown = False
        self._last_nav_time = now
        if self.app.current_word_index > 0:
            self.app.current_word_index -= 1
            self._show_current_word()

    def _next_word_with_cooldown(self):
        if self.app.stage != "recite" or not self.app.today_words:
            return
        now = time.time()
        if now - self._last_nav_time < self._nav_cooldown:
            if not self._nav_hint_shown:
                self.show_message(self._t("learning.msg.cooldown", "别那么急嘛！好好背单词 📖"), "warning")
                self._nav_hint_shown = True
            return
        self._nav_hint_shown = False
        self._last_nav_time = now
        if self.app.current_word_index < len(self.app.today_words) - 1:
            self.app.current_word_index += 1
            self._show_current_word()
        else:
            self._handle_stage_complete()

    def _toggle_favorite(self):
        if not self.app.today_words:
            return
        idx = self.app.current_word_index
        if idx >= len(self.app.today_words):
            return
        current = self.app.today_words[idx]
        word_key = current.word

        if self.app.favorites_manager.is_favorite(word_key):
            self.app.favorites_manager.remove_word(word_key)
            self._controls.update_fav_button(False)
            self.show_message(self._t("learning.msg.unfavored", "已取消收藏: {word}").format(word=word_key), "info")
        else:
            self.app.favorites_manager.add_from_vocabulary(current)
            self._controls.update_fav_button(True)
            self.show_message(self._t("learning.msg.favored", "已收藏: {word}").format(word=word_key), "success")
        self.app.favorites_manager.save_favorites()
        self.app.update_favorites_count()

    def _play_pronunciation(self):
        if not self.app.today_words:
            return
        idx = self.app.current_word_index
        if idx >= len(self.app.today_words):
            return
        if not self.app.tts_manager.is_available():
            self.show_message(self._t("learning.msg.tts_unavailable", "发音功能不可用"), "warning")
            return
        current = self.app.today_words[idx]
        if self.app.tts_manager.speak_word(current.word):
            self.app.update_status(self._t("learning.status.playing", "正在播放: {word}").format(word=current.word))
        else:
            self.show_message(self._t("learning.msg.tts_failed", "发音失败"), "error")

    def _load_ai_sentence_async(self, word):
        if not self.app.ai_manager.is_available():
            return
        request_version = getattr(self, '_current_ai_version', 0)
        self._word_display.set_sentence_loading(self._t("learning.ai.generating", "正在生成例句..."))

        def on_result(success, result):
            if request_version < self.app.ai_manager.current_version:
                self._logger.debug(f"跳过过期例句: {word.word}")
                return
            self.after(0, lambda: self._on_ai_result(success, result))

        self.app.ai_manager.generate_sentence(word.word, word.meaning, callback=on_result, version=request_version)

    def _on_ai_result(self, success, result):
        if success:
            self._word_display.set_sentence(result)
        else:
            self._word_display.set_sentence_loading(self._t("learning.ai.failed", "生成失败: {msg}").format(msg=result))

    def _generate_ai_sentence(self):
        if not self.app.today_words:
            return
        idx = self.app.current_word_index
        if idx >= len(self.app.today_words):
            return
        if not self.app.ai_manager.is_available():
            self.show_message(self._t("learning.msg.ai_not_configured", "AI 功能未配置，请在设置中配置 API Key"), "warning")
            return
        self._load_ai_sentence_async(self.app.today_words[idx])

    def _handle_stage_complete(self):
        t = self._t
        if self.app.stage == "recite":
            if messagebox.askyesno(
                t("learning.dialog.recite_done_title", "背诵完成"),
                t("learning.dialog.recite_done_msg", "背诵完成！共 {count} 个单词\n\n是否进入测试阶段？").format(count=len(self.app.today_words)),
                parent=self.app.root):
                self.app.stage = "test"
                self.app.current_word_index = 0
                self._show_current_word()
            else:
                self._finish_learning()
        else:
            if self.app.unknown_words:
                if messagebox.askyesno(
                    t("learning.dialog.test_done_title", "测试完成"),
                    t("learning.dialog.test_done_msg", "有 {count} 个单词需要复习\n\n是否继续复习？").format(count=len(self.app.unknown_words)),
                    parent=self.app.root):
                    self.app.today_words = self.app.unknown_words.copy()
                    self.app.unknown_words = []
                    self.app.current_word_index = 0
                    self.app.stage = "recite"
                    self._show_current_word()
                else:
                    self._finish_learning()
            else:
                self.show_message(t("learning.msg.all_mastered", "🎉 恭喜！全部掌握！"), "success")
                self._celebrate_mastered()
                self._finish_learning()

    def _celebrate_mastered(self):
        colors = self.colors
        label = self._stage_label
        steps = 6
        pulses = 3
        tag = object()
        self._cel_tag = tag

        def _lerp(c1, c2, t):
            def _h(hx):
                hx = hx.lstrip("#")
                return tuple(int(hx[i:i+2], 16) for i in (0, 2, 4))
            def _f(r, g, b):
                return f"#{int(r):02x}{int(g):02x}{int(b):02x}"
            r1, g1, b1 = _h(c1)
            r2, g2, b2 = _h(c2)
            return _f(r1 + (r2 - r1) * t, g1 + (g2 - g1) * t, b1 + (b2 - b1) * t)

        def flash(p, total):
            if getattr(self, '_cel_tag', None) is not tag:
                return
            if p >= total:
                try:
                    label.configure(fg=colors["fg_primary"])
                except Exception:
                    pass
                return
            for i in range(steps):
                t = (i + 1) / steps
                c = _lerp(colors["fg_primary"], colors["success"], t) if p % 2 == 0 else _lerp(colors["success"], colors["fg_primary"], t)
                self.after(i * 60, lambda cc=c: label.configure(fg=cc) if getattr(self, '_cel_tag', None) is tag else None)
            self.after(steps * 60, flash, p + 1, total)

        flash(0, pulses * 2)

    def _finish_learning(self):
        if self.app.progress_manager.session_start_time is not None:
            self.app.progress_manager.end_session(
                words_studied=len(self.app.today_words),
                words_reviewed=len(self.app.unknown_words)
            )
        self.app.today_words = []
        self.app.current_word_index = 0
        self.app.unknown_words = []
        self.app.stage = "recite"
        self.app.test_mode = False
        self._controls.disable_controls()
        self._options_panel.hide()
        self._word_display.show_placeholder(self._t("learning.placeholder.done", "✅ 学习完成！"))
        self._stage_label.configure(text=self._t("learning.stage.done", "学习完成"))
        self.app.update_status(self._t("learning.status.done", "今日学习已完成"))
        self.app.update_progress("")
        try:
            self._controls.show_start_review_buttons()
        except Exception:
            pass
        try:
            self.app.show_navbar()
        except Exception:
            pass

    def exit_learning(self):
        try:
            if messagebox.askyesno(
                self._t('learning.dialog.exit_confirm_title', '退出学习'),
                self._t('learning.dialog.exit_confirm', '确定要退出当前学习并结束本次会话吗？'),
                parent=self.app.root
            ):
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
        super().apply_theme()
        self._word_display.apply_theme()
        self._review_panel.apply_theme()
        self._options_panel.apply_theme()
        self._controls.apply_theme()
