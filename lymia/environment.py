"""App environment"""

from lymia.colors import Coloring

class Theme:
    """App theme"""
    def __init__(self, cursor_style: int, style: Coloring) -> None:
        self._style = style
        self._cursor_style = cursor_style

    def apply(self):
        """Apply current theme"""
