"""
The :mod:`geometor.model.reports` module provides reporting functions for the Model class.
"""
#  from geometor.elements.model.common import *

import sympy as sp
import sympy.geometry as spg
from rich.console import Console
from rich.table import Table
from rich.text import Text

# from .utils import *


def generate_dot(graph, parent=None, dot_string="", defined_nodes=None):
    if parent is None:
        dot_string += "digraph {\n"
        defined_nodes = set()  # Keep track of defined nodes

    for node, children in graph.items():
        # Define the node with the appropriate shape and label only if not already defined
        if node not in defined_nodes:
            if node.startswith("["):  # Line
                shape = "rectangle"
                label = node[1:-1]
            elif node.startswith("("):  # Circle
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



class ReportMixin:
    """
    Mixin for the Model class containing report generation methods.
    """

    def report_summary(self):
        console = Console()

        console.print(f"\nMODEL summary: {self.name}")
        table = Table(title="Totals")

        table.add_column("type", justify="center")
        table.add_column("count", justify="center")

        table.add_row("elements", str(len(self)))
        table.add_row("points", str(len(self.points)))
        table.add_row("lines", str(len(self.lines)))
        table.add_row("circles", str(len(self.circles)))
        console.print("\n")
        console.print(table)

    def report_group_by_type(self):
        console = Console()

        console.print(f"\nMODEL report: {self.name}")

        # Points
        table = Table(title="Points")
        table.add_column("ID", justify="center")
        table.add_column("x", justify="center")
        table.add_column("y", justify="center")
        table.add_column("classes", justify="center")
        table.add_column("parents", justify="center")

        for el in self.points:
            details = self[el]
            el_classes = list(self[el].classes.keys())
            el_ID = get_colored_ID(el, self[el].ID, el_classes)
            el_parents_text = Text()  # Initialize an empty Text object for parents
            for parent in details.parents.keys():
                parent_classes = list(self[parent].classes.keys())
                el_parents_text.append(
                    get_colored_ID(parent, self[parent].ID, parent_classes)
                )
                el_parents_text.append("\n")

            table.add_row(
                el_ID,
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

        for el in self.lines:
            pt_1, pt_2 = el.points
            details = self[el]
            el_classes = list(self[el].classes.keys())
            el_ID = get_colored_ID(el, self[el].ID, el_classes)
            el_parents_text = Text()  # Initialize an empty Text object for parents
            for parent in details.parents.keys():
                parent_classes = list(self[parent].classes.keys())
                el_parents_text.append(
                    get_colored_ID(parent, self[parent].ID, parent_classes)
                )
                el_parents_text.append("\n")
            table.add_row(
                el_ID,
                str(self[pt_1].ID or pt_1),
                str(self[pt_2].ID or pt_2),
                "\n".join(el_classes),
                el_parents_text,
                str(el.equation()),
            )

        console.print("\n")
        console.print(table)

        # Circles
        table = Table(title="Circles")
        table.add_column("ID", style="red", justify="center")
        table.add_column("pt_ctr", justify="center")
        table.add_column("pt_rad", justify="center")
        table.add_column("classes", justify="center")
        table.add_column("parents", justify="center")
        table.add_column("equation", justify="center")

        for el in self.circles:
            pt_1 = el.center
            pt_2 = self[el].pt_radius
            #  pt_1, pt_2 = el.points
            details = self[el]
            el_classes = list(self[el].classes.keys())
            el_ID = get_colored_ID(el, self[el].ID, el_classes)
            el_parents_text = Text()  # Initialize an empty Text object for parents
            for parent in details.parents.keys():
                parent_classes = list(self[parent].classes.keys())
                el_parents_text.append(
                    get_colored_ID(parent, self[parent].ID, parent_classes)
                )
                el_parents_text.append("\n")
            table.add_row(
                el_ID,
                str(self[pt_1].ID or pt_1),
                str(self[pt_2].ID or pt_2),
                "\n".join(el_classes),
                el_parents_text,
                str(el.equation()),
            )

        console.print("\n")
        console.print(table)

    def report_sequence(self):
        """Generate a sequential report of the model using rich Console layouts."""
        console = Console()

        console.print(f"\nMODEL report: {self.name}")

        table = Table(title="Sequence", row_styles=["on black", ""])

        table.add_column("ID", style="bold", justify="center")
        table.add_column("<", justify="center")
        table.add_column(">", justify="center")
        table.add_column("classes", justify="center")
        table.add_column("parents", justify="center")
        table.add_column("equation", justify="left")

        for el, details in self.items():
            el_classes = list(details.classes.keys())
            el_parents_text = Text()  # Initialize an empty Text object for parents
            #  breakpoint()
            for parent in details.parents.keys():
                parent_classes = list(self[parent].classes.keys())
                el_parents_text.append(
                    get_colored_ID(parent, self[parent].ID, parent_classes)
                )
                el_parents_text.append("\n")

            ID = get_colored_ID(el, details.ID, el_classes)
            row = [
                ID,
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
                row[1] = str(self[pt_1].ID or pt_1)
                row[2] = str(self[pt_2].ID or pt_2)
                row[5] = sp.pretty(el.equation())

            elif isinstance(el, spg.Circle):
                pt_center = el.center
                pt_radius = (
                    details.pt_radius
                )  # Assuming the radius point is stored in the details
                row[1] = str(self[pt_center].ID or pt_center)
                row[2] = str(self[pt_radius].ID or pt_radius)
                row[5] = sp.pretty(el.equation())

            elif isinstance(el, spg.Segment):
                pt_1, pt_2 = el.points
                row[1] = str(self[pt_1].ID or pt_1)
                row[2] = str(self[pt_2].ID or pt_2)

            elif isinstance(el, spg.Polygon):
                vertices = ", ".join(str(self[pt].ID or pt) for pt in el.vertices)
                row[1] = vertices

            table.add_row(*row)

        console.print(table)


from .colors import get_color


def get_colored_ID(el, ID, classes=None):
    """Get the colored ID for a geometric element."""
    ID_color = get_color(el, classes)
    return Text(ID, style=ID_color)
