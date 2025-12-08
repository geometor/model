"""Provides segment construction and manipulation for the Model class.

This module defines `SegmentsMixin`, which allows the creation and management of line segments within the model. Segments are defined by two points and have a measurable length.
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
    """Mixin for the Model class containing segment construction operations.
    
    This mixin augments the Model with functionality to explicitly explicitly define segments between points. While generally used for visualization or specific measurements, these segments are integrated into the model as distinct elements.
    """

    def set_segment_by_IDs(
        self, pt_1_ID: str, pt_2_ID: str, classes: list[str] | None = None, ID: str = ""
    ) -> spg.Segment:
        """Find points by ID and use them with :meth:`Model.set_segment`.
        
        This convenience method enables the creation of segments using the unique string IDs of the start and end points. It retrieves the corresponding point objects from the model and delegates construction to `set_segment`.

        Args:
            pt_1_ID: The ID of the start point.
            pt_2_ID: The ID of the end point.
            classes: A list of class labels.
            ID: A string ID for the segment.

        Returns:
            The constructed :class:`sympy.geometry.line.Segment`.
        """

        pt_1 = self.get_element_by_ID(pt_1_ID)
        pt_2 = self.get_element_by_ID(pt_2_ID)
        return self.set_segment(pt_1, pt_2, classes, ID)

    def set_segment(
        self,
        pt_1: spg.Point,
        pt_2: spg.Point,
        classes: list[str] | None = None,
        ID: str = "",
    ) -> spg.Segment:
        """Set segment (list of points) for demonstration in the model.
        
        This method constructs a segment between two points and adds it to the model. It handles ID generation, class assignment, and logging of the segment's length.

        Args:
            pt_1: The start point of the segment.
            pt_2: The end point of the segment.
            classes: A list of class labels.
            ID: A string ID for the segment. If empty, one is generated.

        Returns:
            The constructed :class:`sympy.geometry.line.Segment`.
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
