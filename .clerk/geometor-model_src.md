## src/geometor/model/__init__.py

```py
"""

The Model module provides a set of tools for constructing geometric models.
It relies heavily on sympy for providing the algebraic infrastructure
the functions here are for creating the abstract model, not the rendering
see the Render module for plotting with matplotlib

This module provides the `Model` class, which is used to represent a geometric model
in 2D space. The `Model` class is based on the `list` data structure, and can contain
points, lines, circles, polygons, and segments.
"""
__author__ = "geometor"
__maintainer__ = "geometor"
__email__ = "github@geometor.com"
__version__ = "0.0.1"
__licence__ = "MIT"

from geometor.model.common import *

from geometor.model.element import *
#  from geometor.model.model import Model
from geometor.model.wedges import Wedge
from geometor.model.sections import Section
from geometor.model.chains import Chain

from geometor.model.reports import *

from collections.abc import Iterator

from geometor.model.utils import *

from geometor.model.element import (
    Element,
    CircleElement,
    _get_ancestors,
    _get_ancestors_labels,
    _get_element_by_label,
)

from geometor.model._points import _set_point
from geometor.model._lines import _construct_line, _construct_line_by_labels
from geometor.model._circles import (
    _construct_circle,
    _construct_circle_by_labels,
)
from geometor.model._polygons import _set_polygon, _set_polygon_by_labels
from geometor.model._segments import _set_segment, _set_segment_by_labels

from geometor.model.wedges import Wedge, _set_wedge # _set_wedge_by_labels
from geometor.model.sections import *
from geometor.model.chains import *

from geometor.model._serialize import _save_to_json, _load_from_json

GeometryObject = (
    spg.Point
    | spg.Line
    | spg.Circle
    | spg.Segment
    | spg.Polygon
    | Wedge
    | Section
    | Chain
)


class Model(dict):
    """
    A collection of geometric elements, including points, lines, circles, and
    polygons, represented using the `sympy.geometry` library.

    When lines and circles are added to the model, intersection points of the
    new element with the preceding elements are identify and added.

    When new elements or points are added to the model, we check for existing
    duplicates.

    parameters
    ----------
    - ``name`` : :class:`str`
        establish name for the model instance

    attributes
    ----------
    - :attr:`name` -> :class:`str` *name of the model*
    - :attr:`points` -> :class:`list` [:class:`Point <sympy.geometry.point.Point>`]
    - :attr:`lines` -> :class:`list` [:class:`Line <sympy.geometry.point.Line>`]
    - :attr:`circles` -> :class:`list` [:class:`Circle <sympy.geometry.point.Circle>`]
    - :attr:`structs` -> :class:`list` [Struct]
        returns list of structs (lines and circles) in the Model

    methods
    -------
    - :meth:`set_point` -> :class:`Point <sympy.geometry.point.Point>`
    - :meth:`construct_line` -> :class:`Line <sympy.geometry.line.Line>`
    - :meth:`construct_line_by_labels` -> :class:`Line <sympy.geometry.line.Line>`
    - :meth:`construct_circle` -> :class:`Circle <sympy.geometry.ellipse.Circle>`
    - :meth:`construct_circle_by_labels` -> :class:`Circle <sympy.geometry.ellipse.Circle>`
    - :meth:`set_segment` -> :class:`Segment <sympy.geometry.line.Segment>`
    - :meth:`set_segment_by_labels` -> :class:`Segment <sympy.geometry.line.Segment>`
    - :meth:`set_polygon` -> :class:`Polygon <sympy.geometry.polygon.Polygon>`
    - :meth:`set_polygon_by_labels` -> :class:`Polygon <sympy.geometry.polygon.Polygon>`
    - :meth:`set_wedge` -> :class:`Wedge`

    - :meth:`limits` -> :class:`list`
        returns the x, y limits of the points and circle boundaries in the model

    - :meth:`get_ancestors` ->
    - :meth:`get_ancestors_labels` ->

    - :meth:`get_element_by_label` ->

    - :meth:`save` ->
    - :meth:`load` ->

    - :meth:`point_label_generator` -> Iterator[str]

    .. todo:: add `get_bounds_polygon` method to Model

    """

    def __init__(self, name: str = ""):
        super().__init__()
        self._name = name
        self.label_gen = self.point_label_generator()

    @property
    def name(self) -> str:
        """The name of the model"""
        return self._name

    @name.setter
    def name(self, value) -> None:
        self._name = value

    def __setitem__(self, key: GeometryObject, value: Element):
        """
        control types for keys and values
        parameters:
            ``key`` : :class:`spg.entity` or custom objects like Wedge
                the geometric element object
            ``value`` : :class:`Element`
                side car object with info about the geometric object
        """
        if not isinstance(key, GeometryObject):
            raise TypeError(f"{key=} must be an instance of Element class")
        if not isinstance(value, Element):
            raise TypeError(f"{ value= } must be an instance of Element class")
        super().__setitem__(key, value)

    set_point = _set_point

    construct_line = _construct_line
    construct_line_by_labels = _construct_line_by_labels

    construct_circle = _construct_circle
    construct_circle_by_labels = _construct_circle_by_labels

    set_segment = _set_segment
    set_segment_by_labels = _set_segment_by_labels

    set_polygon = _set_polygon
    set_polygon_by_labels = _set_polygon_by_labels

    set_wedge = _set_wedge
    #  set_wedge_by_labels = _set_wedge_by_labels

    def remove_by_label(self, label: str) -> None:
        el = self.get_element_by_label(label)
        del self[el]

    @property
    def points(self) -> list[spg.Point]:
        """
        returns point elements from model as list
        """
        return [el for el in self if isinstance(el, spg.Point)]

    @property
    def structs(self) -> list[Struct]:
        """
        returns struct elements (line or circle) from model as list
        """
        return [
            el
            for el in self
            if (
                isinstance(el, (spg.Line, spg.Circle))
                and "guide" not in self[el].classes
            )
        ]

    @property
    def lines(self) -> list[spg.Line]:
        """
        returns line elements from model as list
        """
        return [el for el in self if isinstance(el, spg.Line)]

    @property
    def circles(self) -> list[spg.Circle]:
        """
        returns circle elements from model as list
        """
        return [el for el in self if isinstance(el, spg.Circle)]

    def limits(self) -> tuple[tuple[float, float], tuple[float, float]]:
        """
        Find x, y limits from points and circles of the model

        Returns a list of x, y limits:
            ``((x_min, x_max), (y_min, y_max))``
        """

        x_vals = []
        y_vals = []

        for el in self:
            if isinstance(el, spg.Point):
                x_vals.append(float(el.x))
                y_vals.append(float(el.y))

            elif isinstance(el, spg.Circle):
                x_vals.extend(
                    [float(el.center.x - el.radius), float(el.center.x + el.radius)]
                )
                y_vals.extend(
                    [float(el.center.y - el.radius), float(el.center.y + el.radius)]
                )

        if not x_vals or not y_vals:
            raise ValueError(
                "Model contains no geometric elements to determine limits."
            )

        return [[min(x_vals), max(x_vals)], [min(y_vals), max(y_vals)]]

    get_ancestors = _get_ancestors
    get_ancestors_labels = _get_ancestors_labels

    get_element_by_label = _get_element_by_label

    save = _save_to_json
    load = _load_from_json

    def point_label_generator(self) -> Iterator[str]:
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        repeat = 1

        while True:
            # Iterate through combinations of letters based on the current repeat value
            for letter in letters:
                yield str(letter) * repeat

            # Increment the repeat value for the next cycle
            repeat += 1


if __name__ == "__main__":
    from geometor.model.reports import *

    model = Model("demo")
    A = model.set_point(0, 0, classes=["given"])
    B = model.set_point(1, 0, classes=["given"])
    model.construct_line(A, B)
    model.construct_circle(A, B)
    model.construct_circle(B, A)

    E = model.get_element_by_label("E")
    F = model.get_element_by_label("F")
    model.construct_line(E, F)

    report_sequence(model)
    report_group_by_type(model)
    report_summary(model)

```

## src/geometor/model/__main__.py

```py
"""The package entry point into the application."""
from geometor.model import Model
from geometor.model.reports import *

model = Model("demo")
A = model.set_point(0, 0, classes=["given"])
B = model.set_point(1, 0, classes=["given"])
model.construct_line(A, B)
model.construct_circle(A, B)
model.construct_circle(B, A)

E = model.get_element_by_label("E")
F = model.get_element_by_label("F")
model.construct_line(E, F)

report_sequence(model)
report_group_by_type(model)
report_summary(model)

```

## src/geometor/model/_circles.py

```py
"""
circle functions for Model class
"""

from geometor.model.common import *

from geometor.model.element import (
    Element,
    CircleElement,
    find_all_intersections,
    check_existence,
)


def _construct_circle_by_labels(
    model, pt_1_label: str, pt_2_label: str, classes: list = None, label: str = ""
) -> spg.Line:
    """
    find points by label and use them with :meth:`Model.construct_line`
    """

    pt_1 = model.get_element_by_label(pt_1_label)
    pt_2 = model.get_element_by_label(pt_2_label)
    return model.construct_circle(pt_1, pt_2, classes, label)


def _construct_circle(
    model,
    pt_center: spg.Point,
    pt_radius: spg.Point,
    classes: list = None,
    label: str = "",
) -> spg.Circle:
    """
    Constructs a Circle from two points and adds it to the model.

    operations
    ----------
    - create an instance of :class:`sympy.geometry.ellipse.Circle`as ``circle``
    - create a ``details`` object from :class:`Element`
    - add parents to details
        initial parents are the two starting points
    - check for duplicates in in the ``model``
    - find intersection points for new element with all precedng elements
    - Add ``circle`` to the model.

    parameters
    ----------
    - ``pt_center`` : :class:`sympy.geometry.point.Point` A SymPy Point representing the circle center.
    - ``pt_radius`` : :class:`sympy.geometry.point.Point` A SymPy Point marking the length of the radius.
    - ``classes`` : :class:`list` *optional* A list of string names for classes defining a set of styles. Defaults to None.
    - ``label`` : :class:`str` *optional* A text label for use in plotting and reporting. Defaults to an empty string.

    returns
    -------
    - :class:`Circle <sympy.geometry.ellipse.Circle>`:
        The constructed circle.

    example
    -------
    >>> from geometor.elements import *
    >>> model = Model("demo")
    >>> A = model.set_point(0, 0, classes=["given"], label="A")
    >>> B = model.set_point(1, 0, classes=["given"], label="B")
    >>> model.construct_circle(A, B)
    <spg.Circle object ...>

    notes
    -----
    SymPy defines a circle as a center point and a radius length, so the radius length is calculated for the spg.Circle.

    """

    if classes is None:
        classes = {}
    # find radius length for sympy.Circle
    radius_len = pt_center.distance(pt_radius)

    if not isinstance(pt_center, spg.Point) or not isinstance(pt_radius, spg.Point):
        raise TypeError(
            "Both pt_center and pt_radius must be instances of sympy.geometry.point.Point"
        )

    struct = spg.Circle(pt_center, radius_len)

    if not label:
        pt_1_label = model[pt_center].label
        pt_2_label = model[pt_radius].label
        label = f"( {pt_1_label} {pt_2_label} )"

    details = CircleElement(
        struct,
        parents=[pt_center, pt_radius],
        classes=classes,
        label=label,
        pt_radius=pt_radius,
    )
    #  details.pt_radius = pt_radius

    exists, existing_circle = check_existence(model, struct, model.circles)
    if exists:
        # handle the logic for an existing circle
        model[existing_circle].parents[details.pt_radius] = ""
        model[existing_circle].classes.update(details.classes)
        return existing_circle
    else:
        # add the new circle to the model

        model[struct] = details
        console.print(f"[orchid1]{details.label}[/orchid1] = {str(struct.equation())}")

        find_all_intersections(model, struct)

        return struct

```

## src/geometor/model/_lines.py

```py
"""
helper functions for Model class
"""

from geometor.model.common import *

from geometor.model.element import *

#  from geometor.model.model import Model


def _construct_line_by_labels(
    model, pt_1_label: str, pt_2_label: str, classes: list = None, label: str = ""
) -> spg.Line:
    """
    find points by label and use them with :meth:`Model.construct_line`
    """

    pt_1 = model.get_element_by_label(pt_1_label)
    pt_2 = model.get_element_by_label(pt_2_label)
    return model.construct_line(pt_1, pt_2, classes, label)


def _construct_line(
    model, pt_1: spg.Point, pt_2: spg.Point, classes: list = None, label: str = ""
) -> spg.Line:
    """
    Constructs a :class:`Line <sympy.geometry.line.Line>` from two points and
    adds it to the :class:`Model <geometor.model.model.Model>`

    parameters
    ----------
    - ``pt_1`` : :class:`sympy.geometry.point.Point` *A SymPy Point marking the
      first point of the line*
    - ``pt_2`` : :class:`sympy.geometry.point.Point`: A SymPy Point marking the
      second point of the line
    - ``classes``  : list: Additional classes (optional)
    - ``label``  : str: Label for the line (optional)

    returns
    -------
    - :class:`sympy.geometry.line.Line`: The constructed line

    example
    -------
    >>> from geometor.elements import *
    >>> model = Model("demo")
    >>> A = model.set_point(0, 0, classes=["given"], label="A")
    >>> B = model.set_point(1, 0, classes=["given"], label="B")
    >>> model.construct_line(A, B)
    <spg.Line object ...>

    operations
    ----------
    - create an instance of ``spg.Line``
    - create a ``details`` object from :class:`Element`
    - add parents to details
    - check for duplicates in elements.
    - find intersection points for new element with all precedng elements
    - Add ``line`` to the model.
    """
    if classes is None:
        classes = []

    if not isinstance(pt_1, spg.Point) or not isinstance(pt_2, spg.Point):
        raise TypeError(
            "Both pt_1 and pt_2 must be instances of sympy.geometry.point.Point"
        )

    struct = spg.Line(pt_1, pt_2)

    if not label:
        pt_1_label = model[pt_1].label
        pt_2_label = model[pt_2].label
        label = f"[ {pt_1_label} {pt_2_label} ]"

    details = Element(struct, parents=[pt_1, pt_2], classes=classes, label=label)

    exists, existing_line = check_existence(model, struct, model.lines)

    if exists:
        # handle the logic for an existing circle
        for parent in struct.points:
            model[existing_line].parents[parent] = ""
        model[existing_line].classes.update(details.classes)
    else:
        # add struct
        model[struct] = details
        console.print(f"{details.label} = {struct.equation()}")

        find_all_intersections(model, struct)

        return struct

```

## src/geometor/model/_points.py

```py
"""
helper functions for Model class
"""

from geometor.model.common import *
from geometor.model.utils import *

from geometor.model.element import Element
from geometor.model.reports import get_colored_label


def _set_point(
    self,
    x_val: sp.Expr,
    y_val: sp.Expr,
    parents: list = None,
    classes: list = None,
    label: str = "",
) -> spg.Point:
    """
    Adds a point to the model, finds duplicates, cleans values, and sets
    parents and classes.

    parameters
    ----------
    - ``x_val`` : :class:`sympy.core.expr.Expr`: The x-value of the point.
    - ``y_val`` : :class:`sympy.core.expr.Expr`: The y-value of the point.
    - ``parents`` : list, optional: A list of parent elements or references.
      Defaults to None.
    - ``classes`` list, optional: A list of string names for classes defining
      a set of styles. Defaults to None.
    - ``label`` str, optional: A text label for use in plotting and
      reporting. Defaults to an empty string.

    returns
    -------
    - :class:`sympy.geometry.point.Point`: The set point.

    example
    -------
    >>> from geometor.model import *
    >>> model = Model("demo")
    >>> model.set_point(0, 0, classes=["given"])
    <spg.Point object ...>

    notes
    -----
    The function simplifies the x and y values before adding, and it updates the attributes if the point is already in the model.
    """

    if classes is None:
        classes = []
    if parents is None:
        parents = []

    # simplify values before adding
    x_val = clean_expr(x_val)
    y_val = clean_expr(y_val)

    pt = spg.Point(x_val, y_val)

    details = Element(pt, parents, classes, label)

    if pt in self.points:
        # add attributes
        for parent in details.parents:
            self[pt].parents[parent] = ""
        self[pt].classes.update(details.classes)
        return pt

    else:
        for prev_pt in self.points:
            if pt.equals(prev_pt):
                for parent in details.parents:
                    self[prev_pt].parents[parent] = ""
                self[prev_pt].classes.update(details.classes)
                return prev_pt

    if not label:
        label = next(self.label_gen)

    details = Element(pt, parents, classes, label)
    self[pt] = details
    
    text_label = get_colored_label(pt, label)
    console.print(f"[gold3]{text_label}[/gold3] = {{ {str(pt.x)}, {str(pt.y)} }}")
    #  console.print(f"[gold3]{text_label}[/gold3] = {{ {sp.pretty(pt.x)}, {sp.pretty(pt.y)} }}")
    #  print(f"{text_label} = {{ {sp.pprint(pt.x)}, {str(pt.y)} }}")
    return pt

```

## src/geometor/model/_polygons.py

```py
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

```

## src/geometor/model/_segments.py

```py
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
    return model.set_segment(pt_1, pt_2, classes, label)

def _set_segment(model, pt_1: spg.Point, pt_2: spg.Point, classes=[], label="") -> spg.Segment:
    """
    set segment (list of points) for demonstration in the model
    """
    segment = spg.Segment(pt_1, pt_2)
    details = Element(segment, parents=[pt_1, pt_2], classes=classes, label=label)

    model[segment] = details

    return segment

```

## src/geometor/model/_serialize.py

```py
import json
from .common import *
from .element import Element, CircleElement

def _save_to_json(self, file_path):
    serializable_model = {}
    for key, element in self.items():
        serializable_key = str(key)
        serializable_element = {
            'label': element.label,
            'classes': element.classes,
            'parents': str(element.parents)  # or any other serialization approach for parents
        }
        if isinstance(element, CircleElement):
            serializable_element['pt_radius'] = str(element.pt_radius)
        serializable_model[serializable_key] = serializable_element

    print(serializable_model)

    with open(file_path, 'w') as file:
        json.dump(serializable_model, file, indent=4)


@classmethod
def _load_from_json(cls, file_path):
    namespace = {name: getattr(spg, name) for name in dir(spg)}  # Add all SymPy geometry objects to the namespace
    namespace['sqrt'] = sp.sqrt  # Include the sqrt function from SymPy

    with open(file_path, 'r') as file:
        serializable_model = json.load(file)

    model = cls()
    for key, serializable_element in serializable_model.items():
        sympy_obj = eval(key, namespace)
        if 'Circle' in key:
            element = CircleElement(
                sympy_obj=sympy_obj,
                label=serializable_element['label'],
                classes=serializable_element['classes'],
                parents=eval(serializable_element['parents'], namespace),
                pt_radius=eval(serializable_element['pt_radius'], namespace)
            )
        else:
            element = Element(
                sympy_obj=sympy_obj,
                label=serializable_element['label'],
                classes=serializable_element['classes'],
                parents=eval(serializable_element['parents'], namespace)
            )
        model[eval(key, namespace)] = element

    return model

```

## src/geometor/model/app.py

```py
"""
run the main app
"""
from .model import Model


def run() -> None:
    reply = Model().run()
    print(reply)

```

## src/geometor/model/chains.py

```py
from rich import print
from collections import defaultdict

from geometor.model import *
from geometor.model.utils import *
#  from geometor.render import *
from geometor.model.sections import *


class Chain:
    """
    A class representing a chain of connected golden sections,
    facilitating the extraction of segments, points, and lengths, as well as
    analyzing the flow and symmetry within the chain.

    Each chain’s flow is characterized by the comparative lengths of
    consecutive segments, represented symbolically to understand the
    progression and transitions in segment lengths. Furthermore, this module
    empowers users to explore symmetry lines within chains, unveiling a subtle,
    profound aspect of geometric harmony.

    """

    def __init__(self, sections: list[Section]):
        """
        Initializes a Chain object with a list of connected sections.

        parameters
        ----------
        - ``sections`` : :class:`list[Section]`
            A list of Section objects representing a chain of connected golden sections.
        """
        self.sections = sections
        self.segments = self.extract_segments()
        self.points = self.extract_points()

    def extract_segments(self) -> list[spg.Segment]:
        """
        Extracts unique segments from the chain.

        returns
        -------
        - :class:`list[spg.Segment]`
            A list containing the unique segments in the chain.
        """
        segments = []
        for section in self.sections:
            for segment in section.segments:
                if not any(segment.equals(existing) for existing in segments):
                    segments.append(segment)
        return segments

    def extract_points(self) -> list[spg.Point]:
        """
        Extracts unique points from the chain while maintaining order.

        returns
        -------
        - :class:`list[spg.Point]`
            A list containing the ordered unique points from the chain.
        """
        points = {}
        for section in self.sections:
            for point in section.points:
                points[point] = None
        return list(points.keys())

    @property
    def lengths(self) -> list[sp.Expr]:
        """
        Extract the symbolic lengths of the segments in the chain.

        returns
        -------
        - :class:`list[sp.Expr]`
            A list containing the symbolic lengths of each segment in the chain.
        """
        return [clean_expr(segment.length) for segment in self.segments]

    @property
    def numerical_lengths(self) -> list[float]:
        """
        Calculate and extract the numerical lengths of the segments in the chain.

        returns
        -------
        - :class:`list[float]`
            A list containing the evaluated numerical lengths of each
            segment in the chain.
        """
        return [float(segment.length.evalf()) for segment in self.segments]

    @property
    def flow(self) -> list[str]:
        """
        Determine the flow of the segments in the chain by comparing the lengths
        of consecutive segments.

        returns
        -------
        - :class:`list[str]`
            A list of symbols representing the flow of segment lengths. '>'
            indicates that the previous segment is longer, '<' indicates
            that the next segment is longer.
        """
        flow_symbols = []
        lengths = self.numerical_lengths  # Using numerical lengths for comparison

        for i in range(len(lengths) - 1):
            if lengths[i] > lengths[i + 1]:
                flow_symbols.append(">")
            elif lengths[i] < lengths[i + 1]:
                flow_symbols.append("<")
            else:
                flow_symbols.append("=")  # Equal lengths

        return "".join(flow_symbols)

    def count_symmetry_lines(self) -> int:
        symmetry_count = 0
        flow = self.flow
        flow_length = len(flow)

        # Iterate over the flow string to identify changes in direction
        for i in range(1, flow_length):
            if flow[i] != flow[i - 1]:
                symmetry_count += 1

        return symmetry_count

    @property
    def fibonacci_labels(self) -> list[str]:
        """
        Creates and returns Fibonacci-style labels for each segment based on
        their lengths.

        returns
        -------
        - :class:`list[str]`
            A list of strings where each string is a Fibonacci-style 
            label corresponding to a segment.
        """

        # Step 1: Define Symbols
        a, b = sp.symbols('a b')

        # Step 2: Generate Expressions
        expressions = [a, b]
        unique_lengths = sorted(set(self.numerical_lengths))
        for _ in range(2, len(unique_lengths)):
            next_expr = expressions[-1] + expressions[-2]
            expressions.append(next_expr)

        # Step 3: Mapping Expressions
        length_to_expr = {length: str(expr).replace(" ", "") for length, expr in zip(unique_lengths, expressions)}

        # Assign expressions to segments
        segment_expressions = [str(length_to_expr[length]) for length in self.numerical_lengths]

        return segment_expressions

```

## src/geometor/model/common.py

```py
"""
common imports for all modules

NOTE: do not put local references in here
"""
import sympy as sp
import sympy.plotting as spp
import sympy.geometry as spg
from sympy.abc import x, y

sp.init_printing()

import math as math
import numpy as np
from collections import defaultdict
import logging

from rich import print
from rich.console import Console
from rich.table import Table
from rich.text import Text

console = Console()

from itertools import permutations, combinations
from multiprocessing import Pool, cpu_count


```

## src/geometor/model/element.py

```py
"""
Element type
ElementDetails class
intersection functions
"""
from geometor.model.common import *

Struct = (spg.Line | spg.Circle)

class Element:
    """
    a container for special attributes of an element of a model that are
    not supported by the SymPy elements

    parameters
    ----------
    - ``sympy_obj`` :
        The sympy object representing the geometric entity.
    - ``parents`` : list[objects]
        A list of parent elements (default is None).
    - ``classes`` : list[str]
        A list of class labels (default is None).
    - ``label`` : str
        - A string label for the element
        - if label is none, a label is generated
        - is used as a reference in reports and plots

    attributes
    ----------
    - ``label`` : :class:`python:str`
        name used in presentation and reports
    - ``classes`` : dict
        dict with strings for class name
    - ``parents`` : dict
        dict with keys as parent sympy objects


    """

    def __init__(
        self,
        sympy_obj,
        parents: list | None = None,
        classes: list[str] | None = None,
        label: str = "",
    ):
        """
        Initializes an Element of the model.

        handles default argument issues

        casts classes and parents into keys for a dict
        ensures uniqueness - maintains order

        """
        self.object = sympy_obj
        if classes is None:
            classes = []
        if parents is None:
            parents = []

        self.parents = {key: "" for key in parents}
        self.classes = {key: "" for key in classes}
        self.label = label


class CircleElement(Element):
    '''
    same as :class:`Element` but adds a ``pt_radius``

    parameters
    ----------
    - ``sympy_obj`` :
        The sympy object representing the geometric entity.
    - ``pt_radius`` : spg.Point
        A list of parent elements (default is None).
    - ``parents`` : list[objects]
        A list of parent elements (default is None).
    - ``classes`` : list[str]
        A list of class labels (default is None).
    - ``label`` : str
        - A string label for the element
        - if label is none, a label is generated
        - is used as a reference in reports and plots

    attributes
    ----------
    - ``label`` : :class:`python:str`
        name used in presentation and reports
    - ``classes`` : dict
        dict with strings for class name
    - ``parents`` : dict
        dict with keys as parent sympy objects
    '''
    def __init__(
        self,
        sympy_obj: spg.Circle,
        pt_radius: spg.Point,
        parents: list | None = None,
        classes: list[str] | None = None,
        label: str = "",
    ):
        super().__init__(sympy_obj, parents, classes, label)
        self.pt_radius = pt_radius


def check_existence(
    self, struct: Struct, existing_structs: list[Struct]
) -> tuple[bool, Struct]:
    """Check if a geometric structure exists in the model.
    

    """
    # Check by reference
    if struct in existing_structs:
        return True, struct

    # Check by value
    for prev in existing_structs:
        diff = (prev.equation().simplify() - struct.equation().simplify()).simplify()
        if not diff:
            return True, prev

    return False, None


def find_all_intersections(self, struct: Struct) -> None:
    """find all intersections in the model for the given struct"""
    test_structs = [(el, struct) for el in self.structs if not el.equals(struct)]

    # check intersections
    with Pool(cpu_count()) as pool:
        results = pool.map(find_intersection, test_structs)

    for prev, struct, result in results:
        for pt in result:
            pt_new = self.set_point(pt.x, pt.y, parents=[prev, struct])
            self[prev].parents[pt_new] = ""
            self[struct].parents[pt_new] = ""


def find_intersection(test_tuple: tuple) -> tuple:
    """find intersection for two structs"""
    prev, struct = test_tuple
    result = struct.intersection(prev)

    return prev, struct, result


def _get_ancestors_labels(self, element) -> dict[str, dict]:
    """
    Retrieves the labels of the ancestors for the given element.

    The method recursively traverses the parent elements of the given element
    and constructs a nested dictionary with labels representing the ancestor tree.

    parameters
    ----------
    - element : sympy.geometry object
        The element for which the ancestors' labels are to be retrieved.

    returns
    - dict : A nested dictionary representing the labels of the ancestors.

    example
    -------
    If element A has parents B and C, and B has parent D, the method returns:
    {'A': {'B': {'D': {}}, 'C': {}}}
    """

    ancestors = {self[element].label: {}}

    if "given" in self[element].classes:
        return ancestors

    # Check if the element has parents
    parents = []
    if self[element].parents:
        # Consider only the first two parents
        parents = list(self[element].parents.keys())[:2]

    for parent in parents:
        ancestors[self[element].label].update(self.get_ancestors_labels(parent))

    return ancestors


def _get_ancestors(self, element):
    """
    Retrieves the ancestors for the given element.

    The method recursively traverses the parent elements of the given element
    and constructs a nested dictionary representing the ancestor tree.

    parameters
    ----------
    - element : sympy.geometry object
        The element for which the ancestors are to be retrieved.

    returns
    -------
    - dict : A nested dictionary representing the ancestors.

    example
    -------
    If element A has parents B and C, and B has parent D, the method returns:
    {A: {B: {D: {}}, C: {}}}
    """
    ancestors = {element: {}}

    if "given" in self[element].classes:
        return ancestors

    # Check if the element has parents
    parents = []
    if self[element].parents:
        # Consider only the first two parents
        parents = list(self[element].parents.keys())[:2]

    for parent in parents:
        ancestors[element].update(self.get_ancestors(parent))

    return ancestors


def _get_element_by_label(self, label: str):
    """Finds and returns the element with the given label.

    parameters
    ----------
    - ``label`` : :class:`str`: The label of the desired element.

    returns
    -------
    Element or None: The element with the matching label, or None if no match is found.
    """
    for element_key, element in self.items():
        if hasattr(element, "label") and element.label == label:
            return element_key
    return None

```

## src/geometor/model/helpers.py

```py
"""
a few helper functions from earlier constructions

these types of operations need to be integrated into the euclid model
"""


from geometor.model.common import *
from geometor.model import *


# helpers ******************************
def line_get_y(l1, x):
    """return y value for specific x"""
    a, b, c = l1.coefficients

    return (-a * x - c) / b


def set_given_start_points(model):
    """create inital two points -
    establishing the unit for the field"""
    p1 = model.set_point(sp.Rational(-1, 2), 0, classes=["given"])
    p2 = model.set_point(sp.Rational(1, 2), 0, classes=["given"])
    return p1, p2


def set_given_start_points_zero(model):
    """create inital two points -
    establishing the unit for the field"""
    p1 = model.set_point(0, 0, classes=["given"])
    p2 = model.set_point(1, 0, classes=["given"])
    return p1, p2


def set_equilateral_poles(
    model: Model, pt_1: spg.Point, pt_2: spg.Point, add_circles=True
):
    if add_circles:
        c1 = model.construct_circle(pt_1, pt_2, classes=["guide"])
        c2 = model.construct_circle(pt_2, pt_1, classes=["guide"])
        pts = c1.intersection(c2)
        set_points = []
        for pt in pts:
            pt = model.set_point(pt.x, pt.y)
            set_points.append(pt)
            #  model[pt].parents[c1] = ""
            #  model[pt].parents[c2] = ""

        return set_points
    else:
        c1 = spg.Circle(pt_1, pt_1.distance(pt_2))
        c2 = spg.Circle(pt_2, pt_2.distance(pt_1))
        pts = c1.intersection(c2)
        set_points = []
        for pt in pts:
            pt = model.set_point(pt.x, pt.y)
            set_points.append(pt)
            model[pt].parents[c1] = ""
            model[pt].parents[c2] = ""

        return set_points


def construct_perpendicular_bisector(model, pt_1, pt_2, add_circles=True):
    """perform fundamental operations for two points
    and add perpendicular bisector"""
    pole_1, pole_2 = set_equilateral_poles(model, pt_1, pt_2, add_circles)
    return model.construct_line(pole_1, pole_2, classes=["bisector"])

def set_midpoint(model, pt_1, pt_2, add_circles=True):
    """perform fundamental operations for two points
    and add perpendicular bisector"""
    pole_1, pole_2 = set_equilateral_poles(model, pt_1, pt_2, add_circles)
    return model.construct_line(pole_1, pole_2, classes=["bisector"])


def set_given_rect_points(model, pt, x_offset, y_offset):
    rect_points = [pt]
    pt_x0 = model.set_point(pt.x + x_offset, pt.y, classes=['given'])
    rect_points.append(pt_x0)
    pt_xy = model.set_point(pt.x + x_offset, pt.y + y_offset, classes=['given'])
    rect_points.append(pt_xy)
    pt_0y = model.set_point(pt.x, pt.y + y_offset, classes=['given'])
    rect_points.append(pt_0y)

    return rect_points


def set_given_square_points(model, pt, offset):
    return set_given_rect_points(model, pt, offset, offset)

```

## src/geometor/model/reports.py

```py
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

```

## src/geometor/model/sections.py

```py
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
    def __init__(self, points: list[spg.Point]):
        assert len(points) == 3, "A section must be defined by three points."

        self.points = points
        self.segments = [
            spg.Segment(points[0], points[1]),
            spg.Segment(points[1], points[2]),
        ]

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
        return clean_expr(l1 / l2)

    @property
    def lengths(self) -> list[sp.Expr]:
        return [clean_expr(seg.length) for seg in self.segments]

    @property
    def floats(self) -> list[float]:
        return [float(length.evalf()) for length in self.lengths]

    @property
    def is_golden(self) -> bool:
        phi_ratio_check = (self.ratio / phi).evalf()
        inv_phi_ratio_check = (self.ratio / (1 / phi)).evalf()

        return phi_ratio_check == 1 or inv_phi_ratio_check == 1

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


```

## src/geometor/model/utils.py

```py
"""utils"""
import logging
import os as os

from geometor.model.common import *

#  from geometor.model import *


def clean_expr(expr):
    """
    simplify and denest SymPy expressions
    """
    expr = sp.simplify(expr)
    expr = sp.sqrtdenest(expr)
    return expr

def spread(l1: spg.Line, l2: spg.Line):
    """calculate the spread of two lines"""
    a1, a2, a3 = l1.coefficients
    b1, b2, b3 = l2.coefficients
    # only the first two coefficients are used
    spread = ((a1 * b2 - a2 * b1) ** 2) / ((a1**2 + b1**2) * (a2**2 + b2**2))
    return spread


def compare_points(pt1, pt2):
    if pt1.x.evalf() > pt2.x.evalf():
        return 1
    elif pt1.x.evalf() < pt2.x.evalf():
        return -1
    else:
        if pt1.y.evalf() > pt2.y.evalf():
            return 1
        elif pt1.y.evalf() < pt2.y.evalf():
            return -1
        else:
            return 0


def point_value(pt):
    #  return pt.x.evalf()
    return (pt.x.evalf(), pt.y.evalf())


def sort_points(pts):
    #  return sorted(list(pts), key=point_value)
    return sorted(pts, key=point_value)


def log_init(name):
    sessions = os.path.expanduser("~") + "/Sessions"
    out = f"{sessions}/{name}/"
    os.makedirs(out, exist_ok=True)
    filename = f"{out}/build.log"
    #  with open(filename, 'w'):
    #  pass
    print(f"log to: {filename}")

    logging.basicConfig(
        filename=filename, filemode="w", encoding="utf-8", level=logging.INFO
    )
    logging.info(f"Init {name}")


def print_log(txt=""):
    print(txt)
    logging.info(txt)


# time *********************
import datetime
from timeit import default_timer as timer


def elapsed(start_time):
    secs = timer() - start_time
    return str(datetime.timedelta(seconds=secs))

```

## src/geometor/model/wedges.py

```py
"""
wedge functions for Model class
"""

from geometor.model.common import *

from geometor.model.element import (
    Element,
    CircleElement,
    find_all_intersections,
    check_existence,
)


class Wedge:
    def __init__(
        self,
        pt_center: spg.Point,
        pt_radius: spg.Point,
        pt_sweep_start: spg.Point,
        pt_sweep_end: spg.Point,
        direction: str = "clockwise",
    ):
        #  super().__init__(*args)
        self._circle = spg.Circle(pt_center, pt_center.distance(pt_radius))

        self.pt_center = pt_center
        self.pt_radius = pt_radius
        self.sweep_ray = spg.Ray(pt_center, pt_sweep_end)
        self.start_ray = spg.Ray(
            pt_center, pt_sweep_start if pt_sweep_start else radius_point
        )

        self.start_point, self.end_point = self._find_arc_endpoints()
        self.direction = direction

        self.points = [pt_center, pt_radius, pt_sweep_start, pt_sweep_end]

    def _find_arc_endpoints(self) -> tuple[spg.Point, spg.Point]:
        intersections_start = self.circle.intersection(self.start_ray)
        intersections_sweep = self.circle.intersection(self.sweep_ray)

        # Ensure the rays intersect the circle
        if intersections_start and intersections_sweep:
            return intersections_start[0], intersections_sweep[0]
        else:
            raise ValueError("Rays do not intersect the circle.")

    @property
    def circle(self) -> spg.Circle:
        return self._circle

    @property
    def radians(self) -> sp.Expr:
        angle = self.start_ray.angle_between(self.sweep_ray)
        return angle if self.direction == "clockwise" else 2 * sp.pi - angle

    @property
    def degrees(self) -> sp.Expr:
        return sp.deg(self.radians)

    @property
    def ratio(self) -> sp.Expr:
        return self.radians / (2 * sp.pi)

    @property
    def area(self) -> sp.Expr:
        # Using the ratio of the angle to the full circle to find the area
        return self.circle.area * self.ratio

    @property
    def arc_length(self) -> sp.Expr:
        # Using the ratio of the angle to the full circle to find the arc length
        return self.circle.circumference * self.ratio

    @property
    def perimeter(self) -> sp.Expr:
        # Including the two radii to form the full boundary of the wedge
        return self.arc_length + 2 * self.circle.radius


#  def _set_wedge_by_labels(
    #  model, pt_1_label: str, pt_2_label: str, classes: list = None, label: str = ""
#  ) -> Wedge:
    #  """
    #  find points by label and use them with :meth:`Model.construct_line`
    #  """

    #  pt_1 = model.get_element_by_label(pt_1_label)
    #  pt_2 = model.get_element_by_label(pt_2_label)
    #  model.construct_circle(pt_1, pt_2, classes, label)


def _set_wedge(
    model,
    pt_center: spg.Point,
    pt_radius: spg.Point,
    pt_sweep_start: spg.Point,
    pt_sweep_end: spg.Point,
    direction="clockwise",
    classes: list = None,
    label: str = "",
) -> Wedge:
    """
    sets a Wedge from 3 points and adds it to the model.

    operations
    ~~~~~~~~~~
    - create an instance of :class:`geometor.model.Wedge`
    - create a ``details`` object from :class:`Element`
    - add parents to details
        initial parents are the two starting points
    - check for duplicates in in the ``model``
    - find intersection points for new element with all precedng elements
    - Add ``circle`` to the model.

    parameters
    ----------
    - ``pt_center`` : :class:`sympy.geometry.point.Point` : point for circle center
    - ``pt_radius`` : :class:`sympy.geometry.point.Point` : point to mark radius
    - ``pt_end`` : :class:`sympy.geometry.point.Point` : A SymPy Point marking the sweep of the wedge
    - ``classes`` : :class:`list` *optional* : A list of string names for classes defining a set of styles. Defaults to None.
    - ``label`` : :class:`str` *optional* : A text label for use in plotting and reporting. Defaults to an empty string.

    returns
    -------
    - :class:`Wedge`
        The portion of a circle

    example
    -------
        >>> from geometor.elements import *
        >>> model = Model("demo")
        >>> A = model.set_point(0, 0, classes=["given"], label="A")
        >>> B = model.set_point(1, 0, classes=["given"], label="B")
        >>> model.construct_circle(A, B)
        >>> model.construct_circle(B, A)
        >>> model._set_wedge_by_labels('A', 'B', 'C')
        <Wedge object ...>

    notes
    -----
    SymPy defines a circle as a center point and a radius length, so the radius length is calculated for the spg.Circle.

    """

    if classes is None:
        classes = {}
    # find radius length for sympy.Circle
    #  radius_len = pt_center.distance(pt_radius)

    if not isinstance(pt_center, spg.Point) or not isinstance(pt_radius, spg.Point):
        raise TypeError(
            "Both pt_center and pt_radius must be instances of sympy.geometry.point.Point"
        )

    struct = Wedge(pt_center, pt_radius, pt_sweep_start, pt_sweep_end)

    if not label:
        pt_center_label = model[pt_center].label
        pt_radius_label = model[pt_radius].label
        label = f"( {pt_center_label} {pt_radius_label} )"
        label += f"< {model[pt_sweep_start].label} {pt_center_label} {model[pt_sweep_end].label} >"

    details = CircleElement(
        struct,
        parents=[pt_center, pt_radius],
        classes=classes,
        label=label,
        pt_radius=pt_radius,
    )

    model[struct] = details
    console.print(f"[orchid1]{details.label}[/orchid1]")

    return struct

```

