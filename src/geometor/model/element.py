"""
Element type
ElementDetails class
intersection functions
"""
import sympy.geometry as spg
from multiprocessing import Pool, cpu_count
from geometor.model.utils import clean_expr

Struct = (spg.Line | spg.Circle)

__all__ = ["Element", "CircleElement", "Struct", "check_existence", "find_all_intersections"]

class Element:
    """
    a container for special attributes of an element of a model that are
    not supported by the SymPy elements

    parameters
    ----------
    - ``sympy_obj`` :
        The sympy object representing the geometric entity.
    - ``parents`` : list[objects]
        A list of parent elements (default is None).
    - ``classes`` : list[str]
        A list of class labels (default is None).
    - ``ID`` : str
        - A string ID for the element
        - if ID is none, a ID is generated
        - is used as a reference in reports and plots

    attributes
    ----------
    - ``ID`` : :class:`python:str`
        name used in presentation and reports
    - ``classes`` : dict
        dict with strings for class name
    - ``parents`` : dict
        dict with keys as parent sympy objects


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
        self.ID = ID
        self.guide = guide

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
    '''
    same as :class:`Element` but adds a ``pt_radius``

    parameters
    ----------
    - ``sympy_obj`` :
        The sympy object representing the geometric entity.
    - ``pt_radius`` : spg.Point
        A list of parent elements (default is None).
    - ``parents`` : list[objects]
        A list of parent elements (default is None).
    - ``classes`` : list[str]
        A list of class labels (default is None).
    - ``ID`` : str
        - A string ID for the element
        - if ID is none, a ID is generated
        - is used as a reference in reports and plots

    attributes
    ----------
    - ``ID`` : :class:`python:str`
        name used in presentation and reports
    - ``classes`` : dict
        dict with strings for class name
    - ``parents`` : dict
        dict with keys as parent sympy objects
    '''
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


def check_existence(
    self, struct: Struct, existing_structs: list[Struct]
) -> tuple[bool, Struct]:
    """Check if a geometric structure exists in the model.
    

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
    """find all intersections in the model for the given struct"""
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
    """Finds and returns the element with the given ID.

    parameters
    ----------
    - ``ID`` : :class:`str`: The ID of the desired element.

    returns
    -------
    Element or None: The element with the matching ID, or None if no match is found.
    """
    for element_key, element in self.items():
        if hasattr(element, "ID") and element.ID == ID:
            return element_key
    return None
