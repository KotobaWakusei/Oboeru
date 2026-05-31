"""tkinter 动画工具模块 — color lerp, after-loop scheduler"""
import tkinter as tk


def lerp_color(c1: str, c2: str, t: float) -> str:
    """Linearly interpolate between two hex colors (t in 0..1)."""
    def _h(hx):
        hx = hx.lstrip("#")
        return tuple(int(hx[i:i+2], 16) for i in (0, 2, 4))
    def _f(r, g, b):
        return f"#{int(r):02x}{int(g):02x}{int(b):02x}"
    r1, g1, b1 = _h(c1)
    r2, g2, b2 = _h(c2)
    return _f(r1 + (r2 - r1) * t, g1 + (g2 - g1) * t, b1 + (b2 - b1) * t)


class Animator:
    """Manages tkinter after-based animation loops.

    Usage::
        anim = Animator(root)
        anim.animate(colors, target, 'bg', start_c, end_c, duration=300)
    """

    def __init__(self, master):
        self._master = master
        self._jobs = set()

    def animate(self, steps, final, cb):
        """Generic after-loop.  Calls ``cb(step_i)`` for i in 0..steps-1,
        then calls ``final()`` after the last step."""
        tag = object()
        self._jobs.add(tag)

        def tick(i):
            if tag not in self._jobs:
                return
            if i < steps:
                cb(i)
                self._master.after(16, tick, i + 1)
            else:
                final()
                self._jobs.discard(tag)

        tick(0)

    def animate_bg(self, widget, start_color, end_color, steps=15):
        """Smoothly transition a widget's bg from start_color to end_color."""
        def cb(i):
            t = (i + 1) / steps
            color = lerp_color(start_color, end_color, t)
            try:
                widget.configure(bg=color)
            except Exception:
                pass
        def final():
            try:
                widget.configure(bg=end_color)
            except Exception:
                pass
        self.animate(steps, final, cb)

    def animate_fg(self, widget, start_color, end_color, steps=15):
        """Smoothly transition a widget's fg from start_color to end_color."""
        def cb(i):
            t = (i + 1) / steps
            color = lerp_color(start_color, end_color, t)
            try:
                widget.configure(fg=color)
            except Exception:
                pass
        def final():
            try:
                widget.configure(fg=end_color)
            except Exception:
                pass
        self.animate(steps, final, cb)

    def animate_progress(self, pbar, target_value, steps=20):
        """Smoothly fill a progress bar to target_value."""
        start = pbar["value"]
        delta = target_value - start
        def cb(i):
            t = (i + 1) / steps
            try:
                pbar["value"] = start + delta * t
            except Exception:
                pass
        self.animate(steps, lambda: None, cb)

    def flash_bg(self, widget, flash_color, restore_color, steps=8, hold_steps=6):
        """Flash a widget's bg to flash_color then back to restore_color."""
        def phase1(i):
            t = (i + 1) / steps
            color = lerp_color(restore_color, flash_color, t)
            try:
                widget.configure(bg=color)
            except Exception:
                pass
        def phase2(i):
            t = (i + 1) / steps
            color = lerp_color(flash_color, restore_color, t)
            try:
                widget.configure(bg=color)
            except Exception:
                pass
        tag = object()
        self._jobs.add(tag)

        def tick(i):
            if tag not in self._jobs:
                return
            if i < steps:
                phase1(i)
                self._master.after(16, tick, i + 1)
            elif i < steps + hold_steps:
                self._master.after(16, tick, i + 1)
            elif i < steps * 2 + hold_steps:
                phase2(i - steps - hold_steps)
                self._master.after(16, tick, i + 1)
            else:
                try:
                    widget.configure(bg=restore_color)
                except Exception:
                    pass
                self._jobs.discard(tag)

        tick(0)

    def cancel_all(self):
        self._jobs.clear()
