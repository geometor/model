"""Provides segment construction and manipulation for the Model class.

This module defines `SegmentsMixin`, which allows the creation and management of line
segments within the model. Segments are defined by two points and have a measurable length.
"""

from __future__ import annotations

import sympy as sp
import sympy.geometry as spg
from rich.table import Table

from geometor.model.colors import COLORS
from geometor.model.element import Element

__all__ = ["SegmentsMixin"]


class SegmentsMixin:
    """Mixin for the Model class containing segment construction operations."""

    def set_segment_by_IDs(
        self,
        pt_1_ID: str,
        pt_2_ID: str,
        classes: list[str] | None = None,
        ID: str = "",
        *,
        guide: bool = False,
        by: str = "",
    ) -> spg.Segment:
        """Find points by ID and use them with :meth:`Model.set_segment`."""
        pt_1 = self.get_element_by_ID(pt_1_ID)
        pt_2 = self.get_element_by_ID(pt_2_ID)
        return self.set_segment(pt_1, pt_2, classes, ID, guide=guide, by=by)

    def set_segment(
        self,
        pt_1: spg.Point,
        pt_2: spg.Point,
        classes: list[str] | None = None,
        ID: str = "",
        *,
        guide: bool = False,
        by: str = "",
    ) -> spg.Segment:
        """Construct and register a :class:`sympy.geometry.Segment` ``/ A B /``."""
        segment = spg.Segment(pt_1, pt_2)
        if not ID:
            segment_points_IDs = [str(self[pt].ID or pt) for pt in [pt_1, pt_2]]
            ID = f"/ {' '.join(segment_points_IDs)} /"
        details = Element(segment, parents=[pt_1, pt_2], classes=classes, ID=ID, guide=guide)

        self[segment] = details
        if hasattr(self, "_register_in_scope"):
            self._register_in_scope(segment)
        if hasattr(self, "_record_step"):
            self._record_step(kind="construct", action="segment", elements=[details.ID], by=by)

        if self.is_logging_enabled:
            classes_str = " : " + " ".join(classes) if classes else ""
            self.log(
                f"[{COLORS['segment']} bold]{details.ID}[/{COLORS['segment']} bold]{classes_str}"
            )
            table = Table(show_header=False, box=None, padding=(0, 4))
            table.add_row("    len:", f"[cyan]{sp.pretty(segment.length)}[/cyan]")
            self.log(table)

        return segment

    construct_segment = set_segment
