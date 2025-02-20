"""Cofactor related boolean computations."""

from .algebra_typing import Bits


def cube_cofact(c1: Bits, c2: Bits) -> Bits:
    """Compute the cofactor of c1 with respect to c2."""
    if len(c1) == 0:
        return ()
    if len(c2) == 0:
        return c1
    if all(x is None for x in c1) or c1 == c2:
        return (None,) * len(c1)

    literals = []
    for l1, l2 in zip(c1, c2, strict=True):
        if (l1 is True and l2 is False) or (l1 is False and l2 is True):
            return ()
        literals.append(l1 if l2 is None else None)
    return tuple(literals)
