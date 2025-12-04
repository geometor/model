"""
The :mod:`geometor.model.element` module provides core element classes and intersection logic.
"""

from __future__ import annotations

from multiprocessing import Pool, cpu_count

import sympy.geometry as spg

from geometor.model.utils import clean_expr

Struct = spg.Line | spg.Circle

__all__ = [
    "Element",
    "CircleElement",
    "Struct",
    "check_existence",
    "find_all_intersections",
]


class Element:
    """
    A container for special attributes of an element of a model that are
    not supported by the SymPy elements.

    Args:
        sympy_obj: The sympy object representing the geometric entity.
        parents: A list of parent elements.
        classes: A list of class labels.
        ID: A string ID for the element. If empty, an ID is generated.
        guide: If True, the element is a guide and excluded from intersections.
    """

    def __init__(
        self,
        sympy_obj,
        parents: list | None = None,
        classes: list[str] | None = None,
        ID: str = "",
        guide: bool = False,
    ):
        """
        Initializes an Element of the model.

        Handles default argument issues.
        Casts classes and parents into keys for a dict.
        Ensures uniqueness - maintains order.
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
    def length(self):
        """
        Returns the cleaned length of the element.
        For polygons, it returns the list of cleaned side lengths.
        """
        if hasattr(self, "side_lengths"):
            return self.side_lengths
        if hasattr(self.object, "length"):
            return clean_expr(self.object.length)
        return None


class CircleElement(Element):
    """
    Same as :class:`Element` but adds a ``pt_radius``.

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
    ):
        super().__init__(sympy_obj, parents, classes, ID, guide)
        self.pt_radius = pt_radius
        #: The point defining the radius.


def check_existence(
    self, struct: Struct, existing_structs: list[Struct]
) -> tuple[bool, Struct]:
    """
    Check if a geometric structure exists in the model.

    Args:
        struct: The structure to check.
        existing_structs: List of existing structures in the model.

    Returns:
        tuple[bool, Struct]: A tuple containing a boolean indicating existence
        and the existing structure if found (otherwise None).
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


def find_all_intersections(self, struct: Struct) -> None:
    """
    Find all intersections in the model for the given struct.

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


def find_intersection(test_tuple: tuple) -> tuple:
    """find intersection for two structs"""
    prev, struct = test_tuple
    result = struct.intersection(prev)

    return prev, struct, result


def _get_element_by_ID(self, ID: str):
    """
    Finds and returns the element with the given ID.

    Args:
        ID: The ID of the desired element.

    Returns:
        Element | None: The element with the matching ID, or None if no match is found.
    """
    for element_key, element in self.items():
        if hasattr(element, "ID") and element.ID == ID:
            return element_key
    return None
