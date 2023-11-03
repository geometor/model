"""
report helper functions
"""
#  from geometor.elements.model.common import *

from rich.console import Console
from rich.table import Table
from rich.text import Text

from .common import *

from .utils import *

from .element import (
    Element,
    _get_ancestors,
    _get_ancestors_labels,
    _get_element_by_label,
)


def generate_dot(graph, parent=None, dot_string="", defined_nodes=None):
    if parent is None:
        dot_string += "digraph {\n"
        defined_nodes = set()  # Keep track of defined nodes

    for node, children in graph.items():
        # Define the node with the appropriate shape and label only if not already defined
        if node not in defined_nodes:
            if node.startswith('['):  # Line
                shape = "rectangle"
                label = node[1:-1]
            elif node.startswith('('):  # Circle
                shape = "ellipse"
                label = node[1:-1]
            else:  # Point
                shape = "point"
                label = node

            dot_string += f'    "{node}" [shape={shape}, label="{label}"];\n'
            defined_nodes.add(node)  # Mark the node as defined

        # Recurse for children if present
        if isinstance(children, dict) and children:
            # Add the edge to each child and recurse
            for child in children.keys():
                dot_string += f'    "{node}" -> "{child}";\n'  # Define the edge here
                dot_string = generate_dot(children, child, dot_string, defined_nodes)

    if parent is None:
        dot_string += "}\n"

    return dot_string


def report_summary(model):
    console = Console()

    console.print(f"\nMODEL summary: {model.name}")
    table = Table(title="Totals")

    table.add_column("type", justify="center")
    table.add_column("count", justify="center")

    table.add_row("elements", str(len(model)))
    table.add_row("points", str(len(model.points)))
    table.add_row("lines", str(len(model.lines)))
    table.add_row("circles", str(len(model.circles)))
    console.print("\n")
    console.print(table)


def report_group_by_type(model):
    console = Console()

    console.print(f"\nMODEL report: {model.name}")

    # Points
    table = Table(title="Points")
    table.add_column("Label", justify="center")
    table.add_column("x", justify="center")
    table.add_column("y", justify="center")
    table.add_column("classes", justify="center")
    table.add_column("parents", justify="center")

    for el in model.points:
        details = model[el]
        el_label = get_colored_label(el, model[el].label)
        el_classes = list(model[el].classes.keys())
        el_parents_text = Text()  # Initialize an empty Text object for parents
        for parent in details.parents.keys():
            el_parents_text.append(get_colored_label(parent, model[parent].label))
            el_parents_text.append("\n")

        table.add_row(
            el_label,
            str(el.x),
            str(el.y),
            "\n".join(el_classes),
            el_parents_text,
        )
    console.print("\n")
    console.print(table)

    # Lines
    table = Table(title="Lines")
    table.add_column("#", justify="center")
    table.add_column("pt_1", justify="center")
    table.add_column("pt_2", justify="center")
    table.add_column("classes", justify="center")
    table.add_column("parents", justify="center")
    table.add_column("equation", justify="center")

    for el in model.lines:
        pt_1, pt_2 = el.points
        details = model[el]
        el_label = get_colored_label(el, model[el].label)
        el_classes = list(model[el].classes.keys())
        el_parents_text = Text()  # Initialize an empty Text object for parents
        for parent in details.parents.keys():
            el_parents_text.append(get_colored_label(parent, model[parent].label))
            el_parents_text.append("\n")
        table.add_row(
            el_label,
            str(model[pt_1].label or pt_1),
            str(model[pt_2].label or pt_2),
            "\n".join(el_classes),
            el_parents_text,
            str(el.equation()),
        )

    console.print("\n")
    console.print(table)

    # Circles
    table = Table(title="Circles")
    table.add_column("Label", style="red", justify="center")
    table.add_column("pt_ctr", justify="center")
    table.add_column("pt_rad", justify="center")
    table.add_column("classes", justify="center")
    table.add_column("parents", justify="center")
    table.add_column("equation", justify="center")

    for el in model.circles:
        pt_1 = el.center
        pt_2 = model[el].pt_radius
        #  pt_1, pt_2 = el.points
        details = model[el]
        el_label = get_colored_label(el, model[el].label)
        el_classes = list(model[el].classes.keys())
        el_parents_text = Text()  # Initialize an empty Text object for parents
        for parent in details.parents.keys():
            el_parents_text.append(get_colored_label(parent, model[parent].label))
            el_parents_text.append("\n")
        table.add_row(
            el_label,
            str(model[pt_1].label or pt_1),
            str(model[pt_2].label or pt_2),
            "\n".join(el_classes),
            el_parents_text,
            str(el.equation()),
        )

    console.print("\n")
    console.print(table)


def get_colored_label(el, label):
    """Get the colored label for a geometric element."""
    label_color = ""
    if isinstance(el, spg.Point):
        label_color = "gold3"
    elif isinstance(el, spg.Line):
        label_color = "white"
    elif isinstance(el, spg.Circle):
        label_color = "orchid1"
    elif isinstance(el, spg.Segment):
        label_color = "gold3"
    elif isinstance(el, spg.Polygon):
        label_color = "bright_green"

    return Text(label, style=label_color)


def report_sequence(model):
    """Generate a sequential report of the model using rich Console layouts."""
    console = Console()

    console.print(f"\nMODEL report: {model.name}")

    table = Table(title="Sequence", row_styles=["on black", ""])

    table.add_column("Label", style="bold", justify="center")
    table.add_column("<", justify="center")
    table.add_column(">", justify="center")
    table.add_column("classes", justify="center")
    table.add_column("parents", justify="center")
    table.add_column("equation", justify="left")

    for el, details in model.items():
        el_classes = list(details.classes.keys())
        el_parents_text = Text()  # Initialize an empty Text object for parents
        #  breakpoint()
        for parent in details.parents.keys():
            el_parents_text.append(get_colored_label(parent, model[parent].label))
            el_parents_text.append("\n")

        label = get_colored_label(el, details.label)
        row = [
            label,
            "",
            "",
            "\n".join(el_classes),
            #  el_parents,
            el_parents_text,
            "",
        ]
        if isinstance(el, spg.Point):
            row[1] = str(sp.pretty(el.x))
            row[2] = str(sp.pretty(el.y))

        elif isinstance(el, spg.Line):
            pt_1, pt_2 = el.points
            row[1] = str(model[pt_1].label or pt_1)
            row[2] = str(model[pt_2].label or pt_2)
            row[5] = sp.pretty(el.equation())

        elif isinstance(el, spg.Circle):
            pt_center = el.center
            pt_radius = (
                details.pt_radius
            )  # Assuming the radius point is stored in the details
            row[1] = str(model[pt_center].label or pt_center)
            row[2] = str(model[pt_radius].label or pt_radius)
            row[5] = sp.pretty(el.equation())

        elif isinstance(el, spg.Segment):
            pt_1, pt_2 = el.points
            row[1] = str(model[pt_1].label or pt_1)
            row[2] = str(model[pt_2].label or pt_2)

        elif isinstance(el, spg.Polygon):
            vertices = ", ".join(str(model[pt].label or pt) for pt in el.vertices)
            row[1] = vertices

        table.add_row(*row)

    console.print(table)
