"""
segemnt helper functions for sequencer
"""

from .common import *
from .element import Element

def _set_segment(model, pt_1, pt_2, classes=[], label="") -> spg.Segment:
    """
    set segment (list of points) for demonstration in the model
    """
    segment = spg.Segment(pt_1, pt_2)
    details = Element(segment, parents=[pt_1, pt_2], classes=classes, label=label)

    model[segment] = details

    print(f"{details.label}")
    return segment
