"""Exceptions to throw when performing boolean algebra."""

from collections.abc import Sequence


class CubeLenError(ValueError):
    """Flag when the input data for creating a cube is too long."""

    def __init__(self, cube: Sequence[bool | None], size: int) -> None:
        """Pass message to ValueError exception."""
        msg = f"Invalid cube '{cube}'. Cube must be empty or have exactly {size} items."
        super().__init__(msg)


class LiteralLenError(ValueError):
    """Flag when there are too many literals in a cube class."""

    def __init__(self, literals: list[str], size: int) -> None:
        """Pass message to ValueError exception."""
        msg = f"Invalid literals list '{literals}'. Length must be <= {size}."
        super().__init__(msg)


class LiteralSurplusError(ValueError):
    """Flag when a cube class has exhausted the full alphabet for literal names."""

    def __init__(self, size: int) -> None:
        """Pass message to ValueError exception."""
        msg = f"Full alphabet has been used to represent cube of size '{size}'."
        super().__init__(msg)


class InvalidCubeError(ValueError):
    """Flag when an object that is not a cube is passed to the SOP class."""

    def __init__(self, cube: object) -> None:
        """Pass message to ValueError exception."""
        msg = f"Input '{cube}' to the SOP is not a Cube object."
        super().__init__(msg)


class InvalidSizeError(ValueError):
    """Flag when an invalid cube dimension value is provided."""

    def __init__(self, size: int) -> None:
        """Pass message to ValueError exception."""
        msg = f"Invalid cube size '{size}'. Must be positive int."
        super().__init__(msg)


class InvalidLiteralError(ValueError):
    """Flag when a literal is parsed that is not in the list of known literals."""

    def __init__(self, name: str, literals: list[str]) -> None:
        """Pass message to ValueError exception."""
        msg = f"Invalid literal name '{name}'. Must be from '{literals}'"
        super().__init__(msg)


class BoolExprParseError(ValueError):
    """Flag when a boolean expression parser had an issue parsing a string."""

    def __init__(self, expression: str) -> None:
        """Pass message to ValueError exception."""
        msg = f"Error parsing Boolean expression '{expression}'"
        super().__init__(msg)


class InvalidExprError(TypeError):
    """Flag when a parsing result is not a valid boolean expression."""

    def __init__(self, expr_type: type) -> None:
        """Pass message to TypeError exception."""
        msg = f"Invalid expression type '{expr_type}'. Expected Cube or SOP."
        super().__init__(msg)
