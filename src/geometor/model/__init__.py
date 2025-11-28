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
__version__ = "0.4.2"
__licence__ = "MIT"

import sympy.geometry as spg

Point = spg.Point
Line = spg.Line
Circle = spg.Circle
Polygon = spg.Polygon
Segment = spg.Segment

from geometor.model.element import *
from geometor.model.wedges import Wedge
from geometor.model.sections import Section
from geometor.model.chains import Chain

from geometor.model.reports import *

from collections.abc import Iterator



from geometor.model.polynomials import Polynomial
from geometor.model.serialize import load_model

from .model import Model, GeometryObject

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
    "GeometryObject",
    "load_model",
]