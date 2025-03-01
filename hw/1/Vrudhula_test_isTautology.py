#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 28 14:59:14 2025

@author: svrudhul
"""


def Vrudhula_test_isTautology():

    e1str = "w*~y + x*y + ~w*~z + w*~x*~y + x*~z"
    e1 = parse_boolean_expression(e1str).children[-1]
    print(f"e1 = w*~y + x*y + ~w*~z + w*~x*~y + x*~z.  Result: {e1}")
    print(f"isTautology(e1) = {e1.isTautology()}\n")

    e2str = "x*y + ~x*y*z + x*~y"
    e2 = parse_boolean_expression(e2str).children[-1]
    print(f"e2= x*y + ~x*y*z + x*~y. Result: {e2}")
    print(f"isTautology(e2) = {e2.isTautology()}\n")

    e3str = "w*x*y + w*y*~z + ~w*~x*~y + ~w*z + x*~y + ~w*y"
    e3 = parse_boolean_expression(e3str).children[-1]
    print(f"e3 = w*x*y + w*y*~z + ~w*~x*~y + ~w*z + x*~y + ~w*y. Result: {e3}")
    print(f"isTautology(e3) = {e3.isTautology()}\n")

    e4str = """~w*~x*~y*z + ~w*~y*~z + ~w*x*~y + w*~y + w*~x*y
            + w*x*y*~z + x*z + ~w*y*~z + ~w*y*z
            """
    e4 = parse_boolean_expression(e4str).children[-1]
    print(f"""e4 = w*~x*~y*z + ~w*~y*~z + ~w*x*~y + w*~y + w*~x*y + w*x*y*~z + x*z
          + ~w*y*~z + ~w*y*z. Result: {e4}""")
    print(f"isTautology(e4) = {e4.isTautology()}")


if __name__ == "__main__":
    #    test_completeSOP()
    Vrudhula_test_isTautology()
