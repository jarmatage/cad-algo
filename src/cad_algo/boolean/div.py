"""Division related boolean computations."""

from .algebra_typing import Bits
from .containment import cube_containment


def cube_div(c1: Bits, c2: Bits) -> tuple[Bits, Bits]:
    """Compute the quotient and remainder of c1 divided by c2."""
    if len(c1) == 0:
        return (), ()
    if not cube_containment(c2, c1):
        return (), c1
    return tuple(None if x == y else x for x, y in zip(c1, c2, strict=True)), ()
