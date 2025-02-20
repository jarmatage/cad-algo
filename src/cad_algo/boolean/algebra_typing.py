"""Type hints for boolean algebra objects."""

from collections.abc import Sequence

Bit = bool | None
BitSequence = Sequence[Bit]
Bits = tuple[Bit, ...]
