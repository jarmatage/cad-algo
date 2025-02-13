"""Class defintion for a boolean sum of products."""

from functools import reduce

from .cube import BaseCube

MINIMIZE = True

InputCubes = list[BaseCube] | set[BaseCube] | tuple[BaseCube]


class SOP(set):
    """A set of cubes which represents a sum of products."""

    def __init__(self, cubes: InputCubes) -> None:
        """Initialize a sum of products object."""
        if not all(isinstance(c, BaseCube) for c in cubes):
            msg = "Not all inputs to the SOP are cube objects."
            raise ValueError(msg)

        if len({c.size for c in cubes}) != 1:
            msg = "Not all input cubes to the SOP have the same dimension."
            raise ValueError(msg)

        cubes = [c for c in cubes if not c.is_zero]
        if any(c.is_one() for c in cubes):
            super().__init__({cubes[0].__class__.one})
        else:
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
        return SOP([c.cofactor(cube) for c in self], minimize=self._minimize)

    def __invert__(self) -> "SOP":
        """Return the complement of this SOP."""
        return reduce(lambda s1, s2: s1 * s2, [~c for c in self])

    def __add__(self, other: "BaseCube | SOP") -> "SOP":
        """Add another SOP or cube to this SOP."""
        other = {other} if isinstance(other, BaseCube) else other
        return SOP(self.union(other))

    def __sub__(self, other: "BaseCube | SOP") -> "SOP":
        """Compute the set difference between this SOP and another SOP or cube."""
        other = {other} if isinstance(other, BaseCube) else other
        return self.copy().difference(other)

    def __mul__(self, other: "BaseCube | SOP") -> "SOP":
        """Calculate the product between this SOP and another SOP or cube."""
        other = SOP([other]) if isinstance(other, BaseCube) else other

        if len(self) == 0 or len(other) == 0:
            return SOP([])
        if any(c.is_one for c in self):
            return other
        if any(c.is_one for c in other):
            return self

        return SOP([c1 * c2 for c1 in self for c2 in other])

    def __div__(self, other: "BaseCube | SOP") -> tuple["SOP", "SOP"]:
        """Perform algebraic division of this SOP by another SOP or cube."""
        if isinstance(other, BaseCube):
            quotient = SOP([c / other for c in self])
        else:
            quotients = [(self / c)[0] for c in other]
            quotient = reduce(lambda s1, s2: s1 & s2, quotients)
        return quotient, self - quotient * other
