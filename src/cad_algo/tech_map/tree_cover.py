"""Class for holding the cover of an AIG circuit using a standard cell library."""

from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx

from .cell_lib import CellLib
from .rooted_dag import RootedDAG
from .tree_node import TreeNode

# Key is a circuit's node and value is a mapping to a node in the libcell
LeafMap = dict[TreeNode, TreeNode]


class TreeCover:
    """Class for tracking the cost of covering a RootedDAG node with a standard cell."""

    def __init__(self, circuit: RootedDAG, library: CellLib) -> None:
        """
        Create a cover of a RootedDAG circuit with a specified standard cell library.

        Each node in the circuit has a cost associated with it that represents the total
        cell area of the subtree rooted at the node. The cost of a leaf node is 0 since
        a leaf is just a circuit input pin which does not consume area. The initial cost
        of all gate nodes is -1. The cost is updated when a matching libcell is found
        for the node.

        The libcell associated with a node represents a cell from standard cell library
        which matches a partial of the subtree rooted at the node.

        Each node also has a leaf map dictionary which maps nodes in the circuit to the
        inputs of the libcell for the node. This enables traversal of the circuit from
        one libcell to the next.

        Parameters
        ----------
        circuit : RootedDAG
            A decomposed combinatorial circuit with a single output.
        library : CellLib
            A standard cell library to use to cover the circuit with.

        Returns
        -------
        None

        Raises
        ------
        TypeError
            If any node in the circuit is not a TreeNode object.

        """
        self._circuit = circuit
        self._library = library

        self._cost: dict[TreeNode, int] = {}
        self._libcells: dict[TreeNode, str] = {}
        self._leaves: dict[TreeNode, LeafMap] = {}

        for node in circuit.nodes():
            if not isinstance(node, TreeNode):
                msg = f"node '{node}' in circuit '{circuit}' is not a TreeNode object."
                raise TypeError(msg)
            self._cost[node] = 0 if node.is_type("leaf") else -1

    @property
    def total_cost(self) -> int:
        """
        Return the total area of the standard cell cover of the circuit.

        Since the cost of a node represents the total area of the subtree rooted at that
        node. The total area of the circuit is the cost at the root (output) of the
        circuit.
        """
        return self._cost[self._circuit.root]

    @property
    def cover_graph(self) -> nx.DiGraph:  # type: ignore # noqa: PGH003
        """
        Return a graph which represents the optimal cover of the circuit.

        Returns
        -------
        nx.DiGraph
            A directed graph where each node is a cell from the standard cell library.

        See Also
        --------
        _get_cover_graph

        """
        cover = nx.DiGraph()  # type: ignore # noqa: PGH003
        return self._get_cover_graph(cover, self._circuit.root)

    def _get_cover_graph(self, cover: nx.DiGraph, node: TreeNode) -> nx.DiGraph:  # type: ignore # noqa: PGH003
        """
        Recursively move through the circuit to connect libcells together.

        Parameters
        ----------
        cover : nx.DiGraph
            A directed graph where the nodes are the names of cells from the standard
            cell library.
        node : TreeNode
            The current node in the circuit that the function is examining.

        Returns
        -------
        nx.DiGraph
            The input cover graph is returned after edges have recursively been added
            to the graph by the function.

        The function will add nodes for the libcell of the input node and for the
        libcell's of the leaves of the input node. Edges are added connecting the
        leaves to the input node.

        A recursive loop is formed by then processing the leaf nodes. The function
        loops until the leaves (input pins) of the circuit are reached.

        """
        libcell_v = self._libcells[node]
        for subject in self._leaves[node]:
            if subject.is_type("leaf"):
                cover.add_edge(subject.name, libcell_v)
            else:
                libcell_u = self._libcells[subject]
                cover.add_edge(libcell_u, libcell_v)
                self._get_cover_graph(cover, subject)
        return cover

    def get_subject(self) -> TreeNode | None:
        """
        Find a node with negative cost whose ancestors all have non-negative cost.

        Returns
        -------
        TreeNode | None
            A node in the circuit with negative cost and non-negative ancestors.
            The function returns None if there are no negative cost nodes remaining in
            the circuit.

        """
        for node in (k for k, v in self._cost.items() if v < 0):
            if all(self._cost[x] >= 0 for x in node.ancestors):
                return node
        return None

    def try_cell(self, node: TreeNode, libcell: str, leaf_map: LeafMap) -> None:
        r"""
        Calculate the cost of a libcell and compare against the node's current cost.

        Parameters
        ----------
        node : TreeNode
            A node in the circuit.
        libcell : str
            The name of a cell from the standard cell library which matches with the
            input node.
        leaf_map : dict[TreeNode, TreeNode]
            A mapping from nodes in the circuit to the input pin(s) of the libcell.

        Returns
        -------
        None

        The cost of pairing the libcell with the node is as follows:
        .. math::
            cost(node) = area(libcell) + \sum_{u \in leaf_map} cost(u)

        If this is the first libcell to match with the node (cost = -1) or if the cost
        is less than the current cost of the node, then the cost is updated and the
        libcell/leaf_map are saved.

        If two libcells yield the same cost, the libcell with the higher area is chosen.
        This ensures that more complex gates are chosen instead of the decomposed
        version of the complex gate.

        If two libcells yield the same cost and have the same area. The libcell with the
        lower depth (levels of logic) is chosen. A gate with a lower depth is better for
        timing.

        """
        libcell_area = self._library[libcell][1]
        cost = libcell_area + sum(self._cost[u] for u in leaf_map)

        new_min = False
        if cost < self._cost[node] or self._cost[node] == -1:
            new_min = True
        elif cost == self._cost[node]:
            current = self._libcells[node]
            current_area = self._library[current][1]
            if libcell_area > current_area:
                new_min = True
            elif libcell_area == current_area:
                libcell_depth = nx.dag_longest_path(self._library[libcell][0])
                current_depth = nx.dag_longest_path(self._library[current][0])
                new_min = len(libcell_depth) < len(current_depth)

        if new_min:
            self._cost[node] = cost
            self._libcells[node] = libcell
            self._leaves[node] = leaf_map

    def draw(self, outfile: Path) -> None:
        """
        Draw the circuit using the optimal cover of the circuit.

        Parameters
        ----------
        outfile : pathlib.Path
            File path to save the plot of the graph to.

        Returns
        -------
        None

        See Also
        --------
        cover_graph

        """
        cover = self.cover_graph
        pos = nx.nx_agraph.graphviz_layout(cover, prog="dot", args="-Grankdir=LR")
        plt.figure(figsize=(6, 4))
        nx.draw(
            cover,
            pos,
            with_labels=True,
            node_size=2000,
            node_color="lightblue",
            font_size=10,
            edge_color="gray",
        )
        plt.savefig(outfile)
