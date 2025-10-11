"""
Browser-specific serialization for the Model class.
"""
from .common import *
from .sections import Section
from .chains import Chain
from .wedges import Wedge

def to_browser_dict(self):
    """
    Serializes the model to a dictionary format suitable for a browser-based
    application, preserving the order of creation.

    This method creates a dictionary containing the model's name and a single
    list of 'elements'. Each item in the list represents a geometric element
    in the order it was added to the model. This format is easy for a web
    client to parse and render sequentially.

    Each element dictionary includes:
    - A 'type' field (e.g., 'point', 'line').
    - Data relevant to the element type, including floating-point values for
      rendering and LaTeX expressions for display.
    """
    browser_elements = []

    for el, data in self.items():
        # Skip elements without a label, as they cannot be referenced
        if not data.label:
            continue

        element_dict = {
            'label': data.label,
            'classes': list(data.classes.keys()),
            'parents': [self[p].label for p in data.parents.keys() if p in self and self[p].label],
        }

        if isinstance(el, spg.Point):
            element_dict.update({
                'type': 'point',
                'x': float(el.x.evalf()),
                'y': float(el.y.evalf()),
                'latex_x': sp.latex(el.x),
                'latex_y': sp.latex(el.y),
            })

        elif isinstance(el, spg.Line):
            element_dict.update({
                'type': 'line',
                'pt1': self[el.p1].label,
                'pt2': self[el.p2].label,
                'equation': str(el.equation()),
                'latex_equation': sp.latex(el.equation()),
            })

        elif isinstance(el, spg.Circle):
            element_dict.update({
                'type': 'circle',
                'center': self[el.center].label,
                'radius_pt': self[data.pt_radius].label,
                'radius': float(el.radius.evalf()),
                'latex_radius': sp.latex(el.radius),
                'equation': str(el.equation()),
                'latex_equation': sp.latex(el.equation()),
            })

        elif isinstance(el, spg.Polygon):
            element_dict.update({
                'type': 'polygon',
                'points': [self[p].label for p in el.vertices],
            })

        elif isinstance(el, spg.Segment):
            element_dict.update({
                'type': 'segment',
                'pt1': self[el.p1].label,
                'pt2': self[el.p2].label,
                'points': [self[p].label for p in [el.p1, el.p2]],
                'length': float(el.length.evalf()),
                'latex_length': sp.latex(el.length),
            })
            
        elif isinstance(el, Wedge):
            element_dict.update({
                'type': 'wedge',
                'center': self[el.pt_center].label,
                'radius_pt': self[el.pt_radius].label,
                'start_ray_pt': self[el.start_ray.p2].label,
                'end_ray_pt': self[el.sweep_ray.p2].label,
                'radius': float(el.circle.radius.evalf()),
                'latex_radius': sp.latex(el.circle.radius),
                'radians': float(el.radians.evalf()),
                'latex_radians': sp.latex(el.radians),
            })

        elif isinstance(el, Section):
            element_dict.update({
                'type': 'section',
                'points': [self[p].label for p in el.points],
                'lengths': [float(l.evalf()) for l in el.lengths],
                'latex_lengths': [sp.latex(l) for l in el.lengths],
                'ratio': float(el.ratio.evalf()),
                'latex_ratio': sp.latex(el.ratio),
                'is_golden': el.is_golden,
            })

        elif isinstance(el, Chain):
            element_dict.update({
                'type': 'chain',
                'points': [self[p].label for p in el.points],
                'segments': [[self[s.p1].label, self[s.p2].label] for s in el.segments],
                'flow': el.flow,
            })
        
        else:
            # Skip unknown types
            continue

        browser_elements.append(element_dict)

    return {
        'name': self.name,
        'elements': browser_elements,
    }
