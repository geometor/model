"""
helper functions for polygons
"""

from geometor.model.common import *
from geometor.model.element import Element


def _set_polygon_by_labels(
        model, poly_pts_labels: list[str], classes: list = None, label: str = ""
) -> spg.Line:
    """
    find points by label and use them with :meth:`Model.construct_line`
    """
    poly_pts = []

    for poly_label in poly_pts_labels:
        poly_pts.append(model.get_element_by_label(poly_label))

    return model.set_polygon(poly_pts, classes)


def _set_polygon(model, poly_pts: list[spg.Point], classes=[], label="") -> spg.Polygon:
    """
    set polygon (list of 3 or more points)
    """

    # TODO: check points and minimum count of 3
    poly = spg.Polygon(*poly_pts)

    if not label:
        poly_pts_labels = [str(model[pt].label or pt) for pt in poly_pts]
        poly_pts_labels = " ".join(poly_pts_labels)
        label = f"< {poly_pts_labels} >"

    details = Element(poly, parents=poly_pts, classes=classes, label=label)

    model[poly] = details

    print(f"{details.label}")
    return poly
