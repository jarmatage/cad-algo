"""Computations related to the string names of literals in a cube."""

import string

from .algebra_typing import Bits
from .exceptions import LiteralLenError, LiteralSurplusError


def fill_literals(literals: tuple[str, ...], size: int) -> list[str]:
    """Use the alphabet to automatically get literal names."""
    result = list(literals)
    if len(result) > size:
        raise LiteralLenError(result, size)

    for char in string.ascii_letters:
        if len(result) == size:
            return result
        if char not in literals:
            result.append(char)
    raise LiteralSurplusError(size)


def repr_cube(bits: Bits, literals: list[str]) -> str:
    """
    Represent the Cube as a string of variable names.

    If any literal name is multiple characters long, the string will be separated by
    '*'. Otherwise, there will be no separation. Don't cares are displayed as '-'.
    """
    multichar = any(len(x) > 1 for x in literals)
    if len(bits) == 0:
        return "0"
    if all(x is None for x in bits):
        return "1"

    chars = []
    for bit, var in zip(bits, literals, strict=True):
        chars.append("-" if bit is None else (var if bit else f"~{var}"))
    return ("*" if multichar else "").join(chars)


def sort_cube(bits: Bits) -> tuple[int, int, bool]:
    """
    Key command for sorting cubes by their bits.

    The first value is the number of explicit literals. A cube with more don't cares
    will be sorted first. The second value is the index of the first explicit literal.
    For the literal names 'abc', a cube 'a' will be sorted before a cube 'b'. The third
    value is the sign of the first explicit literal. A True literal gets sorted before
    a False literal. Finally, 1 and 0 are sorted before any other cube.
    """
    if all(x is None for x in bits):
        return 0, 0, False
    if len(bits) == 0:
        return 0, 0, True
    index = next((i for i, x in enumerate(bits) if x is not None), -1)
    return len(bits) - bits.count(None), index, not bits[index]
