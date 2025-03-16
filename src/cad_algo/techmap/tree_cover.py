"""Class for holding the cover of a AIG circuit using library cells."""

from .cell_lib import CellLib
from .rooted_dag import RootedDAG
from .tree_node import TreeNode

LeafMap = dict[TreeNode, TreeNode]


class TreeCover:
    """Track the cost of mapping circuit nodes to library cells."""

    def __init__(self, circuit: RootedDAG, library: CellLib) -> None:
        """Create a new tree cover and initialize the cost for every circuit node."""
        self._cost = {x: 0 if x.is_type("leaf") else -1 for x in circuit.nodes}
        self._libcells: dict[TreeNode, str] = {}
        self._leaves: dict[TreeNode, LeafMap] = {}
        self._library = library

    def get_subject(self) -> TreeNode | None:
        """Find a node with negative cost whose ancestors all have non-negative cost."""
        for node in (k for k, v in self._cost.items() if v < 0):
            if all(self._cost[x] >= 0 for x in node.ancenstors):
                return node
        return None

    def try_cell(self, node: TreeNode, libcell: str, leaf_map: LeafMap) -> None:
        """See if a matched libcell yields a new minimum cost."""
        cost = self._library[libcell][1] + sum(self._cost[u] for u in leaf_map)
        if cost < self._cost[node] or self._cost[node] == -1:
            self._cost[node] = cost
            self._libcells[node] = libcell
            self._leaves[node] = leaf_map
