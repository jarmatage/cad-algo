"""Algorithms for technology mapping with respect to area optimization."""

from .cell_lib import CellLib
from .rooted_dag import RootedDAG
from .tree_cover import LeafMap, TreeCover
from .tree_node import TreeNode


def Match(s: TreeNode, p: TreeNode) -> tuple[bool, LeafMap]:  # noqa: N802
    """
    Recursively check if the nodes of a pattern match the nodes of a subject.

    Parameters
    ----------
    s : TreeNode
        A node from a RootedDAG which represents a combinatorial circuit with a single
        output.
    p : TreeNode
        A node from the RootedDAG of a cell in a standard cell library. This should
        always be the root of the standard cell if the user is calling the function.

    Returns
    -------
    bool
        True if the pattern node matched with the subject node. This means that there
        exists a subtree of the subject node which is isomorphic with the tree under the
        pattern node.
    dict[TreeNode, TreeNode]
        A mapping of nodes from the subject tree to the leaf nodes of the pattern tree.

    This function essentially checks if two trees are isomorphic.
    Two nodes do not match if they do not have the same number of predecessors.
    If the subject and pattern have the same number of predecessors then we must then
    check if the predecessor nodes match until we have checked all ancestors.

    For nodes with 2 predecessors, both possible tree mappings need to be checked:
        - s_left to p_left and s_right to p_right
        - s_left to p_right and s_right to p_left

    If the pattern node is a leaf node. We always return True and return a dictionary
    which maps the subject node to the pattern node. This dictionary is recursively
    merged together with other function call outputs to yield a final leaf map for the
    pattern tree.

    """
    if p.is_type("leaf"):
        return True, {s: p}
    if s.is_type("leaf") or s.degree != p.degree:
        return False, {}
    if s.is_type("inv"):
        return Match(s.inv_parent, p.inv_parent)

    sleft, sright = s.nand_parents
    pleft, pright = p.nand_parents

    match_l, leaves_l = Match(sleft, pleft)
    match_r, leaves_r = Match(sright, pright)
    if match_l and match_r:
        return True, leaves_l | leaves_r

    match_l, leaves_l = Match(sleft, pright)
    match_r, leaves_r = Match(sright, pleft)
    return match_l and match_r, leaves_l | leaves_r


def MinAreaCover(Circuit: RootedDAG, Library: CellLib) -> TreeCover:  # noqa: N802, N803
    """
    Compute the minimum area cover of a decomposed circuit tree.

    Parameters
    ----------
    Circuit : RootedDAG
        A circuit with a single output which has been decomposed into nand2 and
        inverter gates (AIG form).
    Library : CellLib
        A standard cell library to cover the circuit with.

    Returns
    -------
    TreeCover
        A TreeCover object where the cost dictionary and libcell mapping has been
        optimized for standard cell area.

    The function iterates through all gate nodes in the circuit, starting with the gates
    that connect directly to the leafs (input pins) of the circuit. All cells in the
    standard cell library are matched against the gate node. The matching standard cell
    with the best area cost is then associated with the gate node. This process repeats
    until the root (output pin) of the circuit is reached.

    The area cost of mapping a standard cell to a circuit node represents the total area
    of the tree under the circuit node. This means the most complex gate which matches
    with the circuit node is not always the best choice. It may be better to choose a
    simpler gate if that gate then connects to complex gates further down in the tree.

    See Also
    --------
    TreeCover

    """
    cover = TreeCover(Circuit, Library)
    while (subject := cover.get_subject()) is not None:
        for cell, pattern in Library.items():
            is_match, leaf_map = Match(subject, pattern[0].root)
            if is_match:
                cover.try_cell(subject, cell, leaf_map)
    return cover
