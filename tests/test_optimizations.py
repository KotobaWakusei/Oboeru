import tkinter as tk

import pytest

from modules.utils.file_utils import safe_save_file
from modules.vocabulary_manager import VocabularyManager
from ui.components.word_card import WordCard
from ui.components.navbar import NavBar
from ui.pages.settings_page import SettingsPage
from ui.core.style_manager import StyleManager
from ui.customtinker import CTButton
from modules.favorites_manager import FavoritesManager, FavoriteWord
from ui.pages.favorites_page import FavoritesPage
from ui.core.page_manager import PageManager
from ui.core.base_page import BasePage

def test_vocabulary_lookup_index_updates_after_loading_strings():
    manager = VocabularyManager()

    assert manager.load_from_strings(["apple\tn.\t苹果", "apply\tv.\t申请"]) == 2
    assert manager.get_word_by_text("apple").meaning == "苹果"

    assert manager.load_from_strings(["banana\tn.\t香蕉"]) == 1
    assert manager.get_word_by_text("apple") is None
    assert manager.get_word_by_text("banana").meaning == "香蕉"


def test_generate_options_uses_indexed_similar_word_meanings():
    manager = VocabularyManager()
    manager.load_from_strings(
        [
            "apple\tn.\t苹果",
            "apply\tv.\t申请",
            "banana\tn.\t香蕉",
            "orange\tn.\t橙子",
        ]
    )

    options = manager.generate_options(manager.get_word_by_text("apple"), count=3)

    assert "苹果" in options
    assert len(options) == 4


def test_safe_save_file_replaces_existing_file(tmp_path):
    target = tmp_path / "config.json"
    target.write_text('{"old": true}', encoding="utf-8")

    success, error = safe_save_file(str(target), '{"new": true}')

    assert success, error
    assert target.read_text(encoding="utf-8") == '{"new": true}'
    assert not list(tmp_path.glob("*.tmp"))


@pytest.fixture
def tk_root():
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tkinter display is not available: {exc}")
    try:
        root.withdraw()
        yield root
    finally:
        root.destroy()


def test_ctbutton_refreshes_colors_after_theme_change(tk_root):
    style = StyleManager("dark")
    button = CTButton(tk_root, style_manager=style, text="Test")
    original_bg = button.cget("bg")

    style.set_theme("light")
    button.apply_theme()

    assert button.cget("bg") != original_bg
    assert button.cget("bg") == style.colors["accent"]


def test_word_card_reduces_font_size_for_long_words(tk_root):
    style = StyleManager("dark")
    card = WordCard(tk_root, style_manager=style)

    card.set_word("characteristicallyextendedword", "adj.")

    assert "22" in str(card._word_label.cget("font"))


def test_settings_page_can_build_header_and_cards(tk_root):
    class FakeLanguageManager:
        current_language = "zh"

        def translate(self, key, default=""):
            return default

        def get_available_languages(self):
            return [("zh", "中文")]

        def get_language_display(self, code):
            return "中文"

    class FakeConfig(dict):
        def get_bool(self, key, default=False):
            return bool(self.get(key, default))

        def get_int(self, key, default=0):
            return int(self.get(key, default))

        def get_default_config(self):
            return {}

        def set(self, key, value):
            self[key] = value

    class FakeApp:
        def __init__(self):
            self.root = tk_root
            self.style_manager = StyleManager("dark")
            self.language_manager = FakeLanguageManager()
            self.config = FakeConfig(
                daily_words=20,
                font_size=14,
                ai_provider="xunfei_lite",
                ai_difficulty="junior",
            )

        def update_status(self, message):
            self.status = message

        def update_progress(self, message):
            self.progress = message

    page = SettingsPage(tk_root, FakeApp())

    assert page._scroll_frame.winfo_children()


def test_favorites_page_delete_does_not_assign_dirty_flag(tk_root, tmp_path):
    style = StyleManager("dark")
    fav_file = tmp_path / "favorites.txt"
    manager = FavoritesManager(favorites_file=str(fav_file))
    fw = FavoriteWord(word="hello", pos="n.", meaning="你好")
    manager.add_word(fw)

    class FakeLang:
        def translate(self, key, default=""):
            return default

    class FakeApp:
        def __init__(self):
            self.root = tk_root
            self.style_manager = style
            self.favorites_manager = manager
            self.language_manager = FakeLang()

        def update_favorites_count(self):
            return

        def update_status(self, msg):
            return

        def update_progress(self, msg):
            return

        def show_message(self, msg, t="info"):
            return

    page = FavoritesPage(tk_root, FakeApp())
    # 选中并删除，不应抛出 AttributeError
    page._tree.selection_set("hello")
    page._delete_selected()
    assert "hello" not in [w.word for w in manager.get_all_words()]


def test_favorites_page_learn_selected_navigates_with_resume_mode(tk_root, tmp_path):
    style = StyleManager("dark")
    fav_file = tmp_path / "favorites.txt"
    manager = FavoritesManager(favorites_file=str(fav_file))
    manager.add_word(FavoriteWord(word="hello", pos="n.", meaning="你好"))

    class FakeLang:
        def translate(self, key, default=""):
            return default

    class FakeApp:
        def __init__(self):
            self.root = tk_root
            self.style_manager = style
            self.favorites_manager = manager
            self.language_manager = FakeLang()
            self.today_words = []
            self.current_word_index = -1
            self.unknown_words = []
            self.stage = ""
            self.test_mode = True
            self.navigation = None

        def navigate_to(self, page_id, **kwargs):
            self.navigation = (page_id, kwargs)

        def update_favorites_count(self):
            return

        def update_status(self, msg):
            return

        def update_progress(self, msg):
            return

        def show_message(self, msg, t="info"):
            return

    app = FakeApp()
    page = FavoritesPage(tk_root, app)
    page._tree.selection_set("hello")
    page._learn_selected()

    assert app.navigation == ("learning", {"mode": "resume"})
    assert len(app.today_words) == 1
    assert app.current_word_index == 0
    assert app.stage == "recite"
    assert app.test_mode is False


def test_page_manager_no_duplicate_history(tk_root):
    style = StyleManager("dark")

    class DummyPage(BasePage):
        page_id = "p1"

        def create_widgets(self):
            pass

        def setup_layout(self):
            pass

    class DummyPage2(BasePage):
        page_id = "p2"

        def create_widgets(self):
            pass

        def setup_layout(self):
            pass

    class FakeApp:
        def __init__(self):
            self.root = tk_root
            self.style_manager = style
            self.page_container = tk_root

    pm = PageManager(FakeApp())
    pm.register(DummyPage)
    pm.register(DummyPage2)

    assert pm.navigate_to("p1")
    # 再次导航到相同页面不应把当前页加入历史
    assert pm.navigate_to("p1")
    assert pm.get_history() == []


def test_navbar_refresh_layout_uses_compact_and_full_labels(tk_root):
    style = StyleManager("dark")
    items = [
        {"id": "home", "icon": "🏠", "title": "首页"},
        {"id": "settings", "icon": "⚙️", "title": "设置"},
    ]
    navbar = NavBar(tk_root, style_manager=style, on_navigate=lambda *_: None, items=items)

    navbar.refresh_layout(640)
    assert navbar._nav_buttons["home"].cget("text") == "🏠"

    navbar.apply_translation(lambda key, default="": {"nav.home": "Home", "nav.settings": "Settings"}.get(key, default))
    navbar.refresh_layout(900)
    assert navbar._nav_buttons["home"].cget("text") == "🏠 Home"
    assert navbar._nav_buttons["settings"].cget("text") == "⚙️ Settings"
