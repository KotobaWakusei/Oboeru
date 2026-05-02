"""背单词软件 - 多层架构版本
主程序入口"""
import os
import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox


MINIMUM_PYTHON = (3, 8)


def _ensure_working_directory():
    """确保以项目根目录作为当前工作目录启动。"""
    project_root = Path(__file__).resolve().parent
    os.chdir(project_root)
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


def main():
    """主函数"""
    _ensure_working_directory()
    from modules.utils.constants import Constants
    Constants.ensure_directories()

    from ui.core.application import Application
    app = Application()
    app.run()


if __name__ == "__main__":
    if sys.version_info < MINIMUM_PYTHON:
        message = (
            f"Python {MINIMUM_PYTHON[0]}.{MINIMUM_PYTHON[1]} 或更高版本是必需的。"
            f" 当前版本：{sys.version_info.major}.{sys.version_info.minor}."
        )
        print(message)
        sys.exit(1)

    try:
        main()
    except Exception as exc:
        try:
            from modules.logger import get_logger
            logger = get_logger()
            logger.exception(f"应用启动失败: {exc}")
        except Exception:
            pass
        try:
            messagebox.showerror("应用错误", "程序启动失败，请查看 logs/app.log 获取详细信息。")
        except Exception:
            pass
        raise
