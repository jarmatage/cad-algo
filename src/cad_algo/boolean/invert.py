"""Inversion related boolean computations."""

from .algebra_typing import Bits


def one_hot(size: int, index: int, *, bit: bool = True) -> Bits:
    """Create a cube object which has don't cares everywhere except a single bit."""
    result: list[bool | None] = [None] * size
    result[index] = bit
    return tuple(result)


def de_morgans(c1: Bits) -> set[Bits]:
    """Apply De Morgan's law to compute the inverse of a cube."""
    cubes = set()
    for i, bit in enumerate(c1):
        if bit is not None:
            cubes.add(one_hot(len(c1), i, bit=not bit))
    return cubes
