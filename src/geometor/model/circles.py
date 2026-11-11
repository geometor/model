"""Provides circle construction and manipulation for the Model class.

This module manages the creation of symbolic circles defined by a center point and
a radius point, handling deduplication and exact symbolic intersections.
"""

from __future__ import annotations

from collections.abc import Sequence

import sympy as sp
import sympy.geometry as spg
from rich.table import Table

from geometor.model.colors import get_color
from geometor.model.element import (
    CircleElement,
    Struct,
    check_existence,
    find_all_intersections,
)

__all__ = ["CirclesMixin"]


class CirclesMixin:
    """Mixin for the Model class containing circle construction operations."""

    def construct_circle_by_IDs(
        self,
        pt_1_ID: str,
        pt_2_ID: str,
        classes: list[str] | None = None,
        ID: str = "",
        *,
        guide: bool = False,
        intersect: bool | Sequence[Struct] | None = None,
        by: str = "",
    ) -> spg.Circle:
        """Find points by ID and construct a circle via :meth:`Model.construct_circle`."""
        pt_1 = self.get_element_by_ID(pt_1_ID)
        pt_2 = self.get_element_by_ID(pt_2_ID)
        return self.construct_circle(
            pt_1,
            pt_2,
            classes=classes,
            ID=ID,
            guide=guide,
            intersect=intersect,
            by=by,
        )

    def construct_circle(
        self,
        pt_center: spg.Point,
        pt_radius: spg.Point,
        classes: list[str] | None = None,
        ID: str = "",
        guide: bool = False,
        *,
        intersect: bool | Sequence[Struct] | None = None,
        by: str = "",
    ) -> spg.Circle:
        """Construct a :class:`sympy.geometry.Circle` from center and radius points.

        Args:
            pt_center: The center point of the circle.
            pt_radius: A point on the circumference of the circle.
            classes: A list of class labels.
            ID: A string ID for the circle. If empty, ``( A B )`` is generated.
            guide: If True, the circle is excluded from automatic intersections.
            intersect: Override automatic intersection behavior (``None``, ``False``,
                ``True``, or a ``Sequence[Struct]``).
            by: Optional Euclidean citation (e.g., ``"Post.3"``).

        Returns:
            The constructed or existing :class:`sympy.geometry.Circle`.
        """
        self.clear_new_points()

        if classes is None:
            classes = []

        if not isinstance(pt_center, spg.Point) or not isinstance(pt_radius, spg.Point):
            raise TypeError(
                "Both pt_center and pt_radius must be instances of sympy.geometry.point.Point"
            )

        radius_len = pt_center.distance(pt_radius)

        struct = spg.Circle(pt_center, radius_len)

        if not ID:
            pt_1_ID = self[pt_center].ID
            pt_2_ID = self[pt_radius].ID
            ID = f"( {pt_1_ID} {pt_2_ID} )"

        details = CircleElement(
            struct,
            parents=[pt_center, pt_radius],
            classes=classes,
            ID=ID,
            pt_radius=pt_radius,
            guide=guide,
        )

        exists, existing_circle = check_existence(self, struct, self.circles)
        if exists and existing_circle is not None:
            self[existing_circle].pts[details.pt_radius] = ""
            self[existing_circle].classes.update(details.classes)
            if not details.guide and self[existing_circle].guide and "guide" not in classes:
                self[existing_circle].guide = False
            return existing_circle

        self[struct] = details
        if hasattr(self, "_register_in_scope"):
            self._register_in_scope(struct)
        if hasattr(self, "_record_step"):
            self._record_step(kind="construct", action="circle", elements=[details.ID], by=by)

        if self.is_logging_enabled:
            classes_str = " : " + " ".join(classes) if classes else ""
            color = get_color(struct, classes)
            self.log(f"[{color} bold]{details.ID}[/{color} bold]{classes_str}")
            table = Table(show_header=False, box=None, padding=(0, 4))
            table.add_row("    ctr:", f"[cyan]{self[pt_center].ID}[/cyan]")
            table.add_row("    r:", f"[cyan]{sp.pretty(struct.radius)}[/cyan]")
            table.add_row("    eq:", f"[cyan]{sp.pretty(struct.equation())}[/cyan]")
            self.log(table)

        if intersect is False:
            return struct
        if isinstance(intersect, Sequence):
            find_all_intersections(self, struct, candidates=intersect, by=by)
        elif intersect is True:
            if not details.guide:
                find_all_intersections(self, struct, candidates=self.structs, by=by)
        else:
            find_all_intersections(self, struct, by=by)

        return struct
