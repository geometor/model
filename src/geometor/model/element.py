"""Provides core element classes and intersection logic.

This module defines the foundational :class:`Element` container which wraps SymPy
geometric objects with causal ancestry (``parents``), incident points (``pts``),
classifications (``classes``), cached numeric coordinates (``approx_coords``), and IDs.
"""

from __future__ import annotations

from collections.abc import Sequence
from multiprocessing import Pool, cpu_count
from typing import TYPE_CHECKING, Any

import sympy as sp
import sympy.geometry as spg
from sympy.geometry.entity import GeometryEntity

from geometor.model.algebra import clean_expr, fast_line_coeffs, zero_test
from geometor.model.intersections import intersect_2d

if TYPE_CHECKING:
    from geometor.model.model import Model

Struct = spg.Line | spg.Circle

# Backward-compatible alias for closed-form 2D exact intersection solver
exact_intersect = intersect_2d

__all__ = [
    "CircleElement",
    "Element",
    "Struct",
    "check_existence",
    "exact_intersect",
    "find_all_intersections",
]


def _compute_approx_coords(obj: Any) -> tuple[float, ...] | None:
    """Compute canonical floating-point signature for fast O(1) geometric pre-filtering."""
    if isinstance(obj, spg.Point):
        return (float(obj.x.evalf()), float(obj.y.evalf()))
    if isinstance(obj, spg.Circle):
        return (
            float(obj.center.x.evalf()),
            float(obj.center.y.evalf()),
            float(obj.radius.evalf()),
        )
    if isinstance(obj, spg.Line):
        p1x, p1y = float(obj.p1.x.evalf()), float(obj.p1.y.evalf())
        p2x, p2y = float(obj.p2.x.evalf()), float(obj.p2.y.evalf())
        a = p1y - p2y
        b = p2x - p1x
        c = p1x * p2y - p2x * p1y
        norm = (a * a + b * b) ** 0.5
        if norm == 0.0:
            return (0.0, 0.0, 0.0)
        ua, ub, uc = a / norm, b / norm, c / norm
        if ua < -1e-13 or (abs(ua) <= 1e-13 and ub < 0.0):
            ua, ub, uc = -ua, -ub, -uc
        return (ua, ub, uc)
    return None


class Element:
    """A container for metadata and cached numeric invariants of a model element.

    Maintains causal lineage in :attr:`parents` (a true directed acyclic graph),
    incident points on lines/circles in :attr:`pts`, style/semantic tags in
    :attr:`classes`, proof diagram markers in :attr:`markers`, and lazily cached
    numeric coordinates in :attr:`approx_coords`.

    Args:
        sympy_obj: The SymPy object representing the geometric entity.
        parents: A list of causal parent elements.
        classes: A list of class labels.
        ID: A string ID for the element. If empty, an ID is generated.
        guide: If True (or if ``"guide"`` is in ``classes``), excluded from auto-intersections.
    """

    def __init__(
        self,
        sympy_obj: GeometryEntity,
        parents: list | None = None,
        classes: list[str] | None = None,
        ID: str = "",
        guide: bool = False,
    ) -> None:
        """Initialize an Element of the model."""
        self.object = sympy_obj
        if classes is None:
            classes = []
        if parents is None:
            parents = []

        self.parents: dict[Any, str] = {key: "" for key in parents}
        #: Dict mapping causal parent geometric objects to ``""``.

        self.pts: dict[spg.Point, str] = {
            key: "" for key in parents if isinstance(key, spg.Point)
        }
        #: Dict mapping known incident ``Point``s on this structure to ``""``.

        self.classes: dict[str, str] = {key: "" for key in classes}
        #: Dict with strings for class names.

        self.ID: str = ID
        #: Name used in presentation and reports.

        self.guide: bool = bool(guide or "guide" in self.classes)
        #: Whether the element is an auxiliary guide excluded from intersections.

        self.markers: list[dict[str, Any]] = []
        #: Diagrammatic proof markers (ticks, angle arcs, parallel arrows) attached to this element.

        self._approx_coords: tuple[float, ...] | None = None

    @property
    def approx_coords(self) -> tuple[float, ...] | None:
        """Lazily computed floating-point signature for fast spatial pre-filtering."""
        if self._approx_coords is None:
            self._approx_coords = _compute_approx_coords(self.object)
        return self._approx_coords

    @property
    def length(self) -> sp.Expr | list[sp.Expr] | None:
        """Return the cleaned symbolic length (or side lengths for polygons)."""
        if hasattr(self, "side_lengths"):
            return self.side_lengths
        if hasattr(self.object, "length"):
            return clean_expr(self.object.length)
        return None


class CircleElement(Element):
    """Same as :class:`Element` but records ``pt_radius`` on the circumference."""

    def __init__(
        self,
        sympy_obj: spg.Circle,
        pt_radius: spg.Point,
        parents: list | None = None,
        classes: list[str] | None = None,
        ID: str = "",
        guide: bool = False,
    ) -> None:
        """Initialize a CircleElement."""
        super().__init__(sympy_obj, parents, classes, ID, guide)
        self.pt_radius = pt_radius
        #: The point defining the radius.


def _structs_numerically_close(
    s1: Struct,
    s2: Struct,
    approx1: tuple[float, ...] | None = None,
    approx2: tuple[float, ...] | None = None,
    tol: float = 1e-9,
) -> bool:
    """Fast O(1) numerical pre-filter using cached coordinates before exact zero_test."""
    if type(s1) is not type(s2):
        return False
    a1 = approx1 if approx1 is not None else _compute_approx_coords(s1)
    a2 = approx2 if approx2 is not None else _compute_approx_coords(s2)
    if a1 is None or a2 is None or len(a1) != len(a2):
        return True
    return all(abs(v1 - v2) < tol for v1, v2 in zip(a1, a2))


def _structs_exact_equal(s1: Struct, s2: Struct) -> bool:
    """Exact algebraic equivalence of two Lines or two Circles without sp.simplify."""
    if s1 == s2:
        return True
    if isinstance(s1, spg.Line) and isinstance(s2, spg.Line):
        a1, b1, c1 = fast_line_coeffs(s1)
        a2, b2, c2 = fast_line_coeffs(s2)
        return (
            zero_test(a1 * b2 - a2 * b1)
            and zero_test(a1 * c2 - a2 * c1)
            and zero_test(b1 * c2 - b2 * c1)
        )
    if isinstance(s1, spg.Circle) and isinstance(s2, spg.Circle):
        return (
            zero_test(s1.center.x - s2.center.x)
            and zero_test(s1.center.y - s2.center.y)
            and zero_test(s1.radius**2 - s2.radius**2)
        )
    return bool(s1.equals(s2))


def check_existence(
    self: Model, struct: Struct, existing_structs: list[Struct]
) -> tuple[bool, Struct | None]:
    """Check if an algebraically equivalent ``Line`` or ``Circle`` already exists in ``self``."""
    if struct in self and isinstance(struct, (spg.Line, spg.Circle)):
        return True, struct

    cand_approx = _compute_approx_coords(struct)
    for prev in existing_structs:
        prev_approx = self[prev].approx_coords if prev in self else None
        if not _structs_numerically_close(prev, struct, prev_approx, cand_approx):
            continue
        if _structs_exact_equal(prev, struct):
            return True, prev

    return False, None


def find_all_intersections(
    self: Model,
    struct: Struct,
    *,
    candidates: Sequence[Struct] | None = None,
    by: str = "",
) -> None:
    """Compute intersections of ``struct`` with eligible structures and register points.

    Respects ``self.auto_intersect``, ``guide`` flags, and active ``subconstruction``
    scopes. Executes in-process by default unless ``self.use_multiprocessing`` is
    enabled and the candidate batch contains at least 64 structures.
    """
    if candidates is None and struct in self and (self[struct].guide or "guide" in self[struct].classes):
        return

    if candidates is not None:
        pool_structs = [
            el
            for el in candidates
            if isinstance(el, (spg.Line, spg.Circle)) and el is not struct
        ]
    else:
        if not getattr(self, "auto_intersect", True):
            return
        scope_stack = getattr(self, "_scope_stack", [])
        if scope_stack and scope_stack[-1].scope_intersections:
            pool_structs = [
                el
                for el in scope_stack[-1].scope_structs
                if el is not struct
                and el in self
                and not self[el].guide
                and "guide" not in self[el].classes
            ]
        else:
            pool_structs = [el for el in self.structs if el is not struct]

    struct_approx = self[struct].approx_coords if struct in self else _compute_approx_coords(struct)
    test_structs = [
        (el, struct)
        for el in pool_structs
        if not (
            _structs_numerically_close(
                el,
                struct,
                self[el].approx_coords if el in self else None,
                struct_approx,
            )
            and _structs_exact_equal(el, struct)
        )
    ]

    if not test_structs:
        return

    if getattr(self, "use_multiprocessing", False) and len(test_structs) >= 64:
        with Pool(cpu_count()) as pool:
            results = pool.map(find_intersection, test_structs)
    else:
        results = [find_intersection(t) for t in test_structs]

    for prev, curr_struct, result in results:
        for pt in result:
            pts_before = len(self.points)
            pt_new = self.set_point(
                pt.x,
                pt.y,
                parents=[prev, curr_struct],
                record_step=False,
            )
            if prev in self:
                self[prev].pts[pt_new] = ""
            if curr_struct in self:
                self[curr_struct].pts[pt_new] = ""
            if len(self.points) > pts_before and hasattr(self, "_record_step"):
                self._record_step(
                    kind="intersect",
                    action="intersect",
                    elements=[self[pt_new].ID],
                    by=by,
                )


def find_intersection(
    test_tuple: tuple[Struct, Struct],
) -> tuple[Struct, Struct, list[spg.Point]]:
    """Worker function computing exact 2D intersections for a pair of structures."""
    prev, struct = test_tuple
    result = intersect_2d(prev, struct)
    return prev, struct, result


def _get_element_by_ID(self: Model, ID: str) -> GeometryEntity | None:
    """Find and return the element key with the given string ``ID``."""
    for element_key, element in self.items():
        if hasattr(element, "ID") and element.ID == ID:
            return element_key
    return None
