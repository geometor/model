"""Provides the central :class:`geometor.model.model.Model` class.

This module defines the core `Model` class, which aggregates all geometric construction, analysis, and management functionalities. It serves as the main entry point for creating and manipulating geometric systems.
"""

from __future__ import annotations

import logging

from typing import Callable

import rich
import sympy as sp
import sympy.geometry as spg
from rich.logging import RichHandler

from .ancestors import AncestorsMixin
from .chains import Chain
from .circles import CirclesMixin
from .delete import DeleteMixin
from .element import Element, Struct, _get_element_by_ID
from .lines import LinesMixin
from .points import PointsMixin
from .polygons import PolygonsMixin
from .polynomials import Polynomial, PolynomialsMixin
from .reports import ReportMixin
from .sections import Section, SectionsMixin
from .segments import SegmentsMixin
from .serialize import SerializeMixin
from .wedges import Wedge, WedgesMixin

GeometryObject = (
    spg.Point
    | spg.Line
    | spg.Circle
    | spg.Segment
    | spg.Polygon
    | Wedge
    | Section
    | Chain
    | Polynomial
    | sp.Expr
    | sp.FiniteSet
)

__all__ = ["Model", "GeometryObject"]


class Model(
    dict,
    PointsMixin,
    LinesMixin,
    CirclesMixin,
    PolygonsMixin,
    SegmentsMixin,
    PolynomialsMixin,
    SerializeMixin,
    ReportMixin,
    DeleteMixin,
    SectionsMixin,
    WedgesMixin,
    AncestorsMixin,
):
    """The central class representing a collection of geometric elements.
    
    The Model class is a comprehensive container that inherits from `dict` to store geometric elements mapped to their symbolic representations. It composes multiple mixins to provide a rich feature set, including point plotting, circle/line construction, serialization, reporting, and more.
    """

    def __init__(self, name: str = "", logger: logging.Logger | None = None) -> None:
        """Initialize the Model.
        
        The constructor sets up the model's environment, initializing identifiers, logging, and state containers for points and analysis hooks.

        Args:
            name: The name of the model.
            logger: An optional logger instance. If None, a default logger is created.
        """
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
        self._poly_count = 0

    def log(self, message: object) -> None:
        if self._logger:
            if hasattr(message, "__rich_console__"):
                rich.print(message)
            else:
                self._logger.info(message)

    def set_analysis_hook(self, hook_function: Callable) -> None:
        self._analysis_hook = hook_function

    @property
    def new_points(self) -> list[spg.Point]:
        """The new_points of the model."""
        return self._new_points

    def clear_new_points(self) -> None:
        self._new_points = []

    @property
    def name(self) -> str:
        """The name of the model."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    def __setitem__(self, key: GeometryObject, value: Element) -> None:
        """Set an item in the model, enforcing type checks.
        
        This override of the dictionary setter ensures type safety for the model. It validates that keys are recognized GeometryObjects and values are Element wrappers, maintaining the integrity of the model's storage.

        Args:
            key: The geometric object (GeometryObject).
            value: The element wrapper (Element).

        Raises:
            TypeError: If key or value are not of the expected types.
        """
        if not isinstance(key, GeometryObject):
            raise TypeError(f"{key=} must be an instance of GeometryObject")
        if not isinstance(value, Element):
            raise TypeError(f"{ value= } must be an instance of Element class")
        super().__setitem__(key, value)

    def remove_by_ID(self, ID: str) -> None:
        el = self.get_element_by_ID(ID)
        del self[el]

    @property
    def points(self) -> list[spg.Point]:
        """Returns point elements from model as list."""
        return [el for el in self if isinstance(el, spg.Point)]

    @property
    def structs(self) -> list[Struct]:
        """Returns struct elements (line or circle) from model as list."""
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
        """Returns line elements from model as list."""
        return [el for el in self if isinstance(el, spg.Line)]

    @property
    def circles(self) -> list[spg.Circle]:
        """Returns circle elements from model as list."""
        return [el for el in self if isinstance(el, spg.Circle)]

    def limits(self) -> tuple[tuple[float, float], tuple[float, float]]:
        """Find x, y limits from points and circles of the model.
        
        This method calculates the bounding box of all geometric elements currently in the model. It iterates through points and circles (accounting for radii) to determine the minimum and maximum coordinates.

        Returns:
            tuple: A tuple containing ((min_x, max_x), (min_y, max_y)).

        Raises:
            ValueError: If the model contains no geometric elements.
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

    get_element_by_ID = _get_element_by_ID
