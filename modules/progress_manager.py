"""学习进度管理模块 - 优化版本"""
import os
import json
import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict

from .utils import safe_save_file, Constants, DirtyTracker
from .logger import get_logger


@dataclass
class StudySession:
    """学习会话"""
    date: str
    words_studied: int
    words_mastered: int
    words_reviewed: int
    study_duration: int  # 秒
    accuracy_rate: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StudySession':
        return cls(**data)


@dataclass
class WordProgress:
    """单词学习进度"""
    word: str
    total_study_count: int      # 总学习次数（包括测试）
    correct_count: int          # 正确次数
    wrong_count: int             # 错误次数
    last_study_date: str        # 最后学习日期
    mastery_level: int           # 掌握等级 0-5
    next_review_date: str       # 下次复习日期
    review_count: int = 0       # 有效复习次数（>=80%准确率）
    is_mastered: bool = False   # 是否已掌握
    
    # 掌握判定阈值
    MASTERY_LEVEL_THRESHOLD = 4       # 掌握等级阈值
    MIN_REVIEW_COUNT = 2             # 最小复习次数
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WordProgress':
        return cls(**data)
    
    @property
    def accuracy_rate(self) -> float:
        """准确率"""
        total = self.total_study_count
        if total == 0:
            return 0.0
        return self.correct_count / total
    
    def check_and_update_mastery(self) -> bool:
        """
        检查并更新掌握状态
        
        掌握条件（双条件判定）：
        1. mastery_level >= MASTERY_LEVEL_THRESHOLD (4)
        2. review_count >= MIN_REVIEW_COUNT (2)
        
        Returns:
            bool: 是否刚刚达到掌握状态
        """
        was_mastered = self.is_mastered
        
        # 双条件判定：掌握等级 + 复习次数
        new_mastered = (
            self.mastery_level >= self.MASTERY_LEVEL_THRESHOLD and 
            self.review_count >= self.MIN_REVIEW_COUNT
        )
        
        self.is_mastered = new_mastered
        
        # 返回是否刚达到掌握
        return new_mastered and not was_mastered


class ProgressManager:
    """学习进度管理器"""
    
    def __init__(self, progress_file: str = Constants.DEFAULT_PROGRESS_FILE):
        self._progress_file = progress_file
        self._study_sessions: List[StudySession] = []
        self._word_progress: Dict[str, WordProgress] = {}
        
        self._current_session: Optional[StudySession] = None
        self._session_start_time: Optional[float] = None
        self._session_correct_count = 0
        self._session_wrong_count = 0
        
        self._logger = get_logger()
        self.load_progress()
    
    @property
    def study_sessions(self) -> List[StudySession]:
        """获取学习会话列表"""
        return self._study_sessions
    
    @property
    def word_progress(self) -> Dict[str, WordProgress]:
        """获取单词进度字典"""
        return self._word_progress
    
    @property
    def session_start_time(self) -> Optional[float]:
        """获取当前会话开始时间"""
        return self._session_start_time
    
    @property
    def mastered_count(self) -> int:
        """已掌握词数（双条件判定：掌握等级>=4 且 复习次数>=2）"""
        return sum(
            1 for p in self._word_progress.values()
            if p.is_mastered
        )
    
    @property
    def learning_count(self) -> int:
        """学习中词数（总学习 - 已掌握）"""
        return max(0, len(self._word_progress) - self.mastered_count)
    
    @property
    def new_words_count(self) -> int:
        """新学习词数（只学过1次的单词）"""
        return sum(
            1 for p in self._word_progress.values()
            if p.total_study_count == 1
        )
    
    @property
    def reviewing_words(self) -> List[str]:
        """需要复习的单词列表"""
        now = datetime.datetime.now().isoformat()[:10]
        return [
            word for word, progress in self._word_progress.items()
            if progress.next_review_date[:10] <= now and not progress.is_mastered
        ]
    
    def load_progress(self) -> None:
        """加载学习进度"""
        if not os.path.exists(self._progress_file):
            return
        
        try:
            with open(self._progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._study_sessions = [
                StudySession.from_dict(s)
                for s in data.get("study_sessions", [])
            ]
            
            word_progress_data = data.get("word_progress", {})
            self._word_progress = {
                word: WordProgress.from_dict(prog)
                for word, prog in word_progress_data.items()
            }
            
            self._logger.info(f"学习进度加载成功: {len(self._study_sessions)} 会话, {len(self._word_progress)} 单词")
            
        except Exception as e:
            self._logger.exception(f"加载学习进度失败: {e}")
            self._study_sessions = []
            self._word_progress = {}
    
    def save_progress(self) -> bool:
        """保存学习进度"""
        try:
            data = {
                "study_sessions": [s.to_dict() for s in self._study_sessions],
                "word_progress": {
                    word: prog.to_dict()
                    for word, prog in self._word_progress.items()
                }
            }
            
            content = json.dumps(data, ensure_ascii=False, indent=2)
            success, error = safe_save_file(self._progress_file, content)
            
            if success:
                self._logger.debug("学习进度保存成功")
            else:
                self._logger.error(f"学习进度保存失败: {error}")
            
            return success
            
        except Exception as e:
            self._logger.exception(f"保存学习进度失败: {e}")
            return False
    
    def start_session(self) -> None:
        """开始学习会话"""
        self._session_start_time = datetime.datetime.now().timestamp()
        self._session_correct_count = 0
        self._session_wrong_count = 0
        self._current_session = None
        self._logger.debug("学习会话开始")
    
    def end_session(self, words_studied: int, words_reviewed: int) -> None:
        """结束学习会话"""
        if self._session_start_time is None:
            return
        
        duration = int(datetime.datetime.now().timestamp() - self._session_start_time)
        total_attempts = self._session_correct_count + self._session_wrong_count
        accuracy = self._session_correct_count / total_attempts if total_attempts > 0 else 0.0
        
        self._current_session = StudySession(
            date=datetime.datetime.now().isoformat(),
            words_studied=words_studied,
            words_mastered=self._session_correct_count,
            words_reviewed=words_reviewed,
            study_duration=duration,
            accuracy_rate=accuracy
        )
        
        self._study_sessions.append(self._current_session)
        self.save_progress()
        
        self._logger.info(f"学习会话结束: {words_studied} 单词, {accuracy:.1%} 准确率")
        
        # 重置会话
        self._session_start_time = None
        self._session_correct_count = 0
        self._session_wrong_count = 0
    
    def record_answer(self, word: str, is_correct: bool) -> None:
        """记录答题结果"""
        now = datetime.datetime.now().isoformat()
        
        if word not in self._word_progress:
            self._word_progress[word] = WordProgress(
                word=word,
                total_study_count=0,
                correct_count=0,
                wrong_count=0,
                last_study_date=now,
                mastery_level=0,
                next_review_date=now
            )
        
        progress = self._word_progress[word]
        progress.total_study_count += 1
        progress.last_study_date = now
        
        if is_correct:
            progress.correct_count += 1
            self._session_correct_count += 1
            
            # 提升掌握等级（最高5）
            if progress.mastery_level < 5:
                progress.mastery_level += 1
            
            # 检查是否是有效复习（非首次学习且准确率>=80%）
            if progress.total_study_count > 1:
                current_accuracy = progress.correct_count / progress.total_study_count
                if current_accuracy >= 0.8:
                    progress.review_count += 1
        else:
            progress.wrong_count += 1
            self._session_wrong_count += 1
            
            # 降低掌握等级（最低0）
            if progress.mastery_level > 0:
                progress.mastery_level = max(0, progress.mastery_level - 1)
        
        # 更新掌握状态
        just_mastered = progress.check_and_update_mastery()
        if just_mastered:
            self._logger.info(f"单词 '{word}' 已达到掌握状态！")
        
        progress.next_review_date = self._calculate_next_review_date(
            progress.mastery_level
        )
    
    def _calculate_next_review_date(self, mastery_level: int) -> str:
        """计算下次复习时间"""
        now = datetime.datetime.now()
        days = Constants.REVIEW_INTERVALS.get(mastery_level, 1)
        next_date = now + datetime.timedelta(days=days)
        return next_date.isoformat()
    
    def get_due_words(self, all_words: List[str], include_last_n: int = 0) -> List[str]:
        """获取需要复习的单词。

        参数:
            all_words: 所有词库中的单词文本列表
            include_last_n: 强制包含最近学习的 N 个单词（优先未掌握的）

        返回:
            List[str]: 需要复习的单词文本列表（去重）
        """
        now = datetime.datetime.now()
        due_set = set()

        for word in all_words:
            if word not in self._word_progress:
                # 未学习过的也视为待处理（方便复习/学习）
                due_set.add(word)
            else:
                progress = self._word_progress[word]
                try:
                    next_review = datetime.datetime.fromisoformat(progress.next_review_date)
                    if now >= next_review and not progress.is_mastered:
                        due_set.add(word)
                except Exception:
                    # 解析错误时保守处理为待复习
                    due_set.add(word)

        # 包含最近学习的 N 个单词（优先未掌握的）
        if include_last_n and include_last_n > 0:
            # 从已有进度中按最后学习时间排序（降序）
            entries = [p for p in self._word_progress.values() if p.word in all_words]
            try:
                entries_sorted = sorted(
                    entries,
                    key=lambda p: datetime.datetime.fromisoformat(p.last_study_date) if p.last_study_date else datetime.datetime.min,
                    reverse=True
                )
            except Exception:
                # 回退到字符串排序（iso 格式可行）
                entries_sorted = sorted(entries, key=lambda p: p.last_study_date or "", reverse=True)

            added = 0
            for prog in entries_sorted:
                if added >= include_last_n:
                    break
                # 如果已掌握则可跳过（避免重复复习掌握词），但若用户希望包含可做配置调整
                if not prog.is_mastered and prog.word in all_words:
                    if prog.word not in due_set:
                        due_set.add(prog.word)
                        added += 1

        return list(due_set)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取学习统计"""
        if not self._study_sessions:
            return {
                "total_sessions": 0,
                "total_words_studied": 0,
                "total_study_time": 0,
                "average_accuracy": 0.0,
                "words_in_progress": len(self._word_progress),
                "mastered_words": 0,
                "daily_stats": {}
            }
        
        total_words_studied = sum(s.words_studied for s in self._study_sessions)
        total_study_time = sum(s.study_duration for s in self._study_sessions)
        avg_accuracy = sum(s.accuracy_rate for s in self._study_sessions) / len(self._study_sessions)
        mastered_count = sum(1 for p in self._word_progress.values() if p.mastery_level >= 4)
        
        daily_stats = defaultdict(lambda: {
            "sessions": 0,
            "words": 0,
            "accuracy": 0.0
        })
        
        for session in self._study_sessions:
            date = session.date[:10]
            daily_stats[date]["sessions"] += 1
            daily_stats[date]["words"] += session.words_studied
            daily_stats[date]["accuracy"] += session.accuracy_rate
        
        
        for date, stats in daily_stats.items():
            if stats["sessions"] > 0:
                stats["accuracy"] /= stats["sessions"]
        
        
        return {
            "total_sessions": len(self._study_sessions),
            "total_words_studied": total_words_studied,
            "total_study_time": total_study_time,
            "average_accuracy": avg_accuracy,
            "words_in_progress": len(self._word_progress),
            "mastered_words": mastered_count,
            "daily_stats": dict(daily_stats)
        }
    
    def get_word_statistics(self, word: str) -> Optional[Dict[str, Any]]:
        """获取特定单词的统计"""
        if word not in self._word_progress:
            return None
        
        progress = self._word_progress[word]
        return {
            "word": progress.word,
            "total_study_count": progress.total_study_count,
            "correct_count": progress.correct_count,
            "wrong_count": progress.wrong_count,
            "accuracy_rate": progress.accuracy_rate,
            "mastery_level": progress.mastery_level,
            "last_study_date": progress.last_study_date,
            "next_review_date": progress.next_review_date
        }
    
    def clear_all_progress(self) -> None:
        """清除所有进度"""
        self._study_sessions = []
        self._word_progress = {}
        self.save_progress()
        self._logger.info("学习进度已清除")
    
    def export_progress(self, file_path: str) -> bool:
        """导出学习进度"""
        try:
            stats = self.get_statistics()
            
            lines = [
                "# 学习进度报告",
                f"# 导出时间: {datetime.datetime.now().isoformat()}",
                "",
                "## 总体统计",
                f"- 总学习会话: {stats['total_sessions']}",
                f"- 总学习单词数: {stats['total_words_studied']}",
                f"- 总学习时间: {stats['total_study_time']}秒",
                f"- 平均准确率: {stats['average_accuracy']:.2%}",
                f"- 掌握单词数: {stats['mastered_words']}",
                "",
                "## 每日统计"
            ]
            
            for date, daily in stats['daily_stats'].items():
                lines.append(f"{date}: {daily['sessions']}会话, {daily['words']}单词, {daily['accuracy']:.2%}准确率")
            
            lines.append("")
            lines.append("## 单词详情")
            
            for word, progress in sorted(self._word_progress.items()):
                lines.append(
                    f"{word}: 学习{progress.total_study_count}次, "
                    f"正确{progress.correct_count}次, "
                    f"掌握等级{progress.mastery_level}/5"
                )
            
            content = "\n".join(lines)
            success, error = safe_save_file(file_path, content)
            
            if success:
                self._logger.info(f"学习进度导出成功: {file_path}")
            else:
                self._logger.error(f"学习进度导出失败: {error}")
            
            return success
            
        except Exception as e:
            self._logger.exception(f"导出进度失败: {e}")
            return False


if __name__ == "__main__":
    print("学习进度管理器测试")
    
    manager = ProgressManager()
    
    print(f"历史会话数: {len(manager._study_sessions)}")
    print(f"跟踪单词数: {len(manager._word_progress)}")
    
    stats = manager.get_statistics()
    print(f"统计信息: {stats}")
    
    manager.start_session()
    manager.record_answer("test", True)
    manager.record_answer("test", False)
    manager.end_session(1, 0)
    
    print("测试完成")
