"""Provides the core symbolic data structures, Euclidean construction kernel, and
rational-trigonometry proof verifier for 2D constructive geometry in GEOMETOR.

Everything centers around :class:`Model`.
"""

from __future__ import annotations

__version__ = "0.5.7"

from geometor.model.algebra import (
    canonicalize_golden,
    canonicalize_kepler,
    clean_expr,
    exact_sign,
    get_algebraic_field,
    get_golden_field,
    get_kepler_field,
    reduce_in_field,
    zero_test,
)
from geometor.model.intersections import (
    ConstructionError,
    SubconstructionScope,
    intersect_2d,
    proposition,
)
from geometor.model.invariants import (
    Angle,
    cross,
    cross_ratio,
    is_harmonic,
    line_spread,
    orientation,
    quadrance,
    vertex_spread,
)
from geometor.model.model import GeometryObject, Model
from geometor.model.proof import ProofAssertionError, Step
from geometor.model.serialize import load_model

__all__ = [
    "Angle",
    "ConstructionError",
    "GeometryObject",
    "Model",
    "ProofAssertionError",
    "Step",
    "SubconstructionScope",
    "canonicalize_golden",
    "canonicalize_kepler",
    "clean_expr",
    "cross",
    "cross_ratio",
    "exact_sign",
    "get_algebraic_field",
    "get_golden_field",
    "get_kepler_field",
    "intersect_2d",
    "is_harmonic",
    "line_spread",
    "load_model",
    "orientation",
    "proposition",
    "quadrance",
    "reduce_in_field",
    "vertex_spread",
    "zero_test",
]
