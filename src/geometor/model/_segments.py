"""
segemnt helper functions for sequencer
"""

from geometor.model.common import *
from geometor.model.element import Element

def _set_segment_by_labels(
    model, pt_1_label: str, pt_2_label: str, classes: list = None, label: str = ""
) -> spg.Line:
    """
    find points by label and use them with :meth:`Model.construct_line`
    """

    pt_1 = model.get_element_by_label(pt_1_label)
    pt_2 = model.get_element_by_label(pt_2_label)
    model.set_segment(pt_1, pt_2, classes, label)

def _set_segment(model, pt_1, pt_2, classes=[], label="") -> spg.Segment:
    """
    set segment (list of points) for demonstration in the model
    """
    segment = spg.Segment(pt_1, pt_2)
    details = Element(segment, parents=[pt_1, pt_2], classes=classes, label=label)

    model[segment] = details

    #  print(f"{details.label}")
    return segment
