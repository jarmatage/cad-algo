"""Classes for directed, acyclic graphes (DAGs)."""

from collections.abc import Generator, Iterable
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx

from .tree_node import TreeNode


class RootedDAG:
    """A DAG with a single output that represents the root node of the graph."""

    def __init__(self, edges: Iterable[tuple[str, str]]) -> None:
        """Create a rooted DAG object."""
        self.graph = nx.DiGraph()  # type: ignore # noqa: PGH003

        # Ensure the input is a valid list of edges
        for edge in edges:
            if len(edge) != 2:  # noqa: PLR2004
                msg = f"invalid rooted DAG edge '{edge}', must be of length 2"
                raise ValueError(msg)
            for node in edge:
                if not isinstance(node, str):
                    msg = f"invalid node '{node}' in edge '{edge}', must be string"
                    raise TypeError(msg)
            parent = TreeNode(edge[0], self.graph)
            child = TreeNode(edge[1], self.graph)
            self.graph.add_edge(parent, child)

        # Ensure the DiGraph is rooted
        roots = {x for x in self.nodes if self.graph.out_degree(x) == 0}
        if len(roots) != 1:
            msg = f"rooted DAG has multiple roots '{roots}', must only have one"
            raise ValueError(msg)
        self.root = roots.pop()

    @property
    def nodes(self) -> Generator[TreeNode]:
        """Generate all TreeNodes from the rooted DAG."""
        yield from self.graph.nodes()

    def get_node(self, name: str) -> TreeNode:
        """Get a TreeNode from the rooted DAG by its node name."""
        node = [x for x in self.nodes if x.name == name]
        if len(node) == 0:
            msg = f"could not find node '{name}' in rooted dag"
            raise KeyError(msg)
        return node.pop()

    def draw(self, outfile: Path) -> None:
        """Draw the DAG."""
        pos = nx.nx_agraph.graphviz_layout(self.graph, prog="dot", args="-Grankdir=LR")
        plt.figure(figsize=(6, 4))
        nx.draw(
            self.graph,
            pos,
            with_labels=True,
            node_size=2000,
            node_color="lightblue",
            font_size=10,
            edge_color="gray",
        )
        plt.savefig(outfile)
