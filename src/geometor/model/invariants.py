"""Rational trigonometry invariants, projective cross-ratios, and first-class Angle elements.

Implements N. J. Wildberger's polynomial/rational invariants (quadrance, spread, cross),
exact signed orientation and projective cross-ratio / harmonic range predicates, and the
first-class :class:`Angle` element (``< B A C )``) for :class:`~geometor.model.Model`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import sympy as sp
import sympy.geometry as spg
from rich.table import Table

from geometor.model.algebra import clean_expr, exact_sign, zero_test
from geometor.model.colors import COLORS

if TYPE_CHECKING:
    from sympy.printing.printer import Printer

__all__ = [
    "Angle",
    "AnglesMixin",
    "cross",
    "cross_ratio",
    "is_harmonic",
    "line_spread",
    "orientation",
    "polygon_area2",
    "quadrance",
    "signed_area2",
    "vertex_dot_sign",
    "vertex_spread",
]


def quadrance(
    p1_or_seg: spg.Point | spg.Segment,
    p2: spg.Point | None = None,
) -> sp.Expr:
    """Compute the exact Euclidean quadrance :math:`Q = (x_2 - x_1)^2 + (y_2 - y_1)^2`.

    Accepts either two :class:`sympy.geometry.Point` instances ``quadrance(P, Q)``
    or a single :class:`sympy.geometry.Segment` ``quadrance(seg)``.

    Args:
        p1_or_seg: First point ``P`` or a segment ``/ P Q /``.
        p2: Second point ``Q`` when ``p1_or_seg`` is a point.

    Returns:
        Exact simplified :class:`sympy.Expr` with zero square roots introduced.
    """
    if isinstance(p1_or_seg, spg.Segment) and p2 is None:
        p1, p2_pt = p1_or_seg.p1, p1_or_seg.p2
    elif isinstance(p1_or_seg, spg.Point) and isinstance(p2, spg.Point):
        p1, p2_pt = p1_or_seg, p2
    else:
        raise TypeError("quadrance expects either (Point, Point) or (Segment,).")

    return clean_expr((p2_pt.x - p1.x) ** 2 + (p2_pt.y - p1.y) ** 2)


def _line_normal(line_like: spg.Line | spg.Segment | tuple[spg.Point, spg.Point]) -> tuple[sp.Expr, sp.Expr]:
    """Extract normal coefficients ``(a, b)`` for a Line, Segment, or pair of Points."""
    if isinstance(line_like, (spg.Line, spg.Segment)):
        p1, p2 = line_like.p1, line_like.p2
    elif isinstance(line_like, tuple) and len(line_like) == 2:
        p1, p2 = line_like
    else:
        raise TypeError(f"Expected Line, Segment, or (Point, Point), got {type(line_like)!r}")

    a = p1.y - p2.y
    b = p2.x - p1.x
    if zero_test(a) and zero_test(b):
        raise ValueError("Degenerate line/segment with coincident endpoints.")
    return a, b


def line_spread(
    l1: spg.Line | spg.Segment | tuple[spg.Point, spg.Point],
    l2: spg.Line | spg.Segment | tuple[spg.Point, spg.Point],
) -> sp.Expr:
    """Compute the exact rational spread :math:`s(l_1, l_2) = \\sin^2\\theta` between two lines.

    Args:
        l1: First line, segment, or ``(P, Q)`` point pair.
        l2: Second line, segment, or ``(P, Q)`` point pair.

    Returns:
        Exact simplified spread in :math:`[0, 1]`.
    """
    a1, b1 = _line_normal(l1)
    a2, b2 = _line_normal(l2)
    denom = (a1**2 + b1**2) * (a2**2 + b2**2)
    if zero_test(denom):
        raise ValueError("Degenerate line with zero normal vector.")
    return clean_expr(((a1 * b2 - a2 * b1) ** 2) / denom)


def cross(
    l1: spg.Line | spg.Segment | tuple[spg.Point, spg.Point],
    l2: spg.Line | spg.Segment | tuple[spg.Point, spg.Point],
) -> sp.Expr:
    """Compute the exact rational cross :math:`c(l_1, l_2) = \\cos^2\\theta = 1 - s(l_1, l_2)`."""
    a1, b1 = _line_normal(l1)
    a2, b2 = _line_normal(l2)
    denom = (a1**2 + b1**2) * (a2**2 + b2**2)
    if zero_test(denom):
        raise ValueError("Degenerate line with zero normal vector.")
    return clean_expr(((a1 * a2 + b1 * b2) ** 2) / denom)


def vertex_spread(B: spg.Point, A: spg.Point, C: spg.Point) -> sp.Expr:
    """Compute the exact spread at vertex ``A`` between rays ``AB`` and ``AC`` (``< B A C )``).

    Args:
        B: Point on the first ray.
        A: The vertex of the angle.
        C: Point on the second ray.

    Returns:
        Exact simplified spread :math:`s(\\angle BAC)`.
    """
    ux, uy = B.x - A.x, B.y - A.y
    vx, vy = C.x - A.x, C.y - A.y
    n_u = ux**2 + uy**2
    n_v = vx**2 + vy**2
    if zero_test(n_u) or zero_test(n_v):
        raise ValueError("Degenerate angle: ray endpoint coincides with vertex.")
    return clean_expr(((ux * vy - uy * vx) ** 2) / (n_u * n_v))


def vertex_dot_sign(B: spg.Point, A: spg.Point, C: spg.Point) -> int:
    """Return ``+1`` if ``< B A C )`` is acute, ``0`` if right, or ``-1`` if obtuse."""
    ux, uy = B.x - A.x, B.y - A.y
    vx, vy = C.x - A.x, C.y - A.y
    if zero_test(ux**2 + uy**2) or zero_test(vx**2 + vy**2):
        raise ValueError("Degenerate angle: ray endpoint coincides with vertex.")
    return exact_sign(ux * vx + uy * vy)


def signed_area2(A: spg.Point, B: spg.Point, C: spg.Point) -> sp.Expr:
    """Return twice the signed area of triangle ``ABC``: :math:`(x_B - x_A)(y_C - y_A) - (y_B - y_A)(x_C - x_A)`."""
    return clean_expr((B.x - A.x) * (C.y - A.y) - (B.y - A.y) * (C.x - A.x))


def orientation(A: spg.Point, B: spg.Point, C: spg.Point) -> int:
    """Return ``+1`` if ``(A, B, C)`` is counter-clockwise, ``-1`` if clockwise, ``0`` if collinear."""
    det = (B.x - A.x) * (C.y - A.y) - (B.y - A.y) * (C.x - A.x)
    return exact_sign(det)


def polygon_area2(vertices: list[spg.Point] | tuple[spg.Point, ...]) -> sp.Expr:
    """Compute exact unsigned twice-area :math:`|2 \\cdot \\text{Area}|` of a simple polygon via shoelace."""
    n = len(vertices)
    if n < 3:
        raise ValueError("Polygon requires at least 3 vertices.")
    acc = sp.Integer(0)
    for i in range(n):
        p1 = vertices[i]
        p2 = vertices[(i + 1) % n]
        acc += p1.x * p2.y - p2.x * p1.y
    cleaned = clean_expr(acc)
    sgn = exact_sign(cleaned)
    return -cleaned if sgn < 0 else cleaned


def cross_ratio(
    A: spg.Point,
    B: spg.Point,
    C: spg.Point,
    D: spg.Point,
) -> sp.Expr:
    """Compute the exact projective cross-ratio :math:`(A, B; C, D) = \\frac{\\overline{AC}\\cdot\\overline{BD}}{\\overline{BC}\\cdot\\overline{AD}}`.

    Projects collinear displacements onto a shared line direction vector so the cross-ratio
    is computed purely rationally without introducing square roots.

    Args:
        A: First base point.
        B: Second base point.
        C: First division point.
        D: Second division point.

    Returns:
        Exact simplified :class:`sympy.Expr`.

    Raises:
        ValueError: If the four points are not collinear or the denominator vanishes.
    """
    # Choose non-zero reference direction along the line
    dx, dy = B.x - A.x, B.y - A.y
    anchor = A
    if zero_test(dx) and zero_test(dy):
        dx, dy = D.x - C.x, D.y - C.y
        anchor = C
    if zero_test(dx) and zero_test(dy):
        raise ValueError("Cross-ratio requires at least two distinct collinear points.")

    for pt in (A, B, C, D):
        cross_term = dx * (pt.y - anchor.y) - dy * (pt.x - anchor.x)
        if not zero_test(cross_term):
            raise ValueError("Points passed to cross_ratio are not collinear.")

    def _proj(p: spg.Point, q: spg.Point) -> sp.Expr:
        return (q.x - p.x) * dx + (q.y - p.y) * dy

    ac = _proj(A, C)
    bd = _proj(B, D)
    bc = _proj(B, C)
    ad = _proj(A, D)
    den = bc * ad
    if zero_test(den):
        raise ValueError("Degenerate cross-ratio with zero denominator (infinite cross-ratio).")
    return clean_expr((ac * bd) / den)


def is_harmonic(
    A: spg.Point,
    B: spg.Point,
    C: spg.Point,
    D: spg.Point,
) -> bool:
    """Return ``True`` iff ``(A, B; C, D) == -1`` forms an exact harmonic range."""
    try:
        cr = cross_ratio(A, B, C, D)
    except ValueError:
        return False
    return zero_test(cr + 1)


class Angle:
    """First-class rectilinear angle ``< B A C )`` with vertex ``A`` and rays ``AB``, ``AC``.

    Stores exact algebraic spread, cross, and acute/right/obtuse dot-product sign without
    requiring transcendental ``acos`` or ``atan2`` evaluation during equality proofs.
    """

    def __init__(
        self,
        p1_or_points: spg.Point | list[spg.Point] | tuple[spg.Point, ...],
        vertex: spg.Point | None = None,
        p2: spg.Point | None = None,
    ) -> None:
        """Initialize an :class:`Angle` from ``(B, A, C)`` or ``([B, A, C])``."""
        if isinstance(p1_or_points, (list, tuple)) and vertex is None and p2 is None:
            if len(p1_or_points) != 3:
                raise ValueError("Angle point list must contain exactly 3 points: [B, A, C].")
            b_pt, a_pt, c_pt = p1_or_points
        elif (
            isinstance(p1_or_points, spg.Point)
            and isinstance(vertex, spg.Point)
            and isinstance(p2, spg.Point)
        ):
            b_pt, a_pt, c_pt = p1_or_points, vertex, p2
        else:
            raise TypeError("Angle expects either (B, A, C) Points or ([B, A, C]).")

        self.p1: spg.Point = b_pt
        self.vertex: spg.Point = a_pt
        self.p2: spg.Point = c_pt
        self.points: list[spg.Point] = [b_pt, a_pt, c_pt]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Angle):
            return NotImplemented
        return self.points == other.points

    def __hash__(self) -> int:
        return hash(tuple(self.points))

    def __repr__(self) -> str:
        pts_repr = ", ".join(sp.srepr(p) for p in self.points)
        return f"Angle([{pts_repr}])"

    def _sstr(self, printer: Printer) -> str:
        pts_repr = ", ".join(printer.doprint(p) for p in self.points)
        return f"Angle([{pts_repr}])"

    @property
    def ray1(self) -> spg.Ray:
        """First ray from ``vertex`` through ``p1``."""
        return spg.Ray(self.vertex, self.p1)

    @property
    def ray2(self) -> spg.Ray:
        """Second ray from ``vertex`` through ``p2``."""
        return spg.Ray(self.vertex, self.p2)

    @property
    def spread(self) -> sp.Expr:
        """Exact rational trigonometry spread :math:`s(\\angle BAC) = \\sin^2\\theta`."""
        return vertex_spread(self.p1, self.vertex, self.p2)

    @property
    def cross(self) -> sp.Expr:
        """Exact rational trigonometry cross :math:`c(\\angle BAC) = \\cos^2\\theta`."""
        return clean_expr(1 - self.spread)

    @property
    def dot_sign(self) -> int:
        """Exact dot-product sign: ``+1`` acute, ``0`` right, ``-1`` obtuse."""
        return vertex_dot_sign(self.p1, self.vertex, self.p2)

    @property
    def is_right(self) -> bool:
        """Return ``True`` iff the angle is an exact right angle."""
        return self.dot_sign == 0

    @property
    def radians(self) -> sp.Expr:
        """Interior angle measure in radians in :math:`[0, \\pi]`."""
        return self.ray1.angle_between(self.ray2)

    @property
    def degrees(self) -> sp.Expr:
        """Interior angle measure in degrees."""
        return sp.deg(self.radians)


class AnglesMixin:
    """Mixin for :class:`~geometor.model.Model` providing rectilinear angle registration."""

    @property
    def angles(self) -> list[Angle]:
        """Return all :class:`Angle` elements registered in the model."""
        return [el for el in self if isinstance(el, Angle)]

    def set_angle_by_IDs(
        self,
        p1_ID: str,
        vertex_ID: str,
        p2_ID: str,
        classes: list[str] | None = None,
        ID: str = "",
        *,
        by: str = "",
    ) -> Angle:
        """Construct and register an :class:`Angle` ``< B A C )`` from three point IDs."""
        p1 = self.get_element_by_ID(p1_ID)
        vertex = self.get_element_by_ID(vertex_ID)
        p2 = self.get_element_by_ID(p2_ID)
        return self.set_angle(p1, vertex, p2, classes=classes, ID=ID, by=by)

    def set_angle(
        self,
        p1: spg.Point,
        vertex: spg.Point,
        p2: spg.Point,
        classes: list[str] | None = None,
        ID: str = "",
        *,
        guide: bool = False,
        by: str = "",
    ) -> Angle:
        """Construct and register a rectilinear :class:`Angle` ``< p1 vertex p2 )``."""
        from geometor.model.element import Element

        if classes is None:
            classes = []
        ang = Angle(p1, vertex, p2)
        if not ID:
            ids = [str(self[pt].ID or pt) for pt in (p1, vertex, p2)]
            ID = f"< {' '.join(ids)} )"

        details = Element(ang, parents=[p1, vertex, p2], classes=classes, ID=ID, guide=guide)
        self[ang] = details
        if hasattr(self, "_register_in_scope"):
            self._register_in_scope(ang)
        if hasattr(self, "_record_step"):
            self._record_step(kind="construct", action="angle", elements=[ID], by=by)

        if self.is_logging_enabled:
            classes_str = " : " + " ".join(classes) if classes else ""
            color = COLORS.get("polygon", "bright_green")
            self.log(f"[{color} bold]{details.ID}[/{color} bold]{classes_str}")
            table = Table(show_header=False, box=None, padding=(0, 4))
            table.add_row("    spread:", f"[cyan]{sp.pretty(ang.spread)}[/cyan]")
            self.log(table)

        return ang

    construct_angle = set_angle
