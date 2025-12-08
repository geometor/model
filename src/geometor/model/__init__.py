"""provides the core data structures and logic for constructing geometric models in 2D space.

everything centers around :class:`Model`
"""

from __future__ import annotations

__version__ = "0.4.6"

from geometor.model.serialize import load_model
from geometor.model.model import GeometryObject, Model

__all__ = [
    "Model",
    "GeometryObject",
    "load_model",
]

""" import sympy.geometry as spg

from geometor.model.chains import Chain
from geometor.model.element import CircleElement, Element
from geometor.model.polynomials import Polynomial
from geometor.model.sections import Section
from geometor.model.wedges import Wedge

Point = spg.Point
Line = spg.Line
Circle = spg.Circle
Polygon = spg.Polygon
Segment = spg.Segment

__all__ = [
    "Model",
    "Point",
    "Line",
    "Circle",
    "Polygon",
    "Segment",
    "Wedge",
    "Section",
    "Chain",
    "Polynomial",
    "Element",
    "CircleElement",
    "GeometryObject",
    "load_model",
] """
