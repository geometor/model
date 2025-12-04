"""
The :mod:`geometor.model.polygons` module provides polygon construction and manipulation for the Model class.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sympy as sp
import sympy.geometry as spg
from rich.table import Table

from geometor.model.colors import COLORS, get_color
from geometor.model.element import Element
from geometor.model.utils import clean_expr

if TYPE_CHECKING:
    pass

__all__ = ["PolygonsMixin"]


class PolygonsMixin:
    """
    Mixin for the Model class containing polygon construction operations.
    """

    def set_polygon_by_IDs(
        self, poly_pts_IDs: list[str], classes: list = None, ID: str = ""
    ) -> spg.Polygon:
        """
        find points by ID and use them with :meth:`Model.set_polygon`
        """
        poly_pts = []

        for poly_ID in poly_pts_IDs:
            poly_pts.append(self.get_element_by_ID(poly_ID))

        return self.set_polygon(poly_pts, classes)

    def set_polygon(self, poly_pts: list[spg.Point], classes=[], ID="") -> spg.Polygon:
        """
        set polygon (list of 3 or more points)
        """

        # TODO: check points and minimum count of 3
        poly = spg.Polygon(*poly_pts)

        if not ID:
            poly_pts_IDs = [str(self[pt].ID or pt) for pt in poly_pts]
            poly_pts_IDs = " ".join(poly_pts_IDs)
            ID = f"< {poly_pts_IDs} >"

        details = Element(poly, parents=poly_pts, classes=classes, ID=ID)

        details.side_lengths = [clean_expr(side.length) for side in poly.sides]

        self[poly] = details

        classes_str = " : " + " ".join(classes) if classes else ""
        color = get_color(poly, classes)
        self.log(f"[{color} bold]{details.ID}[/{color} bold]{classes_str}")
        table = Table(show_header=False, box=None, padding=(0, 4))
        for i, side in enumerate(poly.sides):
            table.add_row(
                f"    side {i + 1}:", f"[cyan]{sp.pretty(side.length)}[/cyan]"
            )
        table.add_row("    area:", f"[cyan]{sp.pretty(poly.area)}[/cyan]")
        self.log(table)

        return poly
