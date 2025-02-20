"""Factory for creating new SOP classes."""

from .cube import BaseCube
from .exceptions import InvalidSizeError
from .literal import fill_literals
from .sop import BaseSOP


def sop_factory(size: int = 6, literals: tuple[str, ...] = ()) -> type[BaseSOP]:
    """Dynamically create a Cube and SOP class with a desired dimension and literals."""
    if not (isinstance(size, int) and size > 0):
        raise InvalidSizeError(size)

    class Cube(BaseCube):
        __slots__: tuple[str, ...] = ("_bits",)
        _size: int = size
        _literals: tuple[str, ...] = tuple(fill_literals(literals, size))

    class SOP(BaseSOP):
        cube: type[BaseCube] = Cube

    return SOP
