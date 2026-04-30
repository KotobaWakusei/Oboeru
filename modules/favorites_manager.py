"""收藏管理模块 - 优化版本"""
import os
import shutil
import datetime
import threading
import time
from typing import Dict, List, Optional, Any, Iterator
from collections import OrderedDict

from .base_word import FavoriteWord, BaseWord
from .utils import safe_save_file, Constants, DirtyTracker
from .logger import get_logger


class FavoritesManager:
    """
    收藏管理器
    
    使用 OrderedDict 同时支持快速查找和有序存储，
    避免重复存储同一数据。
    """
    
    def __init__(
        self,
        favorites_file: str = Constants.DEFAULT_FAVORITES_FILE,
        backup_dir: str = Constants.BACKUP_DIR,
        max_backups: int = Constants.MAX_BACKUPS
    ):
        self._favorites_file = favorites_file
        self._backup_dir = backup_dir
        self._max_backups = max_backups
        
        # 使用 OrderedDict 存储收藏（key=单词, value=FavoriteWord）
        # 既支持 O(1) 查找，又保持插入顺序
        self._favorites: OrderedDict[str, FavoriteWord] = OrderedDict()
        
        # 脏数据追踪器
        self._dirty_tracker = DirtyTracker(
            save_callback=self._do_save,
            auto_save_interval=Constants.AUTO_SAVE_INTERVAL
        )
        
        self._logger = get_logger()
        self.load_favorites()
    
    def _do_save(self) -> bool:
        """执行保存（供 DirtyTracker 回调）"""
        return self._save_internal(create_backup=False)
    
    def load_favorites(self) -> None:
        """加载收藏词库"""
        if not os.path.exists(self._favorites_file):
            return
        
        try:
            self._favorites.clear()
            
            with open(self._favorites_file, 'r', encoding='utf-8') as f:
                for line in f:
                    word = FavoriteWord.from_line(line)
                    if word and word.word:
                        self._favorites[word.word] = word
            
            self._logger.info(f"收藏加载成功: {len(self._favorites)} 个")
            
        except Exception as e:
            self._logger.exception(f"加载收藏失败: {e}")
            self._favorites.clear()
    
    def save_favorites(self, create_backup: bool = True) -> bool:
        """
        保存收藏词库
        
        Args:
            create_backup: 是否创建备份
            
        Returns:
            bool: 是否成功
        """
        return self._save_internal(create_backup)
    
    
    def _save_internal(self, create_backup: bool = True) -> bool:
        """内部保存实现"""
        try:
            # 创建备份
            if create_backup:
                self._create_backup()
            
            # 构建文件内容
            lines = [
                "# 收藏词库文件",
                f"# 创建时间: {datetime.datetime.now().isoformat()}",
                "# 格式: 单词\t词性\t中文意思\t错误选项\t收藏时间\t学习次数\t已掌握",
                ""
            ]
            
            for word in self._favorites.values():
                lines.append(word.to_line())
            
            content = "\n".join(lines)
            success, error = safe_save_file(self._favorites_file, content)
            
            if success:
                self._dirty_tracker.mark_clean()
                self._logger.debug("收藏保存成功")
            else:
                self._logger.error(f"收藏保存失败: {error}")
            
            return success
            
        except Exception as e:
            self._logger.exception(f"保存收藏失败: {e}")
            return False
    
    def _create_backup(self) -> bool:
        """创建备份"""
        try:
            if not os.path.exists(self._favorites_file):
                return True
            
            if not os.path.exists(self._backup_dir):
                os.makedirs(self._backup_dir)
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(
                self._backup_dir,
                f"favorites_backup_{timestamp}.txt"
            )
            
            shutil.copy2(self._favorites_file, backup_file)
            
            # 清理旧备份
            self._cleanup_old_backups()
            
            return True
            
        except Exception as e:
            self._logger.error(f"创建备份失败: {e}")
            return False
    
    def _cleanup_old_backups(self) -> None:
        """清理旧备份"""
        try:
            if not os.path.exists(self._backup_dir):
                return
            
            backup_files = sorted([
                f for f in os.listdir(self._backup_dir)
                if f.startswith("favorites_backup_")
            ], reverse=True)
            
            while len(backup_files) > self._max_backups:
                old_backup = os.path.join(self._backup_dir, backup_files[-1])
                if os.path.exists(old_backup):
                    os.remove(old_backup)
                backup_files.pop()
                
        except Exception as e:
            self._logger.error(f"清理备份失败: {e}")
    
    def restore_from_backup(self) -> bool:
        """从最新备份恢复"""
        try:
            if not os.path.exists(self._backup_dir):
                return False
            
            backup_files = sorted([
                f for f in os.listdir(self._backup_dir)
                if f.startswith("favorites_backup_")
            ], reverse=True)
            
            if not backup_files:
                return False
            
            latest_backup = os.path.join(self._backup_dir, backup_files[0])
            if os.path.exists(latest_backup):
                shutil.copy2(latest_backup, self._favorites_file)
                self.load_favorites()
                return True
            
            return False
            
        except Exception as e:
            self._logger.error(f"从备份恢复失败: {e}")
            return False
    
    def start_auto_save(self) -> None:
        """启动自动保存"""
        self._dirty_tracker.start_auto_save()
    
    def stop_auto_save(self) -> None:
        """停止自动保存"""
        self._dirty_tracker.stop_auto_save()
    
    def add_word(self, word: FavoriteWord) -> bool:
        """
        添加收藏单词
        
        Args:
            word: 收藏单词对象
            
        Returns:
            bool: 是否成功添加（False表示已存在）
        """
        if word.word in self._favorites:
            return False
        
        self._favorites[word.word] = word
        self._dirty_tracker.mark_dirty()
        return True
    
    def add_from_vocabulary(
        self,
        vocab_word: BaseWord,
        fav_time: Optional[str] = None
    ) -> bool:
        """
        从 VocabularyWord 添加收藏
        
        Args:
            vocab_word: VocabularyWord 对象
            fav_time: 收藏时间
            
        Returns:
            bool: 是否成功添加
        """
        word = FavoriteWord.from_vocabulary_word(vocab_word, fav_time)
        return self.add_word(word)
    
    def remove_word(self, word_key: str) -> bool:
        """
        移除收藏单词
        
        Args:
            word_key: 单词文本
            
        Returns:
            bool: 是否成功移除
        """
        if word_key not in self._favorites:
            return False
        
        del self._favorites[word_key]
        self._dirty_tracker.mark_dirty()
        return True
    
    def is_favorite(self, word_key: str) -> bool:
        """检查是否已收藏"""
        return word_key in self._favorites
    
    def get_word(self, word_key: str) -> Optional[FavoriteWord]:
        """获取收藏单词"""
        return self._favorites.get(word_key)
    
    def get_all_words(self) -> List[FavoriteWord]:
        """获取所有收藏单词"""
        return list(self._favorites.values())
    
    def increment_learn_count(self, word_key: str) -> bool:
        """增加学习次数"""
        word = self._favorites.get(word_key)
        if word:
            word.increment_learn_count()
            self._dirty_tracker.mark_dirty()
            return True
        return False
    
    def set_mastered(self, word_key: str, mastered: bool = True) -> bool:
        """设置掌握状态"""
        word = self._favorites.get(word_key)
        if word:
            word.mastered = mastered
            self._dirty_tracker.mark_dirty()
            return True
        return False
    
    def clear_all(self) -> bool:
        """清空所有收藏"""
        self._favorites.clear()
        self._dirty_tracker.mark_dirty()
        return True
    
    @property
    def dirty_flag(self) -> bool:
        """是否有未保存的修改"""
        return self._dirty_tracker.is_dirty
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        words = list(self._favorites.values())
        
        return {
            "total_count": len(words),
            "mastered_count": sum(1 for w in words if w.mastered),
            "unmastered_count": sum(1 for w in words if not w.mastered),
            "total_learn_sessions": sum(w.learn_count for w in words),
            "oldest_fav": min((w.fav_time for w in words), default=None),
            "newest_fav": max((w.fav_time for w in words), default=None)
        }
    
    def sort_by_time(self, reverse: bool = True) -> List[FavoriteWord]:
        """按收藏时间排序"""
        return sorted(
            self._favorites.values(),
            key=lambda w: w.fav_time,
            reverse=reverse
        )
    
    def sort_by_learn_count(self, reverse: bool = True) -> List[FavoriteWord]:
        """按学习次数排序"""
        return sorted(
            self._favorites.values(),
            key=lambda w: w.learn_count,
            reverse=reverse
        )
    
    def sort_by_word(self, reverse: bool = False) -> List[FavoriteWord]:
        """按单词字母排序"""
        return sorted(
            self._favorites.values(),
            key=lambda w: w.word.lower(),
            reverse=reverse
        )
    
    def export_to_file(
        self,
        file_path: str,
        words: Optional[List[FavoriteWord]] = None
    ) -> bool:
        """导出收藏词库到文件"""
        try:
            words_to_export = words or list(self._favorites.values())
            
            lines = [
                "# 我的收藏词库",
                f"# 导出时间: {datetime.datetime.now().isoformat()}",
                "# 格式: 单词\t词性\t中文意思\t错误选项",
                ""
            ]
            
            for word in words_to_export:
                lines.append(word.to_line(include_distractors=True))
            
            content = "\n".join(lines)
            success, error = safe_save_file(file_path, content)
            
            if success:
                self._logger.info(f"收藏导出成功: {file_path}")
            else:
                self._logger.error(f"收藏导出失败: {error}")
            
            return success
            
        except Exception as e:
            self._logger.exception(f"导出收藏失败: {e}")
            return False
    
    def __len__(self) -> int:
        """返回收藏数量"""
        return len(self._favorites)
    
    def __iter__(self) -> Iterator[FavoriteWord]:
        """迭代器"""
        return iter(self._favorites.values())
    
    def __contains__(self, word_key: str) -> bool:
        """支持 in 操作符"""
        return word_key in self._favorites
    
    def __bool__(self) -> bool:
        """检查是否有收藏"""
        return bool(self._favorites)


if __name__ == "__main__":
    manager = FavoritesManager()
    print(f"收藏加载成功，共 {len(manager)} 个收藏")
    stats = manager.get_statistics()
    print(f"统计信息: {stats}")