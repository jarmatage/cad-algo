"""Class definition for a list with a maximum possible length."""


class MaxSizeList(list[str]):
    """A list that has a hard cap on the length of the list."""

    def __init__(self, max_size: int) -> None:
        """Initialize a max size list object."""
        self.max_size = max_size
        super().__init__()

    @property
    def max_size(self) -> int:
        """The maximum possible length for the list."""
        return self._max_size

    @max_size.setter
    def max_size(self, new_size: int) -> None:
        if isinstance(new_size, int):
            self._max_size = new_size
        else:
            msg = f"Invalid max size '{new_size}'. Must be int not '{type(new_size)}'."
            raise (TypeError(msg))

    def append(self, item: str) -> None:
        """Add an item to the list, raise an error if the max size has been reached."""
        if len(self) >= self.max_size and item not in self:
            msg = f"List of variables has reached max size {self.max_size}"
            raise ValueError(msg)
        super().append(item)
