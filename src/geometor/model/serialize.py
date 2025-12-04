"""
The :mod:`geometor.model.serialize` module provides serialization functions for the Model class.
"""

import json
from typing import TYPE_CHECKING

import sympy as sp
from sympy.parsing.sympy_parser import parse_expr

from .element import CircleElement, Element
from .polynomials import Polynomial
from .sections import Section
from .wedges import Wedge

if TYPE_CHECKING:
    pass


class SerializeMixin:
    """
    Mixin for the Model class containing serialization operations.
    """

    def save(self, file_path):
        """
        Saves a Model object to a JSON file as a list of elements.
        """
        serializable_elements = []
        for element in self.values():
            if isinstance(element.object, Section):
                points_repr = [sp.srepr(p) for p in element.object.points]
                sympy_obj_repr = f"Section([{', '.join(points_repr)}])"
            elif isinstance(element.object, Wedge):
                points_repr = [sp.srepr(p) for p in element.object.points]
                sympy_obj_repr = f"Wedge([{', '.join(points_repr)}])"
            else:
                sympy_obj_repr = sp.srepr(element.object)

            element_data = {
                "sympy_obj": sympy_obj_repr,
                "ID": element.ID,
                "classes": list(element.classes),
                "parents": [self[p].ID for p in element.parents.keys()],
                "guide": element.guide,
            }
            if isinstance(element, CircleElement):
                element_data["pt_radius"] = self[element.pt_radius].ID
            elif isinstance(element, Polynomial):
                element_data["type"] = "Polynomial"
                element_data["coeffs"] = [sp.srepr(c) for c in element.coeffs]
            serializable_elements.append(element_data)

        serializable_model = {
            "name": self.name,
            "last_point_id": self.last_point_id,
            "elements": serializable_elements,
        }

        with open(file_path, "w") as file:
            json.dump(serializable_model, file, indent=4)


def load_model(file_path, logger=None):
    """
    Loads a model from a JSON file and returns a new Model instance.
    """
    # Import Model here to avoid circular dependency
    from geometor.model import Model

    with open(file_path, "r") as file:
        serializable_model = json.load(file)

    model = Model(serializable_model.get("name", ""), logger=logger)

    # Restore the ID generator state
    last_point_id = serializable_model.get("last_point_id")
    if last_point_id:
        model.last_point_id = last_point_id
        # Advance the generator to the correct position.
        for ID in model.ID_gen:
            if ID == last_point_id:
                break

    id_to_sympy = {}
    id_to_element_data = {}
    local_dict = {"Section": Section, "Wedge": Wedge, "Polynomial": Polynomial}

    # First pass: create all sympy objects and map them by ID
    for element_data in serializable_model["elements"]:
        sympy_obj = parse_expr(element_data["sympy_obj"], local_dict=local_dict)
        id_to_sympy[element_data["ID"]] = sympy_obj
        id_to_element_data[element_data["ID"]] = element_data

    # Second pass: create elements and link parents
    for id, element_data in id_to_element_data.items():
        sympy_obj = id_to_sympy[id]
        parents = [id_to_sympy[p_id] for p_id in element_data["parents"]]

        if "pt_radius" in element_data:
            pt_radius = id_to_sympy[element_data["pt_radius"]]
            element = CircleElement(
                sympy_obj=sympy_obj,
                ID=element_data["ID"],
                classes=element_data["classes"],
                parents=parents,
                pt_radius=pt_radius,
                guide=element_data.get("guide", False),
            )
        elif element_data.get("type") == "Polynomial":
            coeffs = [parse_expr(c) for c in element_data["coeffs"]]
            element = Polynomial(
                coeffs=coeffs, name=element_data["ID"], classes=element_data["classes"]
            )
            # Polynomial __init__ creates a new Poly object, but we want to ensure it matches the saved one
            # The parents are not directly used in Polynomial __init__ but Element stores them
            # We need to manually set parents if they exist (Polynomials might not have parents in the same way)
            element.parents = {p: "" for p in parents}
            element.guide = element_data.get("guide", False)
        else:
            element = Element(
                sympy_obj=sympy_obj,
                ID=element_data["ID"],
                classes=element_data["classes"],
                parents=parents,
                guide=element_data.get("guide", False),
            )
        # Bypass the custom __setitem__ to avoid triggering intersection searches
        super(Model, model).__setitem__(sympy_obj, element)

    return model
