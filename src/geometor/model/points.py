"""Provides point construction and manipulation for the Model class.

This module handles the creation, deduplication, and management of symbolic points
within the geometric model. It ensures that points are unique, properly linked to
their causal parents, and assigned identifiers for reference.
"""

from __future__ import annotations

import math
from collections.abc import Iterator

import sympy as sp
import sympy.geometry as spg
from rich.table import Table

from geometor.model.algebra import clean_expr, zero_test
from geometor.model.colors import get_color
from geometor.model.element import Element

__all__ = ["PointsMixin"]

_POINT_GRID_H = 1e-6
_POINT_MATCH_TOL = 1e-9


def _approx_xy(x_val: object, y_val: object) -> tuple[float, float]:
    """Return finite float approximations for ``(x_val, y_val)`` or ``(nan, nan)``."""
    try:
        fx = float(x_val) if isinstance(x_val, (int, float)) else float(sp.N(x_val, 20))
        fy = float(y_val) if isinstance(y_val, (int, float)) else float(sp.N(y_val, 20))
    except (TypeError, ValueError):
        return (float("nan"), float("nan"))
    return (fx, fy)


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

        used_ids_set: set[str] | None = getattr(self, "_used_point_ids", None)

        def _next_available_id(exclude: set[str] | None = None) -> str:
            used_ids = (
                used_ids_set
                if used_ids_set is not None
                else {self[p].ID for p in self.points if self[p].ID}
            )
            while True:
                raw_ID = next(self.ID_gen)
                self.last_point_id = raw_ID
                if self.use_point_subscript and len(raw_ID) > 1:
                    char = raw_ID[0]
                    count = len(raw_ID)
                    cand_ID = f"{char}{count}"
                else:
                    cand_ID = raw_ID
                if cand_ID not in used_ids and (not exclude or cand_ID not in exclude):
                    return cand_ID

        def _claim_explicit_id(target_pt: spg.Point, new_id: str) -> None:
            old_target_id = self[target_pt].ID
            if old_target_id == new_id:
                return
            if used_ids_set is None or new_id in used_ids_set:
                for other_pt in self.points:
                    if other_pt != target_pt and self[other_pt].ID == new_id:
                        reassigned = _next_available_id({new_id})
                        self[other_pt].ID = reassigned
                        if used_ids_set is not None:
                            used_ids_set.add(reassigned)
                        break
            if used_ids_set is not None:
                if old_target_id:
                    used_ids_set.discard(old_target_id)
                used_ids_set.add(new_id)
            self[target_pt].ID = new_id

        def _merge_existing(existing_pt: spg.Point) -> spg.Point:
            existing_el = self[existing_pt]
            for parent in parents:
                existing_el.parents[parent] = ""
            for cls in classes:
                existing_el.classes[cls] = ""
            if ID:
                _claim_explicit_id(existing_pt, ID)
            return existing_pt

        # 1. Fast structural lookup before clean_expr (O(1) hash check)
        if (
            isinstance(x_val, (int, sp.Basic))
            and isinstance(y_val, (int, sp.Basic))
            and not isinstance(x_val, sp.Float)
            and not isinstance(y_val, sp.Float)
        ):
            raw_pt = spg.Point(x_val, y_val)
            if raw_pt in self:
                return _merge_existing(raw_pt)

        # 2. Numeric 3x3 spatial grid pre-filter + exact zero_test before clean_expr
        pt_fx, pt_fy = _approx_xy(x_val, y_val)
        point_grid = getattr(self, "_point_grid", None)
        if point_grid is not None and math.isfinite(pt_fx) and math.isfinite(pt_fy):
            ix = math.floor(pt_fx / _POINT_GRID_H)
            iy = math.floor(pt_fy / _POINT_GRID_H)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for prev_pt in point_grid.get((ix + dx, iy + dy), ()):
                        prev_approx = self[prev_pt].approx_coords
                        if (
                            prev_approx is not None
                            and abs(pt_fx - prev_approx[0]) < _POINT_MATCH_TOL
                            and abs(pt_fy - prev_approx[1]) < _POINT_MATCH_TOL
                            and zero_test(x_val - prev_pt.x)
                            and zero_test(y_val - prev_pt.y)
                        ):
                            return _merge_existing(prev_pt)
        elif not (math.isfinite(pt_fx) and math.isfinite(pt_fy)):
            for prev_pt in self.points:
                if zero_test(x_val - prev_pt.x) and zero_test(y_val - prev_pt.y):
                    return _merge_existing(prev_pt)

        # 3. Genuinely new point: canonicalize coordinates and register
        simplifier = getattr(self, "_simplifier", None) or clean_expr
        x_clean = simplifier(x_val)
        y_clean = simplifier(y_val)

        pt = spg.Point(x_clean, y_clean)
        if pt in self:
            return _merge_existing(pt)

        details = Element(pt, parents, classes, ID, guide)
        if math.isfinite(pt_fx) and math.isfinite(pt_fy):
            details._approx_coords = (pt_fx, pt_fy)

        if not ID:
            ID = _next_available_id()
        elif used_ids_set is None or ID in used_ids_set:
            for other_pt in self.points:
                if self[other_pt].ID == ID:
                    reassigned = _next_available_id({ID})
                    self[other_pt].ID = reassigned
                    if used_ids_set is not None:
                        used_ids_set.add(reassigned)
                    break

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
