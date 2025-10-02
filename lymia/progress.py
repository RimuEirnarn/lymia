"""Progress bar"""

# pylint: disable=no-member

import curses
import time

from .panel import Panel

PARTIAL_BLOCKS = ["", "▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"]

class Progress:
    """Progress"""
    def __init__(self, smoothing: float=0.3, min_interval: float=0.1):
        self.smoothing = smoothing
        self.min_interval = min_interval
        self.avg_dt = None
        self.last_update = 0
        self.last_time = time.time()

    def render(self, window: curses.window | Panel, y: int, x: int, width: int, current: int, total: int, prefix: str):
        """
        Draw the progress bar at (y, x) with given width.
        Progress values are provided by the Scene.
        """

        render = window.screen if isinstance(window, Panel) else window

        now = time.time()
        # Throttle redraw
        # if now - self.last_update < self.min_interval and current < total:
        #     return

        fraction = current / max(total, 1)
        filled_cells = fraction * width
        full_blocks = int(filled_cells)
        partial_index = int((filled_cells - full_blocks) * (len(PARTIAL_BLOCKS) - 1))

        bar_str = "█" * full_blocks
        if full_blocks < width:
            bar_str += PARTIAL_BLOCKS[partial_index]
        bar_str = bar_str.ljust(width)

        # Smooth ETA
        dt = now - self.last_time
        self.last_time = now
        if self.avg_dt is None:
            self.avg_dt = dt
        else:
            self.avg_dt = (1 - self.smoothing) * self.avg_dt + self.smoothing * dt

        # if current > 0 and current < total:
        #     eta = self.avg_dt * (total - current)
        #     eta_str = f"ETA {eta:5.1f}s"
        # else:
        #     eta_str = " " * 10

        line = f"{prefix} [{bar_str}] {current}/{total}"

        # Draw in curses window
        render.addnstr(y, x, line, width + 20)  # +20 for metadata
        self.last_update = now
