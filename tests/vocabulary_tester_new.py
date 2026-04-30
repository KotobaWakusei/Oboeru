"""背单词软件 - 分层架构版本
主程序入口"""
import tkinter as tk

from ui.controllers.main_controller import MainController


if __name__ == "__main__":
    root = tk.Tk()
    app = MainController(root)
    app.root.mainloop()
