"""
The :mod:`geometor.model.lines` module provides line construction and manipulation for the Model class.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sympy as sp
import sympy.geometry as spg
from rich.table import Table

from geometor.model.colors import COLORS, get_color
from geometor.model.element import Element, check_existence, find_all_intersections

if TYPE_CHECKING:
    pass

__all__ = ["LinesMixin"]


class LinesMixin:
    """
    Mixin for the Model class containing line construction operations.
    """

    def construct_line_by_IDs(
        self, pt_1_ID: str, pt_2_ID: str, classes: list = None, ID: str = ""
    ) -> spg.Line:
        """
        find points by ID and use them with :meth:`Model.construct_line`
        """

        pt_1 = self.get_element_by_ID(pt_1_ID)
        pt_2 = self.get_element_by_ID(pt_2_ID)
        return self.construct_line(pt_1, pt_2, classes, ID)

    def construct_line(
        self,
        pt_1: spg.Point,
        pt_2: spg.Point,
        classes: list = None,
        ID: str = "",
        guide: bool = False,
    ) -> spg.Line:
        """
        Constructs a :class:`Line <sympy.geometry.line.Line>` from two points and
        adds it to the :class:`Model <geometor.model.model.Model>`
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
