"""Class for transforming a Boolean expression string into a Cube or SOP."""

from functools import reduce

from lark import Transformer, v_args

from .exceptions import InvalidLiteralError
from .factory import sop_factory
from .invert import one_hot
from .sop import BaseSOP


class BoolExprTransformer(Transformer[str, BaseSOP]):
    """Boolean expression transformer."""

    def __init__(self, size: int = 6, literals: tuple[str, ...] = ()) -> None:
        """Initialize a boolean expression transformer for a specific cube type."""
        self._sop = sop_factory(size, literals)
        super().__init__()

    @v_args(inline=True)
    def disjunction(self, *args: BaseSOP) -> BaseSOP:
        """OR."""
        return reduce(lambda x, y: x + y, args)

    @v_args(inline=True)
    def conjunction(self, *args: BaseSOP) -> BaseSOP:
        """AND."""
        return reduce(lambda x, y: x * y, args)

    @v_args(inline=True)
    def exor(self, *args: BaseSOP) -> BaseSOP:
        """XOR."""
        return reduce(lambda x, y: ~x * y + x * ~y, args)

    @v_args(inline=True)
    def complement(self, arg: BaseSOP) -> BaseSOP:
        """NOT."""
        return ~arg

    @v_args(inline=True)
    def group(self, arg: BaseSOP) -> BaseSOP:
        """PASS."""
        return arg

    @v_args(inline=True)
    def literal(self, name: str) -> BaseSOP:
        """Variable name."""
        if name == "0":
            return self._sop({self._sop.cube.zero()})
        if name == "1":
            return self._sop({self._sop.cube.one()})

        literals = self._sop.cube.literals()
        if name not in literals:
            raise InvalidLiteralError(name, literals)
        bits = one_hot(self._sop.cube.size(), literals.index(name))
        return self._sop({self._sop.cube(bits)})
