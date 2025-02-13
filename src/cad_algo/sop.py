"""Class defintion for a boolean sum of products."""

from collections.abc import Set as AbstractSet
from functools import reduce

from .cube import BaseCube

MINIMIZE = True

CubeSet = set[BaseCube]
AbstractCubeSet = AbstractSet[BaseCube | None]


class SOP(CubeSet):
    """A set of cubes which represents a sum of products."""

    def __new__(cls, cubes: CubeSet) -> "SOP":
        """Ensure the input consists of valid cubes."""
        if not all(isinstance(c, BaseCube) for c in cubes):
            msg = "Not all inputs to the SOP are cube objects."
            raise ValueError(msg)

        if len({c.size for c in cubes}) != 1:
            msg = "Not all input cubes to the SOP have the same dimension."
            raise ValueError(msg)

        return super().__new__(cls)

    def __init__(self, cubes: CubeSet) -> None:
        """Initialize and minimize a SOP."""
        if any(c.is_one for c in cubes):
            cubes = {cubes.pop().__class__.one}
        super().__init__(cubes)
        if MINIMIZE:
            self.minimize()

    def __repr__(self) -> str:
        """Represent the sum of products as cubes separated by '+' signs."""
        if len(self) == 0:
            return "0"
        return " + ".join([repr(c) for c in self])

    def minimize(self) -> None:
        """
        Transform the SOP into a minimal SOP with respect to single cube containment.

        Deletes all cubes that are contained in other cubes in the sop.
        """
        i = 0
        j = 1
        cubes = list(self)
        while i < len(self) - 1 and len(self) > 1:
            if cubes[i] <= cubes[j]:
                self.remove(cubes[i])
                del cubes[i]
            elif cubes[j] <= cubes[i]:
                self.remove(cubes[j])
                del cubes[j]
            else:
                j += 1
            if j >= len(self):
                i += 1
                j = i + 1

    def cofactor(self, cube: BaseCube) -> "SOP":
        """Compute the cofactor of each cube in the SOP with respect to another cube."""
        return SOP({c.cofactor(cube) for c in self})

    def __invert__(self) -> "SOP":
        """Return the complement of this SOP."""
        inverts = [~c for c in self]
        sops = [SOP({i}) if isinstance(i, BaseCube) else i for i in inverts]
        return reduce(lambda s1, s2: s1 * s2, sops)

    def __add__(self, other: CubeSet | BaseCube) -> "SOP":
        """Add another SOP or cube to this SOP."""
        other_set = {other} if isinstance(other, BaseCube) else other
        return SOP(self.union(other_set))

    def __sub__(self, other: AbstractCubeSet | BaseCube) -> "SOP":
        """Compute the set difference between this SOP and another SOP or cube."""
        other_set = {other} if isinstance(other, BaseCube) else other
        return SOP(self.difference(other_set))

    def __mul__(self, other: CubeSet | BaseCube) -> "SOP":
        """Calculate the product between this SOP and another SOP or cube."""
        other = SOP({other}) if isinstance(other, BaseCube) else SOP(other)

        if len(self) == 0 or len(other) == 0:
            return SOP(set())
        if any(c.is_one for c in self):
            return other
        if any(c.is_one for c in other):
            return self

        return SOP({c1 * c2 for c1 in self for c2 in other})

    def __rmul__(self, other: "BaseCube | SOP") -> "SOP":
        """Account for when a cube is the left operator in multiplication."""
        return self.__mul__(other)

    def __truediv__(self, other: CubeSet | BaseCube) -> tuple["SOP", "SOP"]:
        """Perform algebraic division of this SOP by another SOP or cube."""
        if isinstance(other, BaseCube):
            quotient = SOP({(c / other)[0] for c in self})
        else:
            quotients = [(self / c)[0] for c in other]
            quotient = reduce(lambda s1, s2: s1 * s2, quotients)
        return quotient, self - quotient * other
