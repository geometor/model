"""Provides wedge construction and manipulation for the Model class.

This module introduces the `Wedge` element, which represents a sector of a circle defined by a center, a radius point, and sweep angles. It handles the creation, validation, and property calculation (like area and arc length) for these wedge shapes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sympy as sp
import sympy.geometry as spg
from rich.table import Table

from geometor.model.colors import COLORS
from geometor.model.element import (
    CircleElement,
)

if TYPE_CHECKING:
    from sympy.printing.printer import Printer


class WedgesMixin:
    """Mixin for the Model class containing wedge construction operations.
    
    This mixin provides the Model with the capability to define and manage `Wedge` elements. It includes methods to construct wedges from defining points and integrate them into the geometric model.
    """

    def set_wedge_by_IDs(
        self,
        pt_center_ID: str,
        pt_radius_ID: str,
        pt_sweep_start_ID: str,
        pt_sweep_end_ID: str,
        direction: str = "clockwise",
        classes: list[str] | None = None,
        ID: str = "",
    ) -> Wedge:
        """Find points by ID and use them with :meth:`Model.set_wedge`.

        Args:
            pt_center_ID: The ID of the center point.
            pt_radius_ID: The ID of the radius point.
            pt_sweep_start_ID: The ID of the sweep start point.
            pt_sweep_end_ID: The ID of the sweep end point.
            direction: Direction of the sweep (default "clockwise").
            classes: A list of class labels.
            ID: A string ID for the wedge.

        Returns:
            The constructed :class:`Wedge`.
        """
        pt_center = self.get_element_by_ID(pt_center_ID)
        pt_radius = self.get_element_by_ID(pt_radius_ID)
        pt_sweep_start = self.get_element_by_ID(pt_sweep_start_ID)
        pt_sweep_end = self.get_element_by_ID(pt_sweep_end_ID)

        return self.set_wedge(
            pt_center,
            pt_radius,
            pt_sweep_start,
            pt_sweep_end,
            direction,
            classes,
            ID,
        )

    def set_wedge(
        self,
        pt_center: spg.Point,
        pt_radius: spg.Point,
        pt_sweep_start: spg.Point,
        pt_sweep_end: spg.Point,
        direction: str = "clockwise",
        classes: list[str] | None = None,
        ID: str = "",
    ) -> Wedge:
        """Sets a Wedge from 3 points and adds it to the model.
        
        This method constructs a `Wedge` defined by a center, a radius point, and sweep points. It handles the low-level details of creating the `Wedge` object, wrapping it in an `Element`, calculating intersections, and adding it to the model structure.

        Args:
            pt_center: Point for circle center.
            pt_radius: Point to mark radius.
            pt_sweep_start: A SymPy Point marking the start of the sweep.
            pt_sweep_end: A SymPy Point marking the end of the sweep.
            direction: Direction of the sweep (default "clockwise").
            classes: A list of string names for classes defining a set of styles.
            ID: A text ID for use in plotting and reporting.

        Returns:
            The constructed :class:`Wedge`.

        **example**

        .. code-block:: python

            from geometor.elements import *
            model = Model("demo")
            A = model.set_point(0, 0, classes=["given"], ID="A")
            B = model.set_point(1, 0, classes=["given"], ID="B")
            model.construct_circle(A, B)
            model.construct_circle(B, A)
            model.set_wedge(A, B, C, D)
            # <Wedge object ...>

        """

        if classes is None:
            classes = {}
        # find radius length for sympy.Circle
        #  radius_len = pt_center.distance(pt_radius)

        if not isinstance(pt_center, spg.Point) or not isinstance(pt_radius, spg.Point):
            raise TypeError(
                "Both pt_center and pt_radius must be instances of sympy.geometry.point.Point"
            )

        struct = Wedge([pt_center, pt_radius, pt_sweep_start, pt_sweep_end], direction)

        if not ID:
            pt_center_ID = self[pt_center].ID
            pt_radius_ID = self[pt_radius].ID
            ID = f"( {pt_center_ID} {pt_radius_ID} )"
            ID += (
                f"< {self[pt_sweep_start].ID} {pt_center_ID} {self[pt_sweep_end].ID} >"
            )

        details = CircleElement(
            struct,
            parents=[pt_center, pt_radius],
            classes=classes,
            ID=ID,
            pt_radius=pt_radius,
        )

        self[struct] = details

        classes_str = " : " + " ".join(classes) if classes else ""
        self.log(
            f"[{COLORS['polygon']} bold]{details.ID}[/{COLORS['polygon']} bold]{classes_str}"
        )
        table = Table(show_header=False, box=None, padding=(0, 4))
        table.add_row("    r:", f"[cyan]{sp.pretty(struct.circle.radius)}[/cyan]")
        table.add_row("    rad:", f"[cyan]{sp.pretty(struct.radians)}[/cyan]")
        table.add_row("    deg:", f"[cyan]{sp.pretty(struct.degrees)}[/cyan]")
        self.log(table)

        return struct


class Wedge:
    def __init__(self, points: list[spg.Point], direction: str = "clockwise") -> None:
        assert len(points) == 4, "A wedge must be defined by four points."
        self.points = points
        self.pt_center = points[0]
        self.pt_radius = points[1]
        self.pt_sweep_start = points[2]
        self.pt_sweep_end = points[3]

        self._circle = spg.Circle(
            self.pt_center, self.pt_center.distance(self.pt_radius)
        )
        self.sweep_ray = spg.Ray(self.pt_center, self.pt_sweep_end)
        self.start_ray = spg.Ray(self.pt_center, self.pt_sweep_start)

        self.start_point, self.end_point = self._find_arc_endpoints()
        self.direction = direction

    def __repr__(self) -> str:
        points_repr = [sp.srepr(p) for p in self.points]
        return f"Wedge([{', '.join(points_repr)}])"

    def _sstr(self, printer: Printer) -> str:
        points_repr = [printer.doprint(p) for p in self.points]
        return f"Wedge([{', '.join(points_repr)}])"

    def _find_arc_endpoints(self) -> tuple[spg.Point, spg.Point]:
        intersections_start = self.circle.intersection(self.start_ray)
        intersections_sweep = self.circle.intersection(self.sweep_ray)

        # Ensure the rays intersect the circle
        if intersections_start and intersections_sweep:
            return intersections_start[0], intersections_sweep[0]
        else:
            raise ValueError("Rays do not intersect the circle.")

    @property
    def circle(self) -> spg.Circle:
        return self._circle

    @property
    def radians(self) -> sp.Expr:
        angle = self.start_ray.angle_between(self.sweep_ray)
        return angle if self.direction == "clockwise" else 2 * sp.pi - angle

    @property
    def degrees(self) -> sp.Expr:
        return sp.deg(self.radians)

    @property
    def ratio(self) -> sp.Expr:
        return self.radians / (2 * sp.pi)

    @property
    def area(self) -> sp.Expr:
        # Using the ratio of the angle to the full circle to find the area
        return self.circle.area * self.ratio

    @property
    def arc_length(self) -> sp.Expr:
        # Using the ratio of the angle to the full circle to find the arc length
        return self.circle.circumference * self.ratio

    @property
    def perimeter(self) -> sp.Expr:
        # Including the two radii to form the full boundary of the wedge
        return self.arc_length + 2 * self.circle.radius
