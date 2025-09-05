"""Password form field"""

from ._base import Forms


class Password(Forms):
    """Password form fields"""

    def __init__(
        self,
        label: str,
        value: str = "",
        suffix: str = ": ",
        margin_left: int = 0,
        field_pos: int = 0,
        style: int = 0,
    ) -> None:
        super().__init__(label, value, suffix, margin_left, field_pos, style)

    @property
    def displayed_value(self):
        return "*" * (len(self._buffer))
