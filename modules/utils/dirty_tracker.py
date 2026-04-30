"""脏数据追踪器 - 用于自动保存"""
import threading
import time
from typing import Callable, Optional


class DirtyTracker:
    """
    脏数据追踪器
    
    追踪数据是否被修改，支持自动保存。
    """
    
    def __init__(
        self,
        save_callback: Callable[[], bool],
        auto_save_interval: int = 30000
    ):
        """
        初始化脏数据追踪器
        
        Args:
            save_callback: 保存回调函数
            auto_save_interval: 自动保存间隔（毫秒）
        """
        self._save_callback = save_callback
        self._auto_save_interval = auto_save_interval
        self._dirty = False
        self._auto_save_thread: Optional[threading.Thread] = None
        self._running = False
        self._lock = threading.Lock()
    
    @property
    def is_dirty(self) -> bool:
        """是否有未保存的修改"""
        with self._lock:
            return self._dirty
    
    def mark_dirty(self) -> None:
        """标记为已修改"""
        with self._lock:
            self._dirty = True
    
    def mark_clean(self) -> None:
        """标记为已保存"""
        with self._lock:
            self._dirty = False
    
    def save(self) -> bool:
        """执行保存"""
        with self._lock:
            if not self._dirty:
                return True
            
            success = self._save_callback()
            if success:
                self._dirty = False
            return success
    
    def start_auto_save(self) -> None:
        """启动自动保存线程"""
        with self._lock:
            if self._running:
                return
            
            self._running = True
        
        def auto_save_loop():
            while self._running:
                time.sleep(self._auto_save_interval / 1000)
                if self.is_dirty:
                    self.save()
        
        self._auto_save_thread = threading.Thread(
            target=auto_save_loop,
            daemon=True
        )
        self._auto_save_thread.start()
    
    def stop_auto_save(self) -> None:
        """停止自动保存线程"""
        with self._lock:
            self._running = False
    
    def force_save(self) -> bool:
        """强制保存（无论是否脏）"""
        with self._lock:
            success = self._save_callback()
            if success:
                self._dirty = False
            return success
