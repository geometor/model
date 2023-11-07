"""
helper functions for Model class
"""
from geometor.model.common import *


class Element:
    """a container for special attributes of an element of a model that are
    not supported by the SymPy elements

    :param sympy_obj: The sympy object representing the geometric entity.
    :param list(object) parents: A list of parent elements (default is None).
    :param list(str) classes: A list of class labels (default is None).
    :param str label: - A string label for the element - if label is none, a label is generated - is used as a reference in reports and plots

    attributes
    ----------
    label : :class:`python:str`
        name used in presentation and reports
    classes : dict
        dict with strings for class name
    parents : dict
        dict with keys as parent sympy objects

    parameters
    ----------
    ``sympy_obj`` :
        The sympy object representing the geometric entity.
    ``parents`` : list(objects)
        A list of parent elements (default is None).
    ``classes`` : list(str)
        A list of class labels (default is None).
    ``label`` : str
        - A string label for the element
        - if label is none, a label is generated
        - is used as a reference in reports and plots

    """

    def __init__(
        self,
        sympy_obj,
        parents: list | None = None,
        classes: list[str] | None = None,
        label: str = "",
    ):
        """
        Initializes an Element of the model.

        handles default argument issues

        casts classes and parents into keys for a dict
        ensures uniqueness - maintains order

        """
        self.object = sympy_obj
        if classes is None:
            classes = []
        if parents is None:
            parents = []

        self.parents = {key: "" for key in parents}
        self.classes = {key: "" for key in classes}
        self.label = label


class CircleElement(Element):
    def __init__(
        self,
        sympy_obj: spg.Circle,
        pt_radius: spg.Point,
        parents: list | None = None,
        classes: list[str] | None = None,
        label: str = "",
    ):
        super().__init__(sympy_obj, parents, classes, label)
        self.pt_radius = pt_radius


def check_existence(
    self, struct: spg.Line | spg.Circle, existing_structs: list[spg.Line | spg.Circle]
) -> tuple[bool, spg.Line | spg.Circle]:
    """Check if a geometric structure exists in the model."""
    # Check by reference
    if struct in existing_structs:
        return True, struct

    # Check by value
    for prev in existing_structs:
        diff = (prev.equation().simplify() - struct.equation().simplify()).simplify()
        if not diff:
            return True, prev

    return False, None


def find_all_intersections(self, struct: spg.Line | spg.Circle) -> None:
    """find all intersections in the model for the given struct"""
    test_structs = [(el, struct) for el in self.structs if not el.equals(struct)]

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


def _get_ancestors_labels(self, element) -> dict[str, dict]:
    """
    Retrieves the labels of the ancestors for the given element.

    The method recursively traverses the parent elements of the given element
    and constructs a nested dictionary with labels representing the ancestor tree.

    parameters:
        element : sympy.geometry object
            The element for which the ancestors' labels are to be retrieved.

    returns:
        dict : A nested dictionary representing the labels of the ancestors.

    example:
        If element A has parents B and C, and B has parent D, the method returns:
        {'A': {'B': {'D': {}}, 'C': {}}}
    """

    ancestors = {self[element].label: {}}

    if "given" in self[element].classes:
        return ancestors

    # Check if the element has parents
    parents = []
    if self[element].parents:
        # Consider only the first two parents
        parents = list(self[element].parents.keys())[:2]

    for parent in parents:
        ancestors[self[element].label].update(self.get_ancestors_labels(parent))

    return ancestors


def _get_ancestors(self, element):
    """
    Retrieves the ancestors for the given element.

    The method recursively traverses the parent elements of the given element
    and constructs a nested dictionary representing the ancestor tree.

    parameters:
        element : sympy.geometry object
            The element for which the ancestors are to be retrieved.

    returns:
        dict : A nested dictionary representing the ancestors.

    example:
        If element A has parents B and C, and B has parent D, the method returns:
        {A: {B: {D: {}}, C: {}}}
    """
    ancestors = {element: {}}

    if "given" in self[element].classes:
        return ancestors

    # Check if the element has parents
    parents = []
    if self[element].parents:
        # Consider only the first two parents
        parents = list(self[element].parents.keys())[:2]

    for parent in parents:
        ancestors[element].update(self.get_ancestors(parent))

    return ancestors


def _get_element_by_label(self, label: str):
    """Finds and returns the element with the given label.

    Parameters:
        - label (str): The label of the desired element.

    Returns:
        Element or None: The element with the matching label, or None if no match is found.
    """
    for element_key, element in self.items():
        if hasattr(element, "label") and element.label == label:
            return element_key
    return None
