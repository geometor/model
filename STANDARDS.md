# Project Standards

This document outlines the standards and patterns established for the `geometor.model` project. These standards ensure consistency, maintainability, and high-quality documentation.

## Architecture: Mixin Pattern

Instead of defining a single massive class or using "monkey-patching" to attach methods dynamically, use a **Mixin Architecture**.

### Rules
1.  **Modular Mixins**: Group related functionality into Mixin classes (e.g., `PointsMixin`, `LinesMixin`).
2.  **Composition**: The main class (e.g., `Model`) should inherit from all Mixins.
3.  **State Management**: Mixins should operate on `self` and assume the existence of shared state (e.g., `self.points`, `self.log`) provided by the main class or other Mixins.
4.  **File Structure**: Each Mixin should reside in its own file, named after the functionality (e.g., `points.py`, `lines.py`).

### Example
**`points.py`**
```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .model import Model

class PointsMixin:
    def set_point(self, x, y):
        # ... implementation ...
        pass
```

**`model.py`**
```python
from .points import PointsMixin
from .lines import LinesMixin

class Model(dict, PointsMixin, LinesMixin):
    def __init__(self):
        super().__init__()
        # ... initialization ...
```

## Type Hinting & Imports

1.  **Future Annotations**: Always include `from __future__ import annotations` at the top of the file to postpone evaluation of type hints.
2.  **Circular Imports**: Use `if TYPE_CHECKING:` blocks to import the main class for type hinting within Mixins.
    ```python
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from .model import Model
    ```
3.  **Explicit Exports**: In `__init__.py`, explicitly define `__all__` to control the public API.
4.  **No Star Imports**: Do not use `from module import *`. Always import modules or specific members explicitly.
    *   *Good*: `import sympy as sp`, `from .element import Element`
    *   *Bad*: `from .common import *`
5.  **Explicit Imports**: Import external libraries explicitly in modules where they are used for type hinting. Avoid relying on star imports (`from .common import *`) for type resolution.
    *   *Good*: `import sympy as sp`
    *   *Bad*: Relying on `sp` from `common.py`

## Documentation

We adopt a **Type Hints First** approach, utilizing **Google Style** docstrings where necessary.

### Core Principles
1.  **Type Hints are Mandatory**: All function arguments and return values must be typed.
2.  **Self-Documenting Names**: Variable and function names should describe their purpose clearly.
3.  **Minimal Docstrings**: If the type signature and name explain the function, a docstring is optional.
4.  **Google Style**: When a docstring is required, use the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).

### Module Level Documentation
Every file (module) **must** have a top-level docstring. AutoAPI uses this summary to create the landing page for that module.

**Requirements:**
*   A concise summary of what the module contains.
*   (Optional) A brief example of usage if the module is complex.

### Class Level Documentation
Classes should have a docstring immediately following the class definition.

**Requirements:**
*   Summary of the class responsibility.
*   If it is a **Mixin**, explicitly state "Mixin for [Parent] class containing [Functionality]."

### Function/Method Level Documentation

#### The "Type Hints First" Rule
If a function is simple, fully typed, and well-named, you do **not** need Args or Returns sections in the docstring. A simple one-line summary is sufficient.

**✅ Good (Simple):**
```python
def get_area(self) -> float:
    return self.radius ** 2 * math.pi
```

#### When to use Full Docstrings
Use a full Google Style docstring when:
1.  **Behavior is conditional** (e.g., "If guide is True, the element is not rendered").
2.  **Side Effects occur** (e.g., "Adds the point to the global index").
3.  **Arguments are ambiguous** (e.g., `*args` or `**kwargs`).
4.  **Exceptions are raised**.

**Structure:**
```python
def construct_line(
    self,
    pt_1: spg.Point,
    pt_2: spg.Point,
    classes: list[str] = None,
    ID: str = "",
    guide: bool = False
) -> spg.Line:
    """
    Constructs a Line from two points and adds it to the Model.

    If the line already exists (defined by the same two points), the
    existing line is returned and updated with any new classes provided.

    Args:
        pt_1: The start point.
        pt_2: The end point.
        classes: CSS-style classes for rendering (e.g., ['guide', 'dashed']).
        ID: A unique identifier. If empty, one is generated automatically.
        guide: If True, this line is excluded from intersection calculations.

    Returns:
        The sympy Line object created or retrieved.

    Raises:
        TypeError: If pt_1 or pt_2 are not valid Geometry objects.
    """
```

### Sphinx and AutoAPI Configuration

We use `sphinx-autoapi` for generating API documentation.

#### Configuration for Namespace Packages
For namespace packages (e.g., `geometor.model` inside `src/geometor/model`), use the following configuration in `conf.py`:

```python
import os
import tomllib

# Dynamically determine autoapi_dirs from pyproject.toml
# Use __file__ to determine the location of conf.py (docsrc/conf.py)
# Project root is one level up from docsrc
conf_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(conf_dir, '..'))
pyproject_path = os.path.join(project_root, 'pyproject.toml')

with open(pyproject_path, 'rb') as f:
    pyproject_data = tomllib.load(f)

try:
    find_config = pyproject_data['tool']['setuptools']['packages']['find']
    where = find_config.get('where', ['.'])[0]
    include = find_config.get('include', ['*'])[0]
    autoapi_dirs = [os.path.join(project_root, where, include)]
except KeyError:
    # Fallback
    autoapi_dirs = [os.path.abspath('../src/geometor')]

# Enable implicit namespaces
autoapi_python_use_implicit_namespaces = True
# Root directory for generated files
autoapi_root = 'modules/api'
```

#### Inherited Members
To show methods inherited from Mixins in the main class documentation:

1.  Enable `inherited-members` in `autoapi_options`.
2.  Ensure the namespace configuration is correct so AutoAPI can resolve the Mixin references.

```python
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "special-members",
    "imported-members",
    "inherited-members",
]
```

## Testing

1.  **Unit Tests**: Ensure tests cover the public API methods exposed by the Mixins.
2.  **Serialization**: If the model supports serialization, ensure `save` and `load` methods are tested and compatible with the new structure.

## Migration Steps (Refactoring Guide)

1.  **Rename Files**: Rename internal modules (e.g., `_points.py` -> `points.py`).
2.  **Wrap Functions**: Wrap existing functions into a Mixin class.
3.  **Update Signatures**: Change the first argument from `model` to `self`.
4.  **Create Main Class**: Create a central file (e.g., `model.py`) to define the main class inheriting from Mixins.
5.  **Update Entry Point**: Update `__init__.py` to import the main class and export the API.
