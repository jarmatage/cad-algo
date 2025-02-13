"""Class for transforming a boolean expression."""

from functools import reduce

from lark import Transformer, v_args

from .cube import BaseCube
from .sop import SOP


class BoolTransformer(Transformer[str, BaseCube | SOP]):
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
