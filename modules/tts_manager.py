"""文本转语音模块 - 高质量版本"""
import os
import subprocess
import tempfile
import threading
import asyncio
from typing import Optional, List
from concurrent.futures import ThreadPoolExecutor

from .logger import get_logger


class TTSManager:
    """文本转语音管理器 - 支持多种高质量引擎"""
    
    # 引擎优先级（从高到低）
    ENGINE_PRIORITY = ["edge_tts", "gtts", "espeak"]
    
    def __init__(self, engine: str = "auto"):
        """
        初始化TTS管理器
        
        Args:
            engine: TTS引擎，支持 "auto", "edge_tts", "gtts", "espeak"
        """
        self._engine = None
        self._current_process: Optional[subprocess.Popen] = None
        self._temp_dir = tempfile.gettempdir()
        self._lock = threading.Lock()
        self._logger = get_logger()
        self._executor = ThreadPoolExecutor(max_workers=2)
        
        # 自动选择最佳引擎
        if engine == "auto":
            self._auto_select_engine()
        else:
            self._set_engine(engine)
        
        if self._engine:
            self._logger.info(f"TTS 引擎初始化: {self._engine}")
    
    def _auto_select_engine(self) -> None:
        """自动选择最佳可用引擎"""
        for engine in self.ENGINE_PRIORITY:
            if self._check_engine_available(engine):
                self._engine = engine
                self._logger.info(f"自动选择 TTS 引擎: {engine}")
                return
        
        self._logger.warning("没有可用的 TTS 引擎")
    
    def _set_engine(self, engine: str) -> None:
        """设置指定引擎"""
        if self._check_engine_available(engine):
            self._engine = engine
        else:
            self._logger.warning(f"引擎 {engine} 不可用，尝试自动选择")
            self._auto_select_engine()
    
    def _check_engine_available(self, engine: str) -> bool:
        """检查引擎是否可用"""
        if engine == "espeak":
            return self._check_command("espeak")
        elif engine == "gtts":
            return self._check_python_module("gtts") and self._check_command("ffplay")
        elif engine == "edge_tts":
            return self._check_python_module("edge_tts") and self._check_command("ffplay")
        return False
    
    def _check_command(self, command: str) -> bool:
        """检查命令是否可用"""
        try:
            import shutil
            return shutil.which(command) is not None
        except Exception:
            return False
    
    def _check_python_module(self, module: str) -> bool:
        """检查Python模块是否可用"""
        try:
            __import__(module)
            return True
        except ImportError:
            return False
    
    def speak(self, text: str, language: str = "en") -> bool:
        """
        朗读文本
        
        Args:
            text: 要朗读的文本
            language: 语言代码，如 "en", "zh", "ja"
            
        Returns:
            bool: 是否成功开始播放
        """
        if not text or not self._engine:
            return False
        
        # 停止当前播放
        self.stop()
        
        if self._engine == "espeak":
            return self._speak_espeak(text, language)
        elif self._engine == "gtts":
            return self._speak_gtts(text, language)
        elif self._engine == "edge_tts":
            return self._speak_edge_tts(text, language)
        
        return False
    
    def _speak_edge_tts(self, text: str, language: str) -> bool:
        """使用 edge-tts 朗读（高质量）"""
        try:
            import edge_tts
            
            # 语言到语音的映射
            voice_map = {
                "en": "en-US-AriaNeural",
                "en-US": "en-US-AriaNeural",
                "en-GB": "en-GB-SoniaNeural",
                "zh": "zh-CN-XiaoxiaoNeural",
                "ja": "ja-JP-NanamiNeural",
                "ko": "ko-KR-SunHiNeural",
                "fr": "fr-FR-DeniseNeural",
                "de": "de-DE-KatjaNeural",
                "es": "es-ES-ElviraNeural",
            }
            voice = voice_map.get(language, "en-US-AriaNeural")
            
            temp_file = os.path.join(self._temp_dir, "tts_edge.mp3")
            
            def generate_and_play():
                try:
                    # 创建新的事件循环
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    async def _generate():
                        communicate = edge_tts.Communicate(text, voice)
                        await communicate.save(temp_file)
                    
                    loop.run_until_complete(_generate())
                    loop.close()
                    
                    # 播放音频
                    with self._lock:
                        try:
                            self._current_process = subprocess.Popen(
                                ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", temp_file],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE
                            )
                            self._current_process.wait()
                        except Exception as e:
                            self._logger.error(f"音频播放失败: {e}")
                        finally:
                            self._current_process = None
                            try:
                                os.remove(temp_file)
                            except:
                                pass
                except Exception as e:
                    self._logger.error(f"edge-tts 生成失败: {e}")
            
            thread = threading.Thread(target=generate_and_play, daemon=True)
            thread.start()
            return True
            
        except ImportError:
            self._logger.warning("edge-tts 未安装，请使用: pip install edge-tts")
            return False
        except Exception as e:
            self._logger.error(f"edge-tts 初始化失败: {e}")
            return False
    
    def _speak_gtts(self, text: str, language: str) -> bool:
        """使用 gtts 朗读"""
        try:
            from gtts import gTTS
            
            # gtts 语言映射
            lang_map = {
                "en": "en",
                "en-US": "en",
                "en-GB": "en-GB",
                "zh": "zh-CN",
                "ja": "ja",
                "ko": "ko",
                "fr": "fr",
                "de": "de",
                "es": "es",
            }
            gtts_lang = lang_map.get(language, "en")
            
            temp_file = os.path.join(self._temp_dir, "tts_gtts.mp3")
            
            def generate_and_play():
                try:
                    tts = gTTS(text=text, lang=gtts_lang, slow=False)
                    tts.save(temp_file)
                    
                    with self._lock:
                        try:
                            self._current_process = subprocess.Popen(
                                ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", temp_file],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE
                            )
                            self._current_process.wait()
                        except Exception as e:
                            self._logger.error(f"音频播放失败: {e}")
                        finally:
                            self._current_process = None
                            try:
                                os.remove(temp_file)
                            except:
                                pass
                except Exception as e:
                    self._logger.error(f"gtts 生成失败: {e}")
            
            thread = threading.Thread(target=generate_and_play, daemon=True)
            thread.start()
            return True
            
        except ImportError:
            self._logger.warning("gtts 未安装，请使用: pip install gtts")
            return False
        except Exception as e:
            self._logger.error(f"gtts 初始化失败: {e}")
            return False
    
    def _speak_espeak(self, text: str, language: str) -> bool:
        """使用 espeak 朗读（备用方案）"""
        try:
            lang_map = {
                "en": "en",
                "en-US": "en-us",
                "en-GB": "en-gb",
                "zh": "zh",
                "ja": "ja",
            }
            espeak_lang = lang_map.get(language, "en")
            
            def play_audio():
                with self._lock:
                    try:
                        # 优化 espeak 参数：降低语速，提高音调
                        self._current_process = subprocess.Popen(
                            ["espeak", "-v", espeak_lang, "-s", "140", "-p", "45", "-a", "150", text],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                        )
                        self._current_process.wait()
                    except Exception as e:
                        self._logger.error(f"espeak 播放失败: {e}")
                    finally:
                        self._current_process = None
            
            thread = threading.Thread(target=play_audio, daemon=True)
            thread.start()
            return True
        except Exception as e:
            self._logger.error(f"espeak 初始化失败: {e}")
            return False
    
    def speak_word(self, word: str, language: str = "en") -> bool:
        """
        朗读单词
        
        Args:
            word: 要朗读的单词
            language: 语言代码
            
        Returns:
            bool: 是否成功开始播放
        """
        return self.speak(word, language=language)
    
    def stop(self) -> None:
        """停止当前播放"""
        with self._lock:
            if self._current_process:
                try:
                    self._current_process.terminate()
                    self._current_process = None
                except Exception as e:
                    self._logger.error(f"停止播放失败: {e}")
    
    def is_available(self) -> bool:
        """检查TTS是否可用"""
        return self._engine is not None
    
    def get_available_engines(self) -> List[str]:
        """获取可用的TTS引擎"""
        engines = []
        for engine in self.ENGINE_PRIORITY:
            if self._check_engine_available(engine):
                engines.append(engine)
        return engines
    
    @property
    def engine(self) -> Optional[str]:
        return self._engine
    
    def get_engine_info(self) -> dict:
        """获取引擎信息"""
        return {
            "current": self._engine,
            "available": self.get_available_engines(),
            "quality_order": ["edge_tts (最高)", "gtts (高)", "espeak (基础)"]
        }


if __name__ == "__main__":
    print("TTS管理器测试")
    
    tts = TTSManager()
    
    print(f"可用引擎: {tts.get_available_engines()}")
    print(f"当前引擎: {tts.engine}")
    
    if tts.is_available():
        print("正在朗读测试单词...")
        tts.speak_word("hello")
        
        import time
        time.sleep(2)
        
        tts.speak("This is a test of the text to speech system.")
    else:
        print("没有可用的TTS引擎")
