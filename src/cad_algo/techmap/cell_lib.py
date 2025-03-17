"""
The default standard cell library for CAD Algo.

The CELL_LIB constant holds the default library which has the following standard cells:
    - INV
    - NAND2
    - AND2
    - NAND4-A
    - NAND4-B
    - OR2
    - NOR2
    - AOI22
    - AOI21

A standard cell library is defined as a dictionary where the keys are standard cell
names and the values are tuples of cell information.

CellLib Parameters
------------------
key : str
    The name of the standard cell.
value[0] : RootedDAG
    The decomposed DAG structure of the standard cell.
value[1] : int
    The area of the standard cell.

The CellLib type hint can be used to indicate a variable contains a dictionary for a
standard cell library.

"""

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
