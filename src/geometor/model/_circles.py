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
    guide: bool = False,
) -> spg.Circle:
    model.clear_new_points()
    """
    Constructs a Circle from two points and adds it to the model.
    """

    if classes is None:
        classes = []
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
        guide=guide,
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
        model.log(f"[bold]{details.ID}[/bold] = {str(struct.equation())}")

        find_all_intersections(model, struct)

        return struct
