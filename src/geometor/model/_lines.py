"""
helper functions for Model class
"""

from geometor.model.common import *

from geometor.model.element import *

#  from geometor.model.model import Model


def _construct_line_by_labels(
    model, pt_1_label: str, pt_2_label: str, classes: list = None, label: str = ""
) -> spg.Line:
    """
    find points by label and use them with :meth:`Model.construct_line`
    """

    pt_1 = model.get_element_by_label(pt_1_label)
    pt_2 = model.get_element_by_label(pt_2_label)
    model.construct_line(pt_1, pt_2, classes, label)


def _construct_line(
    model, pt_1: spg.Point, pt_2: spg.Point, classes: list = None, label: str = ""
) -> spg.Line:
    """
    Constructs a :class:`Line <sympy.geometry.line.Line>` from two points and
    adds it to the :class:`Model <geometor.model.model.Model>`

    parameters
    ----------
    - ``pt_1`` : :class:`sympy.geometry.point.Point` *A SymPy Point marking the
      first point of the line*
    - ``pt_2`` : :class:`sympy.geometry.point.Point`: A SymPy Point marking the
      second point of the line
    - ``classes``  : list: Additional classes (optional)
    - ``label``  : str: Label for the line (optional)

    returns
    -------
    - :class:`sympy.geometry.line.Line`: The constructed line

    example
    -------
    >>> from geometor.elements import *
    >>> model = Model("demo")
    >>> A = model.set_point(0, 0, classes=["given"], label="A")
    >>> B = model.set_point(1, 0, classes=["given"], label="B")
    >>> model.construct_line(A, B)
    <spg.Line object ...>

    operations
    ----------
    - create an instance of ``spg.Line``
    - create a ``details`` object from :class:`Element`
    - add parents to details
    - check for duplicates in elements.
    - find intersection points for new element with all precedng elements
    - Add ``line`` to the model.
    """
    if classes is None:
        classes = []

    if not isinstance(pt_1, spg.Point) or not isinstance(pt_2, spg.Point):
        raise TypeError(
            "Both pt_1 and pt_2 must be instances of sympy.geometry.point.Point"
        )

    struct = spg.Line(pt_1, pt_2)

    if not label:
        pt_1_label = model[pt_1].label
        pt_2_label = model[pt_2].label
        label = f"[ {pt_1_label} {pt_2_label} ]"

    details = Element(struct, parents=[pt_1, pt_2], classes=classes, label=label)

    exists, existing_line = check_existence(model, struct, model.lines)

    if exists:
        # handle the logic for an existing circle
        for parent in struct.points:
            model[existing_line].parents[parent] = ""
        model[existing_line].classes.update(details.classes)
    else:
        # add struct
        model[struct] = details
        console.print(f"{details.label} = {struct.equation()}")

        find_all_intersections(model, struct)

        return struct
