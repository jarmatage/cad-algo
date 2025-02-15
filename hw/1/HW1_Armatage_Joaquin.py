#!/usr/bin/env python3
"""CEN 503: Algorithms for CAD of Digital Systems, Homework 1."""

import string
from collections.abc import Set as AbstractSet
from functools import reduce
from itertools import combinations
from typing import ClassVar

from lark import Lark, Transformer, exceptions, v_args

GRAMMER = r"""
    start: expr

    ?expr: term ("+" term)*             -> disjunction
    ?term: exor ("*" exor)*             -> conjunction
    ?exor: factor ("^" factor)*         -> exor
    ?factor: "~" atom                   -> complement
            | atom "'"                   -> complement
            | atom
    ?atom: "(" expr ")"                 -> group
          | /[01]/                       -> literal
          | /[a-zA-Z]/                   -> literal

    %import common.WS
    %ignore WS
"""
MINIMIZE = True

CubeType = tuple[bool | None, ...]


class BaseCube(CubeType):
    """A tuple where all instances must be the same length."""

    __slots__ = ()
    size: int = 6
    verbose: bool = False
    varlist: ClassVar[list[str]] = []
    zero: "BaseCube"
    one: "BaseCube"

    @classmethod
    def multichar(cls) -> bool:
        """Check if the class varnames have any multi-character strings."""
        return any(len(x) > 1 for x in cls.varlist)

    @classmethod
    def varnames(cls) -> list[str]:
        """Return the class var list with blank entries filled in."""
        result = list(cls.varlist)
        if len(result) > cls.size:
            msg = f"Too many variable names associated with cube of size '{cls.size}'"
            raise ValueError(msg)

        for char in string.ascii_letters:
            if len(result) == cls.size:
                return result
            if char not in result:
                result += [char]

        msg = f"Not enough characters to represent cube of size '{cls.size}'. "
        msg += "Please manually set the varlist for the cube class."
        raise ValueError(msg)

    @classmethod
    def onehot(cls, index: int, *, bit: bool = True) -> "BaseCube":
        """Create a cube object which is don't care everywhere except a single bit."""
        one = (None,) * cls.size
        return cls(one[:index] + (bit,) + one[index + 1 :])

    def __new__(cls, cube: CubeType = ()) -> "BaseCube":
        """
        Ensure the input tuple is the correct size and contains valid values.

        An empty input tuple corresponds to a boolean 0. An input tuple full of None
        corresponds to a boolean 1. Each element of the input tuple must either be True,
        False, or None.
        """
        if not hasattr(cls, "zero"):
            cls.zero = super().__new__(cls, ())
        if not hasattr(cls, "one"):
            cls.one = super().__new__(cls, (None,) * cls.size)

        if len(cube) != 0 and len(cube) != cls.size:
            msg = f"Invalid cube '{cube}'. "
            msg += f"Cube must have exactly {cls.size} elements or be empty."
            raise ValueError(msg)

        for bit in cube:
            if not (bit is None or isinstance(bit, bool)):
                msg = f"Invalid bit '{bit}' in cube '{cube}'. "
                msg += "Bit must be boolean or None."
                raise ValueError(msg)

        return super().__new__(cls, cube)

    @property
    def is_zero(self) -> bool:
        """Check if the cube is the zero special cube."""
        return self == self.__class__.zero

    @property
    def is_one(self) -> bool:
        """Check if the cube is the one special cube."""
        return self == self.__class__.one

    def __add__(self, other: "CubeType | SOP") -> "BaseCube | SOP":  # type: ignore[override]
        """Add another cube or a sum of products to this cube."""
        if isinstance(other, SOP):
            return other + self
        other = self.__class__(other)

        if self <= other:
            return other
        if other < self:
            return self
        return SOP({self, other})

    def __invert__(self) -> "BaseCube | SOP":
        """Apply De Morgan's law to covert this cube into a sum of products."""
        if self.is_zero:
            return self.__class__.one
        if self.is_one:
            return self.__class__.zero

        cubes = set()
        for i, bit in enumerate(self):
            if bit is not None:
                cubes.add(self.__class__.onehot(i, bit=(not bit)))
        return cubes.pop() if len(cubes) == 1 else SOP(cubes)

    def __le__(self, other: "CubeType | SOP") -> bool:
        """Return True is this cube is properly contained in another cube."""
        if isinstance(other, SOP):
            return any(self <= c for c in other)
        other = self.__class__(other)
        if other.is_zero or self.is_one:
            return False
        if self.is_zero or other.is_one:
            return True
        return other.cofactor(self).is_one

    def __lt__(self, other: "CubeType | SOP") -> bool:
        """Return True if this cube is contained in and not equal to another cube."""
        if isinstance(other, SOP):
            return any(self < c for c in other)
        other = self.__class__(other)
        return self != other and self <= other

    def __mod__(self, other: CubeType) -> "BaseCube":
        """
        Compute the consensus between this cube and another cube.

        Return None if no consensus exists, otherwise return the consensus cube. Two
        cubes have a consensus, if there is exactly one True literal in one cube and the
        corresponding literal in the other cube is False.
        """
        other = self.__class__(other)
        consensus = []
        opposition = False

        for l1, l2 in zip(self, other, strict=False):
            if (l1 == l2) or (l2 is None):  # Explicit match or other don't care
                consensus.append(l1)
            elif l1 is None:  # Self don't care, else must be opposition
                consensus.append(l2)
            elif opposition:  # Opposition has already been found; no consensus
                return self.__class__.zero
            else:  # First opposition has been found
                opposition = True
                consensus.append(None)

        return self.__class__(tuple(consensus)) if opposition else self.__class__.zero

    def __mul__(self, other: CubeType) -> "BaseCube":  # type: ignore[override]
        """Compute the product of this cube with another cube."""
        if not isinstance(other, self.__class__):
            return NotImplemented
        other = self.__class__(other)

        if self.is_zero or other.is_zero:
            return self.__class__.zero
        if self.is_one:
            return other
        if other.is_one or self == other:
            return self

        literals = []
        for l1, l2 in zip(self, other, strict=True):
            if l1 == l2 or l1 is None or l2 is None:
                literals.append(l2 if l1 is None else l1)
            else:
                return self.__class__.zero
        return self.__class__(tuple(literals))

    def __repr__(self) -> str:
        """
        Represent the Cube with a string of variable names.

        If any of the class variable names are multiple characters long, the string will
        be separated by '*'. Otherwise, there will be no whitespace separation. If the
        verbose class variable is set to True, don't care variables will be displayed as
        '-'. Otherwise, they will not be shown.
        """
        if self.is_zero:
            return "0"
        if self.is_one:
            return "1"

        chars = []
        for bit, var in zip(self, self.__class__.varnames(), strict=False):
            if bit is True:
                chars.append(var)
            elif bit is False:
                chars.append(f"~{var}")
            elif bit is None and self.__class__.verbose:
                chars.append("-")

        return ("*" if self.__class__.multichar() else "").join(chars)

    def __truediv__(self, other: CubeType) -> tuple["BaseCube", "BaseCube"]:
        """Compute this cube divided by another cube."""
        other = self.__class__(other)

        if self.is_zero:
            quotient = self.__class__.zero
            remainder = self.__class__.zero
        elif not self <= other:
            quotient = self.__class__.zero
            remainder = self
        else:
            cube = [None if x == y else x for x, y in zip(self, other, strict=True)]
            quotient = self.__class__(tuple(cube))
            remainder = self.__class__.zero
        return quotient, remainder

    def cofactor(self, cube: "BaseCube") -> "BaseCube":
        """
        Compute the cofactor of the cube with respect to another cube.

        All cubes are of the same length, so that there is a 1-1 correspondence between
        literals in self and the other cube. If any pair of literals are 0/1 or 1/0,
        then the zero cube is returned. If a literal in the other cube is a don't care,
        then the literal in the cofactor will be passed through from self. Otherwise,
        the literals match and so the cofactor will have a don't care.
        """
        if self.is_zero:
            return self.__class__.zero
        if self.is_one or self == cube:
            return self.__class__.one
        if cube.is_zero:
            return self

        result = []
        for c1, c2 in zip(self, cube, strict=False):
            if (c1 is True and c2 is False) or (c1 is False and c2 is True):
                return self.__class__.zero
            result.append(c1 if c2 is None else None)
        return self.__class__(tuple(result))

    def bit_cofact(self, index: int, *, bit: bool = True) -> "BaseCube":
        """
        Perform cofactor with a one-hot cube.

        In other words, compute the cofactor with respect to a single literal.
        """
        return self.cofactor(self.onehot(index, bit=bit))


def cube_factory(cube_size: int = 3, *, show_dc: bool = False) -> type[BaseCube]:
    """Dynamically create a Cube class with a desired fixed size."""
    if not (isinstance(cube_size, int) and cube_size > 0):
        msg = f"Invalid cube size '{cube_size}'. Must be positive int."
        raise ValueError(msg)

    if not isinstance(show_dc, bool):
        msg = f"Invalid verbose argument '{show_dc}'. Must be bool."
        raise TypeError(msg)

    class Cube(BaseCube):
        __slots__ = ()
        size = cube_size
        verbose = show_dc

    Cube(())
    return Cube


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

    @staticmethod
    def sort_key(cube: BaseCube) -> tuple[int, int, int]:
        """Key command for sorting the cubes of a SOP."""
        if cube.is_zero:
            return 0, 0, 0
        index = next((i for i, x in enumerate(cube) if x is not None), -1)
        return len(cube) - cube.count(None), index, int(not cube[index])

    def __repr__(self) -> str:
        """Represent the sum of products as cubes separated by '+' signs."""
        if len(self) == 0 or all(c.is_zero for c in self):
            return "0"
        cubes = sorted(self, key=self.sort_key)
        return " + ".join([repr(c) for c in cubes])

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

    def cofactor(self, cube: BaseCube) -> "SOP":
        """Compute the cofactor of each cube in the SOP with respect to another cube."""
        return SOP({c.cofactor(cube) for c in self})

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
        cubes = sorted(self, key=lambda x: x.count(None))
        minimals: list[CubeType] = []
        while cubes:
            c1 = cubes.pop(0)
            for c2 in cubes[::-1] + minimals[::-1]:
                if c1 <= c2:  # remove c1 if it is contained by another cube
                    self.remove(c1)
                    break
            if c1 in self:  # c1 was not removed and thus gets saved as a minimal
                minimals.append(c1)

    def complete(self) -> "SOP":
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
        copy = SOP(self.copy())
        while True:
            finished = True
            copy.minimize()
            for consensus in {c1 % c2 for c1, c2 in combinations(copy, 2)}:
                if not (consensus <= copy):
                    copy.add(consensus)
                    finished = False
                    break
            if finished:
                break
        return copy

    def bit_cofact(self, index: int, *, bit: bool = True) -> "SOP":
        """Compute the cofactor of the SOP with respect to a single literal."""
        if len(self) == 0:
            return self
        literal = next(iter(self)).onehot(index, bit=bit)
        return self.cofactor(literal)

    def isTautology(self) -> bool:  # noqa: N802
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
        return SOP(self.copy()).complete().rtautology()

    def rtautology(self, i: int = 0) -> bool:
        """Recursively check if the one and zero cofactors are tautologies."""
        if len(self) == 0 or all(c.is_zero for c in self):
            return False
        if any(c.is_one for c in self):
            return True
        if i >= next(iter(self)).__class__.size:
            return False
        one_cofactor = self.bit_cofact(i, bit=True)
        zero_cofactor = self.bit_cofact(i, bit=False)
        return one_cofactor.rtautology(i + 1) and zero_cofactor.rtautology(i + 1)


Expr = BaseCube | SOP


class BoolTransformer(Transformer[str, Expr]):
    """Boolean expression transformer."""

    def __init__(self, cube_cls: type[BaseCube]) -> None:
        """Initialize a boolean expression transformer for a specific cube type."""
        if not issubclass(cube_cls, BaseCube):
            msg = f"Invalid cube_cls '{cube_cls}'. Must be a BaseCube subclass."
            raise TypeError(msg)
        cube_cls()
        self._cube_cls = cube_cls
        super().__init__()

    @v_args(inline=True)
    def disjunction(self, *args: BaseCube | SOP) -> BaseCube | SOP:
        """OR."""
        return reduce(lambda x, y: x + y, args)

    @v_args(inline=True)
    def conjunction(self, *args: BaseCube | SOP) -> BaseCube | SOP:
        """AND."""
        return reduce(lambda x, y: x * y, args)

    @v_args(inline=True)
    def exor(self, *args: BaseCube | SOP) -> BaseCube | SOP:
        """XOR."""
        return reduce(lambda x, y: ~x * y + x * ~y, args)

    @v_args(inline=True)
    def complement(self, arg: BaseCube) -> BaseCube | SOP:
        """NOT."""
        return ~arg

    @v_args(inline=True)
    def group(self, arg: BaseCube) -> BaseCube:
        """PASS."""
        return arg

    @v_args(inline=True)
    def literal(self, value: str) -> BaseCube:
        """Variable name."""
        lit = str(value)
        if lit == "0":
            return self._cube_cls.zero
        if lit == "1":
            return self._cube_cls.one

        if lit in self._cube_cls.varlist:
            index = self._cube_cls.varlist.index(lit)
        elif len(self._cube_cls.varlist) >= self._cube_cls.size:
            msg = f"Cube varlist has already reached max size '{self._cube_cls.size}'"
            raise ValueError(msg)
        else:
            index = len(self._cube_cls.varlist)
            self._cube_cls.varlist.append(lit)
        return self._cube_cls.onehot(index)


def parse_bool_expr(expr: str, cube_cls: type[BaseCube] = BaseCube) -> Expr:
    """Parse a boolean expression using Lark."""
    parser = Lark(GRAMMER, parser="lalr", transformer=BoolTransformer(cube_cls))
    try:
        token = parser.parse(expr).children[-1]
        if isinstance(token, BaseCube | SOP):
            return token
        msg = f"Parse result is of invalid type '{type(token)}'"
        raise TypeError(msg)
    except exceptions.LarkError as e:
        msg = "Error parsing Boolean expression."
        raise ValueError(msg) from e
