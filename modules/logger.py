"""日志管理模块"""
import os
import logging
from datetime import datetime
from typing import Optional


class Logger:
    """日志管理器"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, log_file: str = "logs/app.log", log_level: str = "INFO"):
        """
        初始化日志管理器
        
        Args:
            log_file: 日志文件路径
            log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        if self._initialized:
            return
        
        self.log_file = log_file
        self.logger = logging.getLogger("VocabularyTester")
        self.logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # 避免重复添加handler
        if not self.logger.handlers:
            self._setup_handlers()
        
        Logger._initialized = True
    
    def _setup_handlers(self) -> None:
        """设置日志处理器"""
        # 文件处理器
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str) -> None:
        """记录调试信息"""
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """记录一般信息"""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """记录警告信息"""
        self.logger.warning(message)
    
    def error(self, message: str, exc_info: bool = False) -> None:
        """记录错误信息"""
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str, exc_info: bool = False) -> None:
        """记录严重错误信息"""
        self.logger.critical(message, exc_info=exc_info)
    
    def exception(self, message: str) -> None:
        """记录异常信息（包含堆栈跟踪）"""
        self.logger.exception(message)
    
    def log_function_call(self, func_name: str, *args, **kwargs) -> None:
        """记录函数调用"""
        args_str = ", ".join(str(arg) for arg in args)
        kwargs_str = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        all_args = ", ".join(filter(None, [args_str, kwargs_str]))
        self.debug(f"调用函数: {func_name}({all_args})")
    
    def log_operation(self, operation: str, status: str = "成功", 
                     details: Optional[str] = None) -> None:
        """记录操作"""
        message = f"操作: {operation} - {status}"
        if details:
            message += f" - {details}"
        
        if status == "成功":
            self.info(message)
        elif status == "失败":
            self.error(message)
        else:
            self.warning(message)
    
    def clear_old_logs(self, days: int = 7) -> None:
        """清除旧日志"""
        try:
            if os.path.exists(self.log_file):
                # 检查文件修改时间
                file_time = datetime.fromtimestamp(os.path.getmtime(self.log_file))
                if (datetime.now() - file_time).days > days:
                    os.remove(self.log_file)
                    self.info(f"已删除 {days} 天前的旧日志文件")
        except Exception as e:
            self.error(f"清除旧日志失败: {e}")


# 创建全局日志实例
logger = Logger()


def get_logger() -> Logger:
    """获取全局日志实例"""
    return logger


if __name__ == "__main__":
    print("日志管理器测试")
    
    log = Logger("test.log")
    
    log.debug("这是一条调试信息")
    log.info("这是一条一般信息")
    log.warning("这是一条警告信息")
    log.error("这是一条错误信息")
    
    log.log_operation("加载词库", "成功", "加载了 100 个单词")
    log.log_operation("保存配置", "失败", "权限不足")
    
    print("测试完成，查看 test.log 文件")