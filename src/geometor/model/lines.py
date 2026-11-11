"""Provides line construction and manipulation for the Model class.

This module encapsulates the logic for creating symbolic lines from points,
managing their inclusion in the model, and determining their intersections.
"""

from __future__ import annotations

from collections.abc import Sequence

import sympy as sp
import sympy.geometry as spg
from rich.table import Table

from geometor.model.colors import get_color
from geometor.model.element import (
    Element,
    Struct,
    check_existence,
    find_all_intersections,
)

__all__ = ["LinesMixin"]


class LinesMixin:
    """Mixin for the Model class containing line construction operations."""

    def construct_line_by_IDs(
        self,
        pt_1_ID: str,
        pt_2_ID: str,
        classes: list[str] | None = None,
        ID: str = "",
        *,
        guide: bool = False,
        intersect: bool | Sequence[Struct] | None = None,
        by: str = "",
    ) -> spg.Line:
        """Find points by ID and construct a line via :meth:`Model.construct_line`."""
        pt_1 = self.get_element_by_ID(pt_1_ID)
        pt_2 = self.get_element_by_ID(pt_2_ID)
        return self.construct_line(
            pt_1,
            pt_2,
            classes=classes,
            ID=ID,
            guide=guide,
            intersect=intersect,
            by=by,
        )

    def construct_line(
        self,
        pt_1: spg.Point,
        pt_2: spg.Point,
        classes: list[str] | None = None,
        ID: str = "",
        guide: bool = False,
        *,
        intersect: bool | Sequence[Struct] | None = None,
        by: str = "",
    ) -> spg.Line:
        """Construct a :class:`sympy.geometry.Line` from two points and add it to the model.

        Args:
            pt_1: The first point of the line.
            pt_2: The second point of the line.
            classes: A list of class labels.
            ID: A string ID for the line. If empty, ``[ A B ]`` is generated.
            guide: If True, the line is excluded from automatic intersections.
            intersect: Override automatic intersection behavior:
                - ``None`` (default): uses ``self.auto_intersect``.
                - ``False``: skip automatic intersections for this line.
                - ``True``: intersect with all eligible non-guide structures.
                - ``Sequence[Struct]``: intersect strictly against the given structures.
            by: Optional Euclidean citation (e.g., ``"Post.1"``).

        Returns:
            The constructed or existing :class:`sympy.geometry.Line`.
        """
        self.clear_new_points()

        if classes is None:
            classes = []

        if not isinstance(pt_1, spg.Point) or not isinstance(pt_2, spg.Point):
            raise TypeError(
                "Both pt_1 and pt_2 must be instances of sympy.geometry.point.Point"
            )

        struct = spg.Line(pt_1, pt_2)

        if not ID:
            pt_1_ID = self[pt_1].ID
            pt_2_ID = self[pt_2].ID
            ID = f"[ {pt_1_ID} {pt_2_ID} ]"

        details = Element(
            struct, parents=[pt_1, pt_2], classes=classes, ID=ID, guide=guide
        )

        exists, existing_line = check_existence(self, struct, self.lines)
        if exists and existing_line is not None:
            for incident_pt in struct.points:
                self[existing_line].pts[incident_pt] = ""
            self[existing_line].classes.update(details.classes)
            if not details.guide and self[existing_line].guide and "guide" not in classes:
                self[existing_line].guide = False
            return existing_line

        self[struct] = details
        if hasattr(self, "_register_in_scope"):
            self._register_in_scope(struct)
        if hasattr(self, "_record_step"):
            self._record_step(kind="construct", action="line", elements=[details.ID], by=by)

        if self.is_logging_enabled:
            classes_str = " : " + " ".join(classes) if classes else ""
            color = get_color(struct, classes)
            self.log(f"[{color} bold]{details.ID}[/{color} bold]{classes_str}")
            table = Table(show_header=False, box=None, padding=(0, 4))
            table.add_row("    eq:", f"[cyan]{sp.pretty(struct.equation())}[/cyan]")
            table.add_row("    coef:", f"[cyan]{struct.coefficients}[/cyan]")
            table.add_row("    pts:", f"[cyan]{self[pt_1].ID}, {self[pt_2].ID}[/cyan]")
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
