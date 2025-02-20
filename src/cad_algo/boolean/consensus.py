"""Consensus related boolean computations."""

from .algebra_typing import Bits


def cube_consensus(c1: Bits, c2: Bits) -> Bits:
    """Compute the consensus of c1 with respect to c2."""
    opposition = False
    consensus = []
    for l1, l2 in zip(c1, c2, strict=False):
        if (l1 == l2) or (l2 is None):
            consensus.append(l1)
        elif l1 is None:
            consensus.append(l2)
        elif opposition:  # Opposition has already been found; no consensus
            return ()
        else:  # First opposition has been found
            opposition = True
            consensus.append(None)
    return tuple(consensus) if opposition else ()
