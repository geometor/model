import json
from sympy.parsing.sympy_parser import parse_expr
from .common import *
from .element import Element, CircleElement

def _save_to_json(self, file_path):
    """
    Saves the model to a JSON file in a structured and secure format.

    This method serializes the model into a JSON file with two main sections:
    "sympy_objects" and "elements".

    - "sympy_objects": A list of all geometric objects in the model, serialized
      to strings using `sympy.srepr`. This provides a safe and unambiguous
      representation of the objects.

    - "elements": A list of dictionaries, each containing the metadata for an
      element (label, classes, parents). The parents are represented by their
      indices in the "sympy_objects" list, creating a relational mapping that
      can be safely reconstructed.

    This approach avoids the use of `eval` and ensures that the model can be
    saved and loaded without loss of information.
    """
    sympy_objects = list(self.keys())
    obj_to_index = {obj: i for i, obj in enumerate(sympy_objects)}

    serializable_elements = []
    for obj in sympy_objects:
        element = self[obj]
        element_data = {
            'label': element.label,
            'classes': list(element.classes.keys()),
            'parents': [obj_to_index[p] for p in element.parents.keys()],
        }
        if isinstance(element, CircleElement):
            element_data['pt_radius'] = obj_to_index[element.pt_radius]
        serializable_elements.append(element_data)

    serializable_model = {
        'name': self.name,
        'sympy_objects': [sp.srepr(obj) for obj in sympy_objects],
        'elements': serializable_elements,
    }

    with open(file_path, 'w') as file:
        json.dump(serializable_model, file, indent=4)

def _load_from_json(self, file_path):
    """
    Loads a model from a JSON file that was saved with `_save_to_json`.

    This method reads a JSON file, parses the "sympy_objects" back into SymPy
    objects using `sympy.parsing.sympy_parser.parse_expr`, and then
    reconstructs the model by linking the elements to their parents using the
    stored indices.

    This approach is secure as it avoids the use of `eval`.
    """
    with open(file_path, 'r') as file:
        serializable_model = json.load(file)

    self.name = serializable_model.get('name', '')
    
    sympy_objects = [parse_expr(s) for s in serializable_model['sympy_objects']]

    for i, element_data in enumerate(serializable_model['elements']):
        sympy_obj = sympy_objects[i]
        parents = [sympy_objects[j] for j in element_data['parents']]
        
        if 'pt_radius' in element_data:
            pt_radius = sympy_objects[element_data['pt_radius']]
            element = CircleElement(
                sympy_obj=sympy_obj,
                label=element_data['label'],
                classes=element_data['classes'],
                parents=parents,
                pt_radius=pt_radius
            )
        else:
            element = Element(
                sympy_obj=sympy_obj,
                label=element_data['label'],
                classes=element_data['classes'],
                parents=parents
            )
        self[sympy_obj] = element
    
    return self