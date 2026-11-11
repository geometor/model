"""Provides core element classes and intersection logic.

This module defines the foundational :class:`Element` container which wraps SymPy geometric objects with additional metadata like parents, user-defined classes, and IDs for the geometor system.
"""

from __future__ import annotations

from multiprocessing import Pool, cpu_count

import sympy.geometry as spg

from typing import TYPE_CHECKING

import sympy as sp
from sympy.geometry.entity import GeometryEntity

from geometor.model.utils import clean_expr

if TYPE_CHECKING:
    from geometor.model.model import Model

Struct = spg.Line | spg.Circle

__all__ = [
    "Element",
    "CircleElement",
    "Struct",
    "check_existence",
    "exact_intersect",
    "find_all_intersections",
]


class Element:
    """A container for special attributes of an element of a model.
    
    The Element class extends the functionality of standard SymPy geometry objects by attaching model-specific metadata. It maintains a record of the element's lineage (parents), classification (classes), and identification (ID), which are essential for the constructive geometry framework.

    Args:
        sympy_obj: The sympy object representing the geometric entity.
        parents: A list of parent elements.
        classes: A list of class labels.
        ID: A string ID for the element. If empty, an ID is generated.
        guide: If True, the element is a guide and excluded from intersections.

    """

    def __init__(
        self,
        sympy_obj: GeometryEntity,
        parents: list | None = None,
        classes: list[str] | None = None,
        ID: str = "",
        guide: bool = False,
    ) -> None:
        """Initialize an Element of the model.

        This method normalizes input arguments, ensuring classes and parents are stored as dictionary keys for efficient lookup and uniqueness. It prepares the element for integration into the model's dependency graph.
        """
        self.object = sympy_obj
        if classes is None:
            classes = []
        if parents is None:
            parents = []

        self.parents = {key: "" for key in parents}
        #: Dict with keys as parent sympy objects.

        self.classes = {key: "" for key in classes}
        #: Dict with strings for class name.

        self.ID = ID
        #: Name used in presentation and reports.

        self.guide = guide
        #: Whether the element is a guide.

    @property
    def length(self) -> sp.Expr | None:
        """Returns the cleaned length of the element.
        
        This property computes or retrieves the geometric length of the element, applying symbolic cleanup to ensure the expression is simplified. For polygons, it returns a list of side lengths.
        """
        if hasattr(self, "side_lengths"):
            return self.side_lengths
        if hasattr(self.object, "length"):
            return clean_expr(self.object.length)
        return None


class CircleElement(Element):
    """Same as :class:`Element` but adds a ``pt_radius``.
    
    This subclass is specifically designed for circle elements where the radius is defined by a specific point on the circumference. It preserves the relationship between the center and the radius point.

    Args:
        sympy_obj: The sympy object representing the geometric entity.
        pt_radius: The point defining the radius.
        parents: A list of parent elements.
        classes: A list of class labels.
        ID: A string ID for the element.
        guide: If True, the element is a guide.

    """

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


def _structs_numerically_close(s1: Struct, s2: Struct, tol: float = 1e-9) -> bool:
    """Fast numerical pre-filter before expensive symbolic equivalence checks."""
    if type(s1) is not type(s2):
        return False
    if isinstance(s1, spg.Circle) and isinstance(s2, spg.Circle):
        return (
            abs(float(s1.center.x.evalf()) - float(s2.center.x.evalf())) < tol
            and abs(float(s1.center.y.evalf()) - float(s2.center.y.evalf())) < tol
            and abs(float(s1.radius.evalf()) - float(s2.radius.evalf())) < tol
        )
    if isinstance(s1, spg.Line) and isinstance(s2, spg.Line):
        a, b, c = [float(v.evalf()) for v in s1.coefficients]
        norm = (a * a + b * b) ** 0.5
        if norm == 0:
            return True
        for pt in (s2.p1, s2.p2):
            px, py = float(pt.x.evalf()), float(pt.y.evalf())
            if abs(a * px + b * py + c) / norm >= tol:
                return False
        return True
    return True


def check_existence(
    self: Model, struct: Struct, existing_structs: list[Struct]
) -> tuple[bool, Struct | None]:
    """Check if a geometric structure exists in the model.
    
    This function verifies whether a given geometric structure (line or circle) is already present in the model's collection. It indicates existence by checking both object identity and mathematical equivalence of the defining equations.

    Args:
        self: The model instance.
        struct: The structure to check.
        existing_structs: List of existing structures in the model.

    Returns:
        tuple[bool, Struct]: A tuple containing a boolean indicating existence and the existing structure if found (otherwise None).

    """
    # Check by reference
    if struct in existing_structs:
        return True, struct

    # Check by value (numeric pre-filter before symbolic simplification)
    for prev in existing_structs:
        if not _structs_numerically_close(prev, struct):
            continue
        if isinstance(prev, spg.Line) and isinstance(struct, spg.Line):
            if prev.equals(struct):
                return True, prev
        else:
            diff = (prev.equation().simplify() - struct.equation().simplify()).simplify()
            if not diff:
                return True, prev

    return False, None


def exact_intersect(s1: Struct, s2: Struct) -> list[spg.Point]:
    """Compute exact symbolic intersections of Euclidean lines and circles.

    Uses closed-form Cramer's rule, orthogonal line-circle projection, and
    circle-circle radical axis formulas to avoid SymPy's quartic ``Ellipse``
    Gröbner-basis solver on nested radicals.
    """
    def _sort_pts(pts: list[spg.Point]) -> list[spg.Point]:
        return sorted(pts, key=lambda p: (float(p.x.evalf()), float(p.y.evalf())))

    if isinstance(s1, spg.Line) and isinstance(s2, spg.Line):
        a1, b1, c1 = s1.coefficients
        a2, b2, c2 = s2.coefficients
        det = a1 * b2 - a2 * b1
        if abs(complex(det.evalf(30))) < 1e-20 and sp.simplify(det) == 0:
            return []
        x = (b1 * c2 - b2 * c1) / det
        y = (c1 * a2 - c2 * a1) / det
        return [spg.Point(x, y)]

    if isinstance(s1, spg.Circle) and isinstance(s2, spg.Line):
        s1, s2 = s2, s1

    if isinstance(s1, spg.Line) and isinstance(s2, spg.Circle):
        a, b, c = s1.coefficients
        h, k = s2.center.x, s2.center.y
        r = s2.radius
        n2 = a**2 + b**2
        s = a * h + b * k + c
        disc = r**2 * n2 - s**2
        disc_num = complex(disc.evalf(40)).real
        if abs(disc_num) < 1e-25 and sp.simplify(disc) == 0:
            return [spg.Point(h - a * s / n2, k - b * s / n2)]
        if disc_num < 0:
            return []
        rt = sp.sqrt(disc)
        return _sort_pts(
            [
                spg.Point(h - (a * s - b * rt) / n2, k - (b * s + a * rt) / n2),
                spg.Point(h - (a * s + b * rt) / n2, k - (b * s - a * rt) / n2),
            ]
        )

    if isinstance(s1, spg.Circle) and isinstance(s2, spg.Circle):
        h1, k1, r1 = s1.center.x, s1.center.y, s1.radius
        h2, k2, r2 = s2.center.x, s2.center.y, s2.radius
        dx, dy = h2 - h1, k2 - k1
        d2 = dx**2 + dy**2
        d2_num = complex(d2.evalf(30)).real
        if abs(d2_num) < 1e-20 and sp.simplify(d2) == 0:
            return []

        # Exact fast-path for equal-radius equilateral poles (P, Q) ∩ (Q, P): r1^2 == r2^2 == d^2
        r1_sq, r2_sq = r1**2, r2**2
        if (
            abs(complex((r1_sq - d2).evalf(30)).real) < 1e-20
            and abs(complex((r2_sq - d2).evalf(30)).real) < 1e-20
            and (sp.expand(r1_sq - d2) == 0 or sp.simplify(r1_sq - d2) == 0)
            and (sp.expand(r2_sq - d2) == 0 or sp.simplify(r2_sq - d2) == 0)
        ):
            s3_half = sp.sqrt(3) / 2
            return _sort_pts(
                [
                    spg.Point(h1 + dx / 2 - s3_half * dy, k1 + dy / 2 + s3_half * dx),
                    spg.Point(h1 + dx / 2 + s3_half * dy, k1 + dy / 2 - s3_half * dx),
                ]
            )

        num_u = r1_sq - r2_sq + d2
        disc = 4 * d2 * r1_sq - num_u**2
        disc_num = complex(disc.evalf(40)).real
        if abs(disc_num) < 1e-25 and sp.simplify(disc) == 0:
            u = num_u / (2 * d2)
            return [spg.Point(h1 + u * dx, k1 + u * dy)]
        if disc_num < 0:
            return []
        u = num_u / (2 * d2)
        v = sp.sqrt(disc) / (2 * d2)
        return _sort_pts(
            [
                spg.Point(h1 + u * dx - v * dy, k1 + u * dy + v * dx),
                spg.Point(h1 + u * dx + v * dy, k1 + u * dy - v * dx),
            ]
        )

    return s1.intersection(s2)


def find_all_intersections(self: Model, struct: Struct) -> None:
    """Find all intersections in the model for the given struct.
    
    This function computes the intersection points between the provided structure and all other eligible structures in the model. It uses parallel processing to efficiently handle potential intersections and updates the model with any newly found points.

    Args:
        self: The model instance.
        struct: The structure to find intersections for.

    """
    if self[struct].guide:
        return
    test_structs = [
        (el, struct)
        for el in self.structs
        if el is not struct
        and not self[el].guide
        and not (_structs_numerically_close(el, struct) and el.equals(struct))
    ]

    if not test_structs:
        return

    # check intersections
    if len(test_structs) <= 4:
        results = [find_intersection(t) for t in test_structs]
    else:
        with Pool(cpu_count()) as pool:
            results = pool.map(find_intersection, test_structs)

    for prev, struct, result in results:
        for pt in result:
            pt_new = self.set_point(pt.x, pt.y, parents=[prev, struct])
            self[prev].parents[pt_new] = ""
            self[struct].parents[pt_new] = ""


def find_intersection(test_tuple: tuple[Struct, Struct]) -> tuple[Struct, Struct, list[spg.Point]]:
    """Find intersection for two structs."""
    prev, struct = test_tuple
    result = exact_intersect(prev, struct)

    return prev, struct, result


def _get_element_by_ID(self: Model, ID: str) -> GeometryEntity | None:
    """Find and return the element with the given ID.
    
    This helper method scans the model for an element matching the provided string ID. It is useful for retrieving specific elements when their variable names are not directly accessible.

    Args:
        self: The model instance.
        ID: The ID of the desired element.

    Returns:
        Element | None: The element with the matching ID, or None if no match is found.

    """
    for element_key, element in self.items():
        if hasattr(element, "ID") and element.ID == ID:
            return element_key
    return None
