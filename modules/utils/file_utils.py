"""文件操作工具"""
import os
import json
import tempfile
import shutil
from typing import Any, Callable, Optional, Tuple
from contextlib import contextmanager


def safe_save_file(
    file_path: str,
    content: str,
    encoding: str = 'utf-8',
    create_backup: bool = False,
    backup_dir: Optional[str] = None
) -> Tuple[bool, str]:
    """
    安全保存文件（原子写入）
    
    使用临时文件 + 重命名策略，确保写入操作的原子性。
    
    Args:
        file_path: 目标文件路径
        content: 文件内容
        encoding: 文件编码
        create_backup: 是否创建备份
        backup_dir: 备份目录
    
    Returns:
        Tuple[bool, str]: (成功标志, 错误信息或备份路径)
    """
    try:
        # 确保目标目录存在
        dir_name = os.path.dirname(file_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        # 创建备份
        backup_path = None
        if create_backup and os.path.exists(file_path):
            backup_path = _create_backup(file_path, backup_dir)
        
        # 原子写入
        temp_file = file_path + '.tmp'
        with open(temp_file, 'w', encoding=encoding) as f:
            f.write(content)
        
        # 原子替换
        if os.path.exists(file_path):
            os.remove(file_path)
        os.rename(temp_file, file_path)
        
        return True, backup_path or ""
        
    except Exception as e:
        # 清理临时文件
        temp_file = file_path + '.tmp'
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass
        return False, str(e)


def atomic_write(
    file_path: str,
    write_func: Callable[[str], None],
    encoding: str = 'utf-8'
) -> Tuple[bool, str]:
    """
    原子写入（使用回调函数）
    
    Args:
        file_path: 目标文件路径
        write_func: 写入函数，接收文件路径作为参数
        encoding: 文件编码
    
    Returns:
        Tuple[bool, str]: (成功标志, 错误信息)
    """
    temp_file = file_path + '.tmp'
    
    try:
        write_func(temp_file)
        
        if os.path.exists(file_path):
            os.remove(file_path)
        os.rename(temp_file, file_path)
        
        return True, ""
        
    except Exception as e:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass
        return False, str(e)


def _create_backup(file_path: str, backup_dir: Optional[str] = None) -> str:
    """创建备份文件"""
    import datetime
    
    if backup_dir is None:
        backup_dir = os.path.join(os.path.dirname(file_path), 'backups')
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.basename(file_path)
    backup_path = os.path.join(backup_dir, f"{filename}.bak_{timestamp}")
    
    shutil.copy2(file_path, backup_path)
    
    return backup_path


@contextmanager
def temp_file_context(suffix: str = '.tmp', delete: bool = True):
    """
    临时文件上下文管理器
    
    确保临时文件在使用后被清理。
    """
    fd, path = tempfile.mkstemp(suffix=suffix)
    try:
        os.close(fd)
        yield path
    finally:
        if delete and os.path.exists(path):
            os.remove(path)


def ensure_directory(file_path: str) -> bool:
    """确保文件所在目录存在"""
    try:
        dir_path = os.path.dirname(file_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        return True
    except Exception:
        return False
