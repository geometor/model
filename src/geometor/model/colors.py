"""
The :mod:`geometor.model.colors` module defines the default colors for geometric elements.
"""

import sympy.geometry as spg
from sympy.geometry.entity import GeometryEntity

COLORS = {
    "point": "gold3",
    "point_given": "green",
    "line": "white",
    "circle": "orchid1",
    "polygon": "bright_green",
    "segment": "gold3",
    "section": "yellow",
    "golden": "yellow",
    "guide": "orange",
    "selected": "cyan",
}


def get_color(
    element: GeometryEntity, classes: list[str] | None = None
) -> str:
    """
    Get the color for a geometric element based on its type and classes.
    """
    if classes is None:
        classes = []

    if "guide" in classes:
        return COLORS["guide"]
    if "given" in classes:
        return COLORS["point_given"]

    if isinstance(element, spg.Point):
        return COLORS["point"]
    elif isinstance(element, spg.Line):
        return COLORS["line"]
    elif isinstance(element, spg.Circle):
        return COLORS["circle"]
    elif isinstance(element, spg.Segment):
        return COLORS["segment"]
    elif isinstance(element, spg.Polygon):
        return COLORS["polygon"]

    return "white"
