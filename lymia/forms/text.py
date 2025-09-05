"""Text form fields"""

from ._base import Forms


class Text(Forms):
    """Text form fields"""

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
