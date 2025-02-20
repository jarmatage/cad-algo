"""Multiplication related boolean computations."""

from .algebra_typing import Bits


def cube_mul(c1: Bits, c2: Bits) -> Bits:
    """Compute the product of two cubes."""
    if len(c1) == 0 or len(c2) == 0:
        return ()
    if all(x is None for x in c1):
        return c2
    if c1 == c2 or all(x is None for x in c2):
        return c1

    literals = []
    for l1, l2 in zip(c1, c2, strict=True):
        if not (l1 == l2 or l1 is None or l2 is None):
            return ()
        literals.append(l2 if l1 is None else l1)
    return tuple(literals)
