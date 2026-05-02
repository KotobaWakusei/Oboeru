"""应用常量配置"""
from pathlib import Path
from typing import Dict, Any


class Constants:
    """应用常量"""

    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    DATA_DIR = str(PROJECT_ROOT / "data")
    LOG_DIR = str(PROJECT_ROOT / "logs")
    BACKUP_DIR = str(PROJECT_ROOT / "backups")
    LOCALES_DIR = str(PROJECT_ROOT / "data" / "locales")

    # 自动保存间隔（毫秒）
    AUTO_SAVE_INTERVAL = 30000  # 30秒
    
    # 缓存配置
    SIMILAR_WORDS_CACHE_SIZE = 100
    AI_SENTENCE_CACHE_SIZE = 200
    AI_CACHE_TTL_SECONDS = 3600  # 1小时
    
    # 备份配置
    MAX_BACKUPS = 5
    
    # 默认文件路径
    DEFAULT_CONFIG_FILE = str(PROJECT_ROOT / "data" / "config.json")
    DEFAULT_VOCAB_FILE = str(PROJECT_ROOT / "data" / "vocabulary.txt")
    DEFAULT_FAVORITES_FILE = str(PROJECT_ROOT / "data" / "favorites.txt")
    DEFAULT_PROGRESS_FILE = str(PROJECT_ROOT / "data" / "study_progress.json")
    DEFAULT_LOG_FILE = str(PROJECT_ROOT / "logs" / "app.log")

    @classmethod
    def ensure_directories(cls) -> None:
        """确保必要的项目目录存在。"""
        for path in [cls.DATA_DIR, cls.LOG_DIR, cls.BACKUP_DIR, cls.LOCALES_DIR]:
            Path(path).mkdir(parents=True, exist_ok=True)
    
    # 学习配置
    DAILY_WORDS_MIN = 1
    DAILY_WORDS_MAX = 100
    DAILY_WORDS_DEFAULT = 20
    
    # 字体配置
    FONT_SIZE_MIN = 12
    FONT_SIZE_MAX = 24
    FONT_SIZE_DEFAULT = 14
    
    # 测试延迟（毫秒）
    TEST_DELAY = 1500
    WRONG_DELAY = 2000
    
    # AI 配置
    AI_DEFAULT_TIMEOUT = 30
    AI_MAX_TOKENS = 512
    
    # 例句难度等级
    AI_DIFFICULTY_LEVELS: Dict[str, Dict[str, Any]] = {
        "primary": {
            "name": "小学",
            "description": "简单词汇，短句，基础语法",
            "max_words": 10,
            "vocab_level": "小学水平"
        },
        "junior": {
            "name": "初中",
            "description": "常用词汇，中等长度句子",
            "max_words": 15,
            "vocab_level": "初中水平"
        },
        "senior": {
            "name": "高中",
            "description": "较复杂词汇，长句，多种句型",
            "max_words": 20,
            "vocab_level": "高中水平"
        },
        "cet4": {
            "name": "四级",
            "description": "四级词汇，复杂句型，学术表达",
            "max_words": 25,
            "vocab_level": "大学英语四级水平"
        },
        "cet6": {
            "name": "六级",
            "description": "六级词汇，高级表达，学术写作风格",
            "max_words": 30,
            "vocab_level": "大学英语六级水平"
        },
        "advanced": {
            "name": "高级",
            "description": "高级词汇，复杂句式，地道表达",
            "max_words": 35,
            "vocab_level": "高级英语水平"
        }
    }
    
    # 预设 API 提供商（OpenAI 兼容接口）
    AI_PROVIDERS: Dict[str, Dict[str, Any]] = {
        "xunfei_lite": {
            "name": "讯飞星火 Lite",
            "api_url": "https://spark-api-open.xf-yun.com/v1/chat/completions",
            "model": "lite",
            "description": "讯飞星火免费版",
            "api_key_hint": "控制台获取 APIPassword"
        },
        "xunfei_pro": {
            "name": "讯飞星火 Pro",
            "api_url": "https://spark-api-open.xf-yun.com/v1/chat/completions",
            "model": "generalv3",
            "description": "讯飞星火专业版",
            "api_key_hint": "控制台获取 APIPassword"
        },
        "openai": {
            "name": "OpenAI",
            "api_url": "https://api.openai.com/v1/chat/completions",
            "model": "gpt-3.5-turbo",
            "description": "OpenAI GPT 模型",
            "api_key_hint": "sk-xxx 格式的 API Key"
        },
        "deepseek": {
            "name": "DeepSeek",
            "api_url": "https://api.deepseek.com/v1/chat/completions",
            "model": "deepseek-chat",
            "description": "DeepSeek 大模型",
            "api_key_hint": "DeepSeek API Key"
        },
        "moonshot": {
            "name": "Moonshot",
            "api_url": "https://api.moonshot.cn/v1/chat/completions",
            "model": "moonshot-v1-8k",
            "description": "月之暗面 Kimi",
            "api_key_hint": "Moonshot API Key"
        },
        "zhipu": {
            "name": "智谱 AI",
            "api_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
            "model": "glm-4-flash",
            "description": "智谱 GLM 模型",
            "api_key_hint": "智谱 API Key"
        },
        "custom": {
            "name": "自定义",
            "api_url": "",
            "model": "",
            "description": "自定义 OpenAI 兼容 API",
            "api_key_hint": "输入您的 API Key"
        }
    }
    
    # 间隔重复算法 - 复习间隔（天）
    REVIEW_INTERVALS: Dict[int, int] = {
        0: 1,      # 1天
        1: 3,      # 3天
        2: 7,      # 1周
        3: 14,     # 2周
        4: 30,     # 1个月
        5: 90      # 3个月
    }
    
    # 主题颜色
    THEMES: Dict[str, Dict[str, Any]] = {
        "default": {
            "name": "默认主题",
            "bg_primary": "#1a1a2e",
            "bg_secondary": "#16213e",
            "bg_card": "#0f3460",
            "fg_primary": "#e8e8e8",
            "fg_secondary": "#a0a0a0",
            "accent": "#e94560",
            "accent_hover": "#ff6b6b",
            "success": "#00d9a5",
            "warning": "#ffc107",
            "error": "#ff4757",
            "border": "#2d4263",
        },
    }
    
    @classmethod
    def get_default_config(cls) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "daily_words": cls.DAILY_WORDS_DEFAULT,
            "daily_words_min": cls.DAILY_WORDS_MIN,
            "daily_words_max": cls.DAILY_WORDS_MAX,
            "vocab_file": cls.DEFAULT_VOCAB_FILE,
            "favorites": [],
            "theme": "default",
            "font_size": cls.FONT_SIZE_DEFAULT,
            "font_size_min": cls.FONT_SIZE_MIN,
            "font_size_max": cls.FONT_SIZE_MAX,
            "show_pinyin": True,
            "auto_play_sound": False,
            "confirm_before_exit": True,
            "shuffle_words": True,
            "show_progress_bar": True,
            "remember_window_size": True,
            "auto_save_config": True,
            "test_delay": cls.TEST_DELAY,
            "wrong_delay": cls.WRONG_DELAY,
            "favorites_font_size": cls.FONT_SIZE_DEFAULT,
            "favorites_sort": "time",
            "favorites_show_time": True,
            "favorites_auto_backup": True,
            "ai_enabled": False,
            "ai_api_key": "",
            "ai_timeout": cls.AI_DEFAULT_TIMEOUT,
            "ai_show_sentence": True,
            "ai_difficulty": "junior",
            "ai_provider": "xunfei_lite",
            "ai_custom_url": "",
            "ai_custom_model": "",
            "language": "zh",
            "review_words_count": 3,  # 背诵阶段显示的最近单词数量
        }
