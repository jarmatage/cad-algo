"""Class for representing a single node in a rooted DAG."""

from collections.abc import Generator
from dataclasses import dataclass
from typing import Literal

import networkx as nx

NodeType = Literal["leaf", "inv", "nand"]


@dataclass(frozen=True, slots=True)
class TreeNode:
    """Immutable, slotted, dataclass for a single node in a RootedDAG."""

    name: str
    graph: nx.DiGraph  # type: ignore # noqa: PGH003

    def __str__(self) -> str:
        """Return the node type followed by the name of the node."""
        return f"{self.node_type} {self.name}"

    @property
    def ancestors(self) -> Generator["TreeNode"]:
        """Yield all the ancestors of the TreeNode in the RootedDAG."""
        yield from (x for x in nx.ancestors(self.graph, self))

    @property
    def degree(self) -> int:
        """Return the number of predecessors the TreeNode has."""
        degree = self.graph.in_degree(self)
        if not isinstance(degree, int):
            msg = f"expected integer for degree of DAG node '{self.name}'"
            raise TypeError(msg)
        return degree

    @property
    def node_type(self) -> NodeType:
        """
        Return the node type of the TreeNode.

        The node type is determined by the number of predecessors the TreeNode has:
            - A leaf node (circuit input pin) has 0 predecessors.
            - An inverter gate has 1 predecessor.
            - A NAND2 gate has 2 predecessors.

        No other gate types are allowed and thus no TreeNode should have greater than 2
        predecessors.

        Returns
        -------
        Literal["leaf", "inv", "nand"]

        """
        if self.degree == 2:  # noqa: PLR2004
            return "nand"
        return "inv" if self.degree == 1 else "leaf"

    @property
    def inv_parent(self) -> "TreeNode":
        """
        Get the parent of an inverter node in the graph.

        This function assumes the user has already verified the node type is 'inv'.
        The function will not work as expected if called on a non-inveter node.

        Returns
        -------
        TreeNode
            The direct predecessor of the INV TreeNode in the RootedDAG.

        """
        parent = next(iter(self.graph.predecessors(self)))
        return self.check_node(parent)

    @property
    def nand_parents(self) -> tuple["TreeNode", "TreeNode"]:
        """
        Get the parents of a NAND2 node in the graph.

        This function assumes the user has already verified the node type is 'nand'.
        The function will not work as expected if called on a non-nand2 node.

        Returns
        -------
        tuple[TreeNode, TreeNode]
            The direct predecessors of the NAND2 TreeNode in the RootedDAG.

        """
        left, right = self.graph.predecessors(self)
        return self.check_node(left), self.check_node(right)

    def is_type(self, node_type: NodeType) -> bool:
        """
        Check if the node is of a specified node type.

        Parameters
        ----------
        node_type : Literal["leaf", "inv", "nand"]
            The node type to check for.

        Returns
        -------
        bool
            Indicates the node is the specified node type.

        """
        return self.node_type == node_type

    @staticmethod
    def check_node(node: "TreeNode") -> "TreeNode":
        """
        Ensure an object is of the TreeNode type.

        Parameters
        ----------
        node : TreeNode
            The TreeNode object to validate.

        Returns
        -------
        TreeNode
            The input TreeNode object is passed through the function.

        Raises
        ------
        TypeError
            If the input object is not a TreeNode.

        """
        if not isinstance(node, TreeNode):
            msg = f"node '{node}' must be of type TreeNode"
            raise TypeError(msg)
        return node
