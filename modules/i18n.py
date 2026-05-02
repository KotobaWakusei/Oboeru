"""国际化/语言管理器（轻量）

负责从 `data/locales` 目录加载语言文件（JSON），并提供查询可用语言、切换语言、获取翻译的接口。
语言文件示例结构：
{
  "language_code": "en",
  "language_name": "English",
  "strings": {
    "settings.ui_language": "Interface language",
    ...
  }
}
"""
import os
import json
from typing import Dict, Optional, Tuple, List

from .utils.constants import Constants


class LanguageManager:
    """管理本地化语言文件并提供简单的翻译查询。"""

    def __init__(self, config=None, locales_dir: Optional[str] = None):
        self._config = config
        self._locales_dir = locales_dir or os.path.join(Constants.DATA_DIR, "locales")
        os.makedirs(self._locales_dir, exist_ok=True)

        # code -> {name: str, strings: dict, file: path}
        self._languages: Dict[str, Dict] = {}
        self._current: Optional[str] = None

        # 加载现有语言
        self.reload()

        # 如果配置里有语言优先使用它
        preferred = None
        try:
            preferred = self._config.get("language") if self._config else None
        except Exception:
            preferred = None

        if preferred and preferred in self._languages:
            self.set_language(preferred, save=False)
        else:
            # 使用第一个语言作为默认（若无则 None）
            codes = list(self._languages.keys())
            if codes:
                default_code = codes[0]
                self.set_language(default_code, save=False)

    def reload(self):
        """重新加载 `locales_dir` 下的所有 .json 语言文件"""
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
                    # 忽略无法解析的文件
                    continue
        except FileNotFoundError:
            # 目录不存在则忽略（会在创建时被创建）
            pass

    def get_available_languages(self) -> List[Tuple[str, str]]:
        """返回列表：(code, display_name)"""
        return [(code, info['name']) for code, info in self._languages.items()]

    def get_language_display(self, code: str) -> Optional[str]:
        return self._languages.get(code, {}).get('name')

    def set_language(self, code: str, save: bool = True) -> bool:
        """切换当前语言；若 `save` 且配置存在则写入配置。"""
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
        """根据当前语言返回翻译；支持简单的 key（不做复杂占位）。"""
        if not self._current:
            return default or key
        strings = self._languages.get(self._current, {}).get('strings', {})
        return strings.get(key, default or key)

    def add_language_from_dict(self, code: str, name: str, strings: Dict[str, str]) -> None:
        """运行时新增语言（不会持久化）"""
        self._languages[code] = {"name": name, "strings": strings, "file": None}
