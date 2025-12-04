"""
The :mod:`geometor.model.circles` module provides circle construction and manipulation for the Model class.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sympy as sp
import sympy.geometry as spg
from rich.table import Table

from geometor.model.colors import COLORS, get_color
from geometor.model.element import (
    CircleElement,
    check_existence,
    find_all_intersections,
)

__all__ = ["CirclesMixin"]


class CirclesMixin:
    """
    Mixin for the Model class containing circle construction operations.
    """

    def construct_circle_by_IDs(
        self, pt_1_ID: str, pt_2_ID: str, classes: list = None, ID: str = ""
    ) -> spg.Line:
        """
        find points by ID and use them with :meth:`Model.construct_line`
        """

        pt_1 = self.get_element_by_ID(pt_1_ID)
        pt_2 = self.get_element_by_ID(pt_2_ID)
        return self.construct_circle(pt_1, pt_2, classes, ID)

    def construct_circle(
        self,
        pt_center: spg.Point,
        pt_radius: spg.Point,
        classes: list = None,
        ID: str = "",
        guide: bool = False,
    ) -> spg.Circle:
        """
        Constructs a Circle from two points and adds it to the model.
        """
        self.clear_new_points()

        if classes is None:
            classes = []
        # find radius length for sympy.Circle
        radius_len = pt_center.distance(pt_radius)

        if not isinstance(pt_center, spg.Point) or not isinstance(pt_radius, spg.Point):
            raise TypeError(
                "Both pt_center and pt_radius must be instances of sympy.geometry.point.Point"
            )

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
        #  details.pt_radius = pt_radius

        exists, existing_circle = check_existence(self, struct, self.circles)
        if exists:
            # handle the logic for an existing circle
            self[existing_circle].parents[details.pt_radius] = ""
            self[existing_circle].classes.update(details.classes)
            return existing_circle
        else:
            # add the new circle to the model

            self[struct] = details

            classes_str = " : " + " ".join(classes) if classes else ""
            color = get_color(struct, classes)
            self.log(f"[{color} bold]{details.ID}[/{color} bold]{classes_str}")
            table = Table(show_header=False, box=None, padding=(0, 4))
            table.add_row("    ctr:", f"[cyan]{self[pt_center].ID}[/cyan]")
            table.add_row("    r:", f"[cyan]{sp.pretty(struct.radius)}[/cyan]")
            table.add_row("    eq:", f"[cyan]{sp.pretty(struct.equation())}[/cyan]")
            self.log(table)

            find_all_intersections(self, struct)

            return struct
