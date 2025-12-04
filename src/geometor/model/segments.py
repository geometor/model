"""
The :mod:`geometor.model.segments` module provides segment construction and manipulation for the Model class.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sympy as sp
import sympy.geometry as spg
from rich.table import Table

from geometor.model.colors import COLORS
from geometor.model.element import Element

if TYPE_CHECKING:
    pass

__all__ = ["SegmentsMixin"]


class SegmentsMixin:
    """
    Mixin for the Model class containing segment construction operations.
    """

    def set_segment_by_IDs(
        self, pt_1_ID: str, pt_2_ID: str, classes: list = None, ID: str = ""
    ) -> spg.Segment:
        """
        find points by ID and use them with :meth:`Model.set_segment`
        """

        pt_1 = self.get_element_by_ID(pt_1_ID)
        pt_2 = self.get_element_by_ID(pt_2_ID)
        return self.set_segment(pt_1, pt_2, classes, ID)

    def set_segment(
        self, pt_1: spg.Point, pt_2: spg.Point, classes=[], ID=""
    ) -> spg.Segment:
        """
        set segment (list of points) for demonstration in the model
        """
        segment = spg.Segment(pt_1, pt_2)
        if not ID:
            segment_points_IDs = [str(self[pt].ID or pt) for pt in [pt_1, pt_2]]
            segment_points_IDs = " ".join(segment_points_IDs)
            ID = f"/ {segment_points_IDs} /"
        details = Element(segment, parents=[pt_1, pt_2], classes=classes, ID=ID)

        self[segment] = details

        classes_str = " : " + " ".join(classes) if classes else ""
        self.log(
            f"[{COLORS['segment']} bold]{details.ID}[/{COLORS['segment']} bold]{classes_str}"
        )
        table = Table(show_header=False, box=None, padding=(0, 4))
        table.add_row("    len:", f"[cyan]{sp.pretty(segment.length)}[/cyan]")
        self.log(table)

        return segment
