"""Provides point construction and manipulation for the Model class.

This module handles the creation, deduplication, and management of symbolic points
within the geometric model. It ensures that points are unique, properly linked to
their causal parents, and assigned identifiers for reference.
"""

from __future__ import annotations

from collections.abc import Iterator

import sympy as sp
import sympy.geometry as spg
from rich.table import Table

from geometor.model.algebra import clean_expr, zero_test
from geometor.model.colors import get_color
from geometor.model.element import Element

__all__ = ["PointsMixin"]


class PointsMixin:
    """Mixin for the Model class containing point construction operations."""

    def point_ID_generator(self) -> Iterator[str]:
        """Generate a sequence of point IDs (A, B, C, ... AA, AB, ...)."""
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        repeat = 1

        while True:
            for letter in letters:
                yield str(letter) * repeat
            repeat += 1

    def given_point(
        self,
        x_val: sp.Expr | float,
        y_val: sp.Expr | float,
        ID: str = "",
        *,
        label: str = "",
        classes: list[str] | None = None,
        by: str = "given",
    ) -> spg.Point:
        """Register an initial given point in the model with ``"given"`` classification."""
        cls = list(classes) if classes else []
        if "given" not in cls:
            cls.insert(0, "given")
        return self.set_point(
            x_val,
            y_val,
            classes=cls,
            ID=ID,
            label=label,
            by=by,
        )

    def set_point(
        self,
        x_val: sp.Expr | float,
        y_val: sp.Expr | float,
        parents: list | None = None,
        classes: list[str] | None = None,
        ID: str = "",
        guide: bool = False,
        label: str = "",
        *,
        by: str = "",
        record_step: bool = True,
    ) -> spg.Point:
        """Add a point to the model, find duplicates, clean values, and set parents and classes.

        Args:
            x_val: The x-value of the point.
            y_val: The y-value of the point.
            parents: A list of causal parent elements.
            classes: A list of string names for classes defining a set of styles.
            ID: A text ID for use in plotting and reporting.
            guide: If True, the point is a guide.
            label: Optional alias for ``ID``.
            by: Optional Euclidean justification citation.
            record_step: Whether to append a ``Step`` entry when a new point is added.

        Returns:
            The exact :class:`sympy.geometry.Point` registered in the model.
        """
        if label and not ID:
            ID = label
        if classes is None:
            classes = []
        if parents is None:
            parents = []

        simplifier = getattr(self, "_simplifier", None) or clean_expr
        x_clean = simplifier(x_val)
        y_clean = simplifier(y_val)

        pt = spg.Point(x_clean, y_clean)
        details = Element(pt, parents, classes, ID, guide)

        def _next_available_id(exclude: set[str] | None = None) -> str:
            used_ids = {self[p].ID for p in self.points if self[p].ID}
            if exclude:
                used_ids.update(exclude)
            while True:
                raw_ID = next(self.ID_gen)
                self.last_point_id = raw_ID
                if self.use_point_subscript and len(raw_ID) > 1:
                    char = raw_ID[0]
                    count = len(raw_ID)
                    cand_ID = f"{char}{count}"
                else:
                    cand_ID = raw_ID
                if cand_ID not in used_ids:
                    return cand_ID

        def _claim_explicit_id(target_pt: spg.Point, new_id: str) -> None:
            for other_pt in self.points:
                if other_pt != target_pt and self[other_pt].ID == new_id:
                    self[other_pt].ID = _next_available_id({new_id})
            self[target_pt].ID = new_id

        # Fast structural lookup in dict first (O(1) hash check)
        if pt in self and isinstance(pt, spg.Point):
            for parent in details.parents:
                self[pt].parents[parent] = ""
            self[pt].classes.update(details.classes)
            if ID:
                _claim_explicit_id(pt, ID)
            return pt

        # Numeric cached bounding-box pre-filter followed by exact algebraic zero_test
        pt_approx = details.approx_coords
        assert pt_approx is not None
        pt_fx, pt_fy = pt_approx
        for prev_pt in self.points:
            prev_approx = self[prev_pt].approx_coords
            if (
                prev_approx is not None
                and abs(pt_fx - prev_approx[0]) < 1e-9
                and abs(pt_fy - prev_approx[1]) < 1e-9
                and zero_test(pt.x - prev_pt.x)
                and zero_test(pt.y - prev_pt.y)
            ):
                for parent in details.parents:
                    self[prev_pt].parents[parent] = ""
                self[prev_pt].classes.update(details.classes)
                if ID:
                    _claim_explicit_id(prev_pt, ID)
                return prev_pt

        if not ID:
            ID = _next_available_id()
        else:
            for other_pt in self.points:
                if self[other_pt].ID == ID:
                    self[other_pt].ID = _next_available_id({ID})

        details.ID = ID
        self[pt] = details
        self._new_points.append(pt)
        if hasattr(self, "_register_in_scope"):
            self._register_in_scope(pt)
        if record_step and hasattr(self, "_record_step"):
            step_kind = "given" if "given" in details.classes else "construct"
            self._record_step(kind=step_kind, action="point", elements=[ID], by=by)

        if self.is_logging_enabled:
            color = get_color(pt, classes)
            classes_str = " : " + " ".join(classes) if classes else ""
            self.log(f"    [{color} bold]{ID}[/{color} bold]{classes_str}")

            table = Table(show_header=False, box=None, padding=(0, 4))
            table.add_row("    x:", f"[cyan]{sp.pretty(pt.x)}[/cyan]")
            table.add_row("    y:", f"[cyan]{sp.pretty(pt.y)}[/cyan]")
            self.log(table)

        if self._analysis_hook:
            self._analysis_hook(self, pt)

        return pt
