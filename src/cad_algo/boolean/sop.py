"""Class defintion for a boolean sum of products (SOP)."""

from collections.abc import Iterable
from collections.abc import Set as AbstractSet
from functools import reduce
from itertools import combinations

from .cube import BaseCube
from .exceptions import InvalidCubeError
from .invert import de_morgans

CubeSet = set[BaseCube]
AbstractCubeSet = AbstractSet[BaseCube | None]


class BaseSOP(CubeSet):
    """A set of cubes which represents a sum of products."""

    cube: type[BaseCube] = BaseCube
    minimal: bool = True

    @classmethod
    def zero(cls) -> "BaseSOP":
        """Return a SOP that represents a boolean 0."""
        return cls()

    @classmethod
    def one(cls) -> "BaseSOP":
        """Return a SOP that represents a boolean 1."""
        return cls({cls.cube.one()})

    def __new__(cls, cubes: Iterable[BaseCube] = ()) -> "BaseSOP":
        """Ensure the input consists of valid cubes."""
        for c in cubes:
            if not isinstance(c, cls.cube):
                raise InvalidCubeError(c)
        return super().__new__(cls)

    def __init__(self, cubes: Iterable[BaseCube] = ()) -> None:
        """Initialize and minimize a SOP."""
        if any(c == 1 for c in cubes):
            cube_set = {self.__class__.cube.one()}
        else:
            cube_set = set(cubes)
            cube_set.discard(self.__class__.cube.zero())
        super().__init__(cube_set)
        if self.__class__.minimal:
            self.minimize()

    def __add__(self, other: CubeSet | BaseCube) -> "BaseSOP":
        """Add another SOP or cube to this SOP."""
        other = {other} if isinstance(other, BaseCube) else other
        return self.__class__(self.union(other))

    def __eq__(self, other: object) -> bool:
        """Return True if another SOP is equal to this SOP."""
        if isinstance(other, self.__class__):
            return self == other
        if other == 1:
            return any(c == 1 for c in self)
        if other == 0:
            return len(self) == 0
        return NotImplemented

    def __invert__(self) -> "BaseSOP":
        """Return the complement of this SOP."""
        return reduce(lambda s1, s2: s1 * s2, [self.cube_invert(c) for c in self])

    def __mod__(self, other: "BaseSOP") -> "BaseSOP":
        """Compute the consensus between two SOPs that represent single cubes."""
        if len(self) > 1 or len(other) > 1:
            raise NotImplementedError
        c1 = next(iter(self), self.__class__.cube.zero())
        c2 = next(iter(other), other.__class__.cube.zero())
        return self.__class__({c1 % c2})

    def __mul__(self, other: CubeSet | BaseCube) -> "BaseSOP":
        """Calculate the product between this SOP and another SOP or cube."""
        other = {other} if isinstance(other, BaseCube) else other
        other = self.__class__(other)

        if len(self) == 0 or len(other) == 0:
            return self.__class__(set())
        if self == 1:
            return other
        if other == 1:
            return self
        return self.__class__({c1 * c2 for c1 in self for c2 in other})

    def __repr__(self) -> str:
        """Represent the sum of products as cubes separated by '+' signs."""
        cubes = sorted([repr(c) for c in self])
        return "0" if len(self) == 0 else " + ".join(cubes)

    def __rmul__(self, other: CubeSet | BaseCube) -> "BaseSOP":
        """Account for when a cube is the left operator in multiplication."""
        return self.__mul__(other)

    def __str__(self) -> str:
        """Print the sum of products as cubes separated by '+' signs."""
        cubes = sorted([str(c) for c in self])
        return "0" if len(self) == 0 else " + ".join(cubes)

    def __sub__(self, other: AbstractCubeSet | BaseCube) -> "BaseSOP":
        """Compute the set difference between this SOP and another SOP or cube."""
        other = {other} if isinstance(other, BaseCube) else other
        return self.__class__(self.difference(other))

    def __truediv__(self, other: CubeSet | BaseCube) -> tuple["BaseSOP", "BaseSOP"]:
        """Perform algebraic division of this SOP by another SOP or cube."""
        if isinstance(other, BaseCube):
            quotient = self.__class__({(c / other)[0] for c in self})
        else:
            quotients = [(self / c)[0] for c in other]
            quotient = reduce(lambda s1, s2: s1 * s2, quotients)
        return quotient, self - quotient * other

    def cube_invert(self, cube: BaseCube) -> "BaseSOP":
        """Compute the inverse of a cube object."""
        return self.__class__({self.__class__.cube(x) for x in de_morgans(cube.bits)})

    def cofact(self, cube: BaseCube) -> "BaseSOP":
        """Compute the cofactor of each cube in the SOP with respect to another cube."""
        return self.__class__({c.cofact(cube) for c in self})

    def literal_cofact(self, index: int, *, bit: bool = True) -> "BaseSOP":
        """Compute the cofactor of the SOP with respect to a single literal."""
        return self.__class__({c.literal_cofact(index, bit=bit) for c in self})

    def minimize(self) -> None:
        """
        Transform the SOP into a minimal SOP with respect to single cube containment.

        Iteratively delete all cubes that are contained in other cubes in the SOP.
        The cube set is converted into a list. Each cube is compared against all
        other cubes. However, a cube is pruned once it is found to be contained thus
        progressively reducing the number of cubes a cube needs to be compared against.

        The only SOP that would take len^2 iterations is a SOP that is already minimal
        which will inherently have a smaller len.

        The list of cubes is sorted by the number of don't cares it has. A cube with
        less don't cares is more likely to be contained and thus is processed first.
        A cube is first compared against the cube with the most don't cares as it is
        most likely to contain other cubes.
        """
        cubes = sorted(self, key=lambda x: x.bits.count(None))
        minimals: list[BaseCube] = []
        while cubes:
            c1 = cubes.pop(0)
            for c2 in cubes[::-1] + minimals[::-1]:
                if c1 <= c2:  # remove c1 if it is contained by another cube
                    self.remove(c1)
                    break
            if c1 in self:  # c1 was not removed and thus gets saved as a minimal
                minimals.append(c1)

    def complete(self) -> "BaseSOP":
        """
        Compute the complete cover for the sum of products.

        A copy of the SOP is worked on so as to not pollute this object.
        First, the copy is minimized wrt single cube containment. This satisfies the
        completness property that no cube is contained in any other cube.

        Next, the consensus of every possible cube pair is calculated. The result
        is a set of all consensus values for the copy. If every consensus is contained
        within a cube of the copy, the copy must be complete.

        We iteratively check if each consensus is contained in the copy.
        If the copy is not complete, we add the consensus to the copy and start
        over again with the minimization process. This cycle repeats until the copy
        is complete.
        """
        copy = self.__class__(self.copy())
        while True:
            finished = True
            copy.minimize()
            for consensus in {c1 % c2 for c1, c2 in combinations(copy, 2)}:
                if not any(consensus <= cube for cube in copy):
                    copy.add(consensus)
                    finished = False
                    break
            if finished:
                break
        return copy

    def is_tautology(self) -> bool:
        """
        Return True if the sum of products is a tautology.

        A copy of the SOP is worked on so as to not pollute this object. The copy is
        converted into a complete SOP to help reduce the number of cofactors
        computations needed. If the copy contains a 1 in it, we can claim the SOP is
        a tautology and end early.

        Next we compute the one and zero cofactor for the first
        literal in the cube. If both cofactors contain a 1, we can claim the SOP is
        a tautology. Else, we enter a recursion and compute the cofactor for the next
        literal in the cube. This contains until a tautology is found or we run through
        all the literals.
        """
        return self.complete().rtautology(0)

    def rtautology(self, i: int = 0) -> bool:
        """Recursively check if the one and zero cofactors are tautologies."""
        if self == 0:
            return False
        if self == 1:
            return True
        if i >= self.__class__.cube.size():
            return False
        one_cofactor = self.literal_cofact(i, bit=True)
        zero_cofactor = self.literal_cofact(i, bit=False)
        return one_cofactor.rtautology(i + 1) and zero_cofactor.rtautology(i + 1)

    def incomplete(self, f_dc: "BaseSOP") -> "BaseSOP":
        """
        Compute the prime implicants of an incompletely specified function.

        It is assumed that this SOP is the on-set of the function and that the
        input to this function is the don't care set (dc-set) of the function.

        It is also assumed that the on-set and the dc-set are independent sets
        with no overlapping minterms.
        """
        if self.is_tautology():
            return self.__class__.one()
        if self == 0:
            return self
        f_on = self.complete()
        f_dc = f_dc.complete()
        return (f_on + f_dc).complete() - f_dc

    @staticmethod
    def is_prime(f_on: "BaseSOP", f_dc: "BaseSOP", cube: BaseCube) -> bool:
        """
        Check if a given cube is a prime implicant of a completely specified function.

        A completely specified boolean fuction requires the specification of two
        covers: f_on and f_dc. The f_on cover represents all inputs where the output of
        the function is 1. The f_dc cover represents all inputs where we don't care
        what the output of the function is.

        We need to make sure any prime implicants of f_on cannot be expanded due to
        don't care minterms in f_dc. Because of this, we add f_on and f_dc together and
        compute the complete cover of the new SOP. If the given cube is in the complete
        cover, it must be a prime implicant of the function f.
        """
        return cube in f_on.incomplete(f_dc)

    def best_ucp_literal(self) -> tuple[int, bool | None, int]:
        """
        Find the literal with the strongest unateness in this SOP.

        A SOP is positive unate in a literal if the literal never appears negated within
        the SOP. In other words, the bit associated with that literal only stores True
        (1) or None (don't care). Similarly, a SOP is negative unate in a literal if the
        bit associated with that literal only stores False (0) or None (don't care).

        There could be multiple literals that have unateness. In this case, the literal
        with the least number of don't cares is best.
        """
        if self == 0:
            return 0, None, 0
        unate_literals = []

        for i in range(self.__class__.cube.size()):
            if any(x.bits[i] is False for x in self):
                continue
            if (count := sum(x.bits[i] is True for x in self)) == 0:
                continue
            unate_literals.append((i, True, count))
        for i in range(self.__class__.cube.size()):
            if any(x.bits[i] is True for x in self):
                continue
            if (count := sum(x.bits[i] is False for x in self)) == 0:
                continue
            unate_literals.append((i, False, count))
        if not unate_literals:
            cube = next(iter(self))
            index = next(i for i, value in enumerate(cube.bits) if value is not None)
            return index, None, 0
        return max(unate_literals, key=lambda x: x[2])

    def literal(self, index: int, *, bit: bool = True) -> BaseCube:
        """Return a cube that represents a single literal."""
        return self.__class__.cube.literal(index, bit=bit)

    def complement(self) -> "BaseSOP":
        """Return the complement of this SOP."""
        if self == 0:
            return self.__class__.one()
        if self == 1:
            return self.__class__.zero()

        index, pos_unate, _ = self.best_ucp_literal()
        pos_cofactor = self.literal_cofact(index, bit=True)
        neg_cofactor = self.literal_cofact(index, bit=False)
        lpos = self.literal(index, bit=True)
        lneg = self.literal(index, bit=False)

        if pos_unate is True:
            return pos_cofactor.complement() + neg_cofactor.complement() * lneg
        if pos_unate is False:
            return pos_cofactor.complement() * lpos + neg_cofactor.complement()
        return pos_cofactor.complement() * lpos + neg_cofactor.complement() * lneg
