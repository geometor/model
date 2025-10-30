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
__version__ = "0.3.2"
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
    _get_ancestors_IDs,
    _get_element_by_ID,
)

from geometor.model._points import _set_point
from geometor.model._lines import _construct_line, _construct_line_by_IDs
from geometor.model._circles import (
    _construct_circle,
    _construct_circle_by_IDs,
)
from geometor.model._polygons import _set_polygon, _set_polygon_by_IDs
from geometor.model._segments import _set_segment, _set_segment_by_IDs
from geometor.model.sections import Section, _set_section, _set_section_by_IDs

from geometor.model.wedges import Wedge, _set_wedge # _set_wedge_by_labels
from geometor.model.sections import *
from geometor.model.chains import *

from geometor.model._serialize import save_model, load_model
from geometor.model._delete import delete_element, get_dependents

GeometryObject = (
    spg.Point
    | spg.Line
    | spg.Circle
    | spg.Segment
    | spg.Polygon
    | Wedge
    | Section
    | Chain
    | sp.FiniteSet
)


import logging
from rich.logging import RichHandler
import rich

class Model(dict):
    """
    A collection of geometric elements, including points, lines, circles, and
    polygons, represented using the `sympy.geometry` library.
    """

    def __init__(self, name: str = "", logger=None):
        super().__init__()
        self._name = name
        if logger:
            self._logger = logger
        else:
            self._logger = logging.getLogger(f"geometor.model.{name}")
            self._logger.setLevel(logging.INFO)
            if not self._logger.handlers:
                self._logger.addHandler(RichHandler(markup=True))

        self.ID_gen = self.point_ID_generator()
        self.last_point_id = ""
        self._analysis_hook = None
        self._new_points = []

    def log(self, message):
        if self._logger:
            if hasattr(message, '__rich_console__'):
                rich.print(message)
            else:
                self._logger.info(message)

    def set_analysis_hook(self, hook_function):
        self._analysis_hook = hook_function

    @property
    def new_points(self) -> list[spg.Point]:
        """The new_points of the model"""
        return self._new_points

    def clear_new_points(self):
        self._new_points = []

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
        """
        if not isinstance(key, GeometryObject):
            raise TypeError(f"{key=} must be an instance of Element class")
        if not isinstance(value, Element):
            raise TypeError(f"{ value= } must be an instance of Element class")
        super().__setitem__(key, value)

    set_point = _set_point

    construct_line = _construct_line
    construct_line_by_IDs = _construct_line_by_IDs

    construct_circle = _construct_circle
    construct_circle_by_IDs = _construct_circle_by_IDs

    set_segment = _set_segment
    set_segment_by_IDs = _set_segment_by_IDs

    set_section = _set_section
    set_section_by_IDs = _set_section_by_IDs

    set_polygon = _set_polygon
    set_polygon_by_IDs = _set_polygon_by_IDs

    set_wedge = _set_wedge

    delete_element = delete_element
    get_dependents = get_dependents

    def remove_by_ID(self, ID: str) -> None:
        el = self.get_element_by_ID(ID)
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
    get_ancestors_IDs = _get_ancestors_IDs

    get_element_by_ID = _get_element_by_ID


    def point_ID_generator(self) -> Iterator[str]:
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        repeat = 1

        while True:
            for letter in letters:
                yield str(letter) * repeat
            repeat += 1