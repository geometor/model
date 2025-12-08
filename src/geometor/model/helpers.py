"""Provides helper functions for geometric constructions.

This module contains various utility functions that streamline common geometric operations, such as creating specific point configurations (rectangles, squares) and performing basic constructions like perpendicular bisectors.
"""

import sympy as sp
import sympy.geometry as spg

from geometor.model.model import Model

__all__ = [
    "line_get_y",
    "set_given_start_points",
    "set_given_start_points_zero",
    "set_equilateral_poles",
    "construct_perpendicular_bisector",
    "set_midpoint",
    "set_given_rect_points",
    "set_given_square_points",
]


# helpers ******************************
def line_get_y(l1: spg.Line, x: sp.Expr) -> sp.Expr:
    """Return y value for specific x.
    
    This function calculates the y-coordinate on a given line for a specified x-value, essentially solving the line equation for y.

    Args:
        l1: The line object.
        x: The x-value to evaluate.

    Returns:
        The corresponding y-value.
    """
    a, b, c = l1.coefficients

    return (-a * x - c) / b


def set_given_start_points(model: Model) -> tuple[spg.Point, spg.Point]:
    p1 = model.set_point(sp.Rational(-1, 2), 0, classes=["given"])
    p2 = model.set_point(sp.Rational(1, 2), 0, classes=["given"])
    return p1, p2


def set_given_start_points_zero(model: Model) -> tuple[spg.Point, spg.Point]:
    p1 = model.set_point(0, 0, classes=["given"])
    p2 = model.set_point(1, 0, classes=["given"])
    return p1, p2


def set_equilateral_poles(
    model: Model, pt_1: spg.Point, pt_2: spg.Point, add_circles: bool = True
) -> list[spg.Point]:
    if add_circles:
        c1 = model.construct_circle(pt_1, pt_2, classes=["guide"])
        c2 = model.construct_circle(pt_2, pt_1, classes=["guide"])
        pts = c1.intersection(c2)
        set_points = []
        for pt in pts:
            pt = model.set_point(pt.x, pt.y)
            set_points.append(pt)
            #  model[pt].parents[c1] = ""
            #  model[pt].parents[c2] = ""

        return set_points
    else:
        c1 = spg.Circle(pt_1, pt_1.distance(pt_2))
        c2 = spg.Circle(pt_2, pt_2.distance(pt_1))
        pts = c1.intersection(c2)
        set_points = []
        for pt in pts:
            pt = model.set_point(pt.x, pt.y)
            set_points.append(pt)
            model[pt].parents[c1] = ""
            model[pt].parents[c2] = ""

        return set_points


def construct_perpendicular_bisector(
    model: Model, pt_1: spg.Point, pt_2: spg.Point, add_circles: bool = True
) -> spg.Line:
    """Perform fundamental operations for two points and add perpendicular bisector.
    
    This function automates the classic geometric construction of a perpendicular bisector. It finds the intersection "poles" of two circles centered at the given points and constructs a line through them.

    Args:
        model: The model to add the construction to.
        pt_1: The first point.
        pt_2: The second point.
        add_circles: Whether to add the construction circles to the model.

    Returns:
        The bisector line.
    """
    pole_1, pole_2 = set_equilateral_poles(model, pt_1, pt_2, add_circles)
    return model.construct_line(pole_1, pole_2, classes=["bisector"])


def set_midpoint(
    model: Model, pt_1: spg.Point, pt_2: spg.Point, add_circles: bool = True
) -> spg.Line:
    """Finds and sets the midpoint between two points.
    
    This function utilizes the perpendicular bisector construction to locate the geometric midpoint between the provided points.

    Args:
        model: The model to add the construction to.
        pt_1: The first point.
        pt_2: The second point.
        add_circles: Whether to add the construction circles to the model.

    Returns:
        The bisector line (note: currently returns the bisector, logic might infer midpoint from intersection).
    """
    pole_1, pole_2 = set_equilateral_poles(model, pt_1, pt_2, add_circles)
    return model.construct_line(pole_1, pole_2, classes=["bisector"])


def set_given_rect_points(
    model: Model, pt: spg.Point, x_offset: sp.Expr, y_offset: sp.Expr
) -> list[spg.Point]:
    rect_points = [pt]
    pt_x0 = model.set_point(pt.x + x_offset, pt.y, classes=["given"])
    rect_points.append(pt_x0)
    pt_xy = model.set_point(pt.x + x_offset, pt.y + y_offset, classes=["given"])
    rect_points.append(pt_xy)
    pt_0y = model.set_point(pt.x, pt.y + y_offset, classes=["given"])
    rect_points.append(pt_0y)

    return rect_points


def set_given_square_points(
    model: Model, pt: spg.Point, offset: sp.Expr
) -> list[spg.Point]:
    return set_given_rect_points(model, pt, offset, offset)
