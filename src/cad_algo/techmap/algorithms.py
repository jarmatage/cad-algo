"""Tree matching and covering algorithms."""

from .cell_lib import CellLib
from .rooted_dag import RootedDAG
from .tree_cover import LeafMap, TreeCover
from .tree_node import TreeNode


def match(s: TreeNode, p: TreeNode) -> tuple[bool, LeafMap]:
    """Recursively check if the nodes of a pattern match the nodes of a subject."""
    if p.is_type("leaf"):
        return True, {s: p}
    if s.is_type("leaf") or s.degree != p.degree:
        return False, {}
    if s.is_type("inv"):
        return match(s.inv_parent, p.inv_parent)

    sleft, sright = s.nand_parents
    pleft, pright = p.nand_parents

    match_l, leaves_l = match(sleft, pleft)
    match_r, leaves_r = match(sright, pright)
    if match_l and match_r:
        return True, leaves_l | leaves_r

    match_l, leaves_l = match(sleft, pright)
    match_r, leaves_r = match(sright, pleft)
    return match_l and match_r, leaves_l | leaves_r


def min_area_cover(circuit: RootedDAG, library: CellLib) -> TreeCover:
    """Compute the minimum area cover of a circuit tree."""
    cover = TreeCover(circuit, library)
    while (subject := cover.get_subject()) is not None:
        for cell, pattern in library.items():
            is_match, leaf_map = match(subject, pattern[0].root)
            if is_match:
                cover.try_cell(subject, cell, leaf_map)
    return cover
