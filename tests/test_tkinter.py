import tkinter as tk

import pytest


def test_tkinter_can_create_and_destroy_root():
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tkinter display is not available: {exc}")

    try:
        root.title("测试")
        root.geometry("300x200")
        label = tk.Label(root, text="Tkinter测试成功！")
        label.pack(pady=50)
        root.update_idletasks()
    finally:
        root.destroy()
