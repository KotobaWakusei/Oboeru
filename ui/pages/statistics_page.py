"""统计页面 - 学习统计"""
import tkinter as tk
from tkinter import ttk
from ui.core.base_page import BasePage
from datetime import datetime


class StatisticsPage(BasePage):
    """统计页面 - 支持滚动和自适应布局"""
    
    page_id = "statistics"
    page_title = "统计"
    page_icon = "📊"
    
    def create_widgets(self):
        """创建组件"""
        colors = self.colors
        
        # 配置页面网格
        self._container.columnconfigure(0, weight=1)
        self._container.rowconfigure(0, weight=1)
        
        # 创建可滚动区域
        self._create_scrollable_area()
        
        self._create_header()
        self._create_summary_stats()
        self._create_chart_area()
        self._create_recent_sessions()
        
        # 延迟绑定滚轮事件
        self.after(100, self._rebind_mousewheel)
    
    def _create_scrollable_area(self):
        """创建可滚动区域"""
        colors = self.colors
        
        # 外层容器
        self._outer_frame = tk.Frame(self._container, bg=colors["bg_primary"])
        self._outer_frame.grid(row=0, column=0, sticky="nsew")
        self._outer_frame.columnconfigure(0, weight=1)
        self._outer_frame.rowconfigure(0, weight=1)
        
        # 创建 Canvas
        self._canvas = tk.Canvas(
            self._outer_frame,
            bg=colors["bg_primary"],
            highlightthickness=0
        )
        
        self._scrollbar = ttk.Scrollbar(
            self._outer_frame,
            orient=tk.VERTICAL,
            command=self._canvas.yview
        )
        
        # 内层容器
        self._scroll_frame = tk.Frame(self._canvas, bg=colors["bg_primary"])
        
        # 配置滚动
        self._canvas.configure(yscrollcommand=self._scrollbar.set)
        
        # 布局
        self._scrollbar.grid(row=0, column=1, sticky="ns")
        self._canvas.grid(row=0, column=0, sticky="nsew")
        
        # 在 Canvas 中创建窗口
        self._canvas_window = self._canvas.create_window(
            (0, 0),
            window=self._scroll_frame,
            anchor="nw",
            width=self._canvas.winfo_reqwidth()
        )
        
        # 绑定事件
        self._scroll_frame.bind("<Configure>", self._on_frame_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)
        
        # 设置内边距
        self._scroll_frame.configure(padx=20, pady=15)
    
    def _rebind_mousewheel(self):
        """重新绑定滚轮事件"""
        self._bind_mousewheel_recursive(self._scroll_frame)
    
    def _bind_mousewheel_recursive(self, widget):
        """递归绑定滚轮事件"""
        widget.bind("<MouseWheel>", self._on_mousewheel)
        widget.bind("<Button-4>", self._on_mousewheel)
        widget.bind("<Button-5>", self._on_mousewheel)
        
        for child in widget.winfo_children():
            self._bind_mousewheel_recursive(child)
    
    def _on_frame_configure(self, event=None):
        """更新滚动区域"""
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))
    
    def _on_canvas_configure(self, event=None):
        """调整内层窗口宽度"""
        self._canvas.itemconfig(self._canvas_window, width=event.width)
    
    def _on_mousewheel(self, event):
        """鼠标滚轮滚动"""
        if event.num == 4:
            self._canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self._canvas.yview_scroll(1, "units")
        else:
            self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def setup_layout(self):
        """设置布局"""
        pass
    
    def _create_header(self):
        """创建标题区域"""
        colors = self.colors
        
        header = tk.Frame(self._scroll_frame, bg=colors["bg_primary"])
        header.pack(fill=tk.X, pady=(0, 12))
        
        title = tk.Label(
            header,
            text="📊 学习统计",
            font=self._style_manager.get_font("title"),
            bg=colors["bg_primary"],
            fg=colors["fg_primary"]
        )
        title.pack(anchor="w")
        
        subtitle = tk.Label(
            header,
            text="查看您的学习进度和成就",
            font=self._style_manager.get_font("caption"),
            bg=colors["bg_primary"],
            fg=colors["fg_secondary"]
        )
        subtitle.pack(anchor="w", pady=(3, 0))
    
    def _create_summary_stats(self):
        """创建概览统计"""
        colors = self.colors
        
        card = tk.Frame(self._scroll_frame, bg=colors["bg_card"])
        card.configure(highlightbackground=colors["border"], highlightthickness=1)
        card.pack(fill=tk.X, pady=(0, 12))
        
        content = tk.Frame(card, bg=colors["bg_card"])
        content.pack(fill=tk.X, padx=12, pady=12)
        
        for i in range(4):
            content.columnconfigure(i, weight=1)
        
        stats = self._get_summary_stats()
        
        items = [
            ("📚", "总学习", stats["total_sessions"], "次"),
            ("📝", "总单词", stats["total_words"], "词"),
            ("⏱️", "总时间", stats["total_time"], "分钟"),
            ("🎯", "准确率", f"{stats['accuracy']}", "%"),
        ]
        
        for i, (icon, label, value, unit) in enumerate(items):
            frame = tk.Frame(content, bg=colors["bg_card"])
            frame.grid(row=0, column=i, padx=8, pady=8)
            
            icon_label = tk.Label(
                frame,
                text=icon,
                font=("Segoe UI", 18),
                bg=colors["bg_card"],
                fg=colors["accent"]
            )
            icon_label.pack()
            
            value_label = tk.Label(
                frame,
                text=str(value),
                font=("Segoe UI", 20, "bold"),
                bg=colors["bg_card"],
                fg=colors["fg_primary"]
            )
            value_label.pack()
            
            label_text = tk.Label(
                frame,
                text=f"{label} {unit}",
                font=self._style_manager.get_font("caption"),
                bg=colors["bg_card"],
                fg=colors["fg_secondary"]
            )
            label_text.pack()
    
    def _create_chart_area(self):
        """创建图表区域"""
        colors = self.colors
        
        card = tk.Frame(self._scroll_frame, bg=colors["bg_card"])
        card.configure(highlightbackground=colors["border"], highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True, pady=(0, 12))
        
        header = tk.Frame(card, bg=colors["bg_secondary"])
        header.pack(fill=tk.X, padx=1, pady=1)
        
        tk.Label(
            header,
            text="📈 每日学习趋势",
            font=self._style_manager.get_font("subheading"),
            bg=colors["bg_secondary"],
            fg=colors["accent"],
            padx=12,
            pady=8
        ).pack(anchor="w")
        
        content = tk.Frame(card, bg=colors["bg_card"])
        content.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)
        
        self._create_bar_chart(content)
    
    def _create_bar_chart(self, parent):
        """创建简单柱状图"""
        colors = self.colors
        
        daily_data = self._get_daily_data()
        
        if not daily_data:
            tk.Label(
                parent,
                text="暂无学习数据",
                font=self._style_manager.get_font("body"),
                bg=colors["bg_card"],
                fg=colors["fg_secondary"]
            ).pack(pady=30)
            return
        
        max_value = max(d["words"] for d in daily_data) if daily_data else 1
        max_value = max(max_value, 1)
        
        chart_frame = tk.Frame(parent, bg=colors["bg_card"])
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        for i, data in enumerate(daily_data):
            col_frame = tk.Frame(chart_frame, bg=colors["bg_card"])
            col_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=3)
            
            height_ratio = data["words"] / max_value if max_value > 0 else 0
            
            bar_container = tk.Frame(col_frame, bg=colors["bg_card"])
            bar_container.pack(fill=tk.BOTH, expand=True)
            
            bar_height = int(150 * height_ratio)
            bar = tk.Frame(
                bar_container,
                bg=colors["accent"],
                width=35,
                height=max(bar_height, 4)
            )
            bar.pack(side=tk.BOTTOM, pady=4)
            bar.pack_propagate(False)
            
            value_label = tk.Label(
                bar_container,
                text=str(data["words"]),
                font=self._style_manager.get_font("caption"),
                bg=colors["bg_card"],
                fg=colors["fg_primary"]
            )
            value_label.pack(side=tk.BOTTOM)
            
            date_label = tk.Label(
                col_frame,
                text=data["date"],
                font=self._style_manager.get_font("small"),
                bg=colors["bg_card"],
                fg=colors["fg_secondary"]
            )
            date_label.pack(pady=4)
    
    def _create_recent_sessions(self):
        """创建最近学习记录"""
        colors = self.colors
        
        card = tk.Frame(self._scroll_frame, bg=colors["bg_card"])
        card.configure(highlightbackground=colors["border"], highlightthickness=1)
        card.pack(fill=tk.X)
        
        header = tk.Frame(card, bg=colors["bg_secondary"])
        header.pack(fill=tk.X, padx=1, pady=1)
        
        tk.Label(
            header,
            text="📝 最近学习记录",
            font=self._style_manager.get_font("subheading"),
            bg=colors["bg_secondary"],
            fg=colors["accent"],
            padx=12,
            pady=8
        ).pack(anchor="w")
        
        content = tk.Frame(card, bg=colors["bg_card"])
        content.pack(fill=tk.X, padx=12, pady=10)
        
        sessions = self.app.progress_manager.study_sessions[-10:]
        
        if not sessions:
            tk.Label(
                content,
                text="暂无学习记录",
                font=self._style_manager.get_font("body"),
                bg=colors["bg_card"],
                fg=colors["fg_secondary"]
            ).pack(pady=8)
            return
        
        header_frame = tk.Frame(content, bg=colors["bg_card"])
        header_frame.pack(fill=tk.X)
        
        headers = ["日期", "学习词数", "复习词数", "准确率", "学习时间"]
        widths = [120, 60, 60, 60, 80]
        
        for h, w in zip(headers, widths):
            tk.Label(
                header_frame,
                text=h,
                font=self._style_manager.get_font("caption"),
                bg=colors["bg_card"],
                fg=colors["fg_secondary"],
                width=w // 10,
                anchor="w"
            ).pack(side=tk.LEFT, padx=4)
        
        sep = tk.Frame(content, bg=colors["border"], height=1)
        sep.pack(fill=tk.X, pady=4)
        
        for session in reversed(sessions):
            row = tk.Frame(content, bg=colors["bg_card"])
            row.pack(fill=tk.X, pady=2)
            
            values = [
                session.date[:16] if len(session.date) > 16 else session.date,
                str(session.words_studied),
                str(session.words_reviewed),
                f"{session.accuracy_rate:.0%}",
                f"{session.study_duration // 60}分钟"
            ]
            
            for v, w in zip(values, widths):
                tk.Label(
                    row,
                    text=v,
                    font=self._style_manager.get_font("caption"),
                    bg=colors["bg_card"],
                    fg=colors["fg_primary"],
                    width=w // 10,
                    anchor="w"
                ).pack(side=tk.LEFT, padx=4)
    
    def _get_summary_stats(self) -> dict:
        """获取概览统计"""
        pm = self.app.progress_manager
        
        total_sessions = len(pm.study_sessions)
        total_words = sum(s.words_studied for s in pm.study_sessions)
        total_time = sum(s.study_duration for s in pm.study_sessions) // 60
        
        if pm.study_sessions:
            accuracy = sum(s.accuracy_rate for s in pm.study_sessions) / len(pm.study_sessions) * 100
        else:
            accuracy = 0
        
        return {
            "total_sessions": total_sessions,
            "total_words": total_words,
            "total_time": total_time,
            "accuracy": int(accuracy)
        }
    
    def _get_daily_data(self) -> list:
        """获取每日数据"""
        pm = self.app.progress_manager
        
        daily = {}
        for session in pm.study_sessions:
            date = session.date[:10]
            if date not in daily:
                daily[date] = 0
            daily[date] += session.words_studied
        
        result = [{"date": k, "words": v} for k, v in daily.items()]
        result.sort(key=lambda x: x["date"])
        
        return result[-7:]
    
    def on_enter(self, **kwargs):
        """进入页面"""
        super().on_enter(**kwargs)
        self.refresh()
        self.app.update_status("查看您的学习数据和成就")
        self.app.update_progress("")
    
    def refresh(self):
        """刷新页面"""
        # 清除滚动框架中的所有内容
        for widget in self._scroll_frame.winfo_children():
            widget.destroy()
        
        # 重新创建组件
        self._create_header()
        self._create_summary_stats()
        self._create_chart_area()
        self._create_recent_sessions()
    
    def apply_theme(self):
        """应用主题"""
        super().apply_theme()
        colors = self.colors
        self._outer_frame.configure(bg=colors["bg_primary"])
        self._canvas.configure(bg=colors["bg_primary"])
        self._scroll_frame.configure(bg=colors["bg_primary"])