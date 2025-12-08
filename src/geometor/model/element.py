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
        """Initializes an Element of the model.

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
        super().__init__(sympy_obj, parents, classes, ID, guide)
        self.pt_radius = pt_radius
        #: The point defining the radius.


def check_existence(
    self: Model, struct: Struct, existing_structs: list[Struct]
) -> tuple[bool, Struct | None]:
    """Check if a geometric structure exists in the model.
    
    This function verifies whether a given geometric structure (line or circle) is already present in the model's collection. It indicates existence by checking both object identity and mathematical equivalence of the defining equations.

    Args:
        struct: The structure to check.
        existing_structs: List of existing structures in the model.

    Returns:
        tuple[bool, Struct]: A tuple containing a boolean indicating existence and the existing structure if found (otherwise None).
    """
    # Check by reference
    if struct in existing_structs:
        return True, struct

    # Check by value
    for prev in existing_structs:
        diff = (prev.equation().simplify() - struct.equation().simplify()).simplify()
        if not diff:
            return True, prev

    return False, None


def find_all_intersections(self: Model, struct: Struct) -> None:
    """Find all intersections in the model for the given struct.
    
    This function computes the intersection points between the provided structure and all other eligible structures in the model. It uses parallel processing to efficiently handle potential intersections and updates the model with any newly found points.

    Args:
        struct: The structure to find intersections for.
    """
    if self[struct].guide:
        return
    test_structs = [
        (el, struct)
        for el in self.structs
        if not el.equals(struct) and not self[el].guide
    ]

    # check intersections
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
    result = struct.intersection(prev)

    return prev, struct, result


def _get_element_by_ID(self: Model, ID: str) -> GeometryEntity | None:
    """Finds and returns the element with the given ID.
    
    This helper method scans the model for an element matching the provided string ID. It is useful for retrieving specific elements when their variable names are not directly accessible.

    Args:
        ID: The ID of the desired element.

    Returns:
        Element | None: The element with the matching ID, or None if no match is found.
    """
    for element_key, element in self.items():
        if hasattr(element, "ID") and element.ID == ID:
            return element_key
    return None
