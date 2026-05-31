"""设置页面子面板（全翻译支持）"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from modules.utils.constants import Constants
from ui.customtinker import CTFrame, CTLabel, CTEntry, CTCombobox

_SORT_OPTIONS = [
    ("time", "settings.sort.time"),
    ("word", "settings.sort.word"),
    ("learn_count", "settings.sort.learn_count"),
]
_SORT_LABELS = {"time": "时间", "word": "字母", "learn_count": "学习次数"}


def _card(parent, sm, title):
    c = sm.colors
    card = CTFrame(parent, style_manager=sm, bg=c["bg_card"])
    card.configure(highlightbackground=c["border"], highlightthickness=1)
    card.pack(fill=tk.X, pady=(0, 12))
    hdr = CTFrame(card, style_manager=sm, bg=c["bg_secondary"])
    hdr.pack(fill=tk.X, padx=1, pady=1)
    acc = CTFrame(hdr, style_manager=sm, bg=c["accent"], width=4)
    acc.pack(side=tk.LEFT, fill=tk.Y)
    acc.pack_propagate(False)
    CTLabel(hdr, style_manager=sm, text=title, font=sm.get_font("subheading"),
            bg=c["bg_secondary"], fg=c["accent"], padx=12, pady=8).pack(anchor="w")
    content = CTFrame(card, style_manager=sm, bg=c["bg_card"])
    content.pack(fill=tk.X, padx=18, pady=14)
    return content


def _row(parent, sm, label, widget):
    c = sm.colors
    r = CTFrame(parent, style_manager=sm, bg=c["bg_card"])
    r.pack(fill=tk.X, pady=5)
    CTLabel(r, style_manager=sm, text=label, font=sm.get_font("body"),
            bg=c["bg_card"], fg=c["fg_primary"], width=12, anchor="w").pack(side=tk.LEFT)
    widget.pack(side=tk.LEFT, padx=(0, 8))
    return r


class _BasePanel:
    def __init__(self, app):
        self._app = app
        self._t = app.language_manager.translate


class LearningSettingsPanel(_BasePanel):
    def __init__(self, parent, sm, app):
        super().__init__(app)
        self._sm = sm
        t = self._t
        c = sm.colors
        card = _card(parent, sm, t("settings.learning_title", "📚 学习设置"))

        r1 = CTFrame(card, style_manager=sm, bg=c["bg_card"])
        r1.pack(fill=tk.X, pady=5)
        CTLabel(r1, style_manager=sm, text=t("settings.daily_words_label", "每日单词量："),
                font=sm.get_font("body"), bg=c["bg_card"], fg=c["fg_primary"], width=12, anchor="w").pack(side=tk.LEFT)
        self._daily_words_var = tk.StringVar(value=str(app.config.get("daily_words", 20)))
        CTEntry(r1, style_manager=sm, textvariable=self._daily_words_var, width=8,
                font=sm.get_font("body")).pack(side=tk.LEFT, padx=(0, 8))
        CTLabel(r1, style_manager=sm,
                text=f"({app.config.get('daily_words_min', 1)}-{app.config.get('daily_words_max', 100)})",
                font=sm.get_font("caption"), bg=c["bg_card"], fg=c["fg_secondary"]).pack(side=tk.LEFT)

        r2 = CTFrame(card, style_manager=sm, bg=c["bg_card"])
        r2.pack(fill=tk.X, pady=5)
        CTLabel(r2, style_manager=sm, text=t("settings.vocab_file_label", "词库文件："),
                font=sm.get_font("body"), bg=c["bg_card"], fg=c["fg_primary"], width=12, anchor="w").pack(side=tk.LEFT)
        self._vocab_file_var = tk.StringVar(value=app.config.get("vocab_file", Constants.DEFAULT_VOCAB_FILE))
        CTEntry(r2, style_manager=sm, textvariable=self._vocab_file_var, width=30,
                font=sm.get_font("body")).pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True)

        def browse():
            fp = filedialog.askopenfilename(title=t("settings.select_vocab_file", "选择词库文件"),
                                            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")], parent=app.root)
            if fp:
                self._vocab_file_var.set(fp)
        ttk.Button(r2, text=t("settings.browse", "浏览"), command=browse, style="Secondary.TButton").pack(side=tk.LEFT)

        r3 = CTFrame(card, style_manager=sm, bg=c["bg_card"])
        r3.pack(fill=tk.X, pady=5)
        self._shuffle_var = tk.BooleanVar(value=app.config.get_bool("shuffle_words", True))
        ttk.Checkbutton(r3, text=t("settings.shuffle_words", "随机打乱单词顺序"), variable=self._shuffle_var, style="TCheckbutton").pack(side=tk.LEFT)

        r4 = CTFrame(card, style_manager=sm, bg=c["bg_card"])
        r4.pack(fill=tk.X, pady=5)
        self._show_pinyin_var = tk.BooleanVar(value=app.config.get_bool("show_pinyin", True))
        ttk.Checkbutton(r4, text=t("settings.show_pinyin", "显示拼音/词性标注"), variable=self._show_pinyin_var, style="TCheckbutton").pack(side=tk.LEFT)

        r5 = CTFrame(card, style_manager=sm, bg=c["bg_card"])
        r5.pack(fill=tk.X, pady=5)
        self._auto_play_var = tk.BooleanVar(value=app.config.get_bool("auto_play_sound", False))
        ttk.Checkbutton(r5, text=t("settings.auto_play_pronunciation", "学习时自动播放发音"), variable=self._auto_play_var, style="TCheckbutton").pack(side=tk.LEFT)

        r6 = CTFrame(card, style_manager=sm, bg=c["bg_card"])
        r6.pack(fill=tk.X, pady=5)
        CTLabel(r6, style_manager=sm, text=t("settings.review_words_label", "回顾单词数："),
                font=sm.get_font("body"), bg=c["bg_card"], fg=c["fg_primary"], width=12, anchor="w").pack(side=tk.LEFT)
        self._review_count_var = tk.StringVar(value=str(app.config.get("review_words_count", 3)))
        CTEntry(r6, style_manager=sm, textvariable=self._review_count_var, width=8,
                font=sm.get_font("body")).pack(side=tk.LEFT, padx=(0, 8))
        CTLabel(r6, style_manager=sm, text=t("settings.review_range_hint", "(1-10) 背诵时显示最近N个单词"),
                font=sm.get_font("caption"), bg=c["bg_card"], fg=c["fg_secondary"]).pack(side=tk.LEFT)

    def read_values(self):
        return {"daily_words": int(self._daily_words_var.get()), "vocab_file": self._vocab_file_var.get(),
                "shuffle_words": self._shuffle_var.get(), "show_pinyin": self._show_pinyin_var.get(),
                "auto_play_sound": self._auto_play_var.get(), "review_words_count": int(self._review_count_var.get())}

    def reset(self, d):
        self._daily_words_var.set(str(d.get("daily_words", 20)))
        self._vocab_file_var.set(d.get("vocab_file", Constants.DEFAULT_VOCAB_FILE))
        self._shuffle_var.set(d.get("shuffle_words", True))
        self._show_pinyin_var.set(d.get("show_pinyin", True))
        self._auto_play_var.set(d.get("auto_play_sound", False))
        self._review_count_var.set(str(d.get("review_words_count", 3)))


class DisplaySettingsPanel(_BasePanel):
    def __init__(self, parent, sm, app):
        super().__init__(app)
        self._sm = sm
        t = self._t
        c = sm.colors
        card = _card(parent, sm, t("settings.display_title", "🖥️ 显示设置"))

        r1 = CTFrame(card, style_manager=sm, bg=c["bg_card"])
        r1.pack(fill=tk.X, pady=5)
        CTLabel(r1, style_manager=sm, text=t("settings.font_size_label", "字体大小："),
                font=sm.get_font("body"), bg=c["bg_card"], fg=c["fg_primary"], width=12, anchor="w").pack(side=tk.LEFT)
        self._font_size_var = tk.StringVar(value=str(app.config.get("font_size", 14)))
        CTEntry(r1, style_manager=sm, textvariable=self._font_size_var, width=8,
                font=sm.get_font("body")).pack(side=tk.LEFT, padx=(0, 8))
        CTLabel(r1, style_manager=sm,
                text=f"({app.config.get('font_size_min', 12)}-{app.config.get('font_size_max', 24)})",
                font=sm.get_font("caption"), bg=c["bg_card"], fg=c["fg_secondary"]).pack(side=tk.LEFT)
        r2 = CTFrame(card, style_manager=sm, bg=c["bg_card"])
        r2.pack(fill=tk.X, pady=5)
        self._progress_var = tk.BooleanVar(value=app.config.get_bool("show_progress_bar", True))
        ttk.Checkbutton(r2, text=t("settings.show_progress_bar", "显示学习进度条"), variable=self._progress_var, style="TCheckbutton").pack(side=tk.LEFT)
        r3 = CTFrame(card, style_manager=sm, bg=c["bg_card"])
        r3.pack(fill=tk.X, pady=5)
        self._remember_size_var = tk.BooleanVar(value=app.config.get_bool("remember_window_size", True))
        ttk.Checkbutton(r3, text=t("settings.remember_window_size", "记住窗口大小和位置"), variable=self._remember_size_var, style="TCheckbutton").pack(side=tk.LEFT)

    def read_values(self):
        return {"font_size": int(self._font_size_var.get()), "show_progress_bar": self._progress_var.get(),
                "remember_window_size": self._remember_size_var.get()}

    def reset(self, d):
        self._font_size_var.set(str(d.get("font_size", 14)))
        self._progress_var.set(d.get("show_progress_bar", True))
        self._remember_size_var.set(d.get("remember_window_size", True))


class BehaviorSettingsPanel(_BasePanel):
    def __init__(self, parent, sm, app):
        super().__init__(app)
        self._sm = sm
        t = self._t
        c = sm.colors
        card = _card(parent, sm, t("settings.behavior_title", "⚡ 行为设置"))

        r1 = CTFrame(card, style_manager=sm, bg=c["bg_card"])
        r1.pack(fill=tk.X, pady=5)
        CTLabel(r1, style_manager=sm, text=t("settings.correct_delay_label", "答对延迟："),
                font=sm.get_font("body"), bg=c["bg_card"], fg=c["fg_primary"], width=12, anchor="w").pack(side=tk.LEFT)
        self._test_delay_var = tk.StringVar(value=str(app.config.get_int("test_delay", 1500)))
        CTEntry(r1, style_manager=sm, textvariable=self._test_delay_var, width=8,
                font=sm.get_font("body")).pack(side=tk.LEFT, padx=(0, 5))
        CTLabel(r1, style_manager=sm, text=t("settings.milliseconds", "毫秒"), font=sm.get_font("caption"),
                bg=c["bg_card"], fg=c["fg_secondary"]).pack(side=tk.LEFT)

        r2 = CTFrame(card, style_manager=sm, bg=c["bg_card"])
        r2.pack(fill=tk.X, pady=5)
        CTLabel(r2, style_manager=sm, text=t("settings.wrong_delay_label", "答错延迟："),
                font=sm.get_font("body"), bg=c["bg_card"], fg=c["fg_primary"], width=12, anchor="w").pack(side=tk.LEFT)
        self._wrong_delay_var = tk.StringVar(value=str(app.config.get_int("wrong_delay", 2000)))
        CTEntry(r2, style_manager=sm, textvariable=self._wrong_delay_var, width=8,
                font=sm.get_font("body")).pack(side=tk.LEFT, padx=(0, 5))
        CTLabel(r2, style_manager=sm, text=t("settings.milliseconds", "毫秒"), font=sm.get_font("caption"),
                bg=c["bg_card"], fg=c["fg_secondary"]).pack(side=tk.LEFT)

        r3 = CTFrame(card, style_manager=sm, bg=c["bg_card"])
        r3.pack(fill=tk.X, pady=5)
        self._confirm_exit_var = tk.BooleanVar(value=app.config.get_bool("confirm_before_exit", True))
        ttk.Checkbutton(r3, text=t("settings.confirm_before_exit", "退出前确认"), variable=self._confirm_exit_var, style="TCheckbutton").pack(side=tk.LEFT)
        r4 = CTFrame(card, style_manager=sm, bg=c["bg_card"])
        r4.pack(fill=tk.X, pady=5)
        self._auto_save_var = tk.BooleanVar(value=app.config.get_bool("auto_save_config", True))
        ttk.Checkbutton(r4, text=t("settings.auto_save_config", "自动保存配置"), variable=self._auto_save_var, style="TCheckbutton").pack(side=tk.LEFT)

    def read_values(self):
        return {"test_delay": int(self._test_delay_var.get()), "wrong_delay": int(self._wrong_delay_var.get()),
                "confirm_before_exit": self._confirm_exit_var.get(), "auto_save_config": self._auto_save_var.get()}

    def reset(self, d):
        self._test_delay_var.set(str(d.get("test_delay", 1500)))
        self._wrong_delay_var.set(str(d.get("wrong_delay", 2000)))
        self._confirm_exit_var.set(d.get("confirm_before_exit", True))
        self._auto_save_var.set(d.get("auto_save_config", True))


class ThemeSettingsPanel(_BasePanel):
    def __init__(self, parent, sm, app):
        super().__init__(app)
        self._sm = sm
        t = self._t
        c = sm.colors
        card = _card(parent, sm, t("settings.theme_title", "🎨 主题设置"))

        r1 = CTFrame(card, style_manager=sm, bg=c["bg_card"])
        r1.pack(fill=tk.X, pady=5)
        CTLabel(r1, style_manager=sm, text=t("settings.theme_label", "选择主题："),
                font=sm.get_font("body"), bg=c["bg_card"], fg=c["fg_primary"], width=12, anchor="w").pack(side=tk.LEFT)
        self._theme_var = tk.StringVar(value=sm.current_theme)
        combo = CTCombobox(r1, style_manager=sm, textvariable=self._theme_var,
                           values=sm.get_available_themes(), state="readonly", width=15, font=sm.get_font("body"))
        combo.pack(side=tk.LEFT)
        combo.bind("<<ComboboxSelected>>", self._on_change)
        self._preview = CTFrame(card, style_manager=sm, bg=c["bg_card"])
        self._preview.pack(fill=tk.X, pady=10)
        self._update_preview()

    def _on_change(self, event=None):
        self._sm.set_theme(self._theme_var.get())
        self._sm.setup_styles(self._app.root)
        self._update_preview()

    def _update_preview(self):
        for w in self._preview.winfo_children():
            w.destroy()
        t = self._t
        cols = self._sm.colors
        for name, color in [(t("settings.theme_color.bg_primary", "主背景"), cols["bg_primary"]),
                            (t("settings.theme_color.bg_secondary", "次背景"), cols["bg_secondary"]),
                            (t("settings.theme_color.bg_card", "卡片"), cols["bg_card"]),
                            (t("settings.theme_color.fg_primary", "主文字"), cols["fg_primary"]),
                            (t("settings.theme_color.accent", "强调色"), cols["accent"]),
                            (t("settings.theme_color.success", "成功"), cols["success"])]:
            f = CTFrame(self._preview, style_manager=self._sm, bg=cols["bg_card"])
            f.pack(side=tk.LEFT, padx=4)
            box = CTFrame(f, style_manager=self._sm, bg=color, width=30, height=30)
            box.pack()
            box.pack_propagate(False)
            CTLabel(f, style_manager=self._sm, text=name, font=self._sm.get_font("small"),
                    bg=cols["bg_card"], fg=cols["fg_secondary"]).pack(pady=(3, 0))

    def read_values(self):
        return {"theme": self._theme_var.get()}

    def reset(self, d):
        self._theme_var.set(d.get("theme", "default"))
        self._on_change()

    def set_sm(self, sm):
        self._sm = sm


class LanguageSettingsPanel(_BasePanel):
    def __init__(self, parent, sm, app):
        super().__init__(app)
        self._sm = sm
        t = self._t
        c = sm.colors
        card = _card(parent, sm, t("settings.language_title", "🌐 语言设置"))

        row = CTFrame(card, style_manager=sm, bg=c["bg_card"])
        row.pack(fill=tk.X, pady=5)
        CTLabel(row, style_manager=sm, text=t("settings.ui_language", "界面语言："),
                font=sm.get_font("body"), bg=c["bg_card"], fg=c["fg_primary"], width=12, anchor="w").pack(side=tk.LEFT)

        lang_mgr = app.language_manager
        available = lang_mgr.get_available_languages() if lang_mgr else []
        self._lang_map = {name: code for code, name in available}
        cur_code = lang_mgr.current_language if lang_mgr else None
        cur_display = lang_mgr.get_language_display(cur_code) if cur_code else (available[0][1] if available else "")
        self._lang_var = tk.StringVar(value=cur_display)
        combo = CTCombobox(row, style_manager=sm, textvariable=self._lang_var,
                           values=[n for _, n in available], state="readonly", width=18, font=sm.get_font("body"))
        combo.pack(side=tk.LEFT)
        combo.bind("<<ComboboxSelected>>", self._on_change)

    def read_values(self):
        return {}

    def reset(self, d):
        lang_mgr = self._app.language_manager
        if lang_mgr:
            cur_code = lang_mgr.current_language
            cur_display = lang_mgr.get_language_display(cur_code) if cur_code else ""
            if cur_display:
                self._lang_var.set(cur_display)

    def _on_change(self, event=None):
        try:
            code = self._lang_map.get(self._lang_var.get())
            if code:
                self._app.language_manager.set_language(code, save=True)
                try:
                    self._app.apply_translation()
                except Exception:
                    pass
        except Exception:
            pass


class AISettingsPanel(_BasePanel):
    def __init__(self, parent, sm, app):
        super().__init__(app)
        self._sm = sm
        t = self._t
        c = sm.colors
        self._provider_keys = [k for k in Constants.AI_PROVIDERS]
        self._diff_keys = [k for k in Constants.AI_DIFFICULTY_LEVELS]

        card = _card(parent, sm, t("settings.ai_title", "🤖 AI 例句设置"))

        row0 = CTFrame(card, style_manager=sm, bg=c["bg_card"])
        row0.pack(fill=tk.X, pady=5)
        self._ai_enabled_var = tk.BooleanVar(value=app.config.get_bool("ai_enabled", False))
        ttk.Checkbutton(row0, text=t("settings.enable_ai_sentences", "启用 AI 例句生成"),
                        variable=self._ai_enabled_var, style="TCheckbutton").pack(side=tk.LEFT)
        CTLabel(row0, style_manager=sm, text=t("settings.ai_description", "(使用 AI 为单词生成例句，需要 API Key)"),
                font=sm.get_font("small"), bg=c["bg_card"], fg=c["fg_secondary"]).pack(side=tk.LEFT, padx=(10, 0))

        rp = CTFrame(card, style_manager=sm, bg=c["bg_card"])
        rp.pack(fill=tk.X, pady=5)
        CTLabel(rp, style_manager=sm, text=t("settings.ai_provider_label", "API 提供商："),
                font=sm.get_font("body"), bg=c["bg_card"], fg=c["fg_primary"], width=12, anchor="w").pack(side=tk.LEFT)
        sel_key = app.config.get("ai_provider", "xunfei_lite")
        self._provider_display = self._build_provider_display(t)
        cur_name = self._provider_display.get(sel_key, list(self._provider_display.values())[0])
        self._ai_provider_var = tk.StringVar(value=cur_name)
        self._provider_rev = {v: k for k, v in self._provider_display.items()}
        pcombo = ttk.Combobox(rp, textvariable=self._ai_provider_var,
                              values=list(self._provider_display.values()),
                              state="readonly", width=18, font=sm.get_font("body"))
        pcombo.pack(side=tk.LEFT)
        pcombo.bind("<<ComboboxSelected>>", self._on_provider_change)
        self._provider_hint = CTLabel(rp, style_manager=sm, text="", font=sm.get_font("small"),
                                      bg=c["bg_card"], fg=c["fg_secondary"])
        self._provider_hint.pack(side=tk.LEFT, padx=(5, 0))
        self._custom_url_visible = False
        self._custom_model_visible = False

        self._custom_url_frame = CTFrame(card, style_manager=sm, bg=c["bg_card"])
        CTLabel(self._custom_url_frame, style_manager=sm, text=t("settings.ai_custom_url_label", "自定义 URL："),
                font=sm.get_font("body"), bg=c["bg_card"], fg=c["fg_primary"], width=12, anchor="w").pack(side=tk.LEFT)
        self._ai_custom_url_var = tk.StringVar(value=app.config.get("ai_custom_url", ""))
        ttk.Entry(self._custom_url_frame, textvariable=self._ai_custom_url_var, width=40,
                  font=sm.get_font("body")).pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True)

        self._custom_model_frame = CTFrame(card, style_manager=sm, bg=c["bg_card"])
        CTLabel(self._custom_model_frame, style_manager=sm, text=t("settings.ai_custom_model_label", "模型名称："),
                font=sm.get_font("body"), bg=c["bg_card"], fg=c["fg_primary"], width=12, anchor="w").pack(side=tk.LEFT)
        self._ai_custom_model_var = tk.StringVar(value=app.config.get("ai_custom_model", ""))
        ttk.Entry(self._custom_model_frame, textvariable=self._ai_custom_model_var, width=25,
                  font=sm.get_font("body")).pack(side=tk.LEFT)

        r1 = CTFrame(card, style_manager=sm, bg=c["bg_card"])
        r1.pack(fill=tk.X, pady=5)
        CTLabel(r1, style_manager=sm, text=t("settings.ai_key_label", "API Key："),
                font=sm.get_font("body"), bg=c["bg_card"], fg=c["fg_primary"], width=12, anchor="w").pack(side=tk.LEFT)
        self._ai_key_var = tk.StringVar(value=app.config.get("ai_api_key", ""))
        self._api_entry = ttk.Entry(r1, textvariable=self._ai_key_var, width=35,
                                    font=sm.get_font("body"), show="*")
        self._api_entry.pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True)
        self._show_key_var = tk.BooleanVar(value=False)
        def toggle_key():
            self._api_entry.configure(show="" if self._show_key_var.get() else "*")
        ttk.Checkbutton(r1, text=t("settings.show_api_key", "显示"), variable=self._show_key_var,
                        command=toggle_key, style="TCheckbutton").pack(side=tk.LEFT)
        ttk.Button(r1, text=t("settings.test_connection", "测试连接"), command=self._test_connection,
                   style="Secondary.TButton").pack(side=tk.LEFT, padx=(5, 0))

        rd = CTFrame(card, style_manager=sm, bg=c["bg_card"])
        rd.pack(fill=tk.X, pady=5)
        CTLabel(rd, style_manager=sm, text=t("settings.ai_difficulty_label", "例句难度："),
                font=sm.get_font("body"), bg=c["bg_card"], fg=c["fg_primary"], width=12, anchor="w").pack(side=tk.LEFT)
        self._diff_display = self._build_diff_display(t)
        sel_diff_key = app.config.get("ai_difficulty", "junior")
        cur_diff_name = self._diff_display.get(sel_diff_key, list(self._diff_display.values())[0])
        self._ai_difficulty_var = tk.StringVar(value=cur_diff_name)
        self._diff_rev = {v: k for k, v in self._diff_display.items()}
        dcombo = ttk.Combobox(rd, textvariable=self._ai_difficulty_var,
                              values=list(self._diff_display.values()),
                              state="readonly", width=12, font=sm.get_font("body"))
        dcombo.pack(side=tk.LEFT)
        dcombo.bind("<<ComboboxSelected>>", lambda e: self._update_display())
        self._diff_hint = CTLabel(rd, style_manager=sm, text="", font=sm.get_font("small"),
                                  bg=c["bg_card"], fg=c["fg_secondary"])
        self._diff_hint.pack(side=tk.LEFT, padx=(5, 0))

        r3 = CTFrame(card, style_manager=sm, bg=c["bg_card"])
        r3.pack(fill=tk.X, pady=5)
        CTLabel(r3, style_manager=sm, text=t("settings.ai_timeout_label", "超时(秒)："),
                font=sm.get_font("body"), bg=c["bg_card"], fg=c["fg_primary"], width=12, anchor="w").pack(side=tk.LEFT)
        self._ai_timeout_var = tk.StringVar(value=str(app.config.get_int("ai_timeout", 30)))
        ttk.Entry(r3, textvariable=self._ai_timeout_var, width=8, font=sm.get_font("body")).pack(side=tk.LEFT)
        CTLabel(r3, style_manager=sm, text=t("settings.ai_timeout_hint", "(网络请求超时时间，建议 10-60 秒)"),
                font=sm.get_font("small"), bg=c["bg_card"], fg=c["fg_secondary"]).pack(side=tk.LEFT, padx=(5, 0))

        r4 = CTFrame(card, style_manager=sm, bg=c["bg_card"])
        r4.pack(fill=tk.X, pady=5)
        self._ai_show_sentence_var = tk.BooleanVar(value=app.config.get_bool("ai_show_sentence", True))
        ttk.Checkbutton(r4, text=t("settings.auto_show_ai_sentences", "学习时自动显示 AI 例句"),
                        variable=self._ai_show_sentence_var, style="TCheckbutton").pack(side=tk.LEFT)
        self._update_display()

    def _build_provider_display(self, t):
        return {k: t(f"settings.ai_provider.{k}", v.get("name", k))
                for k, v in Constants.AI_PROVIDERS.items()}

    def _build_diff_display(self, t):
        return {k: t(f"settings.ai_difficulty.{k}", v.get("name", k))
                for k, v in Constants.AI_DIFFICULTY_LEVELS.items()}

    def _on_provider_change(self, event=None):
        self._update_display()

    def _update_display(self):
        cur_name = self._ai_provider_var.get()
        pkey = self._provider_rev.get(cur_name)
        if pkey:
            cfg = Constants.AI_PROVIDERS.get(pkey, {})
            self._provider_hint.configure(text=cfg.get("api_key_hint", ""))
            frame_visible = (pkey == "custom")
            if frame_visible and not self._custom_url_visible:
                self._custom_url_frame.pack(fill=tk.X, pady=5)
                self._custom_model_frame.pack(fill=tk.X, pady=5)
                self._custom_url_visible = True
                self._custom_model_visible = True
            elif not frame_visible and self._custom_url_visible:
                self._custom_url_frame.pack_forget()
                self._custom_model_frame.pack_forget()
                self._custom_url_visible = False
                self._custom_model_visible = False
        cur_diff = self._ai_difficulty_var.get()
        dkey = self._diff_rev.get(cur_diff)
        if dkey:
            dc = Constants.AI_DIFFICULTY_LEVELS.get(dkey, {})
            self._diff_hint.configure(text=dc.get("description", ""))

    def _test_connection(self):
        t = self._t
        pkey = self._provider_rev.get(self._ai_provider_var.get(), "xunfei_lite")
        dkey = self._diff_rev.get(self._ai_difficulty_var.get(), "junior")
        try:
            timeout = int(self._ai_timeout_var.get())
        except ValueError:
            self._app.show_message(t("settings.invalid_timeout", "请输入有效的超时时间"), "warning")
            return
        self._app.ai_manager.configure(
            api_key=self._ai_key_var.get().strip(), provider=pkey,
            custom_url=self._ai_custom_url_var.get().strip(), custom_model=self._ai_custom_model_var.get().strip(),
            difficulty=dkey, enabled=self._ai_enabled_var.get(), timeout=timeout)
        if not self._app.ai_manager.is_available():
            self._app.show_message(t("settings.connection_failed", "连接失败"), "error")
            return
        self._app.show_message(t("settings.connection_testing", "正在测试连接..."), "info")
        try:
            ok, result = self._app.ai_manager.generate_sentence_sync("test", "test")
            if ok:
                self._app.show_message(t("settings.connection_success", "✓ 连接成功！AI 响应: {result}").format(result=result), "success")
            else:
                self._app.show_message(t("settings.connection_failed_detail", "✗ 连接失败: {result}").format(result=result), "error")
        except Exception as e:
            self._app.show_message(t("settings.connection_failed_detail", "✗ 连接失败: {result}").format(result=str(e)), "error")

    def read_values(self):
        pkey = self._provider_rev.get(self._ai_provider_var.get(), "xunfei_lite")
        dkey = self._diff_rev.get(self._ai_difficulty_var.get(), "junior")
        return {"ai_enabled": self._ai_enabled_var.get(), "ai_api_key": self._ai_key_var.get(),
                "ai_provider": pkey, "ai_custom_url": self._ai_custom_url_var.get(),
                "ai_custom_model": self._ai_custom_model_var.get(), "ai_difficulty": dkey,
                "ai_timeout": int(self._ai_timeout_var.get()), "ai_show_sentence": self._ai_show_sentence_var.get()}

    def reset(self, d):
        self._ai_enabled_var.set(d.get("ai_enabled", False))
        self._ai_key_var.set(d.get("ai_api_key", ""))
        self._ai_timeout_var.set(str(d.get("ai_timeout", 30)))
        self._ai_show_sentence_var.set(d.get("ai_show_sentence", True))
        pkey = d.get("ai_provider", "xunfei_lite")
        self._ai_provider_var.set(self._provider_display.get(pkey, list(self._provider_display.values())[0]))
        self._ai_custom_url_var.set(d.get("ai_custom_url", ""))
        self._ai_custom_model_var.set(d.get("ai_custom_model", ""))
        dkey = d.get("ai_difficulty", "junior")
        self._ai_difficulty_var.set(self._diff_display.get(dkey, list(self._diff_display.values())[0]))
        self._update_display()


class DataSettingsPanel(_BasePanel):
    def __init__(self, parent, sm, app):
        super().__init__(app)
        self._sm = sm
        t = self._t
        c = sm.colors
        card = _card(parent, sm, t("settings.data_title", "📁 数据管理"))

        r1 = CTFrame(card, style_manager=sm, bg=c["bg_card"])
        r1.pack(fill=tk.X, pady=5)
        self._fav_backup_var = tk.BooleanVar(value=app.config.get_bool("favorites_auto_backup", True))
        ttk.Checkbutton(r1, text=t("settings.favorites_auto_backup", "收藏自动备份"),
                        variable=self._fav_backup_var, style="TCheckbutton").pack(side=tk.LEFT)

        r2 = CTFrame(card, style_manager=sm, bg=c["bg_card"])
        r2.pack(fill=tk.X, pady=5)
        CTLabel(r2, style_manager=sm, text=t("settings.favorites_sort_label", "收藏排序："),
                font=sm.get_font("body"), bg=c["bg_card"], fg=c["fg_primary"], width=12, anchor="w").pack(side=tk.LEFT)
        sort_fallback = dict(_SORT_LABELS)
        self._sort_values = [(k, t(kv, sort_fallback.get(k, k))) for k, kv in _SORT_OPTIONS]
        self._rev_sort_map = {v: k for k, v in self._sort_values}
        cur_code = app.config.get("favorites_sort", "time")
        cur_label = dict(self._sort_values).get(cur_code, cur_code)
        self._fav_sort_var = tk.StringVar(value=cur_label)
        combo = ttk.Combobox(r2, textvariable=self._fav_sort_var,
                             values=[v for _, v in self._sort_values],
                             state="readonly", width=15, font=sm.get_font("body"))
        combo.pack(side=tk.LEFT)
        CTLabel(r2, style_manager=sm, text=t("settings.favorites_sort_hint", "(时间/字母/学习次数)"),
                font=sm.get_font("caption"), bg=c["bg_card"], fg=c["fg_secondary"]).pack(side=tk.LEFT, padx=(5, 0))

        br = CTFrame(card, style_manager=sm, bg=c["bg_card"])
        br.pack(fill=tk.X, pady=(10, 5))
        ttk.Button(br, text=t("settings.clear_progress", "🗑️ 清除学习进度"),
                   command=self._clear_progress, style="Secondary.TButton").pack(side=tk.LEFT, padx=3)
        ttk.Button(br, text=t("settings.export_all_data", "📤 导出所有数据"),
                   command=self._export_data, style="Secondary.TButton").pack(side=tk.LEFT, padx=3)

    def _clear_progress(self):
        if messagebox.askyesno(self._t("confirm.title", "确认"),
                               self._t("settings.confirm_clear_progress", "确定要清除所有学习进度吗？\n此操作不可恢复！"),
                               parent=self._app.root):
            self._app.progress_manager.clear_all_progress()
            self._app.show_message(self._t("settings.progress_cleared", "学习进度已清除"), "success")

    def _export_data(self):
        t = self._t
        dir_path = filedialog.askdirectory(title=t("settings.export_dir", "选择导出目录"), parent=self._app.root)
        if not dir_path:
            return
        import datetime, shutil
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        config_path = os.path.join(dir_path, f"config_{ts}.json")
        self._app.config.save_config()
        if os.path.exists(self._app.config._config_file):
            shutil.copy2(self._app.config._config_file, config_path)
        fav_path = os.path.join(dir_path, f"favorites_{ts}.txt")
        self._app.favorites_manager.export_to_file(fav_path)
        prog_path = os.path.join(dir_path, f"progress_{ts}.txt")
        self._app.progress_manager.export_progress(prog_path)
        self._app.show_message(t("settings.export_success", "数据已导出到: {dir}").format(dir=dir_path), "success")

    def read_values(self):
        return {"favorites_auto_backup": self._fav_backup_var.get(), "favorites_sort": self._read_sort_key()}

    def _read_sort_key(self):
        label = self._fav_sort_var.get()
        return self._rev_sort_map.get(label, label)

    def reset(self, d):
        self._fav_backup_var.set(d.get("favorites_auto_backup", True))
        key = d.get("favorites_sort", "time")
        self._fav_sort_var.set(dict(_SORT_OPTIONS).get(key, key))
