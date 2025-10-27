"""
segment helper functions for sequencer
"""

from geometor.model.common import *
from geometor.model.element import Element
from geometor.model.colors import COLORS
from rich.table import Table

def _set_segment_by_IDs(
    model, pt_1_ID: str, pt_2_ID: str, classes: list = None, ID: str = ""
) -> spg.Line:
    """
    find points by ID and use them with :meth:`Model.construct_line`
    """

    pt_1 = model.get_element_by_ID(pt_1_ID)
    pt_2 = model.get_element_by_ID(pt_2_ID)
    return model.set_segment(pt_1, pt_2, classes, ID)

def _set_segment(model, pt_1: spg.Point, pt_2: spg.Point, classes=[], ID="") -> spg.Segment:
    """
    set segment (list of points) for demonstration in the model
    """
    segment = spg.Segment(pt_1, pt_2)
    if not ID:
        segment_points_IDs = [str(model[pt].ID or pt) for pt in [pt_1, pt_2]]
        segment_points_IDs = " ".join(segment_points_IDs)
        ID = f"/ {segment_points_IDs} /"
    details = Element(segment, parents=[pt_1, pt_2], classes=classes, ID=ID)

    model[segment] = details

    classes_str = " : " + " ".join(classes) if classes else ""
    model.log(f"[{COLORS['segment']} bold]{details.ID}[/{COLORS['segment']} bold]{classes_str}")
    table = Table(show_header=False, box=None, padding=(0, 4))
    table.add_row("    len:", f"[cyan]{sp.pretty(segment.length)}[/cyan]")
    model.log(table)

    return segment
