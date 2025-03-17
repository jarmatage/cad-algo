"""Class for creating and working with rooted, directed, acyclic graphs (DAGs)."""

from collections.abc import Iterable
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx

from .tree_node import TreeNode


class RootedDAG(nx.DiGraph):  # type: ignore # noqa: PGH003
    """Subclass of nx.DiGraph for rooted directed, acyclic graphs (DAGs)."""

    def __init__(self, edges: Iterable[tuple[str, str]]) -> None:
        """
        Create a directed, acyclic, rooted graph (DAG) with network X.

        Parameters
        ----------
        edges : Iterable[tuple[str, str]]
            An iterable of node name pairs

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If any input edge does not consist of exactly two elements.
            If the resulting directed graph is not rooted.
        TypeError
            If the name of any node in an input edge is not a string.

        """
        super().__init__()

        # Ensure the input is a valid list of edges
        for edge in edges:
            if len(edge) != 2:  # noqa: PLR2004
                msg = f"invalid rooted DAG edge '{edge}', must be of length 2"
                raise ValueError(msg)
            for node in edge:
                if not isinstance(node, str):
                    msg = f"invalid node '{node}' in edge '{edge}', must be string"
                    raise TypeError(msg)
            parent = TreeNode(edge[0], self)
            child = TreeNode(edge[1], self)
            self.add_edge(parent, child)

        # Ensure the DiGraph is rooted
        roots = {x for x in self.nodes() if self.out_degree(x) == 0}
        if len(roots) != 1:
            msg = f"rooted DAG has multiple roots '{roots}', must only have one"
            raise ValueError(msg)
        self.root = roots.pop()

    def draw(self, outfile: Path) -> None:
        """
        Draw the rooted DAG using graphviz and matplotlib.

        Parameters
        ----------
        outfile : pathlib.Path
            File path to save the plot of the graph to.

        Returns
        -------
        None

        """
        pos = nx.nx_agraph.graphviz_layout(self, prog="dot", args="-Grankdir=LR")
        plt.figure(figsize=(6, 4))
        nx.draw(
            self,
            pos,
            with_labels=True,
            node_size=2000,
            node_color="lightblue",
            font_size=10,
            edge_color="gray",
        )
        plt.savefig(outfile)
