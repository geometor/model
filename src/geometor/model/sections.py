"""
section functions for Model class
"""
#  from __future__ import annotations

from geometor.model.common import *
from geometor.model.utils import *

from geometor.model.element import (
    Element,
    CircleElement,
    find_all_intersections,
    check_existence,
)

#  from geometor.model import Model

phi = sp.Rational(1, 2) + (sp.sqrt(5) / 2)


class Section:
    def __init__(self, points: list[spg.Point]):
        assert len(points) == 3, "A section must be defined by three points."

        self.points = points
        self.segments = [
            spg.Segment(points[0], points[1]),
            spg.Segment(points[1], points[2]),
        ]
        self.clean_expr = clean_expr

    def get_labels(self, model) -> list[str]:
        """
        returns a list of labels
        """
        return [model[pt].label for pt in self.points]

    @property
    def ratio(self) -> sp.Expr:
        """
        returns the ratio of the symbolic lengths of each segment
        """
        l1, l2 = self.lengths
        if l1.evalf() < l2.evalf():
            l1, l2 = l2, l1
        return self.clean_expr(l1 / l2)

    @property
    def lengths(self) -> list[sp.Expr]:
        return [self.clean_expr(seg.length) for seg in self.segments]

    @property
    def floats(self) -> list[float]:
        return [float(length.evalf()) for length in self.lengths]

    @property
    def is_golden(self) -> bool:
        # Use symbolic simplification to check for equality, avoiding float precision issues.
        # We simplify the difference between the ratio and phi (and 1/phi).
        # If the result is 0, they are symbolically equal.
        is_phi = sp.simplify(self.ratio - phi) == 0
        is_inv_phi = sp.simplify(self.ratio - (1 / phi)) == 0
        return is_phi or is_inv_phi

    @property
    def min_length(self) -> sp.Expr:
        return min(self.lengths)

    @property
    def min_float(self) -> float:
        return min(self.floats)

    @property
    def min_segment(self) -> spg.Segment:
        min_length_index = self.lengths.index(self.min_length())
        return self.segments[min_length_index]

    @property
    def max_length(self) -> sp.Expr:
        return max(self.lengths)

    @property
    def max_float(self) -> float:
        return max(self.floats)

    @property
    def max_segment(self) -> spg.Segment:
        max_length_index = self.lengths.index(self.max_length())
        return self.segments[max_length_index]

def _set_section_by_labels(
        model, points_labels: list[str], classes: list = None, label: str = ""
) -> Section:
    """
    find points by label and use them with :meth:`Model.set_section`
    """
    points = []

    for point_label in points_labels:
        points.append(model.get_element_by_label(poly_label))

    return model.set_section(points, classes, label)


def _set_section(model, points: list[spg.Point], classes=[], label="") -> Section:
    """
    set section (list of 3 points on a line)
    """

    # TODO: check points and minimum count of 3
    section = Section(points)
    section_repr = sp.FiniteSet(*points)

    if not label:
        points_labels = [str(model[pt].label or pt) for pt in points]
        points_labels = " ".join(points_labels)
        label = f"/ {points_labels} /"

    details = Element(section_repr, parents=points, classes=classes, label=label)

    model[section_repr] = details

    print(f"{details.label}")
    return section
