"""App environment"""
# pylint: disable=no-member

import curses

from lymia.colors import Coloring

class Theme:
    """App theme"""
    def __init__(self, cursor_style: int, style: Coloring) -> None:
        self._style = style
        self._cursor_style = cursor_style

    def apply(self):
        """Apply current theme"""
        if self._style:
            curses.start_color()
            for style in self._style:
                curses.init_pair(int(style), style.fg, style.bg)
        curses.curs_set(self._cursor_style)
