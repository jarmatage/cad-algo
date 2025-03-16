"""Standard cell library."""

from .rooted_dag import RootedDAG

CellLib = dict[str, tuple[RootedDAG, int]]

CELL_LIB: CellLib = {
    "INV": (
        RootedDAG(
            [
                ("p1", "p2"),
            ]
        ),
        1,
    ),
    "NAND2": (
        RootedDAG(
            [
                ("p1", "p3"),
                ("p2", "p3"),
            ]
        ),
        3,
    ),
    "AND2": (
        RootedDAG(
            [
                ("p1", "p3"),
                ("p2", "p3"),
                ("p3", "p4"),
            ]
        ),
        4,
    ),
    "NAND4-A": (
        RootedDAG(
            [
                ("p1", "p5"),
                ("p2", "p5"),
                ("p3", "p6"),
                ("p4", "p6"),
                ("p5", "p7"),
                ("p6", "p8"),
                ("p7", "p9"),
                ("p8", "p9"),
            ]
        ),
        5,
    ),
    "NAND4-B": (
        RootedDAG(
            [
                ("p1", "p5"),
                ("p2", "p5"),
                ("p3", "p7"),
                ("p4", "p9"),
                ("p5", "p6"),
                ("p6", "p7"),
                ("p7", "p8"),
                ("p8", "p9"),
            ]
        ),
        5,
    ),
    "OR2": (
        RootedDAG(
            [
                ("p1", "p3"),
                ("p2", "p4"),
                ("p3", "p5"),
                ("p4", "p5"),
            ]
        ),
        4,
    ),
    "NOR2": (
        RootedDAG(
            [
                ("p1", "p3"),
                ("p2", "p4"),
                ("p3", "p5"),
                ("p4", "p5"),
                ("p5", "p6"),
            ]
        ),
        5,
    ),
    "AOI22": (
        RootedDAG(
            [
                ("p1", "p5"),
                ("p2", "p5"),
                ("p3", "p6"),
                ("p4", "p6"),
                ("p5", "p7"),
                ("p6", "p7"),
                ("p7", "p8"),
            ]
        ),
        5,
    ),
    "AOI21": (
        RootedDAG(
            [
                ("p1", "p4"),
                ("p2", "p4"),
                ("p3", "p5"),
                ("p4", "p6"),
                ("p5", "p6"),
                ("p6", "p7"),
            ]
        ),
        5,
    ),
}
