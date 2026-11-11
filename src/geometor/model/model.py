"""Provides the central :class:`geometor.model.model.Model` class.

This module defines the core `Model` class, which aggregates all geometric construction,
targeted Euclidean intersection, rational-trigonometry invariant verification, and JSON v2
serialization capabilities.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Callable

import rich
import sympy as sp
import sympy.geometry as spg
from rich.logging import RichHandler

from .ancestors import AncestorsMixin
from .chains import Chain
from .circles import CirclesMixin
from .delete import DeleteMixin
from .element import Element, Struct, _get_element_by_ID
from .intersections import IntersectionsMixin, SubconstructionScope
from .invariants import Angle, AnglesMixin
from .lines import LinesMixin
from .points import PointsMixin
from .polygons import PolygonsMixin
from .polynomials import Polynomial, PolynomialsMixin
from .proof import ProofMixin, Step
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
    | Angle
    | Wedge
    | Section
    | Chain
    | Polynomial
    | sp.Expr
    | sp.FiniteSet
)

__all__ = ["GeometryObject", "Model"]


class Model(
    dict,
    PointsMixin,
    LinesMixin,
    CirclesMixin,
    IntersectionsMixin,
    PolygonsMixin,
    SegmentsMixin,
    AnglesMixin,
    ProofMixin,
    PolynomialsMixin,
    SerializeMixin,
    ReportMixin,
    DeleteMixin,
    SectionsMixin,
    WedgesMixin,
    AncestorsMixin,
):
    """The central class representing an exact symbolic geometric construction and proof."""

    def __init__(
        self,
        name: str = "",
        logger: logging.Logger | bool | None = None,
        use_point_subscript: bool = False,
        *,
        auto_intersect: bool = True,
        use_multiprocessing: bool = False,
        enable_logging: bool | None = None,
    ) -> None:
        """Initialize the Model.

        Args:
            name: The name of the model.
            logger: Optional logger instance, ``False`` to disable logging completely, or
                ``None`` to create a default Rich-configured logger.
            use_point_subscript: If True, generate point labels with subscripts (e.g., ``A2``)
                instead of repeating letters (e.g., ``AA``).
            auto_intersect: If True (default), constructing a non-guide line or circle
                automatically computes intersections with eligible structures. Set ``False``
                for explicit 3-Act constructions using :meth:`intersect`.
            use_multiprocessing: If True, offload large auto-intersection batches (>= 64
                structures) to a process pool. Defaults to ``False`` because closed-form
                in-process 2D algebra is significantly faster than process IPC.
            enable_logging: Optional explicit override to enable or silence console/logger output.
        """
        super().__init__()
        self._name = name
        if logger is False or enable_logging is False:
            self._logger: logging.Logger | None = None
            self._logging_enabled = False
        elif isinstance(logger, logging.Logger):
            self._logger = logger
            self._logging_enabled = True if enable_logging is None else bool(enable_logging)
        else:
            self._logger = logging.getLogger(f"geometor.model.{name}")
            self._logger.setLevel(logging.INFO)
            if not self._logger.handlers:
                self._logger.addHandler(RichHandler(markup=True))
            self._logging_enabled = True if enable_logging is None else bool(enable_logging)

        self.use_point_subscript = use_point_subscript
        self.auto_intersect = auto_intersect
        self.use_multiprocessing = use_multiprocessing
        self.ID_gen = self.point_ID_generator()
        self.last_point_id = ""
        self._analysis_hook: Callable | None = None
        self._simplifier: Callable[[sp.Expr], sp.Expr] | None = None
        self._new_points: list[spg.Point] = []
        self._poly_count = 0
        self.steps: list[Step] = []
        self._scope_stack: list[SubconstructionScope] = []
        self._tick_group_counter = 0
        self._angle_group_counter = 0
        self._parallel_group_counter = 0

    @property
    def is_logging_enabled(self) -> bool:
        """Return ``True`` only when INFO messages have at least one active non-null handler."""
        if not self._logging_enabled or self._logger is None:
            return False
        if not self._logger.isEnabledFor(logging.INFO):
            return False
        curr: logging.Logger | None = self._logger
        while curr is not None:
            for handler in curr.handlers:
                if not isinstance(handler, logging.NullHandler):
                    return True
            if not curr.propagate:
                break
            curr = curr.parent
        return False

    def log(self, message: object) -> None:
        """Log a message to the model's logger or print if it's a Rich renderable."""
        if not self.is_logging_enabled or self._logger is None:
            return
        if hasattr(message, "__rich_console__"):
            rich.print(message)
        else:
            self._logger.info(message)

    def set_analysis_hook(self, hook_function: Callable | None) -> None:
        """Set a hook function to be called during analysis/point addition."""
        self._analysis_hook = hook_function

    def set_simplifier(
        self, simplifier_function: Callable[[sp.Expr], sp.Expr] | None
    ) -> None:
        """Set an optional custom symbolic simplifier for point coordinates."""
        self._simplifier = simplifier_function

    @property
    def new_points(self) -> list[spg.Point]:
        """The points added since the most recent ``clear_new_points()``."""
        return self._new_points

    def clear_new_points(self) -> None:
        """Clear the list of newly added points."""
        self._new_points = []

    @property
    def name(self) -> str:
        """The name of the model."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    def __setitem__(self, key: GeometryObject, value: Element) -> None:
        """Set an item in the model, enforcing type checks."""
        if not isinstance(key, GeometryObject):
            raise TypeError(f"{key=} must be an instance of GeometryObject")
        if not isinstance(value, Element):
            raise TypeError(f"{ value= } must be an instance of Element class")
        super().__setitem__(key, value)

    def remove_by_ID(self, ID: str) -> None:
        """Remove a geometric element from the model by its ID."""
        el = self.get_element_by_ID(ID)
        del self[el]

    @property
    def points(self) -> list[spg.Point]:
        """Return point elements from the model as a list."""
        return [el for el in self if isinstance(el, spg.Point)]

    @property
    def structs(self) -> list[Struct]:
        """Return non-guide structural elements (lines or circles) from the model."""
        return [
            el
            for el in self
            if isinstance(el, (spg.Line, spg.Circle))
            and not self[el].guide
            and "guide" not in self[el].classes
        ]

    @property
    def lines(self) -> list[spg.Line]:
        """Return line elements from the model as a list."""
        return [el for el in self if isinstance(el, spg.Line)]

    @property
    def circles(self) -> list[spg.Circle]:
        """Return circle elements from the model as a list."""
        return [el for el in self if isinstance(el, spg.Circle)]

    @property
    def segments(self) -> list[spg.Segment]:
        """Return segment elements from the model as a list."""
        return [el for el in self if isinstance(el, spg.Segment)]

    @property
    def polygons(self) -> list[spg.Polygon]:
        """Return polygon elements from the model as a list."""
        return [el for el in self if isinstance(el, spg.Polygon)]

    def limits(self) -> list[list[float]]:
        """Find ``[[min_x, max_x], [min_y, max_y]]`` limits from points and circles."""
        x_vals: list[float] = []
        y_vals: list[float] = []

        for el, details in self.items():
            if isinstance(el, spg.Point):
                approx = details.approx_coords
                if approx is not None:
                    x_vals.append(approx[0])
                    y_vals.append(approx[1])
                else:
                    x_vals.append(float(el.x))
                    y_vals.append(float(el.y))

            elif isinstance(el, spg.Circle):
                approx = details.approx_coords
                if approx is not None:
                    cx, cy, r = approx
                    x_vals.extend([cx - r, cx + r])
                    y_vals.extend([cy - r, cy + r])
                else:
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

    def parse_command(self, command: str) -> None:
        """Parse and execute a single command string."""
        command = command.strip()
        if not command:
            return

        # Point: A = 0, 0
        point_match = re.match(
            r"^([A-Za-z0-9_]+)\s*=\s*([-\d\.]+)\s*,\s*([-\d\.]+)(?:\s+(.*))?$", command
        )
        if point_match:
            label, x, y, _ = point_match.groups()
            self.set_point(float(x), float(y), ID=label, classes=["given"])
            return

        # Auto-Label Point: * 0, 0
        auto_point_match = re.match(
            r"^\*\s*([-\d\.]+)\s*,\s*([-\d\.]+)(?:\s+(.*))?$", command
        )
        if auto_point_match:
            x, y, _ = auto_point_match.groups()
            self.set_point(float(x), float(y), classes=["given"])
            return

        # Line: [ A B ]
        line_match = re.match(r"^\[\s*([A-Za-z0-9_]+)\s+([A-Za-z0-9_]+)\s*\]$", command)
        if line_match:
            pt1, pt2 = line_match.groups()
            self.construct_line_by_IDs(pt1, pt2)
            return

        # Circle: ( A B )
        circle_match = re.match(
            r"^\(\s*([A-Za-z0-9_]+)\s+([A-Za-z0-9_]+)\s*\)$", command
        )
        if circle_match:
            pt1, pt2 = circle_match.groups()
            self.construct_circle_by_IDs(pt1, pt2)
            return

        # Polygon: < A B C >
        if match := re.match(r"^<\s*([A-Za-z0-9\s]+?)\s*>$", command):
            pts = match.group(1).split()
            if len(pts) >= 3:
                self.set_polygon_by_IDs(pts)
            else:
                raise ValueError("Polygon requires at least 3 points")
            return

        # Linear Division: / A B ... /
        if match := re.match(r"^/\s*([A-Za-z0-9\s]+?)\s*/$", command):
            pts = match.group(1).split()
            if len(pts) == 2:
                self.set_segment_by_IDs(pts[0], pts[1])
            elif len(pts) == 3:
                self.set_section_by_IDs(pts)
            else:
                raise ValueError(
                    "Linear division requires 2 or 3 points (Segment or Section)"
                )
            return

        # Wedge: < A B E )
        if match := re.match(r"^<\s*([A-Za-z0-9\s]+?)\s*\)$", command):
            pts = match.group(1).split()
            if len(pts) == 3:
                self.set_wedge_by_IDs(pts[0], pts[1], pts[1], pts[2])
            else:
                raise ValueError("Wedge requires 3 points: < Center Radius SweepEnd )")
            return

        raise ValueError(f"Unknown command: {command}")
