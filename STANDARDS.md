# Project Standards

This document outlines the engineering standards and patterns for the `geometor` project. These standards ensure consistency, maintainability, and high-quality documentation across all repositories, with `geometor.model` serving as the reference implementation.

## Architecture: Mixin Pattern

For core libraries and complex objects, avoid massive single classes. Use a **Mixin Architecture**.

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
    """Mixin for Model class containing point-related functionality."""
    
    def set_point(self, x: float, y: float) -> None:
        # ... implementation ...
        pass
```

**`model.py`**
```python
from .points import PointsMixin
from .lines import LinesMixin

class Model(dict, PointsMixin, LinesMixin):
    def __init__(self) -> None:
        super().__init__()
        # ... initialization ...
```

## Type Hinting & Imports (Python 3.13+)

We utilize modern Python type hinting features.

1.  **Future Annotations**: Always include `from __future__ import annotations` at the top of Python files.
2.  **Built-in Generics**: Use standard collection types for hinting.
    *   *Good*: `list[str]`, `dict[str, int]`, `tuple[int, ...]`, `type[Model]`
    *   *Bad*: `typing.List`, `typing.Dict`, `typing.Type`
3.  **Union Operator**: Use `|` for unions and optional types.
    *   *Good*: `int | str`, `str | None`
    *   *Bad*: `typing.Union[int, str]`, `typing.Optional[str]`
4.  **Self Type**: Use `typing.Self` for methods returning an instance of the class.
5.  **Circular Imports**: Use `if TYPE_CHECKING:` blocks to import the main class for type hinting within Mixins.
6.  **Explicit Exports**: In `__init__.py`, explicitly define `__all__` to control the public API.
7.  **No Star Imports**: Do not use `from module import *`.

## Documentation

We adopt a **Type Hints First** approach, utilizing **Google Style** docstrings.

### Core Principles
1.  **Type Hints are Mandatory**: All function arguments and return values must be typed.
2.  **Self-Documenting Names**: Variable and function names should describe their purpose clearly.
3.  **Minimalism**: If the type signature and name explain the function, a docstring is optional. Do not state the obvious.
4.  **Google Style**: When a docstring is required, use the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).

### Module Level
Every file **must** have a top-level docstring summarizing its contents.

### Class Level
Classes should have a docstring immediately following the definition. If it is a Mixin, explicitly state: "Mixin for [Parent] class containing [Functionality]."

### Function/Method Level

#### The "Type Hints First" Rule
**✅ Good (Simple - No Docstring needed):**
```python
def get_area(self) -> float:
    return self.radius ** 2 * math.pi
```

#### When to use Full Docstrings
Use a full Google Style docstring when:
1.  **Behavior is conditional** (e.g., "If guide is True...").
2.  **Side Effects occur** (e.g., "Adds the point to the global index").
3.  **Arguments are ambiguous** (e.g., `*args`, `**kwargs` or specific constraints like "must be non-zero").
4.  **Exceptions are raised**.

**Structure:**
```python
def construct_line(
    self,
    pt_1: spg.Point,
    pt_2: spg.Point,
    classes: list[str] | None = None,
    ID: str = "",
    guide: bool = False
) -> spg.Line:
    """
    Constructs a Line from two points and adds it to the Model.

    If the line already exists, the existing line is returned and updated.

    Args:
        pt_1: The start point.
        pt_2: The end point.
        classes: CSS-style classes for rendering.
        ID: A unique identifier.
        guide: If True, excluded from intersection calculations.

    Returns:
        The sympy Line object created or retrieved.

    Raises:
        TypeError: If pt_1 or pt_2 are not valid Geometry objects.
    """
```

## Sphinx and AutoAPI Configuration

We use `sphinx-autoapi` for generating API documentation.

### Namespace Packages
For namespace packages (e.g., `src/geometor/model`), configure `conf.py` to dynamically find the package root from `pyproject.toml`.

### Inherited Members
To document methods inherited from Mixins:
1.  Enable `inherited-members` in `autoapi_options`.
2.  Ensure namespace configuration allows AutoAPI to resolve Mixin references.

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

1.  **Unit Tests**: Tests must cover the public API methods exposed by Mixins.
2.  **Serialization**: Ensure `save` and `load` methods are tested and compatible with any architectural changes.