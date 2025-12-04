"""
The :mod:`geometor.model.points` module provides point construction and manipulation for the Model class.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

import sympy as sp
import sympy.geometry as spg
from rich.table import Table

from geometor.model.colors import COLORS, get_color
from geometor.model.element import Element
from geometor.model.utils import clean_expr

if TYPE_CHECKING:
    pass

__all__ = ["PointsMixin"]


class PointsMixin:
    """
    Mixin for the Model class containing point construction operations.
    """

    def point_ID_generator(self) -> Iterator[str]:
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        repeat = 1

        while True:
            for letter in letters:
                yield str(letter) * repeat
            repeat += 1

    def set_point(
        self,
        x_val: sp.Expr,
        y_val: sp.Expr,
        parents: list = None,
        classes: list = None,
        ID: str = "",
        guide: bool = False,
    ) -> spg.Point:
        """
        Adds a point to the model, finds duplicates, cleans values, and sets
        parents and classes.

        parameters
        ----------
        - ``x_val`` : :class:`sympy.core.expr.Expr`: The x-value of the point.
        - ``y_val`` : :class:`sympy.core.expr.Expr`: The y-value of the point.
        - ``parents`` : list, optional: A list of parent elements or references.
          Defaults to None.
        - ``classes`` list, optional: A list of string names for classes defining
          a set of styles. Defaults to None.
        - ``ID`` str, optional: A text ID for use in plotting and
          reporting. Defaults to an empty string.

        returns
        -------
        - :class:`sympy.geometry.point.Point`: The set point.

        example
        -------
        >>> from geometor.model import *
        >>> model = Model("demo")
        >>> model.set_point(0, 0, classes=["given"])
        <spg.Point object ...>

        notes
        -----
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

        details = Element(pt, parents, classes, ID, guide)

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

        if not ID:
            ID = next(self.ID_gen)
            self.last_point_id = ID

        details = Element(pt, parents, classes, ID, guide)
        self[pt] = details
        self._new_points.append(pt)

        color = get_color(pt, classes)
        classes_str = " : " + " ".join(classes) if classes else ""
        self.log(f"    [{color} bold]{ID}[/{color} bold]{classes_str}")

        table = Table(show_header=False, box=None, padding=(0, 4))
        table.add_row("    x:", f"[cyan]{sp.pretty(pt.x)}[/cyan]")
        table.add_row("    y:", f"[cyan]{sp.pretty(pt.y)}[/cyan]")
        self.log(table)

        if self._analysis_hook:
            self._analysis_hook(self, pt)

        #  console.print(f"[gold3]{text_ID}[/gold3] = {{ {sp.pretty(pt.x)}, {sp.pretty(pt.y)} }}")
        #  print(f"{text_ID} = {{ {sp.pprint(pt.x)}, {str(pt.y)} }}")
        return pt
