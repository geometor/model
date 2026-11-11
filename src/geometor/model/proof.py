"""Deductive proof ledger, exact algebraic assertion verifier, and construction timeline.

Provides:

- :class:`Step`: Structured chronological step record for ``given``, ``construct``,
  ``intersect``, ``assert``, and ``conclude`` phases.
- :exc:`ProofAssertionError`: Raised when an exact algebraic invariant check fails in SymPy.
- :class:`ProofMixin`: Equips :class:`~geometor.model.Model` with SymPy-verified Euclidean
  demonstration assertions (:meth:`~ProofMixin.assert_equal`,
  :meth:`~ProofMixin.assert_spread_equal`, :meth:`~ProofMixin.assert_perpendicular`,
  :meth:`~ProofMixin.assert_parallel`, :meth:`~ProofMixin.assert_congruent`,
  :meth:`~ProofMixin.assert_area_equal`, :meth:`~ProofMixin.assert_collinear`,
  :meth:`~ProofMixin.assert_concyclic`, :meth:`~ProofMixin.assert_incident`, and
  :meth:`~ProofMixin.conclude`).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

import sympy as sp
import sympy.geometry as spg

from geometor.model.algebra import exact_sign, zero_test
from geometor.model.invariants import (
    Angle,
    _line_normal,
    line_spread,
    polygon_area2,
    quadrance,
    signed_area2,
    vertex_dot_sign,
    vertex_spread,
)

__all__ = [
    "ProofAssertionError",
    "ProofMixin",
    "Step",
]


class ProofAssertionError(AssertionError):
    """Raised when a deductive geometric assertion fails exact symbolic verification."""


@dataclass
class Step:
    """Chronological construction or demonstration step recorded by :class:`~geometor.model.Model`."""

    index: int
    kind: str
    action: str
    elements: list[str] = field(default_factory=list)
    by: str = ""
    label: str = ""
    focus: list[str] = field(default_factory=list)
    parent_scope: str = ""
    primitive: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize this :class:`Step` to a JSON-compatible dictionary."""
        data: dict[str, Any] = {
            "index": self.index,
            "kind": self.kind,
            "action": self.action,
            "elements": list(self.elements),
        }
        if self.by:
            data["by"] = self.by
        if self.label:
            data["label"] = self.label
        if self.focus:
            data["focus"] = list(self.focus)
        if self.parent_scope:
            data["parent_scope"] = self.parent_scope
        if self.primitive:
            data["primitive"] = dict(self.primitive)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Step:
        """Reconstruct a :class:`Step` from its dictionary representation."""
        return cls(
            index=int(data["index"]),
            kind=str(data["kind"]),
            action=str(data["action"]),
            elements=list(data.get("elements", [])),
            by=str(data.get("by", "")),
            label=str(data.get("label", "")),
            focus=list(data.get("focus", [])),
            parent_scope=str(data.get("parent_scope", "")),
            primitive=dict(data.get("primitive", {})),
        )


def _extract_vertices(poly_or_pts: spg.Polygon | spg.Segment | Sequence[spg.Point]) -> list[spg.Point]:
    if isinstance(poly_or_pts, spg.Polygon):
        return list(poly_or_pts.vertices)
    if isinstance(poly_or_pts, (list, tuple)):
        return list(poly_or_pts)
    raise TypeError(f"Expected Polygon or sequence of Points, got {type(poly_or_pts)!r}")


def _line_coeffs(line_like: spg.Line | spg.Segment | tuple[spg.Point, spg.Point]) -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    if isinstance(line_like, (spg.Line, spg.Segment)):
        p1, p2 = line_like.p1, line_like.p2
    elif isinstance(line_like, tuple) and len(line_like) == 2:
        p1, p2 = line_like
    else:
        raise TypeError(f"Expected Line, Segment, or (Point, Point), got {type(line_like)!r}")
    a = p1.y - p2.y
    b = p2.x - p1.x
    c = p1.x * p2.y - p2.x * p1.y
    return a, b, c


class ProofMixin:
    """Mixin for :class:`~geometor.model.Model` providing exact symbolic proof verification."""

    def _resolve_id(self, item: Any) -> str:
        if isinstance(item, str):
            return item
        try:
            if item in self and self[item].ID:
                return self[item].ID
        except TypeError:
            pass
        if isinstance(item, tuple) and all(isinstance(p, spg.Point) for p in item):
            ids = [self._resolve_id(p) for p in item]
            if len(ids) == 2:
                return f"/ {ids[0]} {ids[1]} /"
            if len(ids) == 3:
                return f"< {ids[0]} {ids[1]} {ids[2]} )"
            return f"< {' '.join(ids)} >"
        if isinstance(item, Angle):
            ids = [self._resolve_id(p) for p in item.points]
            return f"< {ids[0]} {ids[1]} {ids[2]} )"
        return str(item)

    def _resolve_ids(self, items: Sequence[Any] | None) -> list[str]:
        if not items:
            return []
        return [self._resolve_id(it) for it in items]

    def _record_step(
        self,
        *,
        kind: str,
        action: str,
        elements: Sequence[Any] | None = None,
        by: str = "",
        label: str = "",
        focus: Sequence[Any] | None = None,
        primitive: dict[str, Any] | None = None,
    ) -> Step:
        scope_stack = getattr(self, "_scope_stack", [])
        parent_scope = scope_stack[-1].scope_id if scope_stack else ""
        el_ids = self._resolve_ids(elements)
        focus_ids = self._resolve_ids(focus) if focus is not None else []
        step = Step(
            index=len(self.steps),
            kind=kind,
            action=action,
            elements=el_ids,
            by=by,
            label=label,
            focus=focus_ids,
            parent_scope=parent_scope,
            primitive=dict(primitive) if primitive else {},
        )
        self.steps.append(step)
        return step

    def assert_equal(
        self,
        *items: spg.Segment | tuple[spg.Point, spg.Point],
        by: str = "",
        label: str = "",
        focus: Sequence[Any] | None = None,
    ) -> Step:
        """Verify exact equality of segment quadrances :math:`Q(s_0) = Q(s_1) = \\dots`.

        Args:
            *items: Two or more :class:`sympy.geometry.Segment` objects or ``(P, Q)`` point pairs.
            by: Optional Euclidean citation (e.g., ``"Def.15"``, ``"C.N.1"``, ``"I.4"``).
            label: Optional step caption.
            focus: Optional sequence of elements to highlight during this step.

        Returns:
            The recorded :class:`Step`.

        Raises:
            ProofAssertionError: If any pair of quadrances differs symbolically.
        """
        if len(items) < 2:
            raise ValueError("assert_equal requires at least 2 segments or point pairs.")

        def _item_quad(it: spg.Segment | tuple[spg.Point, spg.Point]) -> sp.Expr:
            if isinstance(it, spg.Segment):
                return quadrance(it)
            if isinstance(it, tuple) and len(it) == 2:
                return quadrance(it[0], it[1])
            raise TypeError(f"Expected Segment or (Point, Point), got {type(it)!r}")

        q0 = _item_quad(items[0])
        id0 = self._resolve_id(items[0])
        for it in items[1:]:
            qi = _item_quad(it)
            if not zero_test(qi - q0):
                idi = self._resolve_id(it)
                raise ProofAssertionError(
                    f"Quadrance mismatch in assert_equal (by={by!r}): "
                    f"Q({id0}) = {q0} != Q({idi}) = {qi} (diff = {sp.simplify(qi - q0)})"
                )

        self._tick_group_counter += 1
        group_id = self._tick_group_counter
        for it in items:
            if isinstance(it, spg.Segment) and it in self:
                self[it].markers.append({"marker": "tick", "tick_group": group_id})

        return self._record_step(
            kind="assert",
            action="equal",
            elements=items,
            by=by,
            label=label,
            focus=focus,
            primitive={
                "marker": "tick",
                "tick_group": group_id,
                "quadrance_latex": sp.latex(q0),
            },
        )

    def assert_spread_equal(
        self,
        *angles: Angle | tuple[spg.Point, spg.Point, spg.Point] | tuple[Any, Any],
        signed: bool = True,
        by: str = "",
        label: str = "",
        focus: Sequence[Any] | None = None,
    ) -> Step:
        """Verify exact equality of angle spreads (and acute/obtuse sign when ``signed=True``).

        Args:
            *angles: Two or more :class:`Angle` objects, ``(B, A, C)`` point triples (vertex ``A``),
                or ``(line1, line2)`` pairs.
            signed: When ``True`` (default), distinguishes supplementary acute vs obtuse vertex angles.
            by: Optional Euclidean citation (e.g., ``"I.5"``, ``"I.8"``, ``"I.29"``).
            label: Optional step caption.
            focus: Optional sequence of elements to highlight.
        """
        if len(angles) < 2:
            raise ValueError("assert_spread_equal requires at least 2 angles.")

        def _eval_angle(ang: Any) -> tuple[sp.Expr, int | None]:
            if isinstance(ang, Angle):
                return ang.spread, ang.dot_sign
            if (
                isinstance(ang, tuple)
                and len(ang) == 3
                and all(isinstance(p, spg.Point) for p in ang)
            ):
                return vertex_spread(ang[0], ang[1], ang[2]), vertex_dot_sign(ang[0], ang[1], ang[2])
            if isinstance(ang, tuple) and len(ang) == 2:
                return line_spread(ang[0], ang[1]), None
            raise TypeError(
                f"Expected Angle, (B, A, C) Points, or (l1, l2) Lines, got {type(ang)!r}"
            )

        s0, d0 = _eval_angle(angles[0])
        id0 = self._resolve_id(angles[0])
        for ang in angles[1:]:
            si, di = _eval_angle(ang)
            idi = self._resolve_id(ang)
            if not zero_test(si - s0):
                raise ProofAssertionError(
                    f"Spread mismatch in assert_spread_equal (by={by!r}): "
                    f"s({id0}) = {s0} != s({idi}) = {si}"
                )
            if signed and d0 is not None and di is not None and d0 != di:
                raise ProofAssertionError(
                    f"Supplementary angle mismatch in assert_spread_equal (by={by!r}): "
                    f"{id0} (dot_sign={d0}) and {idi} (dot_sign={di}) have equal spread {s0} "
                    "but opposite acute/obtuse orientation."
                )

        self._angle_group_counter += 1
        group_id = self._angle_group_counter
        for ang in angles:
            if isinstance(ang, Angle) and ang in self:
                self[ang].markers.append({"marker": "angle_arc", "angle_group": group_id})

        return self._record_step(
            kind="assert",
            action="spread_equal",
            elements=angles,
            by=by,
            label=label,
            focus=focus,
            primitive={
                "marker": "angle_arc",
                "angle_group": group_id,
                "spread_latex": sp.latex(s0),
            },
        )

    assert_angle_equal = assert_spread_equal

    def assert_perpendicular(
        self,
        l1: spg.Line | spg.Segment | tuple[spg.Point, spg.Point],
        l2: spg.Line | spg.Segment | tuple[spg.Point, spg.Point],
        *,
        at: spg.Point | None = None,
        by: str = "",
        label: str = "",
        focus: Sequence[Any] | None = None,
    ) -> Step:
        """Verify exact orthogonality (:math:`s(l_1, l_2) = 1`, :math:`a_1 a_2 + b_1 b_2 = 0`)."""
        a1, b1, c1 = _line_coeffs(l1)
        a2, b2, c2 = _line_coeffs(l2)
        dot = a1 * a2 + b1 * b2
        if not zero_test(dot):
            raise ProofAssertionError(
                f"Lines {self._resolve_id(l1)} and {self._resolve_id(l2)} are not perpendicular "
                f"(by={by!r}): normal dot product = {dot} != 0."
            )
        if at is not None and (
            not zero_test(a1 * at.x + b1 * at.y + c1)
            or not zero_test(a2 * at.x + b2 * at.y + c2)
        ):
            raise ProofAssertionError(
                f"Foot point {self._resolve_id(at)} does not lie on both perpendicular lines."
            )

        prim: dict[str, Any] = {"marker": "right_angle"}
        if at is not None:
            prim["at"] = self._resolve_id(at)

        return self._record_step(
            kind="assert",
            action="perpendicular",
            elements=[l1, l2],
            by=by,
            label=label,
            focus=focus,
            primitive=prim,
        )

    def assert_parallel(
        self,
        l1: spg.Line | spg.Segment | tuple[spg.Point, spg.Point],
        l2: spg.Line | spg.Segment | tuple[spg.Point, spg.Point],
        *,
        by: str = "",
        label: str = "",
        focus: Sequence[Any] | None = None,
    ) -> Step:
        """Verify exact parallelism (:math:`s(l_1, l_2) = 0`, :math:`a_1 b_2 - a_2 b_1 = 0`)."""
        a1, b1 = _line_normal(l1)
        a2, b2 = _line_normal(l2)
        det = a1 * b2 - a2 * b1
        if not zero_test(det):
            raise ProofAssertionError(
                f"Lines {self._resolve_id(l1)} and {self._resolve_id(l2)} are not parallel "
                f"(by={by!r}): normal cross product = {det} != 0."
            )

        self._parallel_group_counter += 1
        group_id = self._parallel_group_counter
        for ln in (l1, l2):
            if isinstance(ln, (spg.Line, spg.Segment)) and ln in self:
                self[ln].markers.append({"marker": "parallel_arrow", "parallel_group": group_id})

        return self._record_step(
            kind="assert",
            action="parallel",
            elements=[l1, l2],
            by=by,
            label=label,
            focus=focus,
            primitive={
                "marker": "parallel_arrow",
                "parallel_group": group_id,
            },
        )

    def assert_congruent(
        self,
        poly1: spg.Polygon | Sequence[spg.Point],
        poly2: spg.Polygon | Sequence[spg.Point],
        *,
        by: str = "",
        label: str = "",
        focus: Sequence[Any] | None = None,
    ) -> Step:
        """Verify exact vertex-for-vertex Euclidean congruence (all side quadrances & signed angles)."""
        v1 = _extract_vertices(poly1)
        v2 = _extract_vertices(poly2)
        if len(v1) != len(v2) or len(v1) < 3:
            raise ProofAssertionError(
                f"Congruence requires polygons with matching vertex count >= 3; "
                f"got {len(v1)} and {len(v2)}."
            )

        n = len(v1)
        for k in range(n):
            q1 = quadrance(v1[k], v1[(k + 1) % n])
            q2 = quadrance(v2[k], v2[(k + 1) % n])
            if not zero_test(q1 - q2):
                raise ProofAssertionError(
                    f"Side {k} quadrance mismatch in assert_congruent (by={by!r}): "
                    f"{q1} != {q2}."
                )

            p_prev1, p_curr1, p_next1 = v1[(k - 1) % n], v1[k], v1[(k + 1) % n]
            p_prev2, p_curr2, p_next2 = v2[(k - 1) % n], v2[k], v2[(k + 1) % n]
            s1 = vertex_spread(p_prev1, p_curr1, p_next1)
            s2 = vertex_spread(p_prev2, p_curr2, p_next2)
            d1 = vertex_dot_sign(p_prev1, p_curr1, p_next1)
            d2 = vertex_dot_sign(p_prev2, p_curr2, p_next2)
            if not zero_test(s1 - s2) or d1 != d2:
                raise ProofAssertionError(
                    f"Vertex {k} angle mismatch in assert_congruent (by={by!r}): "
                    f"(spread={s1}, sign={d1}) != (spread={s2}, sign={d2})."
                )

        return self._record_step(
            kind="assert",
            action="congruent",
            elements=[poly1, poly2],
            by=by,
            label=label,
            focus=focus,
        )

    def assert_area_equal(
        self,
        poly1: spg.Polygon | Sequence[spg.Point],
        poly2: spg.Polygon | Sequence[spg.Point],
        *,
        by: str = "",
        label: str = "",
        focus: Sequence[Any] | None = None,
    ) -> Step:
        """Verify exact equality of polygon areas (for cut-and-paste / Pythagorean proofs)."""
        v1 = _extract_vertices(poly1)
        v2 = _extract_vertices(poly2)
        a1 = polygon_area2(v1)
        a2 = polygon_area2(v2)
        if not zero_test(a1 - a2):
            raise ProofAssertionError(
                f"Area mismatch in assert_area_equal (by={by!r}): "
                f"Area({self._resolve_id(poly1)}) = {a1 / 2} != Area({self._resolve_id(poly2)}) = {a2 / 2}."
            )

        return self._record_step(
            kind="assert",
            action="area_equal",
            elements=[poly1, poly2],
            by=by,
            label=label,
            focus=focus,
            primitive={"area_latex": sp.latex(a1 / 2)},
        )

    def assert_collinear(
        self,
        *points: spg.Point,
        by: str = "",
        label: str = "",
        focus: Sequence[Any] | None = None,
    ) -> Step:
        """Verify exact collinearity of 3 or more points via signed-area determinants."""
        if len(points) < 3:
            raise ValueError("assert_collinear requires at least 3 points.")

        p0 = points[0]
        p1: spg.Point | None = None
        for cand in points[1:]:
            if not (zero_test(cand.x - p0.x) and zero_test(cand.y - p0.y)):
                p1 = cand
                break

        if p1 is not None:
            for pt in points[1:]:
                det = signed_area2(p0, p1, pt)
                if not zero_test(det):
                    raise ProofAssertionError(
                        f"Points {', '.join(self._resolve_ids(points))} are not collinear "
                        f"(by={by!r}): det = {det} != 0."
                    )

        return self._record_step(
            kind="assert",
            action="collinear",
            elements=points,
            by=by,
            label=label,
            focus=focus,
        )

    def assert_concyclic(
        self,
        *points: spg.Point,
        by: str = "",
        label: str = "",
        focus: Sequence[Any] | None = None,
    ) -> Step:
        """Verify that 4 or more points lie on a single finite Euclidean circle."""
        if len(points) < 4:
            raise ValueError("assert_concyclic requires at least 4 points.")

        p0, p1, p2 = points[0], points[1], points[2]
        if zero_test(signed_area2(p0, p1, p2)):
            raise ProofAssertionError(
                f"First three points ({self._resolve_id(p0)}, {self._resolve_id(p1)}, "
                f"{self._resolve_id(p2)}) are collinear and do not define a finite circle."
            )

        for pt in points[3:]:
            mat = sp.Matrix(
                [
                    [p.x, p.y, p.x**2 + p.y**2, sp.Integer(1)]
                    for p in (p0, p1, p2, pt)
                ]
            )
            det = mat.det()
            if not zero_test(det):
                raise ProofAssertionError(
                    f"Point {self._resolve_id(pt)} is not concyclic with "
                    f"({self._resolve_id(p0)}, {self._resolve_id(p1)}, {self._resolve_id(p2)}) "
                    f"(by={by!r})."
                )

        return self._record_step(
            kind="assert",
            action="concyclic",
            elements=points,
            by=by,
            label=label,
            focus=focus,
        )

    def assert_incident(
        self,
        pt: spg.Point,
        struct: spg.Line | spg.Circle | spg.Segment,
        *,
        by: str = "",
        label: str = "",
        focus: Sequence[Any] | None = None,
    ) -> Step:
        """Verify exact incidence of ``pt`` on a ``Line``, ``Circle``, or ``Segment``."""
        if isinstance(struct, spg.Line):
            a, b, c = _line_coeffs(struct)
            ok = zero_test(a * pt.x + b * pt.y + c)
        elif isinstance(struct, spg.Circle):
            ok = zero_test(
                (pt.x - struct.center.x) ** 2 + (pt.y - struct.center.y) ** 2 - struct.radius**2
            )
        elif isinstance(struct, spg.Segment):
            a_pt, b_pt = struct.p1, struct.p2
            dx, dy = b_pt.x - a_pt.x, b_pt.y - a_pt.y
            d2 = dx**2 + dy**2
            if zero_test(d2):
                ok = zero_test(pt.x - a_pt.x) and zero_test(pt.y - a_pt.y)
            else:
                col = zero_test(dx * (pt.y - a_pt.y) - dy * (pt.x - a_pt.x))
                t_num = (pt.x - a_pt.x) * dx + (pt.y - a_pt.y) * dy
                ok = col and exact_sign(t_num) >= 0 and exact_sign(d2 - t_num) >= 0
        else:
            raise TypeError(f"Expected Line, Circle, or Segment, got {type(struct)!r}")

        if not ok:
            raise ProofAssertionError(
                f"Point {self._resolve_id(pt)} is not incident to {self._resolve_id(struct)} "
                f"(by={by!r})."
            )

        return self._record_step(
            kind="assert",
            action="incident",
            elements=[pt, struct],
            by=by,
            label=label,
            focus=focus,
        )

    def conclude(
        self,
        *elements: Any,
        kind: str = "qed",
        by: str = "",
        label: str = "",
        focus: Sequence[Any] | None = None,
    ) -> Step:
        """Mark target constructed/demonstrated elements as ``result`` and record Q.E.D. / Q.E.F."""
        for el in elements:
            try:
                if el in self:
                    self[el].classes["result"] = ""
                    self[el].guide = False
            except TypeError:
                pass

        return self._record_step(
            kind="conclude",
            action=kind,
            elements=elements,
            by=by,
            label=label,
            focus=focus,
        )
