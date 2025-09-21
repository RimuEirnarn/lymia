"""Panels"""

# pylint: disable=no-member

import curses.panel
import curses
from typing import Any, Callable, ParamSpec


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
        callback: Callable[[curses.window, Any], None] | None = None,
        state: Any = None
    ) -> None:
        self._win = curses.newwin(height, width, start_x, start_y)
        self._panel = curses.panel.new_panel(self._win)
        self._panel.set_userptr(state)
        self._draw = callback

    def set_state(self, obj: Any):
        """Set panel's state"""
        self._panel.set_userptr(obj)

    def get_state(self):
        """Get panel's state"""
        return self._panel.userptr()

    @property
    def screen(self):
        """Return the screen this panel assosciates to"""
        return self._win

    @property
    def panel(self):
        """Return the panel this class references to"""
        return self._panel

    def draw(self):
        """Draw this panel"""
        if callable(self._draw):
            self._draw(self._win, self.get_state())

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
        try:
            self._panel.move(y, x)
        except curses.panel.error as exc:
            exc.add_note(f"x: {x} and y: {y}")
            raise exc
        refresh()

    def replace(self, win: curses.window):
        """Replaces current window"""
        self._panel.replace(win)
        self._win = win
        refresh()
