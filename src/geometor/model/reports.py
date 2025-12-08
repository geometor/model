"""Provides reporting functions for the Model class.

This module offers tools for visualizing and summarizing the state of the geometric model. It includes functions to generate textual reports for the console using `rich` tables and methods to export the model's structure as Graphviz DOT files for diagram generation.
"""
#  from geometor.elements.model.common import *

import sympy as sp
import sympy.geometry as spg
from sympy.geometry.entity import GeometryEntity
from rich.console import Console
from rich.table import Table
from rich.text import Text

# from .utils import *

from .colors import get_color


def generate_dot(
    graph: dict,
    parent: str | None = None,
    dot_string: str = "",
    defined_nodes: set | None = None,
) -> str:
    """Generates a DOT string representing the graph structure of the model.
    
    This function traverses a nested dictionary representing the model's ancestor graph and produces a Graphviz DOT format string. It handles node definition with appropriate shapes (rectangles for lines, ellipses for circles, points for points) and edge creation to visualize dependencies.

    Args:
        graph: A dictionary representing the graph structure/ancestors.
        parent: The key of the parent node (used in recursion).
        dot_string: The accumulating DOT string (used in recursion).
        defined_nodes: A set of already defined nodes to prevent duplicates.

    Returns:
        A string containing the complete DOT graph definition.
    """
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
    """Mixin for the Model class containing report generation methods.
    
    This mixin provides the Model with methods to output formatted summaries and detailed reports of its contents. It utilizes the `rich` library to create readable console tables of elements, organized by type or sequence, facilitating inspection and debugging.
    """

    def report_summary(self) -> None:
        """Prints a summary of the model's contents to the console.
        
        This method compiles a high-level overview of the total number of elements in the model, broken down by category (points, lines, circles). It uses a formatted table for clear presentation of these statistics.
        """
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

    def report_group_by_type(self) -> None:
        """Prints a detailed report of all elements grouped by type.
        
        This method iterates through the model's collections of points, lines, and circles, generating separate tables for each type. Each table includes detailed information such as IDs, coordinates/equations, parent dependencies, and associated classes.
        """
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

    def report_sequence(self) -> None:
        """Generate a sequential report of the model using rich Console layouts.
        
        This method lists all elements in the order they were added to the model. It presents a comprehensive view including the element's ID, defining points or properties, parents, classes, and algebraic equation, providing a chronological log of the construction.
        """
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


def get_colored_ID(
    el: GeometryEntity, ID: str, classes: list[str] | None = None
) -> Text:
    """Get the colored ID for a geometric element.
    
    This helper checks the element's classes to determine its color and returns a styled Text object suitable for rendering in the rich console.
    
    Args:
        el: The geometric entity.
        ID: The text ID of the element.
        classes: A list of class names associated with the element.

    Returns:
        A :class:`rich.text.Text` object containing the styled ID.
    """
    ID_color = get_color(el, classes)
    return Text(ID, style=ID_color)
