import json
from sympy.parsing.sympy_parser import parse_expr
import sympy as sp
from .common import *
from .element import Element, CircleElement

def save_model(model, file_path):
    """
    Saves a Model object to a JSON file.
    """
    sympy_objects = list(model.keys())
    obj_to_index = {obj: i for i, obj in enumerate(sympy_objects)}

    serializable_elements = []
    for obj in sympy_objects:
        element = model[obj]
        element_data = {
            'ID': element.ID,
            'classes': list(element.classes.keys()),
            'parents': [obj_to_index[p] for p in element.parents.keys()],
            'guide': element.guide,
        }
        if isinstance(element, CircleElement):
            element_data['pt_radius'] = obj_to_index[element.pt_radius]
        serializable_elements.append(element_data)

    serializable_model = {
        'name': model.name,
        'last_point_id': model.last_point_id,
        'sympy_objects': [sp.srepr(obj) for obj in sympy_objects],
        'elements': serializable_elements,
    }

    with open(file_path, 'w') as file:
        json.dump(serializable_model, file, indent=4)


def load_model(file_path, logger=None):
    """
    Loads a model from a JSON file and returns a new Model instance.
    """
    # Import Model here to avoid circular dependency
    from geometor.model import Model

    with open(file_path, 'r') as file:
        serializable_model = json.load(file)

    model = Model(serializable_model.get('name', ''), logger=logger)
    
    # Restore the ID generator state
    last_point_id = serializable_model.get('last_point_id')
    if last_point_id:
        model.last_point_id = last_point_id
        # Advance the generator to the correct position.
        for ID in model.ID_gen:
            if ID == last_point_id:
                break
    
    sympy_objects = [parse_expr(s) for s in serializable_model['sympy_objects']]

    for i, element_data in enumerate(serializable_model['elements']):
        sympy_obj = sympy_objects[i]
        parents = [sympy_objects[j] for j in element_data['parents']]
        
        if 'pt_radius' in element_data:
            pt_radius = sympy_objects[element_data['pt_radius']]
            element = CircleElement(
                sympy_obj=sympy_obj,
                ID=element_data['ID'],
                classes=element_data['classes'],
                parents=parents,
                pt_radius=pt_radius,
                guide=element_data.get('guide', False)
            )
        else:
            element = Element(
                sympy_obj=sympy_obj,
                ID=element_data['ID'],
                classes=element_data['classes'],
                parents=parents,
                guide=element_data.get('guide', False)
            )
        # Bypass the custom __setitem__ to avoid triggering intersection searches
        super(Model, model).__setitem__(sympy_obj, element)
    
    return model
