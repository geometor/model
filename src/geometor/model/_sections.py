"""
section functions for Model class
"""
#  from __future__ import annotations

from geometor.model.common import *

from geometor.model.element import (
    Element,
    CircleElement,
    find_all_intersections,
    check_existence,
)

#  from geometor.model import Model

phi = sp.Rational(1, 2) + (sp.sqrt(5) / 2)


class Section:
    def __init__(self, points):
        assert len(points) == 3, "A section must be defined by three points."

        self.points = points
        self.segments = [
            spg.Segment(points[0], points[1]),
            spg.Segment(points[1], points[2]),
        ]

    def get_labels(self, model):
        return [model[pt].label for pt in self.points]

    @property
    def ratio(self):
        l1, l2 = self.lengths
        return clean_expr(l1 / l2)

    @property
    def lengths(self):
        return [clean_expr(seg.length) for seg in self.segments]

    @property
    def floats(self):
        return [float(length.evalf()) for length in self.lengths]

    @property
    def is_golden(self):
        phi_ratio_check = (self.ratio / phi).evalf()
        inv_phi_ratio_check = (self.ratio / (1 / phi)).evalf()

        return phi_ratio_check == 1 or inv_phi_ratio_check == 1

    @property
    def min_length(self):
        return min(self.lengths)

    @property
    def min_float(self):
        return min(self.floats)

    @property
    def min_segment(self):
        min_length_index = self.lengths.index(self.min_length())
        return self.segments[min_length_index]

    @property
    def max_length(self):
        return max(self.lengths)

    @property
    def max_float(self):
        return max(self.floats)

    @property
    def max_segment(self):
        max_length_index = self.lengths.index(self.max_length())
        return self.segments[max_length_index]

