# **Refactor Plan: Migrate Model Class to Mixin Architecture**

## **Objective**

Refactor the geometor.model package to move away from "monkey-patching" functions onto the Model class in \_\_init\_\_.py. Instead, implement a **Mixin** pattern where the Model class inherits functionality from modular mixin classes defined in separate files. This improves code organization, readability, and IDE/static analysis support.

## **Architecture Change**

* **Current:** Model is defined in \_\_init\_\_.py. Helper functions (e.g., \_set\_point in \_points.py) are assigned to Model attributes dynamically.  
* **Target:** Model is defined in model.py. It inherits from PointsMixin, LinesMixin, etc., defined in their respective files (e.g., points.py, lines.py).

## **File Structure Changes**

| Current File | New File | Class to Create |
| :---- | :---- | :---- |
| src/geometor/model/\_points.py | src/geometor/model/points.py | PointsMixin |
| src/geometor/model/\_lines.py | src/geometor/model/lines.py | LinesMixin |
| src/geometor/model/\_circles.py | src/geometor/model/circles.py | CirclesMixin |
| src/geometor/model/\_polygons.py | src/geometor/model/polygons.py | PolygonsMixin |
| src/geometor/model/\_segments.py | src/geometor/model/segments.py | SegmentsMixin |
| src/geometor/model/\_polynomials.py | src/geometor/model/polynomials.py | PolynomialsMixin |
| src/geometor/model/\_serialize.py | src/geometor/model/serialize.py | SerializeMixin |
| src/geometor/model/\_delete.py | src/geometor/model/delete.py | DeleteMixin |
| src/geometor/model/sections.py | src/geometor/model/sections.py | SectionsMixin |
| src/geometor/model/wedges.py | src/geometor/model/wedges.py | WedgesMixin |
| src/geometor/model/\_\_init\_\_.py | (Same path) | (Cleanup) |
| (New) | src/geometor/model/model.py | Model |

## **Step-by-Step Instructions**

### **1\. Refactor Helper Modules into Mixins**

For each file listed in the table above (except \_\_init\_\_.py):

1. **Rename File:** Remove the leading underscore if present (e.g., \_points.py \-\> points.py).  
2. **Create Mixin Class:** Wrap the existing functions inside a class (e.g., class PointsMixin:).  
3. **Update Function Signatures:**  
   * Change the first argument from model to self.  
   * Remove the leading underscore from the function name (e.g., \_set\_point \-\> set\_point).  
4. **Update Function Bodies:**  
   * Replace all references to model with self.  
   * Ensure calls to other model methods use self.method\_name().  
5. **Handle Imports:**  
   * Use from typing import TYPE\_CHECKING to handle circular dependencies.  
   * Inside if TYPE\_CHECKING:, import from .model import Model.

### **2\. Create the Central Model Class (src/geometor/model/model.py)**

Create a new file src/geometor/model/model.py. This will house the main class definition.

1. **Imports:** Import all the new Mixin classes created in Step 1\.  
2. **Class Definition:** Define class Model(dict, PointsMixin, LinesMixin, ...):.  
   * Inherit from dict first, then all Mixins.  
3. **Initialization:** Move the \_\_init\_\_ logic from the old \_\_init\_\_.py into this class.  
   * Ensure super().\_\_init\_\_() is called.  
4. **Properties/Methods:** Move properties (like points, lines, limits) and core methods (like \_\_setitem\_\_) from the old \_\_init\_\_.py to this file.

### **3\. Clean up src/geometor/model/\_\_init\_\_.py**

Refactor the package entry point.

1. **Remove Logic:** Delete the old Model class definition and monkey-patching code.  
2. **Expose API:** Import the new Model class from .model.  
3. **Export:** Ensure Model, Element, and other core classes/functions are exported via \_\_all\_\_ or simple imports.

### **4\. Special Cases**

* **serialize.py:** Keep load\_model as a standalone function (factory pattern), but move save\_model logic into SerializeMixin.save().  
* **sections.py & wedges.py:** These files already contain classes (Section, Wedge). Keep those classes, but wrap the construction functions (like \_set\_section) into their respective Mixins (SectionsMixin, WedgesMixin) within the same file.

## **Verification**

* Ensure no circular import errors at runtime.  
* Ensure all methods previously available on model (e.g., model.set\_point) remain available with the same signature.  
* Check that help(Model) or Sphinx documentation now correctly lists the methods inherited from Mixins.