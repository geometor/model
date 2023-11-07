"""
This module provides the `Model` class, which is used to represent a geometric model
in 2D space. The `Model` class is based on the `list` data structure, and can contain
points, lines, circles, polygons, and segments.
"""

from .common import *

from .utils import *

from .element import (
    Element,
    _get_ancestors,
    _get_ancestors_labels,
    _get_element_by_label,
)
from ._points import _set_point
from ._lines import _construct_line, _construct_line_by_labels
from ._circles import (
    _construct_circle,
    _construct_circle_by_labels,
)
from ._polygons import _set_polygon, _set_polygon_by_labels
from ._segments import _set_segment
from ._wedges import Wedge, _set_wedge, _set_wedge_by_labels

from ._serialize import _save_to_json, _load_from_json

#  from .reports import *


class Model(dict):
    """
    A collection of geometric elements, including points, lines, circles, and
    polygons, represented using the `sympy.geometry` library.

    When lines and circles are added to the model, intersection points of the
    new element with the preceding elements are identify and added.

    When new elements or points are added to the model, we check for existing
    duplicates.

    parameters:
        ``name`` : :class:`str`
            establish name for the model instance

    attributes:
        :attr:`name` : :class:`str`
            name of the model
        :attr:`points` : :class:`list`
            returns list of points in the Model
        :attr:`lines` : :class:`list`
            returns list of lines in the Model
        :attr:`circles` : :class:`list`
            returns list of circles in the Model
        :attr:`structs` : :class:`list`
            returns list of structs (lines and circles) in the Model

    methods:
        :meth:`set_point` : :class:`Point <sympy.geometry.point.Point>`
            - set point from x, y expressions
            - add to model if unique
            - coordinate metadata
        :meth:`construct_line` : :class:`Line <sympy.geometry.line.Line>`
            - construct line from two points
            - add to model if unique
            - coordinate meta data
            - find intersections with other structs
        :meth:`construct_circle` : :class:`Circle <sympy.geometry.ellipse.Circle>`
            - construct line from two points
            - add to model if unique
            - coordinate meta data
            - find intersections with other structs
        :meth:`set_segment` : :class:`Segment <sympy.geometry.line.Segment>`
            - set segment from two points
            - coordinate meta data
        :meth:`set_polygon` : :class:`Polygon <sympy.geometry.polygon.Polygon>`
            - set polygon from list of points
            - coordinate meta data
        :meth:`limits` : :class:`list`
            returns the x, y limits of the points and circle boundaries in the model

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

    # Override set_item to enforce Element type for values
    def __setitem__(self, key, value: Element):
        """
        control types for keys and values
        parameters:
            ``key`` : :class:`spg.entity` or custom objects like Wedge
                the geometric element object
            ``value`` : :class:`Element`
                side car object with info about the geometric object
        """
        if not isinstance(value, Element):
            raise TypeError("value must be an instance of Element class")
        super().__setitem__(key, value)

    set_point = _set_point

    construct_line = _construct_line
    construct_line_by_labels = _construct_line_by_labels

    construct_circle = _construct_circle
    construct_circle_by_labels = _construct_circle_by_labels

    set_segment = _set_segment
    # TODO: set_segment_by_labels

    set_polygon = _set_polygon
    set_polygon_by_labels = _set_polygon_by_labels

    set_wedge = _set_wedge
    set_wedge_by_labels = _set_wedge_by_labels

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
    def structs(self) -> list[spg.Line | spg.Circle]:
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
    def circles(self) -> list:
        """
        returns circle elements from model as list
        """
        return [el for el in self if isinstance(el, spg.Circle)]

    def limits(self) -> list[list[float, float], list[float, float]]:
        """
        Find x, y limits from points and circles of the model

        Returns a list of x, y limits:
            ``[[x_min, x_max], [y_min, y_max]]``
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

    def point_label_generator(self):
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