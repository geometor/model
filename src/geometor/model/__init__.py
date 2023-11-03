"""
The Model module provides a set of tools for constructing geometric models.
It relies heavily on sympy for providing the algebraic infrastructure
the functions here are for creating the abstract model, not the rendering
see the Render module for plotting with matplotlib
"""
__author__ = "geometor"
__maintainer__ = "geometor"
__email__ = "github@geometor.com"
__version__ = "0.0.1"
__licence__ = "MIT"

from geometor.model.common import *

from .model import Model
from ._wedges import Wedge
from ._sections import Section
from ._chains import Chain
#  from .points import *
from .element import *
#  from .lines import *
#  from .circles import *
#  from .polygons import *
#  from .polynomials import *
#  from .helpers import *

from .reports import *


