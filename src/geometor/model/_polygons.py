"""
helper functions for polygons
"""

from geometor.model.common import *
from geometor.model.element import Element
from geometor.model.utils import clean_expr


def _set_polygon_by_IDs(
        model, poly_pts_IDs: list[str], classes: list = None, ID: str = ""
) -> spg.Line:
    """
    find points by ID and use them with :meth:`Model.construct_line`
    """
    poly_pts = []

    for poly_ID in poly_pts_IDs:
        poly_pts.append(model.get_element_by_ID(poly_ID))

    return model.set_polygon(poly_pts, classes)


def _set_polygon(model, poly_pts: list[spg.Point], classes=[], ID="") -> spg.Polygon:
    """
    set polygon (list of 3 or more points)
    """

    # TODO: check points and minimum count of 3
    poly = spg.Polygon(*poly_pts)

    if not ID:
        poly_pts_IDs = [str(model[pt].ID or pt) for pt in poly_pts]
        poly_pts_IDs = " ".join(poly_pts_IDs)
        ID = f"< {poly_pts_IDs} >"

    details = Element(poly, parents=poly_pts, classes=classes, ID=ID)

    details.side_lengths = [clean_expr(side.length) for side in poly.sides]

    model[poly] = details

    print(f"{details.ID}")
    return poly
