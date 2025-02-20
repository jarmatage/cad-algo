"""Containment related boolean computations."""

from .algebra_typing import Bits
from .cofact import cube_cofact


def cube_containment(c1: Bits, c2: Bits) -> bool:
    """Check if c2 is contained within c1."""
    if all(x is None for x in c1) or len(c2) == 0 or c1 == c2:
        return True
    if len(c1) == 0 or all(x is None for x in c2):
        return False
    if len(cofactor := cube_cofact(c1, c2)) == 0:
        return False
    return all(x is None for x in cofactor)
