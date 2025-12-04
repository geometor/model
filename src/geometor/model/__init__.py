"""
The :mod:`geometor.model` module provides the core data structures and logic for constructing
geometric models in 2D space. It serves as the foundation for the Geometor
project, enabling the creation, manipulation, and analysis of geometric
constructions.

Key Components:
---------------
- **Model**: The central class :class:`Model` representing a collection of geometric elements.
- **Elements**: Wrappers around SymPy geometry objects (:class:`Point`, :class:`Line`, :class:`Circle`, :class:`Polygon`).
- **Mixins**: Modular functionality for the Model class.
- **Analysis**: Tools for analyzing geometric relationships (:class:`Section`, :class:`Chain`, :class:`Wedge`).

Usage:
------
Initialize a :class:`Model` and use its methods to add points, construct lines and circles,
and perform geometric operations.
"""

from __future__ import annotations

__author__ = "geometor"
__maintainer__ = "geometor"
__email__ = "github@geometor.com"
__version__ = "0.4.3"
__licence__ = "MIT"

import sympy.geometry as spg

from geometor.model.element import Element, CircleElement
from geometor.model.wedges import Wedge
from geometor.model.sections import Section
from geometor.model.chains import Chain

# from geometor.model.reports import *

# from collections.abc import Iterator

from geometor.model.polynomials import Polynomial
from geometor.model.serialize import load_model

from geometor.model.model import Model, GeometryObject

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
]
