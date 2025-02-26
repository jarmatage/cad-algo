"""Class definition for a tuple to represent a Boolean cube."""

from .algebra_typing import Bits, BitSequence
from .cofact import cube_cofact
from .consensus import cube_consensus
from .containment import cube_containment
from .div import cube_div
from .exceptions import CubeLenError
from .invert import one_hot
from .literal import fill_literals, repr_cube
from .mul import cube_mul


class BaseCube:
    """Holds a tuple of a specified length."""

    __slots__: tuple[str, ...] = ("_bits",)
    _size: int = 6
    _literals: tuple[str, ...] = tuple("abcdef")

    @classmethod
    def size(cls) -> int:
        """Return the dimension of the cube class."""
        return cls._size

    @classmethod
    def literals(cls) -> list[str]:
        """Return the class literal names with blank entries filled in."""
        return fill_literals(cls._literals, cls._size)

    @classmethod
    def zero(cls) -> "BaseCube":
        """Return a cube that represents a boolean 0."""
        return cls()

    @classmethod
    def one(cls) -> "BaseCube":
        """Return a cube that represents a boolean 1."""
        return cls((None,) * cls._size)

    @classmethod
    def literal(cls, index: int, *, bit: bool = True) -> "BaseCube":
        """Return a cube that represents a single literal."""
        return cls(one_hot(cls._size, index, bit=bit))

    def __new__(cls, bits: BitSequence = ()) -> "BaseCube":
        """Ensure the input is the correct size."""
        if len(bits) == 0 or len(bits) == cls._size:
            return super().__new__(cls)
        raise CubeLenError(bits, cls._size)

    def __init__(self, bits: BitSequence = ()) -> None:
        """Initialize a new cube object."""
        self._bits = tuple(None if x is None else bool(x) for x in bits)

    @property
    def bits(self) -> Bits:
        """Return the bits of the cube object."""
        return self._bits

    def __eq__(self, other: object) -> bool:
        """Return True if another cube is equal to this cube."""
        if isinstance(other, self.__class__):
            return self.bits == other.bits
        if other == 1:
            return all(x is None for x in self.bits)
        if other == 0:
            return len(self.bits) == 0
        return NotImplemented

    def __ge__(self, other: object) -> bool:
        """Return True if another cube is contained in this cube."""
        if not isinstance(other, self.__class__):
            return NotImplemented
        return cube_containment(self.bits, other.bits)

    def __gt__(self, other: object) -> bool:
        """Return True if another cube is properly contained in this cube."""
        return other <= self and other != self

    def __hash__(self) -> int:
        """Hash the cube based upon the bits tuple."""
        return hash(self.bits)

    def __mod__(self, other: object) -> "BaseCube":
        """Compute the consensus between this cube and another cube."""
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__class__(cube_consensus(self.bits, other.bits))

    def __mul__(self, other: object) -> "BaseCube":
        """Compute the product between this cube and another."""
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__class__(cube_mul(self.bits, other.bits))

    def __repr__(self) -> str:
        """Represent the Cube as a string of literals."""
        return repr_cube(self.bits, self.literals())

    def __str__(self) -> str:
        """Return repr but don't cares are not displayed."""
        return repr(self).replace("-", "")

    def __truediv__(self, other: object) -> tuple["BaseCube", "BaseCube"]:
        """Compute the quotient and remainder of this cube divided by another cube."""
        if not isinstance(other, self.__class__):
            return NotImplemented
        quotient, remainder = cube_div(self.bits, other.bits)
        return self.__class__(quotient), self.__class__(remainder)

    def cofact(self, other: object) -> "BaseCube":
        """Compute the cofactor of the cube with respect to another cube."""
        if not isinstance(other, self.__class__):
            raise NotImplementedError
        return self.__class__(cube_cofact(self.bits, other.bits))

    def literal_cofact(self, index: int, *, bit: bool = True) -> "BaseCube":
        """Perform cofact with a cube that is a single literal."""
        literal = one_hot(self.__class__.size(), index, bit=bit)
        return self.__class__(cube_cofact(self.bits, literal))
