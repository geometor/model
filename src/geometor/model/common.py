"""
common imports for all modules

NOTE: do not put local references in here
"""
import sympy as sp
import sympy.plotting as spp
import sympy.geometry as spg
from sympy.abc import x, y

sp.init_printing()

import math as math
from collections import defaultdict
import logging

from rich import print
from rich.console import Console
from rich.table import Table
from rich.text import Text

console = Console()

from itertools import permutations, combinations
from multiprocessing import Pool, cpu_count

