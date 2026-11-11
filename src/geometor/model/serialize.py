"""Provides JSON serialization (schema v2) and v1/v2 deserialization for :class:`Model`.

Exports models with ``schema_version: 2``, preserving 100% of v1 fields while adding:

- ``symbolic`` metadata dictionaries (exact LaTeX coordinates/quadrances/spreads and
  cached floating-point coordinates for instant frontend/SVG rendering),
- ``pts`` incident-point lists on lines and circles,
- ``markers`` diagrammatic proof annotations (ticks, angle arcs, parallel arrows),
- ``steps`` chronological construction and deductive proof ledger,
- first-class :class:`~geometor.model.invariants.Angle` serialization and restoration.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

import sympy as sp
import sympy.geometry as spg
from sympy.parsing.sympy_parser import parse_expr

from .algebra import clean_expr, fast_line_coeffs
from .element import CircleElement, Element
from .invariants import Angle, quadrance
from .polynomials import Polynomial
from .proof import Step
from .sections import Section
from .wedges import Wedge

if TYPE_CHECKING:
    from geometor.model.model import Model


def _build_symbolic_metadata(obj: Any, element: Element) -> dict[str, Any]:
    """Build compact pre-computed LaTeX and numerical metadata for ``model.json`` v2."""
    if isinstance(element, Polynomial):
        return {
            "kind": "polynomial",
            "degree": element.degree(),
            "latex_eq": sp.latex(element.equation()),
        }
    if isinstance(obj, spg.Point):
        approx = element.approx_coords or (float(obj.x.evalf()), float(obj.y.evalf()))
        return {
            "kind": "point",
            "latex_coords": [sp.latex(obj.x), sp.latex(obj.y)],
            "approx_coords": [approx[0], approx[1]],
        }
    if isinstance(obj, spg.Line):
        a, b, c = fast_line_coeffs(obj)
        if a.count_ops() <= 20 and b.count_ops() <= 20 and c.count_ops() <= 20:
            a, b, c = clean_expr(a), clean_expr(b), clean_expr(c)
        approx = element.approx_coords or (
            float(a.evalf()),
            float(b.evalf()),
            float(c.evalf()),
        )
        return {
            "kind": "line",
            "latex_coeffs": [sp.latex(a), sp.latex(b), sp.latex(c)],
            "approx_coords": list(approx),
        }
    if isinstance(obj, spg.Circle):
        approx = element.approx_coords or (
            float(obj.center.x.evalf()),
            float(obj.center.y.evalf()),
            float(obj.radius.evalf()),
        )
        meta: dict[str, Any] = {
            "kind": "circle",
            "latex_center": [sp.latex(obj.center.x), sp.latex(obj.center.y)],
            "latex_r": sp.latex(obj.radius),
            "approx_coords": list(approx),
        }
        if isinstance(element, CircleElement) and element.pt_radius is not None:
            q_raw = (element.pt_radius.x - obj.center.x) ** 2 + (
                element.pt_radius.y - obj.center.y
            ) ** 2
            q_val = quadrance(obj.center, element.pt_radius) if q_raw.count_ops() <= 20 else q_raw
            meta["latex_quadrance"] = sp.latex(q_val)
        return meta
    if isinstance(obj, spg.Segment):
        q_raw = (obj.p2.x - obj.p1.x) ** 2 + (obj.p2.y - obj.p1.y) ** 2
        q = quadrance(obj) if q_raw.count_ops() <= 20 else q_raw
        return {
            "kind": "segment",
            "latex_quadrance": sp.latex(q),
            "approx_length": float(complex(sp.sqrt(q_raw).evalf()).real),
        }
    if isinstance(obj, spg.Polygon):
        return {
            "kind": "polygon",
            "vertex_count": len(obj.vertices),
        }
    if isinstance(obj, Angle):
        s = obj.spread
        return {
            "kind": "angle",
            "latex_spread": sp.latex(s),
            "dot_sign": obj.dot_sign,
        }
    if isinstance(obj, Section):
        return {
            "kind": "section",
            "latex_ratio": sp.latex(obj.ratio),
            "is_golden": bool(obj.is_golden),
        }
    if isinstance(obj, Wedge):
        return {
            "kind": "wedge",
            "direction": obj.direction,
        }
    return {"kind": type(obj).__name__.lower()}


class SerializeMixin:
    """Mixin for :class:`~geometor.model.Model` providing JSON v2 persistence."""

    def to_dict(self, *, include_symbolic: bool = True) -> dict[str, Any]:
        """Serialize the model into a JSON-compatible dictionary (``schema_version: 2``)."""
        serializable_elements: dict[str, dict[str, Any]] = {}
        for element in self.values():
            if isinstance(element.object, Section):
                points_repr = [sp.srepr(p) for p in element.object.points]
                sympy_obj_repr = f"Section([{', '.join(points_repr)}])"
            elif isinstance(element.object, Wedge):
                points_repr = [sp.srepr(p) for p in element.object.points]
                if element.object.direction != "clockwise":
                    sympy_obj_repr = (
                        f"Wedge([{', '.join(points_repr)}], {element.object.direction!r})"
                    )
                else:
                    sympy_obj_repr = f"Wedge([{', '.join(points_repr)}])"
            elif isinstance(element.object, Angle):
                points_repr = [sp.srepr(p) for p in element.object.points]
                sympy_obj_repr = f"Angle([{', '.join(points_repr)}])"
            else:
                sympy_obj_repr = sp.srepr(element.object)

            element_data: dict[str, Any] = {
                "sympy_obj": sympy_obj_repr,
                "ID": element.ID,
                "classes": list(element.classes),
                "parents": [self[p].ID for p in element.parents if p in self],
                "guide": element.guide,
            }
            if element.pts:
                element_data["pts"] = [self[p].ID for p in element.pts if p in self]
            if element.markers:
                element_data["markers"] = [dict(m) for m in element.markers]
            if isinstance(element, CircleElement):
                element_data["pt_radius"] = self[element.pt_radius].ID
            elif isinstance(element, Polynomial):
                element_data["type"] = "Polynomial"
                element_data["coeffs"] = [sp.srepr(c) for c in element.coeffs]

            if include_symbolic:
                element_data["symbolic"] = _build_symbolic_metadata(element.object, element)

            serializable_elements[element.ID] = element_data

        return {
            "schema_version": 2,
            "name": self.name,
            "use_point_subscript": self.use_point_subscript,
            "last_point_id": self.last_point_id,
            "elements": serializable_elements,
            "steps": [step.to_dict() for step in getattr(self, "steps", [])],
        }

    def save(self, file_path: str | Path, *, include_symbolic: bool = True) -> None:
        """Save the :class:`~geometor.model.Model` to a JSON file."""
        serializable_model = self.to_dict(include_symbolic=include_symbolic)
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(serializable_model, file, indent=4)


def load_model(
    file_path: str | Path,
    logger: logging.Logger | bool | None = None,
) -> Model:
    """Load a ``model.json`` file (v1 or v2) and reconstitute a :class:`~geometor.model.Model`."""
    from geometor.model import Model

    with open(file_path, "r", encoding="utf-8") as file:
        serializable_model = json.load(file)

    model = Model(
        serializable_model.get("name", ""),
        logger=logger,
        use_point_subscript=serializable_model.get("use_point_subscript", False),
    )

    last_point_id = serializable_model.get("last_point_id")
    if last_point_id:
        model.last_point_id = last_point_id
        for ID in model.ID_gen:
            if ID == last_point_id:
                break

    id_to_sympy: dict[str, Any] = {}
    id_to_element_data: dict[str, dict[str, Any]] = {}
    local_dict = {
        "Section": Section,
        "Wedge": Wedge,
        "Angle": Angle,
        "Polynomial": Polynomial,
    }

    raw_elements = serializable_model["elements"]
    elements_iter = (
        raw_elements.values() if isinstance(raw_elements, dict) else raw_elements
    )
    for element_data in elements_iter:
        sympy_obj = parse_expr(element_data["sympy_obj"], local_dict=local_dict)
        id_to_sympy[element_data["ID"]] = sympy_obj
        id_to_element_data[element_data["ID"]] = element_data

    for el_id, element_data in id_to_element_data.items():
        sympy_obj = id_to_sympy[el_id]
        parents = [
            id_to_sympy[p_id]
            for p_id in element_data.get("parents", [])
            if p_id in id_to_sympy
        ]

        if "pt_radius" in element_data:
            pt_radius = id_to_sympy[element_data["pt_radius"]]
            element: Element = CircleElement(
                sympy_obj=sympy_obj,
                ID=element_data["ID"],
                classes=element_data.get("classes", []),
                parents=parents,
                pt_radius=pt_radius,
                guide=element_data.get("guide", False),
            )
        elif element_data.get("type") == "Polynomial":
            coeffs = [parse_expr(c) for c in element_data["coeffs"]]
            element = Polynomial(
                coeffs=coeffs,
                name=element_data["ID"],
                classes=element_data.get("classes", []),
            )
            element.parents = {p: "" for p in parents}
            element.guide = bool(
                element_data.get("guide", False) or "guide" in element.classes
            )
        else:
            element = Element(
                sympy_obj=sympy_obj,
                ID=element_data["ID"],
                classes=element_data.get("classes", []),
                parents=parents,
                guide=element_data.get("guide", False),
            )

        if "pts" in element_data:
            for pt_id in element_data["pts"]:
                if pt_id in id_to_sympy:
                    element.pts[id_to_sympy[pt_id]] = ""
        if "markers" in element_data:
            element.markers = [dict(m) for m in element_data["markers"]]

        super(Model, model).__setitem__(sympy_obj, element)

    raw_steps = serializable_model.get("steps", [])
    model.steps = [Step.from_dict(s) for s in raw_steps]
    for st in model.steps:
        if "tick_group" in st.primitive:
            model._tick_group_counter = max(
                model._tick_group_counter, int(st.primitive["tick_group"])
            )
        if "angle_group" in st.primitive:
            model._angle_group_counter = max(
                model._angle_group_counter, int(st.primitive["angle_group"])
            )
        if "parallel_group" in st.primitive:
            model._parallel_group_counter = max(
                model._parallel_group_counter, int(st.primitive["parallel_group"])
            )

    return model
