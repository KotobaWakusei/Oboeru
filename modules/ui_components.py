"""UI组件模块"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Callable, List, Optional, Any


class StyleManager:
    """样式管理器"""
    
    def __init__(self, theme: str = "default", font_size: int = 14):
        self.theme = theme
        self.font_size = font_size
        self.style = ttk.Style()
        self.theme_changed_callback = None
    
    def set_theme(self, theme: str) -> None:
        """设置主题"""
        self.theme = theme
        self.setup_styles()
        if self.theme_changed_callback:
            self.theme_changed_callback(theme)
    
    def set_theme_changed_callback(self, callback) -> None:
        """设置主题变更回调"""
        self.theme_changed_callback = callback
    
    def get_theme_colors(self) -> dict:
        """获取主题颜色"""
        theme_colors = {
            "default": {
                "bg": "#ffffff", "fg": "#333333", "btn_bg": "#f0f0f0", 
                "btn_fg": "#333333", "accent": "#4CAF50", "border": "#e0e0e0",
                "success": "#4CAF50", "warning": "#FF9800", "error": "#F44336",
                "info": "#2196F3"
            },
            "dark": {
                "bg": "#1e1e1e", "fg": "#d4d4d4", "btn_bg": "#3c3c3c", 
                "btn_fg": "#ffffff", "accent": "#0e639c", "border": "#3c3c3c",
                "success": "#4CAF50", "warning": "#FF9800", "error": "#F44336",
                "info": "#2196F3"
            },
            "light": {
                "bg": "#f5f5f5", "fg": "#212121", "btn_bg": "#e0e0e0", 
                "btn_fg": "#212121", "accent": "#1976D2", "border": "#bdbdbd",
                "success": "#4CAF50", "warning": "#FF9800", "error": "#F44336",
                "info": "#2196F3"
            },
            "ocean": {
                "bg": "#e3f2fd", "fg": "#0d47a1", "btn_bg": "#90caf9", 
                "btn_fg": "#ffffff", "accent": "#1976d2", "border": "#64b5f6",
                "success": "#00c853", "warning": "#ffab00", "error": "#d50000",
                "info": "#00b0ff"
            },
            "forest": {
                "bg": "#e8f5e9", "fg": "#1b5e20", "btn_bg": "#81c784", 
                "btn_fg": "#ffffff", "accent": "#2e7d32", "border": "#66bb6a",
                "success": "#00c853", "warning": "#ffab00", "error": "#d50000",
                "info": "#00b0ff"
            },
            "sunset": {
                "bg": "#fff3e0", "fg": "#e65100", "btn_bg": "#ffab91", 
                "btn_fg": "#ffffff", "accent": "#ff6f00", "border": "#ff8a65",
                "success": "#00c853", "warning": "#ffab00", "error": "#d50000",
                "info": "#00b0ff"
            },
            "purple": {
                "bg": "#f3e5f5", "fg": "#4a148c", "btn_bg": "#ba68c8", 
                "btn_fg": "#ffffff", "accent": "#7b1fa2", "border": "#ab47bc",
                "success": "#00c853", "warning": "#ffab00", "error": "#d50000",
                "info": "#00b0ff"
            }
        }
        return theme_colors.get(self.theme, theme_colors["default"])
    
    def setup_styles(self) -> None:
        """设置样式 - Material Design风格"""
        colors = self.get_theme_colors()
        
        # 基础样式
        self.style.configure(".", 
                           background=colors["bg"], 
                           foreground=colors["fg"],
                           font=("Microsoft YaHei UI", 10))
        
        # Frame样式 - 扁平化
        self.style.configure("TFrame", 
                           background=colors["bg"])
        
        # Label样式
        self.style.configure("TLabel", 
                           background=colors["bg"], 
                           foreground=colors["fg"], 
                           font=("Microsoft YaHei UI", 10))
        
        # LabelFrame样式 - 卡片式设计
        self.style.configure("TLabelframe", 
                           background=colors["bg"],
                           borderwidth=0,
                           relief="flat")
        self.style.configure("TLabelframe.Label", 
                           background=colors["bg"], 
                           foreground=colors["accent"],
                           font=("Microsoft YaHei UI", 11, "bold"),
                           padding=(10, 5, 10, 5))
        
        # Button样式 - Material Design风格
        self.style.configure("TButton", 
                           background=colors["btn_bg"], 
                           foreground=colors["btn_fg"], 
                           font=("Microsoft YaHei UI", 10),
                           padding=(12, 6, 12, 6),
                           borderwidth=0,
                           relief="flat")
        self.style.map("TButton", 
                      background=[
                          ("active", colors["accent"]),
                          ("pressed", colors["accent"]),
                          ("disabled", "#E0E0E0")
                      ], 
                      foreground=[
                          ("active", "#ffffff"),
                          ("pressed", "#ffffff"),
                          ("disabled", "#BDBDBD")
                      ])
        
        # Entry样式
        self.style.configure("TEntry", 
                           font=("Microsoft YaHei UI", 10),
                           padding=(8, 6, 8, 6),
                           borderwidth=1,
                           relief="solid",
                           fieldbackground=colors["bg"])
        
        # Combobox样式
        self.style.configure("TCombobox", 
                           font=("Microsoft YaHei UI", 10),
                           padding=(8, 6, 8, 6),
                           fieldbackground=colors["bg"])
        
        # Progressbar样式
        self.style.configure("TProgressbar",
                           background=colors["accent"],
                           troughcolor=colors["border"],
                           borderwidth=0,
                           thickness=8)
        
        # 自定义按钮样式
        # 主按钮样式（Primary Button）
        self.style.configure("Primary.TButton", 
                           font=("Microsoft YaHei UI", 11, "bold"),
                           padding=(20, 10, 20, 10),
                           background=colors["accent"],
                           foreground="#ffffff",
                           borderwidth=0)
        self.style.map("Primary.TButton",
                      background=[("active", self._darken_color(colors["accent"], 0.1)),
                                ("pressed", self._darken_color(colors["accent"], 0.2))],
                      foreground=[("active", "#ffffff"), ("pressed", "#ffffff")])
        
        # 次要按钮样式（Secondary Button）
        self.style.configure("Secondary.TButton", 
                           font=("Microsoft YaHei UI", 10),
                           padding=(16, 8, 16, 8),
                           background=colors["btn_bg"],
                           foreground=colors["btn_fg"],
                           borderwidth=1)
        self.style.map("Secondary.TButton",
                      background=[("active", colors["accent"])],
                      foreground=[("active", "#ffffff")])
        
        # 选项按钮样式 - 更大更醒目
        self.style.configure("Option.TButton", 
                           font=("Microsoft YaHei UI", self.font_size, "bold"), 
                           padding=(30, 20, 30, 20),
                           background=colors["bg"],
                           foreground=colors["fg"],
                           borderwidth=2,
                           relief="solid")
        self.style.map("Option.TButton",
                     background=[("active", colors["accent"]), ("disabled", "#FAFAFA")],
                     foreground=[("active", "#ffffff"), ("disabled", "#BDBDBD")],
                     bordercolor=[("active", colors["accent"])])
        
        # 导航按钮样式
        self.style.configure("Nav.TButton", 
                           font=("Microsoft YaHei UI", 10),
                           padding=(16, 8, 16, 8),
                           width=12)
        
        # 收藏按钮样式
        self.style.configure("Fav.TButton", 
                           font=("Microsoft YaHei UI", 10),
                           padding=(14, 8, 14, 8),
                           width=12)
        
        # 控制按钮样式
        self.style.configure("Control.TButton", 
                           font=("Microsoft YaHei UI", 10, "bold"),
                           padding=(18, 10, 18, 10),
                           width=14)
        
        # 复习按钮样式
        self.style.configure("Review.TButton", 
                           font=("Microsoft YaHei UI", 11, "bold"), 
                           padding=(20, 12, 20, 12),
                           width=15,
                           foreground=colors["info"])
        self.style.map("Review.TButton", 
                      background=[("active", colors["info"])], 
                      foreground=[("active", "#ffffff")])
        
        # 测试按钮样式
        self.style.configure("Test.TButton", 
                           font=("Microsoft YaHei UI", 11, "bold"), 
                           padding=(20, 12, 20, 12),
                           width=15,
                           foreground=colors["success"])
        self.style.map("Test.TButton", 
                      background=[("active", colors["success"])], 
                      foreground=[("active", "#ffffff")])
        
        # 危险按钮样式
        self.style.configure("Danger.TButton",
                           font=("Microsoft YaHei UI", 10, "bold"),
                           padding=(16, 8, 16, 8),
                           foreground=colors["error"])
        self.style.map("Danger.TButton",
                      background=[("active", colors["error"])],
                      foreground=[("active", "#ffffff")])
    
    def _darken_color(self, color: str, factor: float) -> str:
        """使颜色变暗"""
        try:
            # 转換hex為RGB
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            
            # 變暗
            r = int(r * (1 - factor))
            g = int(g * (1 - factor))
            b = int(b * (1 - factor))
            
            # 轉回hex
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return color


class Dialogs:
    """对话框集合"""
    
    @staticmethod
    def show_info(parent: tk.Tk, title: str, message: str) -> None:
        """显示信息对话框"""
        messagebox.showinfo(title, message, parent=parent)
    
    @staticmethod
    def show_warning(parent: tk.Tk, title: str, message: str) -> None:
        """显示警告对话框"""
        messagebox.showwarning(title, message, parent=parent)
    
    @staticmethod
    def show_error(parent: tk.Tk, title: str, message: str) -> None:
        """显示错误对话框"""
        messagebox.showerror(title, message, parent=parent)
    
    @staticmethod
    def ask_yesno(parent: tk.Tk, title: str, message: str) -> bool:
        """显示是/否对话框"""
        return messagebox.askyesno(title, message, parent=parent)
    
    @staticmethod
    def ask_string(parent: tk.Tk, title: str, prompt: str) -> Optional[str]:
        """显示输入对话框"""
        return simpledialog.askstring(title, prompt, parent=parent)


class RecitationCompleteDialog:
    """背诵完成选择对话框"""
    
    def __init__(self, parent: tk.Tk, word_count: int,
                on_review: Callable, on_skip: Callable):
        self.parent = parent
        self.word_count = word_count
        self.on_review = on_review
        self.on_skip = on_skip
        self.dialog = None
        
        self.show()
    
    def show(self) -> None:
        """显示对话框"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("背诵完成")
        self.dialog.geometry("400x250")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        center_x = (self.dialog.winfo_screenwidth() - 400) // 2
        center_y = (self.dialog.winfo_screenheight() - 250) // 2
        self.dialog.geometry(f"+{center_x}+{center_y}")
        
        main_frame = ttk.Frame(self.dialog, padding="25")
        main_frame.grid(row=0, column=0, 
                       sticky=(tk.W, tk.E, tk.N, tk.S))
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        
        success_label = ttk.Label(
            main_frame, text="✓", 
            font=("SimHei", 48), 
            foreground="#4CAF50"
        )
        success_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        title_label = ttk.Label(
            main_frame, text="背诵完成！", 
            font=("SimHei", 18, "bold"), 
            foreground="#333333"
        )
        title_label.grid(row=1, column=0, columnspan=2, pady=(0, 5))
        
        info_label = ttk.Label(
            main_frame, 
            text=f"已完成 {self.word_count} 个单词的背诵", 
            font=("SimHei", 12), 
            foreground="#666666"
        )
        info_label.grid(row=2, column=0, columnspan=2, pady=(0, 20))
        
        choice_label = ttk.Label(
            main_frame, text="请选择下一步操作：", 
            font=("SimHei", 11), 
            foreground="#888888"
        )
        choice_label.grid(row=3, column=0, columnspan=2, pady=(0, 15))
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        review_btn = ttk.Button(
            btn_frame, text="📚 复习模式", 
            command=self._on_review_click,
            style="Review.TButton", width=15
        )
        review_btn.grid(row=0, column=0, padx=10, pady=10)
        
        test_btn = ttk.Button(
            btn_frame, text="📝 直接测试", 
            command=self._on_skip_click,
            style="Test.TButton", width=15
        )
        test_btn.grid(row=0, column=1, padx=10, pady=10)
        
        help_frame = ttk.Frame(main_frame)
        help_frame.grid(row=5, column=0, columnspan=2, pady=(15, 0))
        
        help_label1 = ttk.Label(
            help_frame, 
            text="• 复习模式：重新背诵所有单词", 
            font=("SimHei", 10), 
            foreground="#999999"
        )
        help_label1.pack(anchor=tk.W)
        
        help_label2 = ttk.Label(
            help_frame, 
            text="• 直接测试：不背诵直接答题", 
            font=("SimHei", 10), 
            foreground="#999999"
        )
        help_label2.pack(anchor=tk.W)
        
        self.dialog.bind("<Escape>", lambda e: self._on_skip_click())
        self.dialog.bind("<Return>", lambda e: self._on_skip_click())
        self.dialog.bind("<r>", lambda e: self._on_review_click())
        
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_skip_click)
    
    def _on_review_click(self) -> None:
        """复习模式按钮点击"""
        self.dialog.destroy()
        self.on_review()
    
    def _on_skip_click(self) -> None:
        """直接测试按钮点击"""
        self.dialog.destroy()
        self.on_skip()


class TestCompleteDialog:
    """测试完成选择对话框"""
    
    def __init__(self, parent: tk.Tk, remaining_count: int,
                on_continue: Callable, on_finish: Callable):
        self.parent = parent
        self.remaining_count = remaining_count
        self.on_continue = on_continue
        self.on_finish = on_finish
        self.dialog = None
        
        self.show()
    
    def show(self) -> None:
        """显示对话框"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("测试完成")
        self.dialog.geometry("400x220")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        center_x = (self.dialog.winfo_screenwidth() - 400) // 2
        center_y = (self.dialog.winfo_screenheight() - 220) // 2
        self.dialog.geometry(f"+{center_x}+{center_y}")
        
        main_frame = ttk.Frame(self.dialog, padding="25")
        main_frame.grid(row=0, column=0, 
                       sticky=(tk.W, tk.E, tk.N, tk.S))
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        
        info_label = ttk.Label(
            main_frame, 
            text=f"测试完成！还有 {self.remaining_count} 个单词需要复习", 
            font=("SimHei", 12), 
            foreground="#666666"
        )
        info_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        review_btn = ttk.Button(
            btn_frame, text="🔄 继续复习", 
            command=self._on_continue_click,
            style="Review.TButton", width=15
        )
        review_btn.grid(row=0, column=0, padx=10, pady=10)
        
        finish_btn = ttk.Button(
            btn_frame, text="✓ 完成学习", 
            command=self._on_finish_click,
            style="Test.TButton", width=15
        )
        finish_btn.grid(row=0, column=1, padx=10, pady=10)
        
        self.dialog.bind("<Escape>", lambda e: self._on_finish_click())
        self.dialog.bind("<Return>", lambda e: self._on_continue_click())
        
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_finish_click)
    
    def _on_continue_click(self) -> None:
        """继续复习按钮点击"""
        self.dialog.destroy()
        self.on_continue()
    
    def _on_finish_click(self) -> None:
        """完成学习按钮点击"""
        self.dialog.destroy()
        self.on_finish()


class AllMasteredDialog:
    """全部掌握庆祝对话框"""
    
    def __init__(self, parent: tk.Tk, on_close: Callable):
        self.parent = parent
        self.on_close = on_close
        self.dialog = None
        
        self.show()
    
    def show(self) -> None:
        """显示对话框"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("恭喜")
        self.dialog.geometry("350x180")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        center_x = (self.dialog.winfo_screenwidth() - 350) // 2
        center_y = (self.dialog.winfo_screenheight() - 180) // 2
        self.dialog.geometry(f"+{center_x}+{center_y}")
        
        main_frame = ttk.Frame(self.dialog, padding="25")
        main_frame.grid(row=0, column=0, 
                       sticky=(tk.W, tk.E, tk.N, tk.S))
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        
        trophy_label = ttk.Label(
            main_frame, text="🏆", 
            font=("SimHei", 48)
        )
        trophy_label.grid(row=0, column=0, pady=(0, 10))
        
        title_label = ttk.Label(
            main_frame, text="恭喜！所有单词都掌握了！", 
            font=("SimHei", 14, "bold"), 
            foreground="#4CAF50"
        )
        title_label.grid(row=1, column=0, pady=(0, 20))
        
        close_btn = ttk.Button(
            main_frame, text="✓ 完成学习", 
            command=self._on_close_click,
            style="Test.TButton", width=15
        )
        close_btn.grid(row=2, column=0, pady=10)
        
        self.dialog.bind("<Escape>", lambda e: self._on_close_click())
        self.dialog.bind("<Return>", lambda e: self._on_close_click())
        
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_close_click)
    
    def _on_close_click(self) -> None:
        """关闭按钮点击"""
        self.dialog.destroy()
        self.on_close()


class FavoritesManagerDialog:
    """收藏词库管理对话框"""
    
    def __init__(self, parent: tk.Tk, favorites_manager, 
                on_learn: Callable, on_delete: Callable):
        self.parent = parent
        self.favorites_manager = favorites_manager
        self.on_learn = on_learn
        self.on_delete = on_delete
        self.dialog = None
        
        self.show()
    
    def show(self) -> None:
        """显示对话框"""
        if not self.favorites_manager.favorites:
            messagebox.showinfo("提示", "收藏词库为空，请先收藏一些单词")
            return
        
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("收藏词库管理")
        self.dialog.geometry("600x400")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        main_frame = ttk.Frame(self.dialog, padding="15")
        main_frame.grid(row=0, column=0, 
                       sticky=(tk.W, tk.E, tk.N, tk.S))
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        columns = ("word", "pos", "meaning", "time", "count")
        tree = ttk.Treeview(
            main_frame, columns=columns, 
            show="headings", selectmode="browse"
        )
        
        tree.heading("word", text="单词")
        tree.heading("pos", text="词性")
        tree.heading("meaning", text="中文意思")
        tree.heading("time", text="收藏时间")
        tree.heading("count", text="学习次数")
        
        tree.column("word", width=100)
        tree.column("pos", width=80)
        tree.column("meaning", width=200)
        tree.column("time", width=120)
        tree.column("count", width=80)
        
        scrollbar = ttk.Scrollbar(
            main_frame, orient=tk.VERTICAL, 
            command=tree.yview
        )
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.grid(row=0, column=0, 
                 sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, 
                      sticky=(tk.N, tk.S))
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        for word in self.favorites_manager.favorites:
            fav_time = word.fav_time[:19].replace('T', ' ')
            tree.insert("", tk.END, values=(
                word.word,
                word.pos,
                word.meaning,
                fav_time,
                word.learn_count
            ))
        
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.grid(row=1, column=0, pady=10, sticky=tk.E)
        
        ttk.Button(
            btn_frame, text="学习选中", 
            command=lambda: self._learn_selected(tree)
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            btn_frame, text="删除选中", 
            command=lambda: self._delete_selected(tree)
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            btn_frame, text="关闭", 
            command=self.dialog.destroy
        ).pack(side=tk.RIGHT, padx=5)
    
    def _learn_selected(self, tree: ttk.Treeview) -> None:
        """学习选中的单词"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选中一个单词")
            return
        
        item = tree.item(selected[0])
        word_text = item["values"][0]
        
        self.dialog.destroy()
        self.on_learn(word_text)
    
    def _delete_selected(self, tree: ttk.Treeview) -> None:
        """删除选中的单词"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选中一个单词")
            return
        
        item = tree.item(selected[0])
        word_text = item["values"][0]
        
        if messagebox.askyesno("确认", 
                              f"确定要删除收藏的单词 '{word_text}' 吗？"):
            self.dialog.destroy()
            self.on_delete(word_text)


class FileDialogs:
    """文件对话框集合"""
    
    @staticmethod
    def ask_open_file(parent: tk.Tk, title: str = "选择文件",
                     filetypes: List[tuple] = None) -> Optional[str]:
        """打开文件对话框"""
        if filetypes is None:
            filetypes = [("文本文件", "*.txt"), ("所有文件", "*.*")]
        
        file_path = filedialog.askopenfilename(
            title=title,
            parent=parent,
            filetypes=filetypes
        )
        return file_path if file_path else None
    
    @staticmethod
    def ask_save_file(parent: tk.Tk, title: str = "保存文件",
                     defaultextension: str = ".txt",
                     filetypes: List[tuple] = None,
                     initialfile: str = "") -> Optional[str]:
        """保存文件对话框"""
        if filetypes is None:
            filetypes = [("文本文件", "*.txt"), ("所有文件", "*.*")]
        
        file_path = filedialog.asksaveasfilename(
            title=title,
            parent=parent,
            defaultextension=defaultextension,
            filetypes=filetypes,
            initialfile=initialfile
        )
        return file_path if file_path else None


if __name__ == "__main__":
    print("UI组件模块测试")
    
    root = tk.Tk()
    root.withdraw()
    
    style_manager = StyleManager()
    style_manager.setup_styles()
    
    print("样式管理器初始化成功")
    
    root.destroy()
