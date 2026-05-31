"""设置页面 - 应用配置（全翻译支持）"""
import os
import tkinter as tk
from tkinter import ttk, messagebox

from modules.utils.constants import Constants
from ui.core.base_page import BasePage
from ui.customtinker import CTFrame, CTLabel, CTScrollableFrame
from ui.components.settings_panels import (
    LearningSettingsPanel, DisplaySettingsPanel, BehaviorSettingsPanel,
    ThemeSettingsPanel, LanguageSettingsPanel, AISettingsPanel, DataSettingsPanel,
)


class SettingsPage(BasePage):
    """设置页面 - 支持滚动"""

    page_id = "settings"
    page_title = "设置"
    page_icon = "⚙️"

    def create_widgets(self):
        self._panels = []
        self._create_scrollable_area()
        self._create_header()
        self._panels.append(LearningSettingsPanel(self._scroll_frame, self._style_manager, self.app))
        self._panels.append(DisplaySettingsPanel(self._scroll_frame, self._style_manager, self.app))
        self._panels.append(LanguageSettingsPanel(self._scroll_frame, self._style_manager, self.app))
        self._panels.append(BehaviorSettingsPanel(self._scroll_frame, self._style_manager, self.app))
        self._panels.append(ThemeSettingsPanel(self._scroll_frame, self._style_manager, self.app))
        self._panels.append(AISettingsPanel(self._scroll_frame, self._style_manager, self.app))
        self._panels.append(DataSettingsPanel(self._scroll_frame, self._style_manager, self.app))
        self._create_action_buttons()
        self.after(100, self._rebind_mousewheel)

    def setup_layout(self):
        pass

    def apply_translation(self):
        if not self._is_initialized:
            return
        try:
            if hasattr(self, '_container') and self._container:
                self._container.destroy()
            self._setup_page()
            self.apply_theme()
        except Exception:
            pass

    def _rebind_mousewheel(self):
        self._bind_mousewheel_recursive(self._scroll_frame)

    def _create_scrollable_area(self):
        colors = self.colors
        self._outer_frame = CTScrollableFrame(
            self._container, style_manager=self._style_manager,
            bg=colors["bg_primary"], padx=15, pady=15
        )
        self._outer_frame.pack(fill=tk.BOTH, expand=True)
        self._canvas = self._outer_frame._canvas
        self._scrollbar = self._outer_frame._scrollbar
        self._scroll_frame = self._outer_frame._scroll_frame
        self._canvas_window = self._outer_frame._canvas_window

    def _bind_mousewheel_recursive(self, widget):
        widget.bind("<MouseWheel>", self._on_mousewheel)
        widget.bind("<Button-4>", self._on_mousewheel)
        widget.bind("<Button-5>", self._on_mousewheel)
        for child in widget.winfo_children():
            self._bind_mousewheel_recursive(child)

    def _on_mousewheel(self, event):
        if event.num == 4:
            self._canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self._canvas.yview_scroll(1, "units")
        else:
            self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _create_header(self):
        colors = self.colors
        header = CTFrame(self._scroll_frame, style_manager=self._style_manager, bg=colors["bg_primary"])
        header.pack(fill=tk.X, pady=(0, 15))
        header.columnconfigure(0, weight=1)

        title_group = CTFrame(header, style_manager=self._style_manager, bg=colors["bg_primary"])
        title_group.grid(row=0, column=0, sticky="w")
        CTLabel(title_group, style_manager=self._style_manager, text="Oboeru",
                font=self._style_manager.get_font("caption"), bg=colors["bg_primary"],
                fg=colors["accent"]).pack(anchor="w")
        CTLabel(title_group, style_manager=self._style_manager, text=self._t("settings.page_title", "⚙️ 应用设置"),
                font=self._style_manager.get_font("title"), bg=colors["bg_primary"],
                fg=colors["fg_primary"]).pack(anchor="w")
        CTLabel(title_group, style_manager=self._style_manager, text=self._t("settings.page_subtitle", "自定义您的学习体验"),
                font=self._style_manager.get_font("caption"), bg=colors["bg_primary"],
                fg=colors["fg_secondary"]).pack(anchor="w", pady=(3, 0))

        action_group = CTFrame(header, style_manager=self._style_manager, bg=colors["bg_primary"])
        action_group.grid(row=0, column=1, sticky="e")
        self.create_button(action_group, self._t("settings.save_btn", "💾 保存设置"), self._save_settings,
                           style="Primary.TButton").pack(side=tk.RIGHT, padx=(6, 0))
        self.create_button(action_group, self._t("settings.load_vocab_btn", "📁 加载词库"), self._load_vocabulary,
                           style="Secondary.TButton").pack(side=tk.RIGHT, padx=(6, 0))

    def _create_action_buttons(self):
        colors = self.colors
        btn_frame = CTFrame(self._scroll_frame, style_manager=self._style_manager, bg=colors["bg_primary"])
        btn_frame.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(btn_frame, text=self._t("settings.reset_btn", "🔄 重置为默认"), command=self._reset_settings,
                   style="Secondary.TButton").pack(side=tk.RIGHT, padx=3)

    def _save_settings(self):
        try:
            values = {}
            for p in self._panels:
                values.update(p.read_values())

            daily_words = values["daily_words"]
            dmn, dmx = self.app.config.get("daily_words_min", 1), self.app.config.get("daily_words_max", 100)
            if not (dmn <= daily_words <= dmx):
                self.show_message(self._t("settings.msg.daily_words_range", "每日单词量必须在 {min}-{max} 之间").format(min=dmn, max=dmx), "warning")
                return

            font_size = values["font_size"]
            fmn, fmx = self.app.config.get("font_size_min", 12), self.app.config.get("font_size_max", 24)
            if not (fmn <= font_size <= fmx):
                self.show_message(self._t("settings.msg.font_size_range", "字体大小必须在 {min}-{max} 之间").format(min=fmn, max=fmx), "warning")
                return

            review_count = values["review_words_count"]
            if not (1 <= review_count <= 10):
                self.show_message(self._t("settings.msg.review_count_range", "回顾单词数必须在 1-10 之间"), "warning")
                return

            if not (0 <= values["test_delay"] <= 10000):
                self.show_message(self._t("settings.msg.test_delay_range", "答对延迟必须在 0-10000 毫秒之间"), "warning")
                return
            if not (0 <= values["wrong_delay"] <= 10000):
                self.show_message(self._t("settings.msg.wrong_delay_range", "答错延迟必须在 0-10000 毫秒之间"), "warning")
                return

            if values.get("ai_enabled", False):
                if not values.get("ai_api_key", ""):
                    self.show_message(self._t("settings.msg.ai_key_required", "启用 AI 功能需要填写 API Key"), "warning")
                    return
                if not (5 <= values.get("ai_timeout", 30) <= 120):
                    self.show_message(self._t("settings.msg.ai_timeout_range", "超时时间必须在 5-120 秒之间"), "warning")
                    return
                if values.get("ai_provider") == "custom":
                    url = values.get("ai_custom_url", "")
                    if not url:
                        self.show_message(self._t("settings.msg.ai_custom_url_required", "自定义提供商需要填写 API URL"), "warning")
                        return
                    if not url.startswith(("http://", "https://")):
                        self.show_message(self._t("settings.msg.ai_url_invalid", "API URL 必须以 http:// 或 https:// 开头"), "warning")
                        return

            for key, val in values.items():
                self.app.config.set(key, val)

            self.app.ai_manager.configure(
                api_key=values.get("ai_api_key", ""),
                provider=values.get("ai_provider", "xunfei_lite"),
                custom_url=values.get("ai_custom_url", ""),
                custom_model=values.get("ai_custom_model", ""),
                difficulty=values.get("ai_difficulty", "junior"),
                enabled=values.get("ai_enabled", False),
                timeout=values.get("ai_timeout", 30)
            )
            self.app.config.save_config()
            self.show_message(self._t("settings.msg.saved", "设置已保存"), "success")

        except ValueError as e:
            self.show_message(self._t("settings.msg.invalid_number", "请输入有效的数值: {error}").format(error=e), "error")

    def _reset_settings(self):
        if not messagebox.askyesno(
            self._t("confirm.title", "确认"),
            self._t("settings.msg.reset_confirm", "确定要重置所有设置为默认值吗？"),
            parent=self.app.root):
            return
        defaults = self.app.config.get_default_config()
        for p in self._panels:
            p.reset(defaults)
        self._save_settings()
        for p in self._panels:
            if isinstance(p, (ThemeSettingsPanel,)):
                p._on_change()
                break
        self.show_message(self._t("settings.msg.reset_done", "已重置为默认设置"), "info")

    def _load_vocabulary(self):
        t = self._t
        vocab_file = self.app.config.get("vocab_file", Constants.DEFAULT_VOCAB_FILE)
        if not os.path.exists(vocab_file):
            self.show_message(t("settings.msg.file_not_found", "词库文件不存在: {path}").format(path=vocab_file), "error")
            return
        success, result = self.app.vocabulary_manager.load_from_file(vocab_file)
        if success:
            self.show_message(t("settings.msg.vocab_loaded", "词库加载成功，共 {count} 个单词").format(count=result), "success")
            self.app.update_status(t("settings.status.vocab_loaded", "词库已加载: {count} 个单词").format(count=result))
        else:
            self.show_message(t("settings.msg.vocab_load_failed", "加载词库失败: {error}").format(error=result), "error")

    def on_enter(self, **kwargs):
        super().on_enter(**kwargs)
        self.app.update_status(self._t("settings.status.hint", "配置您的学习偏好"))
        self.app.update_progress("")
        self._canvas.yview_moveto(0)

    def apply_theme(self):
        super().apply_theme()
        colors = self.colors
        self._canvas.configure(bg=colors["bg_primary"])
        self._outer_frame.configure(bg=colors["bg_primary"])
        self._scroll_frame.configure(bg=colors["bg_primary"])
