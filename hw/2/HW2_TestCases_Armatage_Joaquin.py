#!/usr/bin/env python3
"""
CEN 503: Homework 1 unit tests.

Boolean Algebra Calculator for getting complete cover of expression strings:
https://www.emathhelp.net/calculators/discrete-mathematics/boolean-algebra-calculator/
"""

from HW2_Armatage_Joaquin import SOP, BaseCube, Expr, cube_factory, parse_bool_expr

Cube6 = cube_factory(6, show_dc=False)


def parse_cube(name: str, expr: str, expected: str) -> BaseCube:
    """Parse a cube boolean expression and print the results."""
    result = parse_bool_expr(expr, Cube6)
    print_test(name, expr, result, expected)
    if not isinstance(result, BaseCube):
        msg = f"Result for test '{name}' is not a Cube"
        raise TypeError(msg)
    return result


def parse_sop(name: str, expr: str, expected: str) -> SOP:
    """Parse a SOP boolean expression and print the results."""
    result = parse_bool_expr(expr, Cube6)
    print_test(name, expr, result, expected)
    if not isinstance(result, SOP):
        msg = f"Result for test '{name}' is not a SOP"
        raise TypeError(msg)
    return result


def print_test(name: str, input_str: str, result: Expr, expected: str) -> None:
    """Print the results of any test in a nice format."""
    print(f"\nTest: '{name}'")
    print(f"\tInput:    '{input_str}'")
    print(f"\tResult:   '{result}'")
    print(f"\tExpected: '{expected}'")
    if str(result) != expected:
        msg = f"Result for test '{name}' does not match expectation."
        raise ValueError(msg)


def print_bool(name: str, input_str: str, *, result: bool, expected: bool) -> None:
    """Print the results of a boolean check in a nice format."""
    print(f"\nTest: '{name}'")
    print(f"\tInput:    '{input_str}'")
    print(f"\tResult:   '{result}'")
    print(f"\tExpected: '{expected}'")
    if result != expected:
        msg = f"Result for test '{name}' does not match expectation."
        raise ValueError(msg)


def testsop() -> None:  # noqa: PLR0915
    """Perform tests with sum of products."""
    print("\n***** Testing Cube Expressions *****")

    c1 = parse_cube("Basic cube (c1)", "a*b*c", "abc")
    c2 = parse_cube("Cube with complement (c2)", "b*c*d*~e", "bcd~e")
    c3 = parse_cube("Another cube (c3)", "c*d*e*~f", "cde~f")
    c4 = parse_cube("Yet another cube (c4)", "a*c*~d", "ac~d")
    c5 = parse_cube("And another (c5)", "c*d*~e", "cd~e")

    c_zero = parse_cube("Special zero cube", "0", "0")
    c_one = parse_cube("Special one cube", "1", "1")

    print("\n***** Testing SOP Expressions *****")

    parse_sop("Basic sum", "a + b + c", "a + b + c")
    parse_sop("Apply De Morgan's", "~(a*~b*d*~e)", "~a + b + ~d + e")
    parse_sop("Complex expr", "a*b*~c + ~b + d*~e + a*f", "~b + af + d~e + ab~c")
    parse_sop("XOR operator", "a^b^c * ~c * (~a + ~b)", "a~b~c + ~ab~c")
    parse_sop("Multiply by 0 cube", "0 * (a + 1) + 1 * (a + b) * 0", "0")
    parse_sop("Multiply by 1 cube", "0 * (a + 1) + 1 * (a + b) * 1", "a + b")
    parse_sop("Add 1 cube", "1 * (a + 1) + 1 * (a + b) * 1", "1")
    exp1 = parse_sop(
        "Complex expr (exp1)",
        "~b*~c + ~a*b + a*b*c + a*~b*c",
        "~ab + ~b~c + abc + a~bc",
    )
    exp2 = parse_sop("Distribution (exp2)", "a + b*(a + c)*(c + d*e*(a + c))", "a + bc")
    exp3 = parse_sop(
        "Nested parentheses (exp3)", "((a*b)) + ~(b*c) + b*c*d", "~b + ~c + ab + bcd"
    )
    print("\t^minimized wrt SCC but not complete")
    exp4 = parse_sop(
        "Another SOP (exp4)", "a*b + ~b + ~c + b*c*d", "~b + ~c + ab + bcd"
    )
    print("\t^minimized wrt SCC but not complete")
    exp5 = parse_sop(
        "Big SOP (exp5)",
        "~b*~c*~d + a*d + a*c*~d + ~a*c*d + ~a*~b*c + ~a*~c*~d + ~a*~b*~c",
        "ad + ac~d + ~acd + ~a~bc + ~a~c~d + ~a~b~c + ~b~c~d",
    )
    print("\t^minimized wrt SCC but not complete")

    print("\n***** Testing Cube Arithmetic *****")

    print_test("Product of cubes (p12)", f"{c1} * {c2}", c1 * c2, "abcd~e")
    print_test(
        "Addition of cubes (s14)", f"{c1} + {c4}", (s14 := c1 + c4), "abc + ac~d"
    )
    print_test("Consensus (con13)", f"{c1} % {c3}", c1 % c3, "0")
    print_test("Consensus (con24)", f"{c2} % {c4}", c2 % c4, "abc~e")
    print_test("Invert cube (inv1)", f"~({c1})", ~c1, "~a + ~b + ~c")

    print("\n***** Testing SOP Arithmetic *****")

    print_test(
        "Cubes and a SOP (exp2)",
        f"{c1}*({c2}+{c5}) + {c4}*{c5} + {s14}",
        (exp6 := c1 * (c2 + c5) + c4 * c5 + s14),
        "abc + ac~d",
    )
    if isinstance(exp6, BaseCube):
        raise TypeError
    print_test("Invert SOP", f"~({exp6})", ~exp6, "~a + ~c + ~bd")

    print("\n***** Testing Complete SOP *****")

    print_test(
        "Complete exp1", f"{exp1}", exp1.complete(), "ac + a~b + ~a~c + ~ab + bc + ~b~c"
    )
    print(
        "\t^Demonstrates all prime implicants have been found, not just the essentials"
    )
    print("\tActual fully minimized cover is 'a~b + bc + ~a~c'")
    print_test("Complete exp2", f"{exp2}", exp2.complete(), "a + bc")
    print_test("Complete exp3", f"{exp3}", exp3.complete(), "a + ~b + ~c + d")
    print_test("Complete exp4", f"{exp4}", exp4.complete(), "a + ~b + ~c + d")
    print_test(
        "Complete exp5", f"{exp5}", exp5.complete(), "~b + ac + ad + cd + ~a~c~d"
    )
    print_test("Complete exp6", f"{exp6}", exp6.complete(), "abc + ac~d")
    taut1 = parse_sop(
        "Parse a tautology expr",
        "b + ~b*c + ~a*~c + a*~b*~c",
        "b + ~a~c + ~bc + a~b~c",
    )
    print_test("Complete a known tautology", f"{taut1}", taut1.complete(), "1")
    print("\t^For this particular tautology the complete cover is 1")

    print("\n***** Testing isTautology *****")

    print_bool("isTautology", "1", result=SOP({c_one}).isTautology(), expected=True)
    print_bool("isTautology", "0", result=SOP({c_zero}).isTautology(), expected=False)
    print_bool("isTautology", str(exp1), result=exp1.isTautology(), expected=False)
    print_bool("isTautology", str(taut1), result=taut1.isTautology(), expected=True)

    expr = parse_bool_expr("a*~c + b*c + ~a*~d + a*~b*~c + b*~d")
    assert isinstance(expr, SOP)
    print_bool("isTautology", str(expr), result=expr.isTautology(), expected=False)
    expr = parse_bool_expr("b*c + ~b*c*d + b*~c")
    assert isinstance(expr, SOP)
    print_bool("isTautology", str(expr), result=expr.isTautology(), expected=False)
    expr = parse_bool_expr("a*b*c + a*c*~d + ~a*~b*~c + ~a*d + b*~c + ~a*c")
    assert isinstance(expr, SOP)
    print_bool("isTautology", str(expr), result=expr.isTautology(), expected=False)
    expr = parse_bool_expr(
        "~a*~b*~c*d+~a*~c*~d+~a*b*~c+a*~c+a*~b*c+a*b*c*~d+b*d+~a*c*~d+~a*c*d"
    )
    assert isinstance(expr, SOP)
    print_bool("isTautology", str(expr), result=expr.isTautology(), expected=True)


if __name__ == "__main__":
    testsop()
