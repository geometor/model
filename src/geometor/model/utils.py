"""Provides utility functions for the Model class.

This module collects general-purpose utility functions used throughout the package. It includes tools for symbolic expression simplification (cleaning), point comparison and sorting, and logging setup.
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


def clean_expr(expr: sp.Expr) -> sp.Expr:
    """Simplify and denest SymPy expressions.
    
    This function applies a standard set of simplification routines to symbolic expressions, specifically targeting the simplification of square roots and nested radicals which are common in constructive geometry.

    Args:
        expr: The SymPy expression to clean.

    Returns:
        The simplified expression.
    """
    expr = sp.simplify(expr)
    expr = sp.sqrtdenest(expr)
    return expr


def spread(l1: spg.Line, l2: spg.Line) -> sp.Expr:
    """Calculate the spread of two lines.
    
    The spread is a rational invariant of two lines, equivalent to the square of the sine of the angle between them. It is a fundamental concept in rational trigonometry.

    Args:
        l1: The first line.
        l2: The second line.

    Returns:
        The spread as a symbolic expression.
    """
    a1, a2, a3 = l1.coefficients
    b1, b2, b3 = l2.coefficients
    # only the first two coefficients are used
    spread = ((a1 * b2 - a2 * b1) ** 2) / ((a1**2 + b1**2) * (a2**2 + b2**2))
    return spread


def compare_points(pt1: spg.Point, pt2: spg.Point) -> int:
    """Compare two points for sorting.
    
    This comparison function orders points primarily by their x-coordinates and secondarily by their y-coordinates. It returns 1 if pt1 > pt2, -1 if pt1 < pt2, and 0 if they are equal.

    Args:
        pt1: The first point.
        pt2: The second point.

    Returns:
        An integer indicating the relative order (-1, 0, 1).
    """
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


def point_value(pt: spg.Point) -> tuple[float, float]:
    """Get the numerical coordinates of a point.
    
    This helper extracts the floating-point values of a point's x and y coordinates, suitable for use in sorting keys or numerical comparisons.

    Args:
        pt: The point to evaluate.

    Returns:
        A tuple of (x, y) floats.
    """
    #  return pt.x.evalf()
    return (pt.x.evalf(), pt.y.evalf())


def sort_points(pts: list[spg.Point]) -> list[spg.Point]:
    """Sort a list of points.
    
    This function sorts a list of points using the `point_value` helper as the key.

    Args:
        pts: The list of points to sort.

    Returns:
        The sorted list of points.
    """
    #  return sorted(list(pts), key=point_value)
    return sorted(pts, key=point_value)


def log_init(name: str) -> None:
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


def print_log(txt: str = "") -> None:
    print(txt)
    logging.info(txt)


def elapsed(start_time: float) -> str:
    secs = timer() - start_time
    return str(datetime.timedelta(seconds=secs))
