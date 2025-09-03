"""Password form field"""

from ._base import Forms

class Password(Forms):
    """Password form fields"""

    @property
    def displayed_value(self):
        return "*" * (len(self._buffer))
