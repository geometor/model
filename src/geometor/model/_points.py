"""
helper functions for Model class
"""

from .common import *
from .utils import *

from .element import Element
from .reports import get_colored_label


def _set_point(
    self,
    x_val: sp.Expr,
    y_val: sp.Expr,
    parents: list = None,
    classes: list = None,
    label: str = "",
) -> spg.Point:
    """
    Adds a point to the model, finds duplicates, cleans values, and sets parents and classes.

    Parameters:
        - ``x_val`` (:class:`sympy.core.expr.Expr`): The x-value of the point.
        - ``y_val`` (:class:`sympy.core.expr.Expr`): The y-value of the point.
        - ``parents`` (list, optional): A list of parent elements or references. Defaults to None.
        - ``classes`` (list, optional): A list of string names for classes defining a set of styles. Defaults to None.
        - ``label`` (str, optional): A text label for use in plotting and reporting. Defaults to an empty string.

    Returns:
        :class:`sympy.geometry.point.Point`: The set point.

    Example:
        >>> from geometor.model import *
        >>> model = Model("demo")
        >>> model.set_point(0, 0, classes=["given"])
        <spg.Point object ...>

    Notes:
        The function simplifies the x and y values before adding, and it updates the attributes if the point is already in the model.
    """

    if classes is None:
        classes = []
    if parents is None:
        parents = []

    # simplify values before adding
    x_val = clean_expr(x_val)
    y_val = clean_expr(y_val)

    pt = spg.Point(x_val, y_val)

    details = Element(pt, parents, classes, label)

    if pt in self.points:
        # add attributes
        for parent in details.parents:
            self[pt].parents[parent] = ""
        self[pt].classes.update(details.classes)
        return pt

    else:
        for prev_pt in self.points:
            if pt.equals(prev_pt):
                for parent in details.parents:
                    self[prev_pt].parents[parent] = ""
                self[prev_pt].classes.update(details.classes)
                return prev_pt

    if not label:
        label = next(self.label_gen)

    details = Element(pt, parents, classes, label)
    self[pt] = details
    
    text_label = get_colored_label(pt, label)
    console.print(f"[gold3]{text_label}[/gold3] = {{ {str(pt.x)}, {str(pt.y)} }}")
    #  console.print(f"[gold3]{text_label}[/gold3] = {{ {sp.pretty(pt.x)}, {sp.pretty(pt.y)} }}")
    #  print(f"{text_label} = {{ {sp.pprint(pt.x)}, {str(pt.y)} }}")
    return pt
