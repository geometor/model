"""
circle functions for Model class
"""

from geometor.model.common import *

from geometor.model.element import (
    Element,
    CircleElement,
    find_all_intersections,
    check_existence,
)


def _construct_circle_by_IDs(
    model, pt_1_ID: str, pt_2_ID: str, classes: list = None, ID: str = ""
) -> spg.Line:
    """
    find points by ID and use them with :meth:`Model.construct_line`
    """

    pt_1 = model.get_element_by_ID(pt_1_ID)
    pt_2 = model.get_element_by_ID(pt_2_ID)
    return model.construct_circle(pt_1, pt_2, classes, ID)


def _construct_circle(
    model,
    pt_center: spg.Point,
    pt_radius: spg.Point,
    classes: list = None,
    ID: str = "",
) -> spg.Circle:
    """
    Constructs a Circle from two points and adds it to the model.

    operations
    ----------
    - create an instance of :class:`sympy.geometry.ellipse.Circle`as ``circle``
    - create a ``details`` object from :class:`Element`
    - add parents to details
        initial parents are the two starting points
    - check for duplicates in in the ``model``
    - find intersection points for new element with all precedng elements
    - Add ``circle`` to the model.

    parameters
    ----------
    - ``pt_center`` : :class:`sympy.geometry.point.Point` A SymPy Point representing the circle center.
    - ``pt_radius`` : :class:`sympy.geometry.point.Point` A SymPy Point marking the length of the radius.
    - ``classes`` : :class:`list` *optional* A list of string names for classes defining a set of styles. Defaults to None.
    - ``ID`` : :class:`str` *optional* A text ID for use in plotting and reporting. Defaults to an empty string.

    returns
    -------
    - :class:`Circle <sympy.geometry.ellipse.Circle>`:
        The constructed circle.

    example
    -------
    >>> from geometor.elements import *
    >>> model = Model("demo")
    >>> A = model.set_point(0, 0, classes=["given"], ID="A")
    >>> B = model.set_point(1, 0, classes=["given"], ID="B")
    >>> model.construct_circle(A, B)
    <spg.Circle object ...>

    notes
    -----
    SymPy defines a circle as a center point and a radius length, so the radius length is calculated for the spg.Circle.

    """

    if classes is None:
        classes = {}
    # find radius length for sympy.Circle
    radius_len = pt_center.distance(pt_radius)

    if not isinstance(pt_center, spg.Point) or not isinstance(pt_radius, spg.Point):
        raise TypeError(
            "Both pt_center and pt_radius must be instances of sympy.geometry.point.Point"
        )

    struct = spg.Circle(pt_center, radius_len)

    if not ID:
        pt_1_ID = model[pt_center].ID
        pt_2_ID = model[pt_radius].ID
        ID = f"( {pt_1_ID} {pt_2_ID} )"

    details = CircleElement(
        struct,
        parents=[pt_center, pt_radius],
        classes=classes,
        ID=ID,
        pt_radius=pt_radius,
    )
    #  details.pt_radius = pt_radius

    exists, existing_circle = check_existence(model, struct, model.circles)
    if exists:
        # handle the logic for an existing circle
        model[existing_circle].parents[details.pt_radius] = ""
        model[existing_circle].classes.update(details.classes)
        return existing_circle
    else:
        # add the new circle to the model

        model[struct] = details
        console.print(f"[orchid1]{details.ID}[/orchid1] = {str(struct.equation())}")

        find_all_intersections(model, struct)

        return struct
