"""配置管理模块 - 优化版本"""
import os
import json
from typing import Any, Dict, Union, Tuple

from .utils import safe_save_file, Constants, DirtyTracker
from .logger import get_logger


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = Constants.DEFAULT_CONFIG_FILE):
        self._config_file = config_file
        self._config: Dict[str, Any] = {}
        
        # 使用脏数据追踪器
        self._dirty_tracker = DirtyTracker(
            save_callback=self._do_save,
            auto_save_interval=Constants.AUTO_SAVE_INTERVAL
        )
        
        self._logger = get_logger()
        self.load_config()
    
    def _do_save(self) -> bool:
        """执行保存（供 DirtyTracker 回调）"""
        return self._save_internal()
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return Constants.get_default_config()
    
    def load_config(self) -> None:
        """加载配置"""
        default_config = self.get_default_config()
        
        if os.path.exists(self._config_file):
            try:
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                
                # 合并默认配置（处理新增配置项）
                for key, value in default_config.items():
                    if key not in self._config:
                        self._config[key] = value
                
                self._logger.info(f"配置加载成功: {len(self._config)} 项")
                
            except Exception as e:
                self._logger.exception(f"加载配置失败: {e}")
                self._config = default_config.copy()
        else:
            self._config = default_config.copy()
    
    def save_config(self) -> bool:
        """保存配置"""
        return self._save_internal()
    
    def _save_internal(self) -> bool:
        """内部保存实现"""
        try:
            content = json.dumps(self._config, ensure_ascii=False, indent=2)
            success, error = safe_save_file(self._config_file, content)
            
            if success:
                self._dirty_tracker.mark_clean()
                self._logger.debug("配置保存成功")
            else:
                self._logger.error(f"配置保存失败: {error}")
            
            return success
            
        except Exception as e:
            self._logger.exception(f"保存配置失败: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        self._config[key] = value
        self._dirty_tracker.mark_dirty()
    
    def get_int(self, key: str, default: int = 0) -> int:
        """获取整数配置值"""
        try:
            return int(self._config.get(key, default))
        except (ValueError, TypeError):
            return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """获取布尔配置值"""
        return bool(self._config.get(key, default))
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """获取浮点数配置值"""
        try:
            return float(self._config.get(key, default))
        except (ValueError, TypeError):
            return default
    
    def start_auto_save(self) -> None:
        """启动自动保存"""
        self._dirty_tracker.start_auto_save()
    
    def stop_auto_save(self) -> None:
        """停止自动保存"""
        self._dirty_tracker.stop_auto_save()
    
    @property
    def dirty_flag(self) -> bool:
        """是否有未保存的修改"""
        return self._dirty_tracker.is_dirty
    
    def validate_daily_words(self, value: str) -> Tuple[bool, Union[int, str]]:
        """验证每日单词量"""
        daily_words_min = self._config.get("daily_words_min", Constants.DAILY_WORDS_MIN)
        daily_words_max = self._config.get("daily_words_max", Constants.DAILY_WORDS_MAX)
        
        try:
            num = int(value)
            if daily_words_min <= num <= daily_words_max:
                self._config["daily_words"] = num
                self._dirty_tracker.mark_dirty()
                return True, num
            else:
                return False, f"必须在 {daily_words_min}-{daily_words_max} 之间"
        except ValueError:
            return False, "请输入有效的数字"
    
    def validate_font_size(self, value: str) -> Tuple[bool, Union[int, str]]:
        """验证字体大小"""
        font_size_min = self._config.get("font_size_min", Constants.FONT_SIZE_MIN)
        font_size_max = self._config.get("font_size_max", Constants.FONT_SIZE_MAX)
        
        try:
            num = int(value)
            if font_size_min <= num <= font_size_max:
                self._config["font_size"] = num
                self._dirty_tracker.mark_dirty()
                return True, num
            else:
                return False, f"必须在 {font_size_min}-{font_size_max} 之间"
        except ValueError:
            return False, "请输入有效的数字"
    
    def get_theme_colors(self) -> Dict[str, str]:
        """获取主题颜色"""
        theme = self._config.get("theme", "default")
        return Constants.THEMES.get(theme, Constants.THEMES["default"])
    
    def get_favorites(self) -> list:
        """获取收藏列表"""
        return self._config.get("favorites", [])
    
    def set_favorites(self, favorites: list) -> None:
        """设置收藏列表"""
        self._config["favorites"] = favorites
        self._dirty_tracker.mark_dirty()
    
    def add_favorite(self, word: str) -> None:
        """添加收藏"""
        favorites = self.get_favorites()
        if word not in favorites:
            favorites.append(word)
            self.set_favorites(favorites)
    
    def remove_favorite(self, word: str) -> None:
        """移除收藏"""
        favorites = self.get_favorites()
        if word in favorites:
            favorites.remove(word)
            self.set_favorites(favorites)
    
    def is_favorite(self, word: str) -> bool:
        """检查是否已收藏"""
        return word in self.get_favorites()
    
    def __contains__(self, key: str) -> bool:
        return key in self._config
    
    def __getitem__(self, key: str) -> Any:
        return self._config[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)


if __name__ == "__main__":
    manager = ConfigManager()
    print(f"配置加载成功，共 {len(manager._config)} 项配置")
    print(f"每日单词量: {manager.get('daily_words')}")
    print(f"主题: {manager.get('theme')}")