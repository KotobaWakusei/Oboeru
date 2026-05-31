"""国际化/语言管理器（增强版）

支持：
- 从 data/locales 加载 JSON 语言文件
- 系统语言自动检测（locale.getdefaultlocale）
- 回退链：当前语言 → en → key 本身
- 运行时动态新增语言
"""
import os
import json
import locale as std_locale
from typing import Dict, Optional, Tuple, List

from .utils.constants import Constants


FALLBACK_LANGUAGE = "en"


class LanguageManager:
    """管理本地化语言文件并提供翻译查询。"""

    def __init__(self, config=None, locales_dir: Optional[str] = None):
        self._config = config
        self._locales_dir = locales_dir or os.path.join(Constants.DATA_DIR, "locales")
        os.makedirs(self._locales_dir, exist_ok=True)

        # code -> {name: str, strings: dict, file: path}
        self._languages: Dict[str, Dict] = {}
        self._current: Optional[str] = None

        self.reload()

        preferred = None
        try:
            preferred = self._config.get("language") if self._config else None
        except Exception:
            preferred = None

        if preferred and preferred in self._languages:
            self.set_language(preferred, save=False)
        else:
            # 尝试自动检测系统语言
            sys_lang = self._detect_system_language()
            if sys_lang and sys_lang in self._languages:
                self.set_language(sys_lang, save=False)
            else:
                codes = list(self._languages.keys())
                if codes:
                    self.set_language(codes[0], save=False)

    @staticmethod
    def _detect_system_language() -> Optional[str]:
        """检测系统语言，返回语言代码（如 'zh', 'en', 'ja'）。"""
        try:
            code, _ = std_locale.getdefaultlocale()
            if code:
                lang = code.split("_")[0].lower()
                return lang
        except Exception:
            pass
        return None

    def reload(self):
        """重新加载 locales_dir 下的所有 .json 语言文件"""
        self._languages.clear()
        try:
            for fname in sorted(os.listdir(self._locales_dir)):
                if not fname.lower().endswith('.json'):
                    continue
                path = os.path.join(self._locales_dir, fname)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    code = data.get('language_code') or os.path.splitext(fname)[0]
                    name = data.get('language_name') or code
                    strings = data.get('strings', {}) or {}
                    self._languages[code] = {"name": name, "strings": strings, "file": path}
                except Exception:
                    continue
        except FileNotFoundError:
            pass

    def get_available_languages(self) -> List[Tuple[str, str]]:
        return [(code, info['name']) for code, info in self._languages.items()]

    def get_language_display(self, code: str) -> Optional[str]:
        return self._languages.get(code, {}).get('name')

    def set_language(self, code: str, save: bool = True) -> bool:
        if code not in self._languages:
            return False
        self._current = code
        if self._config and save:
            try:
                self._config.set('language', code)
            except Exception:
                pass
        return True

    @property
    def current_language(self) -> Optional[str]:
        return self._current

    def translate(self, key: str, default: Optional[str] = None) -> str:
        """返回翻译，回退链：当前语言 → en → key/defalut"""
        if not self._languages:
            return default or key

        # 1. 当前语言查找
        if self._current:
            strings = self._languages.get(self._current, {}).get('strings', {})
            val = strings.get(key)
            if val is not None:
                return val

        # 2. 回退到英语
        if self._current != FALLBACK_LANGUAGE:
            strings = self._languages.get(FALLBACK_LANGUAGE, {}).get('strings', {})
            val = strings.get(key)
            if val is not None:
                return val

        # 3. 返回默认值
        return default or key

    def add_language_from_dict(self, code: str, name: str, strings: Dict[str, str]) -> None:
        """运行时新增语言（不会持久化到磁盘）"""
        self._languages[code] = {"name": name, "strings": strings, "file": None}
