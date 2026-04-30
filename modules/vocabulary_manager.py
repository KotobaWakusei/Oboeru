"""词库管理模块 - 优化版本"""
import os
import random
import difflib
import datetime
from typing import Dict, List, Optional, Any, Iterator, Union, Tuple

from .base_word import BaseWord, VocabularyWord
from .utils import LRUCache, safe_save_file, Constants
from .logger import get_logger


class VocabularyManager:
    """
    词库管理器
    
    使用 LRU 缓存优化相似词查找性能。
    """
    
    def __init__(self):
        self._vocabulary: List[VocabularyWord] = []
        self._current_index = 0
        
        # 使用 LRU 缓存替代无限制字典
        self._similar_words_cache = LRUCache(
            max_size=Constants.SIMILAR_WORDS_CACHE_SIZE
        )
        
        self._logger = get_logger()
    
    def load_from_file(self, file_path: str) -> Tuple[bool, Union[int, str]]:
        """
        从文件加载词库
        
        Returns:
            tuple: (成功标志, 单词数量或错误信息)
        """
        if not os.path.exists(file_path):
            return False, f"词库文件不存在: {file_path}"
        
        try:
            self._vocabulary = []
            self._similar_words_cache.clear()
            
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    word = VocabularyWord.from_line(line)
                    if word:
                        self._vocabulary.append(word)
            
            if not self._vocabulary:
                return False, "词库中没有有效的单词"
            
            self._logger.info(f"词库加载成功: {len(self._vocabulary)} 个单词")
            return True, len(self._vocabulary)
            
        except Exception as e:
            self._logger.exception(f"加载词库失败: {e}")
            return False, f"加载词库失败: {str(e)}"
    
    def load_from_strings(self, lines: List[str]) -> int:
        """
        从字符串列表加载词库
        
        Args:
            lines: 字符串列表，每行一个单词信息
            
        Returns:
            int: 加载的单词数量
        """
        self._vocabulary = []
        
        for line in lines:
            word = VocabularyWord.from_line(line)
            if word:
                self._vocabulary.append(word)
        
        return len(self._vocabulary)
    
    def get_words(
        self, 
        count: Optional[int] = None, 
        shuffle: bool = False
    ) -> List[VocabularyWord]:
        """
        获取单词列表
        
        Args:
            count: 获取数量，None表示全部
            shuffle: 是否打乱顺序
            
        Returns:
            List[VocabularyWord]: 单词列表
        """
        words = self._vocabulary.copy()
        
        if shuffle:
            random.shuffle(words)
        
        if count is not None:
            words = words[:min(count, len(words))]
        
        return words
    
    def get_word_by_index(self, index: int) -> Optional[VocabularyWord]:
        """根据索引获取单词"""
        if 0 <= index < len(self._vocabulary):
            return self._vocabulary[index]
        return None
    
    def get_word_by_text(self, text: str) -> Optional[VocabularyWord]:
        """根据单词文本获取单词"""
        for word in self._vocabulary:
            if word.word == text:
                return word
        return None
    
    def search_words(self, query: str) -> List[VocabularyWord]:
        """搜索单词"""
        results = []
        query_lower = query.lower()
        
        for word in self._vocabulary:
            if (query_lower in word.word.lower() or 
                query_lower in word.meaning.lower()):
                results.append(word)
        
        return results
    
    def generate_options(
        self, 
        current_word: VocabularyWord,
        count: int = 3
    ) -> List[str]:
        """
        生成测试选项
        
        Args:
            current_word: 当前单词
            count: 错误选项数量
            
        Returns:
            List[str]: 选项列表（包含正确答案）
        """
        correct = current_word.meaning
        all_distractors: List[str] = []
        
        # 添加预定义的干扰项
        all_distractors.extend(current_word.distractors)
        
        # 使用 LRU 缓存获取相似词
        word_key = current_word.word
        similar_words = self._similar_words_cache.get(word_key)
        
        if similar_words is None:
            # 缓存未命中，计算相似词
            word_list = [w.word for w in self._vocabulary if w.word != word_key]
            similar_words = difflib.get_close_matches(
                word_key, word_list, n=10, cutoff=0.6
            )
            self._similar_words_cache.set(word_key, similar_words)
        
        # 添加相似词的意思作为干扰项
        for similar_word in similar_words:
            for w in self._vocabulary:
                if w.word == similar_word:
                    all_distractors.append(w.meaning)
                    break
        
        # 添加随机干扰项
        random_distractors = [
            w.meaning for w in random.sample(
                self._vocabulary, min(20, len(self._vocabulary))
            )
        ]
        all_distractors.extend(random_distractors)
        
        # 去重并移除正确答案
        all_distractors = list(set(all_distractors))
        if correct in all_distractors:
            all_distractors.remove(correct)
        
        # 选择干扰项
        if len(all_distractors) >= count:
            distractors = random.sample(all_distractors, count)
        else:
            while len(all_distractors) < count:
                all_distractors.append(
                    random.choice(all_distractors) if all_distractors else "错误选项"
                )
            distractors = all_distractors[:count]
        
        options = [correct] + distractors
        random.shuffle(options)
        return options
    
    def clear_cache(self) -> None:
        """清除缓存"""
        self._similar_words_cache.clear()
    
    @property
    def cache_stats(self) -> dict:
        """获取缓存统计信息"""
        return self._similar_words_cache.stats
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取词库统计信息"""
        return {
            "total_words": len(self._vocabulary),
            "unique_pos": list(set(w.pos for w in self._vocabulary)),
            "has_distractors": sum(1 for w in self._vocabulary if w.has_distractors),
            "missing_distractors": sum(1 for w in self._vocabulary if not w.has_distractors),
            "cache_stats": self.cache_stats
        }
    
    def export_to_file(
        self, 
        file_path: str, 
        words: Optional[List[VocabularyWord]] = None
    ) -> bool:
        """
        导出词库到文件
        
        Args:
            file_path: 目标文件路径
            words: 要导出的单词列表，None表示全部
            
        Returns:
            bool: 是否成功
        """
        try:
            words_to_export = words or self._vocabulary
            
            lines = [
                "# 词库导出",
                f"# 导出时间: {datetime.datetime.now().isoformat()}",
                "# 格式: 单词\t词性\t中文意思\t错误选项",
                ""
            ]
            
            for word in words_to_export:
                lines.append(word.to_line())
            
            content = "\n".join(lines)
            success, error = safe_save_file(file_path, content)
            
            if success:
                self._logger.info(f"词库导出成功: {file_path}")
            else:
                self._logger.error(f"词库导出失败: {error}")
            
            return success
            
        except Exception as e:
            self._logger.exception(f"导出词库失败: {e}")
            return False
    
    def __len__(self) -> int:
        """返回单词数量"""
        return len(self._vocabulary)
    
    def __iter__(self) -> Iterator[VocabularyWord]:
        """迭代器"""
        return iter(self._vocabulary)
    
    def __getitem__(self, index: int) -> VocabularyWord:
        """支持索引访问"""
        return self._vocabulary[index]
    
    def __bool__(self) -> bool:
        """检查是否有单词"""
        return bool(self._vocabulary)


if __name__ == "__main__":
    manager = VocabularyManager()
    success, result = manager.load_from_file("data/vocabulary.txt")
    
    if success:
        print(f"词库加载成功，共 {result} 个单词")
        stats = manager.get_statistics()
        print(f"统计信息: {stats}")
    else:
        print(f"加载失败: {result}")