"""
The :mod:`geometor.model.helpers` module provides helper functions for geometric constructions.
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
def line_get_y(l1, x):
    """return y value for specific x"""
    a, b, c = l1.coefficients

    return (-a * x - c) / b


def set_given_start_points(model):
    """create inital two points -
    establishing the unit for the field"""
    p1 = model.set_point(sp.Rational(-1, 2), 0, classes=["given"])
    p2 = model.set_point(sp.Rational(1, 2), 0, classes=["given"])
    return p1, p2


def set_given_start_points_zero(model):
    """create inital two points -
    establishing the unit for the field"""
    p1 = model.set_point(0, 0, classes=["given"])
    p2 = model.set_point(1, 0, classes=["given"])
    return p1, p2


def set_equilateral_poles(
    model: Model, pt_1: spg.Point, pt_2: spg.Point, add_circles=True
):
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


def construct_perpendicular_bisector(model, pt_1, pt_2, add_circles=True):
    """perform fundamental operations for two points
    and add perpendicular bisector"""
    pole_1, pole_2 = set_equilateral_poles(model, pt_1, pt_2, add_circles)
    return model.construct_line(pole_1, pole_2, classes=["bisector"])


def set_midpoint(model, pt_1, pt_2, add_circles=True):
    """perform fundamental operations for two points
    and add perpendicular bisector"""
    pole_1, pole_2 = set_equilateral_poles(model, pt_1, pt_2, add_circles)
    return model.construct_line(pole_1, pole_2, classes=["bisector"])


def set_given_rect_points(model, pt, x_offset, y_offset):
    rect_points = [pt]
    pt_x0 = model.set_point(pt.x + x_offset, pt.y, classes=["given"])
    rect_points.append(pt_x0)
    pt_xy = model.set_point(pt.x + x_offset, pt.y + y_offset, classes=["given"])
    rect_points.append(pt_xy)
    pt_0y = model.set_point(pt.x, pt.y + y_offset, classes=["given"])
    rect_points.append(pt_0y)

    return rect_points


def set_given_square_points(model, pt, offset):
    return set_given_rect_points(model, pt, offset, offset)
