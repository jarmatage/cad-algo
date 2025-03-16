"""Class for representing a single node in a rooted DAG."""

from collections.abc import Generator
from dataclasses import dataclass
from typing import Literal

import networkx as nx

NodeType = Literal["leaf", "inv", "nand"]

# Key is a circuit's node and value is a mapping to a node in the libcell
LeafMap = dict["TreeNode", "TreeNode"]


@dataclass(frozen=True, slots=True)
class TreeNode:
    """A node with a reference back to the DAG graph that it is a part of."""

    name: str
    graph: nx.DiGraph  # type: ignore # noqa: PGH003

    def __str__(self) -> str:
        """Display the name of the node."""
        return f"{self.node_type} {self.name}"

    @property
    def ancenstors(self) -> Generator["TreeNode"]:
        """Yield all the ancestors in the graph of this DAG node."""
        yield from (x for x in nx.ancestors(self.graph, self.name))

    @property
    def degree(self) -> int:
        """Return the number of parents the node has."""
        degree = self.graph.in_degree(self)
        if not isinstance(degree, int):
            msg = f"expected integer for degree of DAG node '{self.name}'"
            raise TypeError(msg)
        return degree

    @property
    def node_type(self) -> NodeType:
        """Return the node type of a node in the DAG."""
        if self.degree == 2:  # noqa: PLR2004
            return "nand"
        return "inv" if self.degree == 1 else "leaf"

    @property
    def inv_parent(self) -> "TreeNode":
        """Get the parent of an inverter node in the graph."""
        parent = next(iter(self.graph.predecessors(self)))
        return self.check_node(parent)

    @property
    def nand_parents(self) -> tuple["TreeNode", "TreeNode"]:
        """Get the parents of a NAND2 node in the graph."""
        left, right = self.graph.predecessors(self)
        return self.check_node(left), self.check_node(right)

    def is_type(self, node_type: NodeType) -> bool:
        """Check if the node is of a specified type."""
        return self.node_type == node_type

    @staticmethod
    def check_node(node: "TreeNode") -> "TreeNode":
        """Ensure a node is of the TreeNode type."""
        if not isinstance(node, TreeNode):
            msg = f"node '{node}' must be of type TreeNode"
            raise TypeError(msg)
        return node
