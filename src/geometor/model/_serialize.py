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
            'label': element.label,
            'classes': list(element.classes.keys()),
            'parents': [obj_to_index[p] for p in element.parents.keys()],
        }
        if isinstance(element, CircleElement):
            element_data['pt_radius'] = obj_to_index[element.pt_radius]
        serializable_elements.append(element_data)

    # Capture the next label from the generator
    # This is a bit of a hack; we generate the next label and then have to prepend it
    # to the generator sequence when we load. A better way might be to store the
    # generator's state, but that's more complex.
    next_label = next(model.label_gen)

    serializable_model = {
        'name': model.name,
        'next_label': next_label,
        'sympy_objects': [sp.srepr(obj) for obj in sympy_objects],
        'elements': serializable_elements,
    }

    with open(file_path, 'w') as file:
        json.dump(serializable_model, file, indent=4)


def load_model(file_path):
    """
    Loads a model from a JSON file and returns a new Model instance.
    """
    # Import Model here to avoid circular dependency
    from geometor.model import Model

    with open(file_path, 'r') as file:
        serializable_model = json.load(file)

    model = Model(serializable_model.get('name', ''))
    
    # Restore the label generator state
    next_label = serializable_model.get('next_label')
    if next_label:
        # This is a bit of a trick. We need to effectively "put back" the saved
        # next_label into the generator sequence.
        from itertools import chain
        model.label_gen = chain([next_label], model.label_gen)
    
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
        model[sympy_obj] = element
    
    return model
