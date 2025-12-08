"""Provides section construction and manipulation for the Model class.

This module defines the `Section` class and associated mixin methods. A section represents a sequence of three points on a line, and this module provides tools to create them, calculate their ratios, and determine if they exhibit Golden Ratio properties.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sympy as sp
import sympy.geometry as spg
from rich.table import Table

from geometor.model.colors import COLORS
from geometor.model.element import (
    Element,
)
from geometor.model.utils import clean_expr

if TYPE_CHECKING:
    from sympy.printing.printer import Printer

    from geometor.model.model import Model

phi = sp.Rational(1, 2) + (sp.sqrt(5) / 2)


class SectionsMixin:
    """Mixin for the Model class containing section construction operations.
    
    This mixin equips the Model with methods to construct `Section` objects. It allows sections to be defined by listing point objects or their IDs, facilitating the study of collinear points and their proportional relationships.
    """

    def set_section_by_IDs(
        self, points_IDs: list[str], classes: list[str] | None = None, ID: str = ""
    ) -> Section:
        """Find points by ID and use them with :meth:`Model.set_section`.
        
        This convenience method resolves string identifiers for points into their corresponding model elements and then creates a section. It simplifies the creation of sections when working with named points in the model.

        Args:
            points_IDs: A list of point IDs.
            classes: A list of class labels.
            ID: A string ID for the section.

        Returns:
             The constructed :class:`Section`.
        """
        points = []

        for point_ID in points_IDs:
            points.append(self.get_element_by_ID(point_ID))

        return self.set_section(points, classes, ID)

    def set_section(
        self, points: list[spg.Point], classes: list[str] | None = None, ID: str = ""
    ) -> Section:
        """Set section (list of 3 points on a line).
        
        This method constructs a `Section` from a list of three collinear points and adds it to the model. It automatically calculates the section's ratio, generates an ID if needed, and logs the section's details including segment lengths.

        Args:
            points: A list of 3 collinear points.
            classes: A list of class labels.
            ID: A string ID for the section. If empty, one is generated.

        Returns:
            The constructed :class:`Section`.
        """

        # TODO: check points and minimum count of 3
        section = Section(points)

        if not ID:
            points_IDs = [str(self[pt].ID or pt) for pt in points]
            points_IDs = " ".join(points_IDs)
            ID = f"/ {points_IDs} /"

        details = Element(section, parents=points, classes=classes, ID=ID)

        self[section] = details

        classes_str = " : " + " ".join(classes) if classes else ""
        self.log(
            f"[{COLORS['section']} bold]{details.ID}[/{COLORS['section']} bold]{classes_str}"
        )
        table = Table(show_header=False, box=None, padding=(0, 4))
        for i, length in enumerate(section.lengths):
            table.add_row(f"    len {i + 1}:", f"[cyan]{sp.pretty(length)}[/cyan]")
        table.add_row("    ratio:", f"[cyan]{sp.pretty(section.ratio)}[/cyan]")
        self.log(table)

        return section


class Section:
    def __init__(self, points: list[spg.Point]) -> None:
        assert len(points) == 3, "A section must be defined by three points."

        self.points = points
        self.segments = [
            spg.Segment(points[0], points[1]),
            spg.Segment(points[1], points[2]),
        ]
        self.clean_expr = clean_expr

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Section):
            return NotImplemented
        return self.points == other.points

    def __hash__(self) -> int:
        # Use a tuple of points for hashing, as lists are not hashable
        return hash(tuple(self.points))

    def __repr__(self) -> str:
        points_repr = [sp.srepr(p) for p in self.points]
        return f"Section([{', '.join(points_repr)}])"

    def _sstr(self, printer: Printer) -> str:
        points_repr = [printer.doprint(p) for p in self.points]
        return f"Section([{', '.join(points_repr)}])"

    def get_IDs(self, model: Model) -> list[str]:
        """Returns a list of IDs.
        
        This method retrieves the unique identifiers for each of the three points that define the section, referencing the provided model.

        Args:
            model: The model containing the points.

        Returns:
             A list of point IDs.
        """
        return [model[pt].ID for pt in self.points]

    @property
    def ratio(self) -> sp.Expr:
        """Returns the ratio of the symbolic lengths of each segment.
        
        This property calculates the ratio between the longer and shorter segments of the section. The result is returned as a simplified symbolic expression.

        Returns:
             The ratio as a symbolic expression.
        """
        l1, l2 = self.lengths
        if l1.evalf() < l2.evalf():
            l1, l2 = l2, l1
        return self.clean_expr(l1 / l2)

    @property
    def lengths(self) -> list[sp.Expr]:
        return [self.clean_expr(seg.length) for seg in self.segments]

    @property
    def floats(self) -> list[float]:
        return [float(length.evalf()) for length in self.lengths]

    @property
    def is_golden(self) -> bool:
        # First, perform a quick check using floating-point numbers.
        l1_float, l2_float = self.floats
        if l1_float < l2_float:
            l1_float, l2_float = l2_float, l1_float

        if l2_float == 0:
            return False

        ratio_float = l1_float / l2_float
        phi_float = phi.evalf()

        # Set a tolerance for the floating-point comparison.
        tolerance = 1e-5

        # Check if the ratio is close to phi.
        if abs(ratio_float - phi_float) > tolerance:
            return False

        # If the floating-point check passes, then perform the symbolic comparison.
        is_phi = sp.simplify(self.ratio - phi) == 0
        is_inv_phi = sp.simplify(self.ratio - (1 / phi)) == 0
        return is_phi or is_inv_phi

    @property
    def min_length(self) -> sp.Expr:
        return min(self.lengths)

    @property
    def min_float(self) -> float:
        return min(self.floats)

    @property
    def min_segment(self) -> spg.Segment:
        min_length_index = self.lengths.index(self.min_length())
        return self.segments[min_length_index]

    @property
    def max_length(self) -> sp.Expr:
        return max(self.lengths)

    @property
    def max_float(self) -> float:
        return max(self.floats)

    @property
    def max_segment(self) -> spg.Segment:
        max_length_index = self.lengths.index(self.max_length())
        return self.segments[max_length_index]
