"""Grammer definition for a lark parser that can read boolean expressions."""

from lark import Lark, ParseTree, exceptions

from .bool_transformer import BoolTransformer
from .cube import BaseCube

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


def parse_bool_expr(expression: str, *, cube_cls: type[BaseCube]) -> ParseTree:
    """Parse a boolean expression using Lark."""
    parser = Lark(GRAMMER, parser="lalr", transformer=BoolTransformer(cube_cls))
    try:
        parser.parse(expression)
    except exceptions.LarkError as e:
        return f"Error parsing expression: {e}"
