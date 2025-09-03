"""Colors"""

from . import _color_const as color

class Color:
    """Define colors with fg and bg"""
    def __init__(self, fg: int, bg: int) -> None:
        self._fg = fg
        self._bg = bg
        self._id = -1

    @property
    def id(self):
        """Id"""
        return self._id

    def set_id(self, cid: int):
        """Set this color id"""
        self._id = cid

class Coloring:
    """Coloring"""
    def __init__(self) -> None:
        self._fields = {}
        for index, (key, value) in enumerate(type(self).__dict__.items()):
            if not isinstance(value, Color):
                continue
            value.set_id(index)
            self._fields[key] = value

__all__ = ['Color', 'color', "Coloring"]
