# **Documentation Standards**

This project adopts a **Type Hints First** approach to documentation, utilizing **Google Style** docstrings where necessary.

Our goal is to keep code clean and readable. We rely on Python's type system and expressive naming conventions to convey *what* the code inputs and outputs are, reserving docstrings for explaining *why* logic exists, how complex behaviors work, or listing side effects.

We use **Sphinx** with **AutoAPI** to generate documentation sites. This means our source code structure and docstrings directly dictate the output of the documentation website.

## **Core Principles**

1. **Type Hints are Mandatory**: All function arguments and return values must be typed.  
2. **Self-Documenting Names**: Variable and function names should describe their purpose clearly.  
3. **Minimal Docstrings**: If the type signature and name explain the function, a docstring is optional.  
4. **Google Style**: When a docstring is required, use the [Google Python Style Guide](https://www.google.com/search?q=https://google.github.io/styleguide/pyguide.html%2338-comments-and-docstrings).

## **Module Level Documentation**

Every file (module) **must** have a top-level docstring. This is critical because AutoAPI uses this summary to create the landing page for that module in the documentation.

**Requirements:**

* A concise summary of what the module contains.  
* (Optional) A brief example of usage if the module is complex.

**Example:**

"""  
Geometry primitives for constructing and manipulating circles.

This module provides the \`CirclesMixin\` class, which contains methods for   
defining circles by center/radius or by geometric relationships to other elements.  
"""  
from typing import TYPE\_CHECKING  
...

## **Class Level Documentation**

Classes should have a docstring immediately following the class definition.

**Requirements:**

* Summary of the class responsibility.  
* If it is a **Mixin**, explicitly state "Mixin for \[Parent\] class containing \[Functionality\]."

**Example:**

class CirclesMixin:  
    """  
    Mixin for the Model class containing all circle construction operations.  
      
    This class is not intended to be instantiated directly but inherited   
    by the main Model class.  
    """

## **Function/Method Level Documentation**

### **The "Type Hints First" Rule**

If a function is simple, fully typed, and well-named, you do **not** need Args or Returns sections in the docstring. A simple one-line summary is sufficient (or sometimes no docstring at all if it's an internal helper).

**✅ Good (Simple):**

def get\_area(self) \-\> float:  
    return self.radius \*\* 2 \* math.pi

*No docstring needed. The name and return type are obvious.*

**✅ Good (One-liner):**

def set\_color(self, color\_code: str) \-\> None:  
    """Updates the element's render color."""  
    self.styles\['color'\] \= color\_code

### **When to use Full Docstrings**

Use a full Google Style docstring when:

1. **Behavior is conditional** (e.g., "If guide is True, the element is not rendered").  
2. **Side Effects occur** (e.g., "Adds the point to the global index").  
3. **Arguments are ambiguous** (e.g., \*args or \*\*kwargs).  
4. **Exceptions are raised** (This is crucial for consumers).

**Structure:**

def construct\_line(  
    self,   
    pt\_1: spg.Point,   
    pt\_2: spg.Point,   
    classes: list\[str\] \= None,   
    ID: str \= "",   
    guide: bool \= False  
) \-\> spg.Line:  
    """  
    Constructs a Line from two points and adds it to the Model.

    If the line already exists (defined by the same two points), the   
    existing line is returned and updated with any new classes provided.

    Args:  
        pt\_1: The start point.  
        pt\_2: The end point.  
        classes: CSS-style classes for rendering (e.g., \['guide', 'dashed'\]).  
        ID: A unique identifier. If empty, one is generated automatically.  
        guide: If True, this line is excluded from intersection calculations.

    Returns:  
        The sympy Line object created or retrieved.

    Raises:  
        TypeError: If pt\_1 or pt\_2 are not valid Geometry objects.  
    """

## **Type Hinting Standards**

We use standard library typing.

* **Circular Imports:** Use typing.TYPE\_CHECKING to avoid runtime circular dependencies when hinting relationships between Models and Elements.  
* **Collections:** Use list\[...\], dict\[...\], tuple\[...\], set\[...\].  
* **Optionals:** Use arg: str | None \= None (Python 3.10+) or Optional\[str\].

**Example:**

from typing import TYPE\_CHECKING

if TYPE\_CHECKING:  
    from .model import Model

def get\_ancestors(self, element: "Element") \-\> dict\[str, list\["Element"\]\]:  
    ...

## **Sphinx AutoAPI Specifics**

* **\_\_all\_\_**: Ensure \_\_init\_\_.py files define \_\_all\_\_. AutoAPI respects this to determine what is public API vs internal implementation.  
* **Formatting**: You can use basic reStructuredText (reST) or Markdown in your docstrings (if the parser is configured). Keep formatting simple (bold, lists, code ticks).

\_\_all\_\_ \= \[  
    "Model",  
    "Point",  
    "Line",  
\]  
