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

from geometor.model.element import *
from geometor.model.model import Model
from geometor.model.wedges import Wedge
from geometor.model.sections import Section
from geometor.model.chains import Chain

from geometor.model.reports import *


