"""Class for parsing boolean expressions with Lark."""

from lark import Lark, exceptions

from .exceptions import BoolExprParseError
from .sop import BaseSOP
from .transformer import BoolExprTransformer

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


class Parser:
    """Boolean expression parser."""

    def __init__(self, size: int = 6, literals: tuple[str, ...] = ()) -> None:
        """Initialize a boolean expression parser for a specific cube type."""
        self._transformer = BoolExprTransformer(size, literals)
        self._lark = Lark(GRAMMER, parser="lalr", transformer=self._transformer)

    def parse(self, expression: str) -> BaseSOP:
        """Parse a boolean expression string using Lark."""
        try:
            token = self._lark.parse(expression).children[-1]
            if isinstance(token, BaseSOP):
                token.minimize()
                return token
            msg = f"Parse result is of invalid type '{type(token)}'"
            raise TypeError(msg)
        except exceptions.LarkError as e:
            raise BoolExprParseError(expression) from e
