"""AI 例句生成模块 - 支持多语言和版本控制"""
import json
import threading
import urllib.request
import urllib.error
from typing import Optional, Callable, Dict, Any, Tuple, List
from collections import deque
from concurrent.futures import ThreadPoolExecutor
import re

from .utils import TTLCache, Constants
from .logger import get_logger


# 语言配置映射
LANGUAGE_CONFIGS = {
    "en": {
        "name": "英语",
        "prompt_template": """You are an English teaching assistant. Generate an example sentence for the English word "{word}" (meaning: {meaning}).

CRITICAL REQUIREMENTS:
1. The example sentence MUST be written in ENGLISH (not Chinese or other languages)
2. The sentence MUST contain the exact word "{word}" - this is mandatory
3. Difficulty level: {difficulty_name} ({vocab_level})
4. Sentence characteristics: {description}
5. Maximum length: {max_words} words
6. The vocabulary and grammar must match {difficulty_name} level

Output format (strictly follow this):
Sentence: [Your English example sentence containing "{word}"]
Translation: [Chinese translation of the sentence]""",
    },
    "zh": {
        "name": "中文",
        "prompt_template": """你是一个中文教学助手。请为中文词语"{word}"（意思：{meaning}）生成一个例句。

【必须遵守的要求】：
1. 例句必须用中文编写（不是英文或其他语言）
2. 例句必须包含词语"{word}"
3. 例句应该自然、实用、符合日常表达习惯

请严格按以下格式回复：
例句: [包含"{word}"的中文例句]
拼音: [拼音]""",
    },
    "ja": {
        "name": "日语",
        "prompt_template": """あなたは日本語教師です。日本語の単語「{word}」（意味：{meaning}）の例文を作成してください。

【必須要件】：
1. 例文は必ず日本語で書いてください（中国語や英語ではありません）
2. 例文には必ず「{word}」を含めてください
3. 自然で実用的な日本語表現を使用してください

以下の形式で回答してください：
例文: [「{word}」を含む日本語の例文]
読み: [ふりがな]
訳: [中国語訳]""",
    },
    "ko": {
        "name": "韩语",
        "prompt_template": """당신은 한국어 교사입니다. 한국어 단어 "{word}"(의미: {meaning})의 예문을 만들어 주세요.

【필수 요구사항】：
1. 예문은 반드시 한국어로 작성해 주세요 (중국어나 영어가 아닙니다)
2. 예문에는 반드시 "{word}"가 포함되어야 합니다
3. 자연스럽고 실용적인 한국어 표현을 사용하세요

다음 형식으로 답변해 주세요:
예문: ["{word}"가 포함된 한국어 예문]
발음: [발음]
번역: [중국어 번역]""",
    },
    "fr": {
        "name": "法语",
        "prompt_template": """Vous êtes un assistant d'enseignement du français. Générez une phrase d'exemple pour le mot français "{word}" (signification : {meaning}).

EXIGENCES CRITIQUES :
1. La phrase d'exemple DOIT être écrite en FRANÇAIS (pas en chinois ou autre langue)
2. La phrase DOIT contenir le mot exact "{word}"
3. La phrase doit être naturelle et pratique

Répondez sous ce format :
Exemple : [Votre phrase française contenant "{word}"]
Traduction : [traduction chinoise]""",
    },
    "de": {
        "name": "德语",
        "prompt_template": """Sie sind ein Deutschlehrer. Erstellen Sie einen Beispielsatz für das deutsche Wort "{word}" (Bedeutung: {meaning}).

KRITISCHE ANFORDERUNGEN:
1. Der Beispielsatz MUSS auf DEUTSCH geschrieben werden (nicht Chinesisch oder andere Sprachen)
2. Der Satz MUSS das genaue Wort "{word}" enthalten
3. Der Satz sollte natürlich und praktisch sein

Antworten Sie in folgendem Format:
Beispiel: [Ihr deutscher Satz mit "{word}"]
Übersetzung: [chinesische Übersetzung]""",
    },
    "es": {
        "name": "西班牙语",
        "prompt_template": """Eres un profesor de español. Genera una oración de ejemplo para la palabra española "{word}" (significado: {meaning}).

REQUISITOS CRÍTICOS:
1. La oración de ejemplo DEBE estar escrita en ESPAÑOL (no en chino u otro idioma)
2. La oración DEBE contener la palabra exacta "{word}"
3. La oración debe ser natural y práctica

Responda en el siguiente formato:
Ejemplo: [Su oración en español que contiene "{word}"]
Traducción: [traducción al chino]""",
    },
}


def detect_language(word: str, meaning: str = "") -> str:
    """
    检测单词语言
    
    Args:
        word: 单词文本
        meaning: 中文意思
        
    Returns:
        str: 语言代码 (en, zh, ja, ko, fr, de, es)
    """
    if not word:
        return "en"
    
    # 检测中文
    if re.search(r'[\u4e00-\u9fff]', word):
        return "zh"
    
    # 检测日文（平假名/片假名）
    if re.search(r'[\u3040-\u309f\u30a0-\u30ff]', word):
        return "ja"
    
    # 检测韩文
    if re.search(r'[\uac00-\ud7af]', word):
        return "ko"
    
    # 检测法文特殊字符
    french_chars = set('àâäéèêëïîôùûüÿçœæ')
    if any(c in french_chars for c in word.lower()):
        return "fr"
    
    # 检测德文特殊字符
    german_chars = set('äöüß')
    if any(c in german_chars for c in word.lower()):
        return "de"
    
    # 检测西班牙文特殊字符
    spanish_chars = set('ñáéíóúü¿¡')
    if any(c in spanish_chars for c in word.lower()):
        return "es"
    
    # 默认英语
    return "en"


class AIManager:
    """
    AI 例句生成管理器
    
    支持：
    - 多种 OpenAI 兼容 API（讯飞星火、OpenAI、DeepSeek 等）
    - 自定义 API 端点
    - 多语言例句生成
    - 例句难度等级
    - 预加载队列
    - 请求版本控制（防竞态）
    """
    
    def __init__(self):
        self._api_key: str = ""
        self._api_url: str = ""
        self._model: str = ""
        self._provider: str = ""
        self._difficulty: str = "junior"
        self._enabled: bool = False
        self._timeout: int = Constants.AI_DEFAULT_TIMEOUT
        self._max_tokens: int = Constants.AI_MAX_TOKENS
        
        # 使用 TTL 缓存
        self._cache = TTLCache(
            max_size=Constants.AI_SENTENCE_CACHE_SIZE,
            ttl_seconds=Constants.AI_CACHE_TTL_SECONDS
        )
        
        self._loading: bool = False
        self._lock = threading.Lock()
        
        # 请求版本控制 - 用于防止竞态条件
        self._request_version: int = 0
        
        # 预加载相关
        self._preload_queue: deque = deque(maxlen=20)
        self._preload_lock = threading.Lock()
        self._executor: Optional[ThreadPoolExecutor] = None
        self._max_preload_workers: int = 3
        
        self._logger = get_logger()
    
    def configure(
        self,
        api_key: str,
        provider: str = "xunfei_lite",
        custom_url: str = "",
        custom_model: str = "",
        difficulty: str = "junior",
        enabled: bool = True,
        timeout: int = Constants.AI_DEFAULT_TIMEOUT,
        **kwargs
    ) -> None:
        """配置 AI 参数"""
        # 如果配置发生变化，先关闭现有线程池
        old_enabled = self._enabled
        old_api_key = self._api_key
        old_api_url = self._api_url
        
        self._api_key = api_key.strip() if api_key else ""
        self._provider = provider
        self._difficulty = difficulty
        self._timeout = timeout
        
        # 根据 provider 设置 API URL 和模型
        if provider == "custom" and custom_url:
            self._api_url = custom_url
            self._model = custom_model
        elif provider in Constants.AI_PROVIDERS:
            provider_config = Constants.AI_PROVIDERS[provider]
            self._api_url = provider_config["api_url"]
            self._model = provider_config["model"]
        else:
            # 默认使用讯飞星火 Lite
            self._api_url = Constants.AI_PROVIDERS["xunfei_lite"]["api_url"]
            self._model = Constants.AI_PROVIDERS["xunfei_lite"]["model"]
        
        self._enabled = enabled and bool(self._api_key) and bool(self._api_url)
        
        # 如果之前启用了但现在禁用了，或者API配置发生变化，关闭现有线程池
        if (old_enabled and not self._enabled) or \
           (old_enabled and (old_api_key != self._api_key or old_api_url != self._api_url)):
            self.shutdown()
        
        # 初始化线程池（如果需要）
        if self._enabled and self._executor is None:
            self._executor = ThreadPoolExecutor(
                max_workers=self._max_preload_workers,
                thread_name_prefix="ai_preload"
            )
            self._logger.info(f"AI 线程池已初始化，最大工作线程数: {self._max_preload_workers}")
        
        if self._enabled:
            provider_name = Constants.AI_PROVIDERS.get(provider, {}).get("name", provider)
            self._logger.info(f"AI 已启用: {provider_name}, 模型: {self._model}")
        elif old_enabled and not self._enabled:
            self._logger.info("AI 已禁用")
    
    def is_available(self) -> bool:
        """检查 AI 功能是否可用"""
        return self._enabled and bool(self._api_key) and bool(self._api_url)
    
    def get_difficulty_config(self) -> Dict[str, Any]:
        """获取当前难度配置"""
        return Constants.AI_DIFFICULTY_LEVELS.get(
            self._difficulty, 
            Constants.AI_DIFFICULTY_LEVELS["junior"]
        )
    
    def generate_sentence(
        self,
        word: str,
        meaning: str,
        callback: Optional[Callable[[bool, str], None]] = None,
        version: Optional[int] = None,
        language: Optional[str] = None
    ) -> int:
        """
        生成例句（异步，带版本控制和多语言支持）
        
        Args:
            word: 单词
            meaning: 意思
            callback: 回调函数 (success, result)
            version: 请求版本号，用于防止竞态
            language: 指定语言，None则自动检测
            
        Returns:
            int: 当前请求版本号
        """
        if not self.is_available():
            if callback:
                callback(False, "AI 功能未配置")
            return self._request_version
        
        # 自动检测语言
        if language is None:
            language = detect_language(word, meaning)
        
        # 获取当前版本号
        with self._lock:
            current_version = self._request_version
            if version is None:
                version = current_version
        
        # 检查缓存（包含难度和语言）
        cache_key = f"{word}_{meaning}_{self._difficulty}_{language}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            self._logger.debug(f"AI 缓存命中: {word} ({language})")
            if callback:
                callback(True, cached)
            return current_version
        
        # 在后台线程中执行
        thread = threading.Thread(
            target=self._generate_in_thread,
            args=(word, meaning, cache_key, callback, version, language),
            daemon=True
        )
        thread.start()
        
        return current_version
    
    def _generate_in_thread(
        self,
        word: str,
        meaning: str,
        cache_key: str,
        callback: Optional[Callable[[bool, str], None]],
        request_version: int,
        language: str
    ) -> None:
        """在后台线程中生成例句（带版本检查）"""
        try:
            with self._lock:
                self._loading = True
            
            prompt = self._build_prompt(word, meaning, language)
            result = self._call_api(prompt)
            
            # 版本检查：如果版本已过期，不回调（防竞态）
            with self._lock:
                is_expired = request_version < self._request_version
            
            if result and "error" not in result:
                sentence = self._parse_response(result)
                if sentence:
                    self._cache.set(cache_key, sentence)
                    self._logger.debug(f"AI 生成成功: {word} ({language})")
                    # 只有版本没过期才回调
                    if callback and not is_expired:
                        callback(True, sentence)
                    elif is_expired:
                        self._logger.debug(f"跳过过期回调: {word} (version={request_version})")
                    return
                else:
                    error_msg = "无法解析 AI 响应"
            elif result:
                error_msg = result.get("error", "API 调用失败")
            else:
                error_msg = "API 调用失败"
            
            self._logger.warning(f"AI 生成失败: {word} - {error_msg}")
            if callback and not is_expired:
                callback(False, error_msg)
                
        except Exception as e:
            self._logger.exception(f"AI 生成异常: {e}")
            if callback:
                callback(False, f"生成例句时出错: {str(e)}")
        finally:
            with self._lock:
                self._loading = False
    
    def increment_version(self) -> int:
        """递增请求版本号（切换单词时调用）"""
        with self._lock:
            self._request_version += 1
            new_version = self._request_version
            self._logger.debug(f"请求版本更新为: {new_version}")
        return new_version
    
    @property
    def current_version(self) -> int:
        """获取当前请求版本号"""
        with self._lock:
            return self._request_version
    
    def preload_sentences_async(
        self,
        words: List[Tuple[str, str]],
        on_complete: Optional[Callable[[int, int], None]] = None
    ) -> None:
        """
        异步批量预加载例句（不阻塞UI）
        
        Args:
            words: [(单词, 意思), ...] 列表
            on_complete: 完成回调 (成功数, 总数)
        """
        if not self.is_available() or not words:
            if on_complete:
                on_complete(0, len(words))
            return
        
        def process_in_background():
            success_count = 0
            total = min(len(words), 10)
            
            for word, meaning in words[:total]:
                cache_key = f"{word}_{meaning}_{self._difficulty}_{detect_language(word, meaning)}"
                
                # 先检查缓存
                cached = self._cache.get(cache_key)
                if cached is not None:
                    success_count += 1
                    continue
                
                # 生成例句
                try:
                    language = detect_language(word, meaning)
                    prompt = self._build_prompt(word, meaning, language)
                    result = self._call_api(prompt)
                    
                    if result and "error" not in result:
                        sentence = self._parse_response(result)
                        if sentence:
                            self._cache.set(cache_key, sentence)
                            success_count += 1
                            self._logger.debug(f"预加载成功: {word}")
                except Exception as e:
                    self._logger.debug(f"预加载失败: {word} - {e}")
            
            if on_complete:
                on_complete(success_count, total)
        
        # 在后台线程中运行，不阻塞主线程
        thread = threading.Thread(target=process_in_background, daemon=True)
        thread.start()
    
    def preload_for_session(self, words_list: List[Any]) -> None:
        """为学习会话异步预加载例句（不阻塞）"""
        words = [(w.word, w.meaning) for w in words_list[:15]]
        if words:
            self.preload_sentences_async(
                words,
                on_complete=lambda s, t: self._logger.info(f"预加载完成: {s}/{t} 个例句")
            )
    
    def cancel_pending_requests(self) -> None:
        """取消所有待处理请求（通过递增版本实现）"""
        with self._lock:
            self._request_version += 100
            self._logger.info("已取消所有待处理 AI 请求")
    
    def shutdown(self) -> None:
        """关闭 AI 管理器，清理资源"""
        with self._lock:
            if self._executor is not None:
                self._executor.shutdown(wait=False)
                self._executor = None
                self._logger.info("AI 线程池已关闭")
            self._loading = False
            self._request_version = 0
            self._cache.clear()
    
    def _build_prompt(self, word: str, meaning: str, language: str = "en") -> str:
        """根据语言和难度构建提示词"""
        lang_config = LANGUAGE_CONFIGS.get(language, LANGUAGE_CONFIGS["en"])
        difficulty_config = self.get_difficulty_config()
        
        template = lang_config["prompt_template"]
        
        # 对于非英语语言，使用简化模板
        if language == "en":
            return template.format(
                word=word,
                meaning=meaning,
                difficulty_name=difficulty_config['name'],
                vocab_level=difficulty_config['vocab_level'],
                description=difficulty_config['description'],
                max_words=difficulty_config['max_words']
            )
        else:
            # 其他语言使用简单模板
            return template.format(
                word=word,
                meaning=meaning
            )
    
    def _call_api(self, prompt: str) -> Optional[Dict[str, Any]]:
        """调用 AI API"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._api_key}"
            }
            
            data = {
                "model": self._model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": self._max_tokens,
                "temperature": 0.7
            }
            
            request = urllib.request.Request(
                self._api_url,
                data=json.dumps(data).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                result = response.read().decode("utf-8")
                return json.loads(result)
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else ""
            self._logger.error(f"AI API HTTP 错误: {e.code} - {error_body}")
            return {"error": f"HTTP {e.code}: {error_body}"}
        except urllib.error.URLError as e:
            self._logger.error(f"AI API 网络错误: {e.reason}")
            return {"error": f"网络错误: {str(e.reason)}"}
        except Exception as e:
            self._logger.exception(f"AI API 调用异常: {e}")
            return {"error": str(e)}
    
    def _parse_response(self, response: Dict[str, Any]) -> Optional[str]:
        """解析 API 响应"""
        try:
            if "choices" in response:
                content = response["choices"][0]["message"]["content"]
                return content.strip()
            return None
        except (KeyError, IndexError, TypeError):
            return None
    
    def generate_sentence_sync(self, word: str, meaning: str, language: Optional[str] = None) -> Tuple[bool, str]:
        """同步生成例句（阻塞调用）"""
        if not self.is_available():
            return False, "AI 功能未配置"
        
        if language is None:
            language = detect_language(word, meaning)
        
        cache_key = f"{word}_{meaning}_{self._difficulty}_{language}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return True, cached
        
        try:
            prompt = self._build_prompt(word, meaning, language)
            result = self._call_api(prompt)
            
            if result and "error" not in result:
                sentence = self._parse_response(result)
                if sentence:
                    self._cache.set(cache_key, sentence)
                    return True, sentence
            
            return False, result.get("error", "生成失败") if result else "API 调用失败"
            
        except Exception as e:
            self._logger.exception(f"同步生成例句异常: {e}")
            return False, str(e)
    
    def is_loading(self) -> bool:
        """检查是否正在加载"""
        with self._lock:
            return self._loading
    
    def clear_cache(self) -> None:
        """清除缓存"""
        self._cache.clear()
        self._logger.debug("AI 缓存已清除")
    
    @property
    def cache_stats(self) -> dict:
        """获取缓存统计信息"""
        return self._cache.stats
    
    @property
    def model(self) -> str:
        return self._model
    
    @property
    def provider(self) -> str:
        return self._provider
    
    @property
    def difficulty(self) -> str:
        return self._difficulty
    
    @property
    def enabled(self) -> bool:
        return self._enabled


if __name__ == "__main__":
    manager = AIManager()
    print(f"AI 可用: {manager.is_available()}")
    print(f"支持语言: {list(LANGUAGE_CONFIGS.keys())}")
    print(f"可用难度等级: {list(Constants.AI_DIFFICULTY_LEVELS.keys())}")
    print(f"可用提供商: {list(Constants.AI_PROVIDERS.keys())}")
    print(f"缓存统计: {manager.cache_stats}")
    
    # 测试语言检测
    test_words = [
        ("apple", "", "en"),
        ("你好", "", "zh"),
        ("こんにちは", "", "ja"),
        ("안녕하세요", "", "ko"),
        ("bonjour", "", "fr"),
    ]
    for word, _, expected in test_words:
        detected = detect_language(word)
        status = "✓" if detected == expected else "✗"
        print(f"{status} '{word}' -> {detected} (期望: {expected})")
