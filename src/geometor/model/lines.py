"""Provides line construction and manipulation for the Model class.

This module encapsulates the logic for creating symbolic lines from points, managing their inclusion in the model, and determining their intersections with other geometric elements.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sympy as sp
import sympy.geometry as spg
from rich.table import Table

from geometor.model.colors import get_color
from geometor.model.element import Element, check_existence, find_all_intersections

if TYPE_CHECKING:
    pass

__all__ = ["LinesMixin"]


class LinesMixin:
    """Mixin for the Model class containing line construction operations.
    
    This mixin provides methods to construct lines using pairs of points, identified either by their element IDs or directly by their SymPy Point objects. It handles the registration of lines in the model and the detection of intersections.
    """

    def construct_line_by_IDs(
        self, pt_1_ID: str, pt_2_ID: str, classes: list[str] | None = None, ID: str = ""
    ) -> spg.Line:
        """Find points by ID and use them with :meth:`Model.construct_line`.
        
        This convenience method allows for the creation of lines using the unique string identifiers of the start and end points, retrieving the corresponding point objects from the model before proceeding with construction.

        Args:
            pt_1_ID: The ID of the first point.
            pt_2_ID: The ID of the second point.
            classes: A list of class labels.
            ID: A string ID for the line.

        Returns:
            The constructed :class:`sympy.geometry.line.Line`.
        """

        pt_1 = self.get_element_by_ID(pt_1_ID)
        pt_2 = self.get_element_by_ID(pt_2_ID)
        return self.construct_line(pt_1, pt_2, classes, ID)

    def construct_line(
        self,
        pt_1: spg.Point,
        pt_2: spg.Point,
        classes: list[str] | None = None,
        ID: str = "",
        guide: bool = False,
    ) -> spg.Line:
        """Constructs a :class:`Line <sympy.geometry.line.Line>` from two points and adds it to the :class:`Model <geometor.model.model.Model>`.
        
        This method creates a line connecting two given points. It checks if an equivalent line already exists in the model to prevent duplicates, merging attributes if necessary. If it's a new line, it calculates intersections with existing structures.

        Args:
            pt_1: The first point of the line.
            pt_2: The second point of the line.
            classes: A list of class labels.
            ID: A string ID for the line. If empty, one is generated.
            guide: If True, the line is a guide.

        Returns:
            The constructed or retrieved :class:`sympy.geometry.line.Line`.

        Raises:
            TypeError: If ``pt_1`` or ``pt_2`` are not instances of ``sympy.geometry.point.Point``.
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

        if exists:
            # handle the logic for an existing circle
            for parent in struct.points:
                self[existing_line].parents[parent] = ""
            self[existing_line].classes.update(details.classes)
        else:
            # add struct
            self[struct] = details

            classes_str = " : " + " ".join(classes) if classes else ""
            color = get_color(struct, classes)
            self.log(f"[{color} bold]{details.ID}[/{color} bold]{classes_str}")
            table = Table(show_header=False, box=None, padding=(0, 4))
            table.add_row("    eq:", f"[cyan]{sp.pretty(struct.equation())}[/cyan]")
            table.add_row("    coef:", f"[cyan]{struct.coefficients}[/cyan]")
            table.add_row("    pts:", f"[cyan]{self[pt_1].ID}, {self[pt_2].ID}[/cyan]")
            self.log(table)

            find_all_intersections(self, struct)

            return struct
