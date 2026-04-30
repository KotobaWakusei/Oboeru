"""单词基类 - 提供公共属性和方法"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class BaseWord:
    """
    单词基类
    
    提供单词的基本属性和序列化方法。
    """
    
    word: str
    pos: str  # 词性
    meaning: str
    distractors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseWord':
        """从字典创建"""
        return cls(
            word=data.get("word", ""),
            pos=data.get("pos", ""),
            meaning=data.get("meaning", ""),
            distractors=data.get("distractors", [])
        )
    
    def to_line(self, include_distractors: bool = True) -> str:
        """
        转换为行格式（用于文件存储）
        
        格式: 单词\t词性\t中文意思\t错误选项
        """
        line = f"{self.word}\t{self.pos}\t{self.meaning}"
        if include_distractors and self.distractors:
            line += f"\t{','.join(self.distractors)}"
        return line
    
    @classmethod
    def from_line(cls, line: str) -> Optional['BaseWord']:
        """从行格式解析"""
        line = line.strip()
        if not line or line.startswith('#'):
            return None
        
        parts = line.split('\t')
        if len(parts) < 3:
            return None
        
        return cls(
            word=parts[0].strip(),
            pos=parts[1].strip(),
            meaning=parts[2].strip(),
            distractors=parts[3].split(',') if len(parts) > 3 and parts[3] else []
        )
    
    @property
    def has_distractors(self) -> bool:
        """是否有干扰项"""
        return bool(self.distractors)
    
    def __str__(self) -> str:
        return f"{self.word} [{self.pos}] {self.meaning}"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.word!r}, {self.pos!r}, {self.meaning!r})"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseWord):
            return NotImplemented
        return self.word == other.word
    
    def __hash__(self) -> int:
        return hash(self.word)


class VocabularyWord(BaseWord):
    """词库单词类（用于学习）"""
    pass


@dataclass
class FavoriteWord(BaseWord):
    """
    收藏单词类
    
    扩展基础单词，添加收藏相关属性。
    """
    
    fav_time: str = ""
    learn_count: int = 0
    mastered: bool = False
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.fav_time:
            from datetime import datetime
            self.fav_time = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = super().to_dict()
        data.update({
            "fav_time": self.fav_time,
            "learn_count": self.learn_count,
            "mastered": self.mastered
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FavoriteWord':
        """从字典创建"""
        return cls(
            word=data.get("word", ""),
            pos=data.get("pos", ""),
            meaning=data.get("meaning", ""),
            distractors=data.get("distractors", []),
            fav_time=data.get("fav_time", ""),
            learn_count=data.get("learn_count", 0),
            mastered=data.get("mastered", False)
        )
    
    def to_line(self, include_distractors: bool = True) -> str:
        """
        转换为行格式
        
        格式: 单词\t词性\t中文意思\t错误选项\t收藏时间\t学习次数\t已掌握
        """
        line = super().to_line(include_distractors)
        line += f"\t{self.fav_time}"
        line += f"\t{self.learn_count}"
        line += f"\t{self.mastered}"
        return line
    
    @classmethod
    def from_line(cls, line: str) -> Optional['FavoriteWord']:
        """从行格式解析"""
        line = line.strip()
        if not line or line.startswith('#'):
            return None
        
        parts = line.split('\t')
        if len(parts) < 3:
            return None
        
        return cls(
            word=parts[0].strip(),
            pos=parts[1].strip(),
            meaning=parts[2].strip(),
            distractors=parts[3].split(',') if len(parts) > 3 and parts[3] else [],
            fav_time=parts[4].strip() if len(parts) > 4 else "",
            learn_count=int(parts[5]) if len(parts) > 5 and parts[5].isdigit() else 0,
            mastered=parts[6].strip() == "True" if len(parts) > 6 else False
        )
    
    @classmethod
    def from_vocabulary_word(
        cls, 
        vocab_word: BaseWord,
        fav_time: Optional[str] = None
    ) -> 'FavoriteWord':
        """从 VocabularyWord 创建"""
        return cls(
            word=vocab_word.word,
            pos=vocab_word.pos,
            meaning=vocab_word.meaning,
            distractors=vocab_word.distractors,
            fav_time=fav_time or ""
        )
    
    def increment_learn_count(self) -> None:
        """增加学习次数"""
        self.learn_count += 1
