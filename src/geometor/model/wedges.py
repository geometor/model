"""
The :mod:`geometor.model.wedges` module provides wedge construction and manipulation for the Model class.
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
    pass


class WedgesMixin:
    """
    Mixin for the Model class containing wedge construction operations.
    """

    def set_wedge(
        self,
        pt_center: spg.Point,
        pt_radius: spg.Point,
        pt_sweep_start: spg.Point,
        pt_sweep_end: spg.Point,
        direction="clockwise",
        classes: list = None,
        ID: str = "",
    ) -> Wedge:
        """
        sets a Wedge from 3 points and adds it to the model.

        operations
        ~~~~~~~~~~
        - create an instance of :class:`geometor.model.Wedge`
        - create a ``details`` object from :class:`Element`
        - add parents to details
            initial parents are the two starting points
        - check for duplicates in in the ``model``
        - find intersection points for new element with all precedng elements
        - Add ``circle`` to the model.

        parameters
        ----------
        - ``pt_center`` : :class:`sympy.geometry.point.Point` : point for circle center
        - ``pt_radius`` : :class:`sympy.geometry.point.Point` : point to mark radius
        - ``pt_end`` : :class:`sympy.geometry.point.Point` : A SymPy Point marking the sweep of the wedge
        - ``classes`` : :class:`list` *optional* : A list of string names for classes defining a set of styles. Defaults to None.
        - ``ID`` : :class:`str` *optional* : A text ID for use in plotting and reporting. Defaults to an empty string.

        returns
        -------
        - :class:`Wedge`
            The portion of a circle

        example
        -------
            >>> from geometor.elements import *
            >>> model = Model("demo")
            >>> A = model.set_point(0, 0, classes=["given"], ID="A")
            >>> B = model.set_point(1, 0, classes=["given"], ID="B")
            >>> model.construct_circle(A, B)
            >>> model.construct_circle(B, A)
            >>> model._set_wedge_by_IDs('A', 'B', 'C')
            <Wedge object ...>

        notes
        -----
        SymPy defines a circle as a center point and a radius length, so the radius length is calculated for the spg.Circle.

        """

        if classes is None:
            classes = {}
        # find radius length for sympy.Circle
        #  radius_len = pt_center.distance(pt_radius)

        if not isinstance(pt_center, spg.Point) or not isinstance(pt_radius, spg.Point):
            raise TypeError(
                "Both pt_center and pt_radius must be instances of sympy.geometry.point.Point"
            )

        struct = Wedge([pt_center, pt_radius, pt_sweep_start, pt_sweep_end])

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
    def __init__(self, points: list[spg.Point]):
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
        # self.direction = direction

    def __repr__(self):
        points_repr = [sp.srepr(p) for p in self.points]
        return f"Wedge([{', '.join(points_repr)}])"

    def _sstr(self, printer):
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
