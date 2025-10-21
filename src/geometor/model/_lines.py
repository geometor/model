"""
helper functions for Model class
"""

from geometor.model.common import *

from geometor.model.element import *

#  from geometor.model.model import Model


def _construct_line_by_IDs(
    model, pt_1_ID: str, pt_2_ID: str, classes: list = None, ID: str = ""
) -> spg.Line:
    """
    find points by ID and use them with :meth:`Model.construct_line`
    """

    pt_1 = model.get_element_by_ID(pt_1_ID)
    pt_2 = model.get_element_by_ID(pt_2_ID)
    return model.construct_line(pt_1, pt_2, classes, ID)


def _construct_line(
    model, pt_1: spg.Point, pt_2: spg.Point, classes: list = None, ID: str = "", logger=None
) -> spg.Line:
    model.clear_new_points()
    """
    Constructs a :class:`Line <sympy.geometry.line.Line>` from two points and
    adds it to the :class:`Model <geometor.model.model.Model>`
    """
    if classes is None:
        classes = []

    if not isinstance(pt_1, spg.Point) or not isinstance(pt_2, spg.Point):
        raise TypeError(
            "Both pt_1 and pt_2 must be instances of sympy.geometry.point.Point"
        )

    struct = spg.Line(pt_1, pt_2)

    if not ID:
        pt_1_ID = model[pt_1].ID
        pt_2_ID = model[pt_2].ID
        ID = f"- {pt_1_ID} {pt_2_ID} -"

    details = Element(struct, parents=[pt_1, pt_2], classes=classes, ID=ID)

    exists, existing_line = check_existence(model, struct, model.lines)

    if exists:
        # handle the logic for an existing circle
        for parent in struct.points:
            model[existing_line].parents[parent] = ""
        model[existing_line].classes.update(details.classes)
    else:
        # add struct
        model[struct] = details
        if logger:
            logger.info(f"{details.ID} = {struct.equation()}")

        find_all_intersections(model, struct)

        return struct
