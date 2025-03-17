"""Unit tests for the tree covering algorithm."""  # noqa: INP001

import argparse
from pathlib import Path

from tech_map.algorithms import MinAreaCover
from tech_map.cell_lib import CELL_LIB
from tech_map.rooted_dag import RootedDAG
from tech_map.tree_node import TreeNode

# ruff: noqa: S101, SLF001, PLR2004
PLOT_DIR = Path(__file__).parent / "plots"


def get_node(circuit: RootedDAG, name: str) -> TreeNode:
    """Get a node from a circuit by the name of the node."""
    node = [x for x in circuit.nodes() if x.name == name]
    assert isinstance(node[0], TreeNode)
    return node[0]


def test_cover(*, plot: bool = False) -> None:
    """Run unit tests on the tree covering algorithm."""
    for cell in CELL_LIB:
        dag = CELL_LIB[cell][0]
        cover = MinAreaCover(dag, CELL_LIB)
        assert cover.total_cost == CELL_LIB[cell][1]
        assert cover._libcells[dag.root] == cell
        if plot:
            cover.draw(PLOT_DIR / f"{cell}_cover.png")
    # NAND6
    nand6 = RootedDAG(
        [
            ("s1", "s7"),
            ("s2", "s7"),
            ("s3", "s8"),
            ("s4", "s8"),
            ("s5", "s9"),
            ("s6", "s9"),
            ("s7", "s10"),
            ("s8", "s11"),
            ("s9", "s12"),
            ("s10", "s13"),
            ("s11", "s13"),
            ("s12", "s15"),
            ("s13", "s14"),
            ("s14", "s15"),
        ]
    )

    cover = MinAreaCover(nand6, CELL_LIB)
    assert cover.total_cost == 12
    assert cover._libcells[get_node(nand6, "s13")] == "NAND4-A"
    assert cover._libcells[get_node(nand6, "s15")] == "OR2"
    assert cover._libcells[get_node(nand6, "s9")] == "NAND2"
    if plot:
        cover.draw(PLOT_DIR / "nand6_cover.png")

    # OR4
    or4 = RootedDAG(
        [
            ("s1", "s5"),
            ("s2", "s6"),
            ("s3", "s7"),
            ("s4", "s8"),
            ("s5", "s9"),
            ("s6", "s9"),
            ("s7", "s10"),
            ("s8", "s10"),
            ("s9", "s11"),
            ("s10", "s12"),
            ("s11", "s13"),
            ("s12", "s13"),
        ]
    )

    cover = MinAreaCover(or4, CELL_LIB)
    assert cover.total_cost == 9
    assert cover._libcells[get_node(or4, "s13")] == "NAND4-A"
    assert cover._libcells[get_node(or4, "s5")] == "INV"
    assert cover._libcells[get_node(or4, "s10")] == "OR2"
    if plot:
        cover.draw(PLOT_DIR / "or4_cover.png")

    # AOI22 + AND2
    aoi22_and2 = RootedDAG(
        [
            ("s1", "s6"),
            ("s2", "s6"),
            ("s3", "s7"),
            ("s4", "s7"),
            ("s5", "s10"),
            ("s6", "s8"),
            ("s7", "s8"),
            ("s8", "s9"),
            ("s9", "s10"),
            ("s10", "s11"),
        ]
    )

    cover = MinAreaCover(aoi22_and2, CELL_LIB)
    assert cover.total_cost == 9
    assert cover._libcells[get_node(aoi22_and2, "s9")] == "AOI22"
    assert cover._libcells[get_node(aoi22_and2, "s10")] == "NAND2"
    assert cover._libcells[get_node(aoi22_and2, "s11")] == "AND2"
    if plot:
        cover.draw(PLOT_DIR / "aoi22_and2_cover.png")

    # AOB21
    aob21 = RootedDAG(
        [
            ("s1", "s4"),
            ("s2", "s4"),
            ("s3", "s5"),
            ("s4", "s6"),
            ("s5", "s6"),
        ]
    )

    cover = MinAreaCover(aob21, CELL_LIB)
    assert cover.total_cost == 7
    assert cover._libcells[get_node(aob21, "s4")] == "NAND2"
    assert cover._libcells[get_node(aob21, "s5")] == "INV"
    assert cover._libcells[get_node(aob21, "s6")] == "NAND2"
    if plot:
        cover.draw(PLOT_DIR / "aob21_cover.png")

    # AOB21 w/new lib cell
    aob21_lib = {
        "AOB21": (
            RootedDAG(
                [
                    ("p1", "p4"),
                    ("p2", "p4"),
                    ("p3", "p5"),
                    ("p4", "p6"),
                    ("p5", "p6"),
                ]
            ),
            6,
        )
    }

    cover = MinAreaCover(aob21, CELL_LIB | aob21_lib)
    assert cover.total_cost == 6
    assert cover._libcells[get_node(aob21, "s4")] == "NAND2"
    assert cover._libcells[get_node(aob21, "s5")] == "INV"
    assert cover._libcells[get_node(aob21, "s6")] == "AOB21"
    if plot:
        cover.draw(PLOT_DIR / "aob21_cover_modified_lib.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="test the tree matching algorithm")
    parser.add_argument(
        "--plot", action="store_true", help="enable plotting the test DAGs."
    )
    args = parser.parse_args()
    test_cover(plot=args.plot)
