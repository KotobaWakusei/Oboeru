"""背单词软件 - 多层架构版本
主程序入口"""
from ui.core.application import Application


def main():
    """主函数"""
    app = Application()
    app.run()


if __name__ == "__main__":
    main()
