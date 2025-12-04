"""
The :mod:`geometor.model.utils` module provides utility functions for the Model class.
"""

# time *********************
import datetime
import logging
import os as os
from timeit import default_timer as timer

import sympy as sp
import sympy.geometry as spg
from rich import print

__all__ = [
    "clean_expr",
    "spread",
    "compare_points",
    "point_value",
    "sort_points",
    "log_init",
    "print_log",
    "elapsed",
]

#  from geometor.model import *


def clean_expr(expr):
    """
    simplify and denest SymPy expressions
    """
    expr = sp.simplify(expr)
    expr = sp.sqrtdenest(expr)
    return expr


def spread(l1: spg.Line, l2: spg.Line):
    """calculate the spread of two lines"""
    a1, a2, a3 = l1.coefficients
    b1, b2, b3 = l2.coefficients
    # only the first two coefficients are used
    spread = ((a1 * b2 - a2 * b1) ** 2) / ((a1**2 + b1**2) * (a2**2 + b2**2))
    return spread


def compare_points(pt1, pt2):
    if pt1.x.evalf() > pt2.x.evalf():
        return 1
    elif pt1.x.evalf() < pt2.x.evalf():
        return -1
    else:
        if pt1.y.evalf() > pt2.y.evalf():
            return 1
        elif pt1.y.evalf() < pt2.y.evalf():
            return -1
        else:
            return 0


def point_value(pt):
    #  return pt.x.evalf()
    return (pt.x.evalf(), pt.y.evalf())


def sort_points(pts):
    #  return sorted(list(pts), key=point_value)
    return sorted(pts, key=point_value)


def log_init(name):
    sessions = os.path.expanduser("~") + "/Sessions"
    out = f"{sessions}/{name}/"
    os.makedirs(out, exist_ok=True)
    filename = f"{out}/build.log"
    #  with open(filename, 'w'):
    #  pass
    print(f"log to: {filename}")

    logging.basicConfig(
        filename=filename, filemode="w", encoding="utf-8", level=logging.INFO
    )
    logging.info(f"Init {name}")


def print_log(txt=""):
    print(txt)
    logging.info(txt)


def elapsed(start_time):
    secs = timer() - start_time
    return str(datetime.timedelta(seconds=secs))
