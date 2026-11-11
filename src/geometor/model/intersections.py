"""Closed-form 2D symbolic intersections, Euclidean selectors, and scoped sub-constructions.

Provides:

- :func:`intersect_2d`: Exact closed-form solver for 2D ``Line``, ``Circle``, and ``Segment``
  pairs (bypassing SymPy's quartic ``Ellipse`` Gröbner-basis routines).
- :exc:`ConstructionError`: Raised when a geometric *diorismos* or Euclidean selector fails.
- :class:`IntersectionsMixin`: Adds :meth:`Model.intersect`, :meth:`Model.intersect_all`, and
  :meth:`Model.subconstruction` to :class:`~geometor.model.Model`.
- :func:`proposition`: Composable decorator turning any Euclidean construction function into
  a scoped, reusable lemma/problem across ``elements`` and ``etc``.
"""

from __future__ import annotations

import functools
import inspect
from collections.abc import Callable, Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import sympy as sp
import sympy.geometry as spg
from sympy.geometry.entity import GeometryEntity

from geometor.model.algebra import exact_sign, fast_line_coeffs, zero_test
from geometor.model.invariants import Angle, orientation

if TYPE_CHECKING:
    from geometor.model.element import Struct
    from geometor.model.model import Model

__all__ = [
    "ConstructionError",
    "IntersectionsMixin",
    "SubconstructionScope",
    "intersect_2d",
    "proposition",
]


class ConstructionError(ValueError):
    """Raised when a compass-and-straightedge intersection violates its *diorismos* or selector."""


def _sort_pts(pts: list[spg.Point]) -> list[spg.Point]:
    """Deterministically sort 2D points lexicographically by numerical ``(x, y)``."""
    return sorted(pts, key=lambda p: (float(p.x.evalf()), float(p.y.evalf())))


def _point_on_segment(pt: spg.Point, seg: spg.Segment) -> bool:
    """Return ``True`` iff collinear point ``pt`` lies on closed segment ``[seg.p1, seg.p2]``."""
    a, b = seg.p1, seg.p2
    dx, dy = b.x - a.x, b.y - a.y
    d2 = dx**2 + dy**2
    if zero_test(d2):
        return zero_test(pt.x - a.x) and zero_test(pt.y - a.y)
    if not zero_test(dx * (pt.y - a.y) - dy * (pt.x - a.x)):
        return False
    t_num = (pt.x - a.x) * dx + (pt.y - a.y) * dy
    return exact_sign(t_num) >= 0 and exact_sign(d2 - t_num) >= 0


def intersect_2d(s1: GeometryEntity, s2: GeometryEntity) -> list[spg.Point]:
    """Compute exact symbolic intersections of 2D lines, circles, and segments.

    Uses closed-form homogeneous cross-products (line-line), orthogonal projection
    discriminants (line-circle), and radical-axis projections (circle-circle) so
    nested radical expressions never fall into SymPy's slow ``Ellipse`` quartic solver.

    Args:
        s1: First 2D geometric entity (``Line``, ``Circle``, or ``Segment``).
        s2: Second 2D geometric entity (``Line``, ``Circle``, or ``Segment``).

    Returns:
        Deterministically sorted list of exact real :class:`sympy.geometry.Point` intersections.
    """
    seg1 = s1 if isinstance(s1, spg.Segment) else None
    seg2 = s2 if isinstance(s2, spg.Segment) else None
    g1 = spg.Line(s1.p1, s1.p2) if seg1 is not None else s1
    g2 = spg.Line(s2.p1, s2.p2) if seg2 is not None else s2

    pts: list[spg.Point]
    if isinstance(g1, spg.Line) and isinstance(g2, spg.Line):
        a1, b1, c1 = fast_line_coeffs(g1)
        a2, b2, c2 = fast_line_coeffs(g2)
        det = a1 * b2 - a2 * b1
        if zero_test(det):
            return []
        x = (b1 * c2 - b2 * c1) / det
        y = (c1 * a2 - c2 * a1) / det
        pts = [spg.Point(x, y)]

    elif (isinstance(g1, spg.Line) and isinstance(g2, spg.Circle)) or (
        isinstance(g1, spg.Circle) and isinstance(g2, spg.Line)
    ):
        line_obj, circ_obj = (g1, g2) if isinstance(g1, spg.Line) else (g2, g1)
        a, b, c = fast_line_coeffs(line_obj)
        h, k = circ_obj.center.x, circ_obj.center.y
        r_sq = circ_obj.radius**2
        n2 = a**2 + b**2
        s = a * h + b * k + c
        disc = r_sq * n2 - s**2
        sgn = exact_sign(disc)
        if sgn < 0:
            return []
        if sgn == 0:
            pts = [spg.Point(h - a * s / n2, k - b * s / n2)]
        else:
            rt = sp.sqrt(disc)
            pts = _sort_pts(
                [
                    spg.Point(h - (a * s - b * rt) / n2, k - (b * s + a * rt) / n2),
                    spg.Point(h - (a * s + b * rt) / n2, k - (b * s - a * rt) / n2),
                ]
            )

    elif isinstance(g1, spg.Circle) and isinstance(g2, spg.Circle):
        h1, k1, r1 = g1.center.x, g1.center.y, g1.radius
        h2, k2, r2 = g2.center.x, g2.center.y, g2.radius
        dx, dy = h2 - h1, k2 - k1
        d2 = dx**2 + dy**2
        if zero_test(d2):
            return []

        r1_sq, r2_sq = r1**2, r2**2
        # Exact fast-path for symmetric equilateral poles (P, Q) ∩ (Q, P): r1^2 == r2^2 == d^2
        if zero_test(r1_sq - d2) and zero_test(r2_sq - d2):
            s3_half = sp.sqrt(3) / 2
            pts = _sort_pts(
                [
                    spg.Point(h1 + dx / 2 - s3_half * dy, k1 + dy / 2 + s3_half * dx),
                    spg.Point(h1 + dx / 2 + s3_half * dy, k1 + dy / 2 - s3_half * dx),
                ]
            )
        else:
            num_u = r1_sq - r2_sq + d2
            disc = 4 * d2 * r1_sq - num_u**2
            sgn = exact_sign(disc)
            if sgn < 0:
                return []
            if sgn == 0:
                u = num_u / (2 * d2)
                pts = [spg.Point(h1 + u * dx, k1 + u * dy)]
            else:
                u = num_u / (2 * d2)
                v = sp.sqrt(disc) / (2 * d2)
                pts = _sort_pts(
                    [
                        spg.Point(h1 + u * dx - v * dy, k1 + u * dy + v * dx),
                        spg.Point(h1 + u * dx + v * dy, k1 + u * dy - v * dx),
                    ]
                )
    else:
        pts = [p for p in g1.intersection(g2) if isinstance(p, spg.Point)]

    if seg1 is not None:
        pts = [p for p in pts if _point_on_segment(p, seg1)]
    if seg2 is not None:
        pts = [p for p in pts if _point_on_segment(p, seg2)]
    return pts


def _points_coincide(p: spg.Point, q: spg.Point) -> bool:
    """Fast numeric + exact symbolic point equality check."""
    if p == q:
        return True
    if abs(float(p.x.evalf()) - float(q.x.evalf())) > 1e-9:
        return False
    if abs(float(p.y.evalf()) - float(q.y.evalf())) > 1e-9:
        return False
    return zero_test(p.x - q.x) and zero_test(p.y - q.y)


def _line_param(a: spg.Point, b: spg.Point, p: spg.Point) -> sp.Expr | None:
    """Return parameter ``t`` where ``p = a + t*(b - a)`` if ``p`` is collinear with ``ab``, else ``None``."""
    dx, dy = b.x - a.x, b.y - a.y
    d2 = dx**2 + dy**2
    if zero_test(d2):
        raise ValueError("Reference ray/segment endpoints must be distinct.")
    if not zero_test(dx * (p.y - a.y) - dy * (p.x - a.x)):
        return None
    return ((p.x - a.x) * dx + (p.y - a.y) * dy) / d2


@dataclass
class SubconstructionScope:
    """Active scope state for :meth:`Model.subconstruction`."""

    name: str
    g_id: str = ""
    scope_intersections: bool = True
    hide_guides: bool = True
    initial_keys: set[ Any ] = field(default_factory=set)
    scope_structs: list[ Any ] = field(default_factory=list)
    created_elements: list[ Any ] = field(default_factory=list)
    returned_elements: set[ Any ] = field(default_factory=set)

    @property
    def scope_id(self) -> str:
        """Canonical identifier recorded on nested steps."""
        return self.g_id or self.name

    def include(self, *elements: Any) -> None:
        """Include existing outer lines/circles in this scope's intersection pool."""
        for el in elements:
            if isinstance(el, (spg.Line, spg.Circle)) and el not in self.scope_structs:
                self.scope_structs.append(el)

    def keep(self, *elements: Any) -> None:
        """Preserve specific elements created inside this scope as primary (non-guide) outputs."""
        for item in elements:
            self._collect_kept(item)

    def _collect_kept(self, obj: Any) -> None:
        if obj is None:
            return
        if isinstance(obj, (tuple, list, set)):
            for sub in obj:
                self._collect_kept(sub)
            return
        if isinstance(obj, dict):
            for sub in obj.values():
                self._collect_kept(sub)
            return
        if isinstance(obj, (spg.Point, spg.Line, spg.Circle)):
            self.returned_elements.add(obj)
        elif isinstance(obj, spg.Segment):
            self.returned_elements.add(obj)
            self.returned_elements.add(obj.p1)
            self.returned_elements.add(obj.p2)
        elif isinstance(obj, spg.Polygon):
            self.returned_elements.add(obj)
            for v in obj.vertices:
                self.returned_elements.add(v)
        elif isinstance(obj, Angle) or (
            hasattr(obj, "points") and isinstance(obj.points, list)
        ):
            self.returned_elements.add(obj)
            for p in obj.points:
                if isinstance(p, spg.Point):
                    self.returned_elements.add(p)


def proposition(
    prop_id: str,
    *,
    g_id: str = "",
    kind: str = "problem",
    title: str = "",
    hide_guides: bool = True,
    scope_intersections: bool = True,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator marking a Euclidean construction function as a composable proposition.

    Executes the wrapped function inside :meth:`Model.subconstruction`, scoping automatic
    intersections to the proposition and automatically marking un-returned auxiliary
    lines, circles, and guide poles with ``guide=True``.

    Args:
        prop_id: Proposition or center identifier (e.g., ``"I.1"``, ``"X(13)"``).
        g_id: Optional G-Index node identifier (e.g., ``"G.17"``).
        kind: ``"problem"`` (Q.E.F.) or ``"theorem"`` (Q.E.D.).
        title: Optional human-readable proposition title.
        hide_guides: Default ``hide_guides`` setting when invoked.
        scope_intersections: Default ``scope_intersections`` setting when invoked.
    """

    def _decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        sig = inspect.signature(func)
        accepts_hide_guides = "hide_guides" in sig.parameters
        accepts_scope = "scope_intersections" in sig.parameters

        @functools.wraps(func)
        def _wrapper(*args: Any, **kwargs: Any) -> Any:
            call_hide = kwargs.get("hide_guides", hide_guides)
            call_scope = kwargs.get("scope_intersections", scope_intersections)
            if not accepts_hide_guides:
                kwargs.pop("hide_guides", None)
            if not accepts_scope:
                kwargs.pop("scope_intersections", None)

            model_obj: Model | None = None
            if args and hasattr(args[0], "subconstruction"):
                model_obj = args[0]
            elif "model" in kwargs and hasattr(kwargs["model"], "subconstruction"):
                model_obj = kwargs["model"]

            if model_obj is None:
                return func(*args, **kwargs)

            with model_obj.subconstruction(
                prop_id,
                g_id=g_id,
                scope_intersections=call_scope,
                hide_guides=call_hide,
            ) as scope:
                for arg in args[1:]:
                    if isinstance(arg, (spg.Line, spg.Circle)):
                        scope.include(arg)
                for val in kwargs.values():
                    if isinstance(val, (spg.Line, spg.Circle)):
                        scope.include(val)

                result = func(*args, **kwargs)
                scope.keep(result)
                return result

        _wrapper.prop_id = prop_id  # type: ignore[attr-defined]
        _wrapper.g_id = g_id  # type: ignore[attr-defined]
        _wrapper.kind = kind  # type: ignore[attr-defined]
        _wrapper.title = title  # type: ignore[attr-defined]
        return _wrapper

    return _decorator


class IntersectionsMixin:
    """Mixin for :class:`~geometor.model.Model` providing targeted intersections & sub-constructions."""

    def _describe_entity(self, entity: GeometryEntity) -> str:
        if entity in self and self[entity].ID:
            return self[entity].ID
        return str(entity)

    def _register_in_scope(self, element: Any) -> None:
        """Record a newly created element in any active subconstruction scope."""
        stack: list[SubconstructionScope] = getattr(self, "_scope_stack", [])
        if not stack:
            return
        top = stack[-1]
        if element not in top.initial_keys and element not in top.created_elements:
            top.created_elements.append(element)
        if (
            isinstance(element, (spg.Line, spg.Circle))
            and not self[element].guide
            and element not in top.scope_structs
        ):
            top.scope_structs.append(element)

    @contextmanager
    def subconstruction(
        self,
        name: str,
        *,
        g_id: str = "",
        scope_intersections: bool = True,
        hide_guides: bool = True,
    ) -> Iterator[SubconstructionScope]:
        """Execute a scoped sub-construction block with automatic guide encapsulation.

        Args:
            name: Proposition or sub-construction name (e.g., ``"I.1"``).
            g_id: Optional G-Index identifier (e.g., ``"G.17"``).
            scope_intersections: If ``True``, automatic intersections inside the block only
                test lines and circles belonging to this scope.
            hide_guides: If ``True``, un-kept auxiliary lines, circles, and points created
                inside the block are marked ``guide=True`` upon exit.
        """
        scope = SubconstructionScope(
            name=name,
            g_id=g_id,
            scope_intersections=scope_intersections,
            hide_guides=hide_guides,
            initial_keys=set(self.keys()),
        )
        self._scope_stack.append(scope)
        try:
            yield scope
        finally:
            self._scope_stack.pop()
            if hide_guides:
                for el in scope.created_elements:
                    if el not in self:
                        continue
                    details = self[el]
                    if (
                        el not in scope.returned_elements
                        and "result" not in details.classes
                        and "given" not in details.classes
                    ):
                        details.guide = True
                        details.classes["guide"] = ""
            # Propagate kept outputs into parent scope if nested!
            if self._scope_stack:
                parent_scope = self._scope_stack[-1]
                for el in scope.returned_elements:
                    if el not in parent_scope.initial_keys and el not in parent_scope.created_elements:
                        parent_scope.created_elements.append(el)
                    if (
                        isinstance(el, (spg.Line, spg.Circle))
                        and el in self
                        and not self[el].guide
                        and el not in parent_scope.scope_structs
                    ):
                        parent_scope.scope_structs.append(el)

    def intersect_all(
        self,
        s1: Struct | spg.Segment,
        s2: Struct | spg.Segment,
        *,
        classes: list[str] | None = None,
        guide: bool = False,
        by: str = "",
    ) -> list[spg.Point]:
        """Compute and register all real intersections between ``s1`` and ``s2``."""
        raw_pts = intersect_2d(s1, s2)
        parents = [s for s in (s1, s2) if isinstance(s, GeometryEntity)]
        out: list[spg.Point] = []
        for raw in raw_pts:
            pt_new = self.set_point(
                raw.x,
                raw.y,
                parents=parents,
                classes=list(classes) if classes else None,
                guide=guide,
                record_step=False,
            )
            if s1 in self:
                self[s1].pts[pt_new] = ""
            if s2 in self:
                self[s2].pts[pt_new] = ""
            if hasattr(self, "_record_step"):
                self._record_step(
                    kind="intersect",
                    action="intersect",
                    elements=[self[pt_new].ID],
                    by=by,
                )
            out.append(pt_new)
        return out

    def intersect(
        self,
        s1: Struct | spg.Segment,
        s2: Struct | spg.Segment,
        *,
        side_of: tuple[spg.Point, spg.Point, int] | None = None,
        other_than: spg.Point | Sequence[spg.Point] | None = None,
        on_ray: tuple[spg.Point, spg.Point] | None = None,
        beyond: tuple[spg.Point, spg.Point] | None = None,
        between: tuple[spg.Point, spg.Point] | None = None,
        near: spg.Point | None = None,
        index: int | None = None,
        ID: str = "",
        label: str = "",
        classes: list[str] | None = None,
        guide: bool = False,
        by: str = "",
    ) -> spg.Point:
        """Compute a targeted intersection of ``s1`` and ``s2`` selected by Euclidean predicates.

        Args:
            s1: First ``Line``, ``Circle``, or ``Segment``.
            s2: Second ``Line``, ``Circle``, or ``Segment``.
            side_of: ``(A, B, +1|-1|0)`` selecting the half-plane relative to directed line ``AB``.
            other_than: Known ``Point`` (or sequence of ``Point`` instances) to exclude.
            on_ray: ``(A, B)`` selecting points on ray ``AB`` (:math:`t \\ge 0`).
            beyond: ``(A, B)`` selecting points on ray ``AB`` strictly past ``B`` (:math:`t > 1`).
            between: ``(A, B)`` selecting points strictly between ``A`` and ``B`` (:math:`0 < t < 1`).
            near: Reference ``Point`` selecting the closest candidate.
            index: Explicit index ``0`` or ``1`` into deterministically sorted candidates.
            ID: Optional identifier for the constructed point.
            label: Optional alias for ``ID``.
            classes: Optional list of CSS/semantic classes.
            guide: Whether to mark the point as a guide.
            by: Optional Euclidean justification citation (e.g., ``"I.1"``, ``"Post.2"``).

        Returns:
            The exact :class:`sympy.geometry.Point` registered in the model.

        Raises:
            ConstructionError: If ``s1`` and ``s2`` do not intersect or no candidate matches the selector.
        """
        candidates = intersect_2d(s1, s2)
        if not candidates:
            raise ConstructionError(
                f"No real intersection between {self._describe_entity(s1)} and "
                f"{self._describe_entity(s2)} (diorismos violated)."
            )

        if other_than is not None:
            excluded = (
                [other_than]
                if isinstance(other_than, spg.Point)
                else list(other_than)
            )
            candidates = [
                p for p in candidates if not any(_points_coincide(p, ex) for ex in excluded)
            ]

        if side_of is not None:
            ref_a, ref_b, target_sgn = side_of
            expected = 1 if target_sgn > 0 else (-1 if target_sgn < 0 else 0)
            candidates = [
                p for p in candidates if orientation(ref_a, ref_b, p) == expected
            ]

        if on_ray is not None:
            ray_a, ray_b = on_ray
            filtered = []
            for p in candidates:
                t_val = _line_param(ray_a, ray_b, p)
                if t_val is not None and exact_sign(t_val) >= 0:
                    filtered.append(p)
            candidates = filtered

        if beyond is not None:
            bey_a, bey_b = beyond
            filtered = []
            for p in candidates:
                t_val = _line_param(bey_a, bey_b, p)
                if t_val is not None and exact_sign(t_val - 1) > 0:
                    filtered.append(p)
            candidates = filtered

        if between is not None:
            bet_a, bet_b = between
            filtered = []
            for p in candidates:
                t_val = _line_param(bet_a, bet_b, p)
                if t_val is not None and exact_sign(t_val) > 0 and exact_sign(1 - t_val) > 0:
                    filtered.append(p)
            candidates = filtered

        if not candidates:
            raise ConstructionError(
                f"Intersection of {self._describe_entity(s1)} and {self._describe_entity(s2)} "
                "produced no point matching the Euclidean selector."
            )

        if near is not None:
            nx, ny = float(near.x.evalf()), float(near.y.evalf())
            candidates = sorted(
                candidates,
                key=lambda p: (float(p.x.evalf()) - nx) ** 2 + (float(p.y.evalf()) - ny) ** 2,
            )
            chosen = candidates[0]
        elif index is not None:
            try:
                chosen = candidates[index]
            except IndexError as exc:
                raise ConstructionError(
                    f"Intersection selector index={index} out of range for {len(candidates)} candidate(s)."
                ) from exc
        else:
            chosen = candidates[0]

        parents = [s for s in (s1, s2) if isinstance(s, GeometryEntity)]
        pt_new = self.set_point(
            chosen.x,
            chosen.y,
            parents=parents,
            classes=list(classes) if classes else None,
            ID=ID,
            guide=guide,
            label=label,
            record_step=False,
        )
        if s1 in self:
            self[s1].pts[pt_new] = ""
        if s2 in self:
            self[s2].pts[pt_new] = ""
        if hasattr(self, "_record_step"):
            self._record_step(
                kind="intersect",
                action="intersect",
                elements=[self[pt_new].ID],
                by=by,
            )
        return pt_new
