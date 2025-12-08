"""Provides polygon construction and manipulation for the Model class.

This module facilitates the creation and management of polygon elements within the model. It allows for defining polygons using lists of points or point identifiers and supports calculating properties like side lengths and area.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sympy as sp
import sympy.geometry as spg
from rich.table import Table

from geometor.model.colors import get_color
from geometor.model.element import Element
from geometor.model.utils import clean_expr

if TYPE_CHECKING:
    pass

__all__ = ["PolygonsMixin"]


class PolygonsMixin:
    """Mixin for the Model class containing polygon construction operations.
    
    This mixin extends the Model with functionality to define polygons. It includes methods for creating polygons from both direct point objects and their corresponding string IDs, ensuring flexibility in how geometric shapes are defined.
    """

    def set_polygon_by_IDs(
        self, poly_pts_IDs: list[str], classes: list[str] | None = None, ID: str = ""
    ) -> spg.Polygon:
        """Find points by ID and use them with :meth:`Model.set_polygon`.
        
        This helper method resolves a list of point IDs to their corresponding point objects in the model and then delegates to `set_polygon` to create the polygon element.

        Args:
            poly_pts_IDs: A list of point IDs.
            classes: A list of class labels.
            ID: A string ID for the polygon.

        Returns:
            The constructed :class:`sympy.geometry.polygon.Polygon`.
        """
        poly_pts = []

        for poly_ID in poly_pts_IDs:
            poly_pts.append(self.get_element_by_ID(poly_ID))

        return self.set_polygon(poly_pts, classes)

    def set_polygon(
        self, poly_pts: list[spg.Point], classes: list[str] | None = None, ID: str = ""
    ) -> spg.Polygon:
        """Set polygon (list of 3 or more points).
        
        This method constructs a polygon from a list of points and adds it to the model. It calculates the lengths of the polygon's sides, generates an ID if one is not provided, and logs the polygon's properties including side lengths and area.

        Args:
            poly_pts: A list of 3 or more points defining the polygon vertices.
            classes: A list of class labels.
            ID: A string ID for the polygon. If empty, one is generated.

        Returns:
            The constructed :class:`sympy.geometry.polygon.Polygon`.
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
