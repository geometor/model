import json
from sympy.parsing.sympy_parser import parse_expr
import sympy as sp
from .common import *
from .element import Element, CircleElement
from .sections import Section
from .wedges import Wedge

def save_model(model, file_path):
    """
    Saves a Model object to a JSON file as a list of elements.
    """
    serializable_elements = []
    for element in model.values():
        if isinstance(element.object, Section):
            points_repr = [sp.srepr(p) for p in element.object.points]
            sympy_obj_repr = f"Section([{', '.join(points_repr)}])"
        elif isinstance(element.object, Wedge):
            points_repr = [sp.srepr(p) for p in element.object.points]
            sympy_obj_repr = f"Wedge([{', '.join(points_repr)}])"
        else:
            sympy_obj_repr = sp.srepr(element.object)

        element_data = {
            'sympy_obj': sympy_obj_repr,
            'ID': element.ID,
            'classes': list(element.classes),
            'parents': [model[p].ID for p in element.parents.keys()],
            'guide': element.guide,
        }
        if isinstance(element, CircleElement):
            element_data['pt_radius'] = model[element.pt_radius].ID
        serializable_elements.append(element_data)

    serializable_model = {
        'name': model.name,
        'last_point_id': model.last_point_id,
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
    
    id_to_sympy = {}
    id_to_element_data = {}
    local_dict = {'Section': Section, 'Wedge': Wedge}

    # First pass: create all sympy objects and map them by ID
    for element_data in serializable_model['elements']:
        sympy_obj = parse_expr(element_data['sympy_obj'], local_dict=local_dict)
        id_to_sympy[element_data['ID']] = sympy_obj
        id_to_element_data[element_data['ID']] = element_data

    # Second pass: create elements and link parents
    for id, element_data in id_to_element_data.items():
        sympy_obj = id_to_sympy[id]
        parents = [id_to_sympy[p_id] for p_id in element_data['parents']]
        
        if 'pt_radius' in element_data:
            pt_radius = id_to_sympy[element_data['pt_radius']]
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
