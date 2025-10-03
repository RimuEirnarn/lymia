"""Form fields"""

from ._base import Forms
from .text import Text
from .password import Password


class FormFields:
    """Form fields"""

    def __init__(self, fields: tuple[Forms, ...], margin_top: int = 0) -> None:
        self._fields = fields
        for index, field in enumerate(fields):
            field.set_field_pos(margin_top + index)

    def to_menu_fields(self):
        """To menu fields"""
        return tuple((field.label, field) for field in self._fields)


__all__ = ["FormFields", "Forms", "Text", "Password"]
