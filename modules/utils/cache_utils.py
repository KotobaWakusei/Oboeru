"""缓存工具"""
from collections import OrderedDict
from typing import Any, Callable, Optional
from functools import wraps


class LRUCache:
    """
    LRU (Least Recently Used) 缓存实现
    
    自动淘汰最久未使用的缓存项，防止内存无限增长。
    """
    
    def __init__(self, max_size: int = 100):
        """
        初始化 LRU 缓存
        
        Args:
            max_size: 最大缓存数量
        """
        self._max_size = max_size
        self._cache: OrderedDict = OrderedDict()
        self._hits = 0
        self._misses = 0
    
    def get(self, key: Any) -> Optional[Any]:
        """
        获取缓存值
        
        如果存在，将其移到队尾（最近使用）
        """
        if key in self._cache:
            self._hits += 1
            self._cache.move_to_end(key)
            return self._cache[key]
        self._misses += 1
        return None
    
    def set(self, key: Any, value: Any) -> None:
        """
        设置缓存值
        
        如果超出容量，淘汰最久未使用的项
        """
        if key in self._cache:
            self._cache.move_to_end(key)
        else:
            if len(self._cache) >= self._max_size:
                self._cache.popitem(last=False)
        self._cache[key] = value
    
    def contains(self, key: Any) -> bool:
        """检查键是否存在"""
        return key in self._cache
    
    def remove(self, key: Any) -> bool:
        """移除缓存项"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
    
    @property
    def size(self) -> int:
        """当前缓存大小"""
        return len(self._cache)
    
    @property
    def max_size(self) -> int:
        """最大缓存大小"""
        return self._max_size
    
    @max_size.setter
    def max_size(self, value: int) -> None:
        """设置最大缓存大小"""
        self._max_size = value
        # 如果当前大小超过新限制，淘汰多余项
        while len(self._cache) > self._max_size:
            self._cache.popitem(last=False)
    
    @property
    def hit_rate(self) -> float:
        """缓存命中率"""
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0
    
    @property
    def stats(self) -> dict:
        """缓存统计信息"""
        return {
            "size": self.size,
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self.hit_rate
        }
    
    def __contains__(self, key: Any) -> bool:
        return self.contains(key)
    
    def __len__(self) -> int:
        return self.size
    
    def __getitem__(self, key: Any) -> Any:
        value = self.get(key)
        if value is None:
            raise KeyError(key)
        return value
    
    def __setitem__(self, key: Any, value: Any) -> None:
        self.set(key, value)


def lru_cache_method(max_size: int = 100):
    """
    方法级 LRU 缓存装饰器
    
    为实例方法提供缓存功能，缓存在实例上。
    
    Args:
        max_size: 最大缓存数量
    
    Usage:
        class MyClass:
            @lru_cache_method(max_size=50)
            def expensive_computation(self, key):
                return some_expensive_operation(key)
    """
    def decorator(func: Callable) -> Callable:
        cache_attr = f'_lru_cache_{func.__name__}'
        
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # 在实例上创建缓存
            if not hasattr(self, cache_attr):
                setattr(self, cache_attr, LRUCache(max_size))
            
            cache = getattr(self, cache_attr)
            
            # 使用 args + tuple(sorted(kwargs.items())) 作为键
            cache_key = args + tuple(sorted(kwargs.items()))
            
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            result = func(self, *args, **kwargs)
            cache.set(cache_key, result)
            return result
        
        # 添加缓存管理方法
        def clear_cache(self):
            if hasattr(self, cache_attr):
                getattr(self, cache_attr).clear()
        
        def get_cache_stats(self):
            if hasattr(self, cache_attr):
                return getattr(self, cache_attr).stats
            return None
        
        wrapper.clear_cache = clear_cache
        wrapper.get_cache_stats = get_cache_stats
        
        return wrapper
    
    return decorator


class TTLCache(LRUCache):
    """
    带 TTL (Time To Live) 的 LRU 缓存
    
    缓存项在指定时间后自动过期。
    """
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        super().__init__(max_size)
        self._ttl = ttl_seconds
    
    def get(self, key: Any) -> Optional[Any]:
        import time
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self._ttl:
                self._hits += 1
                self._cache.move_to_end(key)
                return value
            else:
                # 过期，移除
                del self._cache[key]
        self._misses += 1
        return None
    
    def set(self, key: Any, value: Any) -> None:
        import time
        super().set(key, (value, time.time()))
