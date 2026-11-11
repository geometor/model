"""Construct and compare three exact symbolic models of the regular heptadecagon (17-gon):

1. H. W. Richmond (1893) compass-and-straightedge angle-quartering construction
2. Duane W. DeTemple (1991) 4-Carlyle-circle Gauss period construction
3. Mohr–Mascheroni pure-compass construction (strictly collapsible circles, zero lines)
"""

import sys
from pathlib import Path

# Ensure sibling package `demos/heptadecagon` is importable when run directly as a script
_DEMOS_DIR = Path(__file__).resolve().parent
if str(_DEMOS_DIR) not in sys.path:
    sys.path.insert(0, str(_DEMOS_DIR))

from heptadecagon.report import run_report

if __name__ == "__main__":
    run_report()
