"""Class definition for a tuple to represent a Boolean cube."""

import string
from typing import ClassVar

from .sop import SOP


class BaseCube(tuple):
    """A tuple where all instances must be the same length."""

    __slots__ = ()
    size: int = 3
    verbose: bool = False
    varlist: ClassVar[list[str]] = []
    zero: "BaseCube" = None
    one: "BaseCube" = None

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
        one = [None] * cls.size
        return cls(one[:index] + [bit] + one[index + 1 :])

    def __new__(cls, cube: tuple) -> "BaseCube":
        """
        Ensure the input tuple is the correct size and contains valid values.

        An empty input tuple corresponds to a boolean 0. An input tuple full of None
        corresponds to a boolean 1. Each element of the input tuple must either be True,
        False, or None.
        """
        if cls.zero is None:
            cls.zero = super().__new__(cls, ())
        if cls.one is None:
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

    def __add__(self, other: "BaseCube | SOP") -> "BaseCube | SOP":
        """Add another cube or a sum of products to this cube."""
        if isinstance(other, SOP):
            return other + self
        if self <= other:
            return other
        if other < self:
            return self
        return SOP(self, other).minimal_scc()

    def __invert__(self) -> SOP:
        """Apply De Morgan's law to covert this cube into a sum of products."""
        if self.is_zero:
            return self.__class__.one
        if self.is_one:
            return self.__class__.zero

        cubes = []
        for i, bit in enumerate(self):
            if bit is not None:
                cubes.append(self.__class__.onehot(i, bit=(not bit)))
        return SOP(cubes)

    def __le__(self, other: "BaseCube") -> bool:
        """Return True is this cube is properly contained in another cube."""
        if other.is_zero or self.is_one:
            return False
        if self.is_zero or other.is_one:
            return True
        return other._cofactor(self).is_one

    def __lt__(self, other: "BaseCube") -> bool:
        """Return True if this cube is contained in and not equal to another cube."""
        return self != other and self <= other

    def __mod__(self, other: "BaseCube") -> "BaseCube| None":
        """
        Compute the consensus between this cube and another cube.

        Return None if no consensus exists, otherwise return the consensus cube. Two
        cubes have a consensus, if there is exactly one True literal in one cube and the
        corresponding literal in the other cube is False.
        """
        consensus = []
        found_opposition = False

        for l1, l2 in zip(self, other, strict=False):
            if (l1 == l2) or (l2 is None):  # Explicit match or other don't care
                consensus.append(l1)
            elif l1 is None:  # Self don't care, else must be opposition
                consensus.append(l2)
            elif found_opposition:  # Opposition has already been found; no consensus
                return None
            else:  # First opposition has been found
                found_opposition = True
                consensus.append(None)

        return self.__class__(consensus)

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

    def _cofactor(self, cube: "BaseCube") -> "BaseCube":
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
        return self.__class__(result)


def cube_factory(cube_size: int = 3, *, show_dc: bool = False) -> BaseCube:
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
