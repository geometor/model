"""Provides polygon construction and manipulation for the Model class.

This module facilitates the creation and management of polygon elements within the model.
"""

from __future__ import annotations

import sympy as sp
import sympy.geometry as spg
from rich.table import Table

from geometor.model.colors import get_color
from geometor.model.element import Element
from geometor.model.utils import clean_expr

__all__ = ["PolygonsMixin"]


class PolygonsMixin:
    """Mixin for the Model class containing polygon construction operations."""

    def set_polygon_by_IDs(
        self,
        poly_pts_IDs: list[str],
        classes: list[str] | None = None,
        ID: str = "",
        *,
        guide: bool = False,
        by: str = "",
    ) -> spg.Polygon:
        """Find points by ID and use them with :meth:`Model.set_polygon`."""
        poly_pts = [self.get_element_by_ID(poly_ID) for poly_ID in poly_pts_IDs]
        return self.set_polygon(poly_pts, classes, ID, guide=guide, by=by)

    def set_polygon(
        self,
        poly_pts: list[spg.Point],
        classes: list[str] | None = None,
        ID: str = "",
        *,
        guide: bool = False,
        by: str = "",
    ) -> spg.Polygon:
        """Construct and register a :class:`sympy.geometry.Polygon` ``< A B C >``."""
        poly = spg.Polygon(*poly_pts)

        if not ID:
            poly_pts_IDs = [str(self[pt].ID or pt) for pt in poly_pts]
            ID = f"< {' '.join(poly_pts_IDs)} >"

        details = Element(poly, parents=poly_pts, classes=classes, ID=ID, guide=guide)
        details.side_lengths = [clean_expr(side.length) for side in poly.sides]

        self[poly] = details
        if hasattr(self, "_register_in_scope"):
            self._register_in_scope(poly)
        if hasattr(self, "_record_step"):
            self._record_step(kind="construct", action="polygon", elements=[details.ID], by=by)

        if self.is_logging_enabled:
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

    construct_polygon = set_polygon
