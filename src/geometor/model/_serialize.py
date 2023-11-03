import json
from .common import *
from .element import Element, CircleElement

def _save_to_json(self, file_path):
    serializable_model = {}
    for key, element in self.items():
        serializable_key = str(key)
        serializable_element = {
            'label': element.label,
            'classes': element.classes,
            'parents': str(element.parents)  # or any other serialization approach for parents
        }
        if isinstance(element, CircleElement):
            serializable_element['pt_radius'] = str(element.pt_radius)
        serializable_model[serializable_key] = serializable_element

    print(serializable_model)

    with open(file_path, 'w') as file:
        json.dump(serializable_model, file, indent=4)


@classmethod
def _load_from_json(cls, file_path):
    namespace = {name: getattr(spg, name) for name in dir(spg)}  # Add all SymPy geometry objects to the namespace
    namespace['sqrt'] = sp.sqrt  # Include the sqrt function from SymPy

    with open(file_path, 'r') as file:
        serializable_model = json.load(file)

    model = cls()
    for key, serializable_element in serializable_model.items():
        sympy_obj = eval(key, namespace)
        if 'Circle' in key:
            element = CircleElement(
                sympy_obj=sympy_obj,
                label=serializable_element['label'],
                classes=serializable_element['classes'],
                parents=eval(serializable_element['parents'], namespace),
                pt_radius=eval(serializable_element['pt_radius'], namespace)
            )
        else:
            element = Element(
                sympy_obj=sympy_obj,
                label=serializable_element['label'],
                classes=serializable_element['classes'],
                parents=eval(serializable_element['parents'], namespace)
            )
        model[eval(key, namespace)] = element

    return model
