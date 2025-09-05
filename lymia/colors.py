"""Colors"""

from . import _color_const as color

class ColorPair:
    """Define colors with fg and bg"""
    def __init__(self, fg: int, bg: int) -> None:
        self._fg = fg
        self._bg = bg
        self._id = -1

    @property
    def id(self):
        """Id"""
        return self._id

    @property
    def fg(self):
        """Foreground"""
        return self._fg

    @property
    def bg(self):
        """background"""
        return self._bg

    def __int__(self):
        if self._id == -1:
            raise ValueError("This color must be initialized")
        return self._id

    def set_id(self, cid: int):
        """Set this color id"""
        self._id = cid

    def __repr__(self) -> str:
        return f"<ColorPair[{self._id}] fg={self._fg} bg={self._bg}>"

class Coloring:
    """Coloring"""
    def __init__(self) -> None:
        self._fields: dict[str, ColorPair] = {}
        for index, (key, value) in enumerate(type(self).__dict__.items()):
            if not isinstance(value, ColorPair):
                continue
            value.set_id(index)
            self._fields[key] = value

    def __iter__(self):
        return (field for field in self._fields.values())

    def __bool__(self):
        return bool(self._fields)

__all__ = ['ColorPair', 'color', "Coloring"]
