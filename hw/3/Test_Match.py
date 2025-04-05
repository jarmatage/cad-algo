"""Unit tests for the tree matching algorithm."""  # noqa: INP001

import argparse
import sys
from pathlib import Path

from tech_map.algorithms import Match
from tech_map.cell_lib import CELL_LIB
from tech_map.rooted_dag import RootedDAG
from tech_map.tree_node import TreeNode

# ruff: noqa: S101
PLOT_DIR = Path(__file__).parent / "plots"


def get_node(circuit: RootedDAG, name: str) -> TreeNode:
    """Get a node from a circuit by the name of the node."""
    node = [x for x in circuit.nodes() if x.name == name]
    assert isinstance(node[0], TreeNode)
    return node[0]


def test_match(*, plot: bool = False) -> None:  # noqa: PLR0915
    """Run unit tests on the tree matching algorithm."""
    for cell in CELL_LIB:
        dag = CELL_LIB[cell][0]
        match, leaves = Match(dag.root, dag.root)
        assert match
        for subject, pattern in leaves.items():
            assert subject == pattern
        if plot:
            dag.draw(PLOT_DIR / f"{cell}.png")

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
    if plot:
        nand6.draw(PLOT_DIR / "nand6.png")

    match, _ = Match(get_node(nand6, "s13"), CELL_LIB["NAND4-A"][0].root)
    assert match
    print("node s13 in nand6 matches NAND4-A")

    match, _ = Match(get_node(nand6, "s15"), CELL_LIB["OR2"][0].root)
    assert match
    print("node s15 in nand6 matches OR2")

    match, _ = Match(get_node(nand6, "s11"), CELL_LIB["AND2"][0].root)
    assert match
    print("node s11 in nand6 matches AND2")

    match, leaves = Match(get_node(nand6, "s14"), CELL_LIB["INV"][0].root)
    assert match
    print("node s14 in nand6 matches INV")

    match, _ = Match(get_node(nand6, "s13"), CELL_LIB["AOI22"][0].root)
    assert not match
    print("node s13 in nand6 does not match AOI22")

    match, leaves = Match(get_node(nand6, "s12"), CELL_LIB["NAND2"][0].root)
    assert not match
    print("node s13 in nand6 does not match NAND2")

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
    if plot:
        or4.draw(PLOT_DIR / "or4.png")

    match, _ = Match(get_node(or4, "s13"), CELL_LIB["NAND4-A"][0].root)
    assert match
    print("node s13 in or4 matches NAND4-A")

    match, _ = Match(get_node(or4, "s9"), CELL_LIB["OR2"][0].root)
    assert match
    print("node s15 in or4 matches OR2")

    match, _ = Match(get_node(or4, "s11"), CELL_LIB["AND2"][0].root)
    assert match
    print("node s11 in or4 matches AND2")

    match, leaves = Match(get_node(or4, "s12"), CELL_LIB["INV"][0].root)
    assert match
    print("node s12 in or4 matches INV")

    match, _ = Match(get_node(or4, "s13"), CELL_LIB["AOI22"][0].root)
    assert not match
    print("node s13 in or4 does not match AOI22")

    match, leaves = Match(get_node(or4, "s8"), CELL_LIB["NAND2"][0].root)
    assert not match
    print("node s13 in or4 does not match AND2")

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
    if plot:
        aoi22_and2.draw(PLOT_DIR / "aoi22_and2.png")

    match, _ = Match(get_node(aoi22_and2, "s9"), CELL_LIB["AOI22"][0].root)
    assert match
    print("node s9 in aoi22_and2 matches AOI22")

    match, _ = Match(get_node(aoi22_and2, "s11"), CELL_LIB["AND2"][0].root)
    assert match
    print("node s11 in aoi22_and2 matches AND2")

    match, _ = Match(get_node(aoi22_and2, "s9"), CELL_LIB["AND2"][0].root)
    assert match
    print("node s9 in aoi22_and2 matches AND2")

    match, leaves = Match(get_node(aoi22_and2, "s6"), CELL_LIB["NAND2"][0].root)
    assert match
    print("node s6 in aoi22_and2 matches NAND2")

    match, _ = Match(get_node(aoi22_and2, "s8"), CELL_LIB["INV"][0].root)
    assert not match
    print("node s8 in aoi22_and2 does not match INV")

    match, leaves = Match(get_node(aoi22_and2, "s10"), CELL_LIB["NAND4-B"][0].root)
    assert not match
    print("node s10 in aoi22_and2 does not match NAND4-A")

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
    if plot:
        aob21.draw(PLOT_DIR / "aob21.png")

    match, _ = Match(get_node(aob21, "s4"), CELL_LIB["NAND2"][0].root)
    assert match
    print("node s4 in aob21 matches NAND2")

    match, leaves = Match(get_node(aob21, "s6"), CELL_LIB["NAND2"][0].root)
    assert match
    print("node s6 in aob21 matches NAND2")

    match, _ = Match(get_node(aob21, "s5"), CELL_LIB["INV"][0].root)
    assert match
    print("node s4 in aob21 matches INV")

    match, leaves = Match(get_node(aob21, "s6"), CELL_LIB["AOI21"][0].root)
    assert not match
    print("node s6 in aob21 does not match AOI21")

    # Create the circuit for HW3 Addendum Q3
    circuit = RootedDAG(
        [
            ("s1", "s9"),
            ("s2", "s9"),
            ("s3", "s10"),
            ("s4", "s10"),
            ("s5", "s11"),
            ("s6", "s12"),
            ("s7", "s12"),
            ("s8", "s15"),
            ("s9", "s13"),
            ("s10", "s13"),
            ("s11", "s16"),
            ("s12", "s14"),
            ("s13", "s16"),
            ("s14", "s15"),
            ("s15", "s18"),
            ("s16", "s17"),
            ("s17", "s18"),
        ]
    )
    if plot:
        circuit.draw(PLOT_DIR / "addendum_circuit.png")

    print("\nHW3 Addendum:")
    print("LibCell, [matching subject nodes]")
    for std_cell in CELL_LIB:
        PrintMatch_Out(circuit, std_cell)
    print("\n")


def PrintMatch_Out(SG: RootedDAG, PG: str) -> None:  # noqa: N802, N803
    """Find all nodes in a subject graph which match with a pattern graph."""
    matches = []
    for node in sorted(SG.nodes, key=lambda x: int(x.name[1:])):
        match, _ = Match(node, CELL_LIB[PG][0].root)
        if match:
            matches.append(node.name)
    print(f"{PG:7}, {matches}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="test the tree matching algorithm")
    parser.add_argument(
        "--plot", action="store_true", help="enable plotting the test DAGs."
    )
    args = parser.parse_args()
    test_match(plot=args.plot)
    sys.exit(0)
