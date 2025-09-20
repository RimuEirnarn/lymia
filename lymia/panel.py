"""Panels"""

# pylint: disable=no-member

import curses.panel
import curses
from typing import Callable, ParamSpec, Concatenate


def refresh():
    """Refresh method"""
    curses.panel.update_panels()
    curses.doupdate()

Ps = ParamSpec("Ps")

REQ_REFRESH_METHODS = [
    "above",
    "below",
    "top",
    "bottom",
    "hide",
    "show",
    "move",
    "replace",
]


class Panel:
    """Panel"""

    __slots__ = ("_win", "_panel", "_draw")

    def __init__(
        self,
        height: int,
        width: int,
        start_x: int = 0,
        start_y: int = 0,
        callback: Callable[Concatenate[curses.window, Ps], None] | None = None,
    ) -> None:
        self._win = curses.newwin(height, width, start_x, start_y)
        self._panel = curses.panel.new_panel(self._win)
        self._draw = callback

    @property
    def screen(self):
        """Return the screen this panel assosciates to"""
        return self._win

    @property
    def panel(self):
        """Return the panel this class references to"""
        return self._panel

    def draw(self, *args, **kwargs):
        """Draw this panel"""
        if callable(self._draw):
            self._draw(self._win, *args, **kwargs)

    def above(self):
        """Put panel above"""
        self._panel.above()
        refresh()

    def below(self):
        """Put panel below"""
        self._panel.below()
        refresh()

    def top(self):
        """Put panel on top"""
        self._panel.top()
        refresh()

    def bottom(self):
        """Put panel on bottom"""
        self._panel.bottom()
        refresh()

    def hide(self):
        """Hide"""
        self._panel.hide()
        refresh()

    def show(self):
        """Show"""
        self._panel.show()
        refresh()

    def move(self, x: int, y: int):
        """Move current panel"""
        self._panel.move(y, x)
        refresh()

    def replace(self, win: curses.window):
        """Replaces current window"""
        self._panel.replace(win)
        self._win = win
        refresh()
