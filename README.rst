`geometor.model`` is the foundational library for the GEOMETOR_ initiative.

Additional information about ``geometor.model`` can be seen at the `Project's Website`_


* Contents:

  + 1 mission_
  + 2 overview_
  + 3 installation_
  + 4 usage_
  + 5 dependencies_
  + 6 contributing_
  + 7 license_

mission
-------

The mission of this module is to establish a rigorous system for defining
classical geometric constructions of points, lines and circles. But in our
case, we are not using straight edge and compass. We are creating the geometric
elements as expressions in symbolic algebra thanks to the power of the `Sympy`_
library.

overview
--------

At the core of the module is the ``Model`` class which establishes the field
and methods of operation for creating the geometric constructions while
maintaining integrity. 

The **field** might be easy to consider as a Cartesian grid. But in reality, it
is an ordered set of information and operations. Points are the information.
Lines and circles are the operations.

In our system, all geometric elements of the ``Model`` are defined as `Sympy
Geometry`_ objects. This means a ``Point`` can be defined as a pair of any
algebraic `Sympy Expressions`_ that can be evaluated into a floating point
value. 

``Line`` and ``Circle`` are each defined by two points. So each construction
must begin with at least two given points at the start. As lines and circles
are added, intersection points are discovered with previous lines and circles
and added to the model, so they may be used with new lines and circles. 

There are three main operations of the ``Model``:

- set_point
- construct_line
- construct_circle

The major responsibilities of the ``Model``:

- **deduplicate**

  when elements are added to the model, we check to see if they already exist. This is particularly important for intersection points that often coincide with exisitng points. 
- clean values
- discover intersections
- save to and load from json
- maintain a set of related info for each element:

  - ancestral relationships
  - establish labels for elements
  - classes for styles
  - event triggers

All of the plotting functionality is now handled by the **GEOMETOR** `explorer`_. However, there are several report functions in the this module:

- report_summary
- report_group_by_type
- report_sequence

.. image:: screenshot.png


Key Files
---------

-   ``__init__.py``: Main ``Model`` class, a ``dict`` subclass with an event system.
-   ``element.py``: The core ``Element`` class for all geometric objects.
-   ``_points.py``: ``Point`` class and related functions.
-   ``_lines.py``: ``Line`` class and related functions.
-   ``_circles.py``: ``Circle`` class and related functions.
-   ``_polygons.py``: ``Polygon`` class and related functions.
-   ``_serialize.py``: JSON serialization and deserialization for the model.


installation
------------

You can install ``geometor.model`` using pip:

.. code-block:: bash

   pip install geometor-model

or clone this repo and install it directly.

.. code-block:: bash

   git clone https://github.com/geometor/model
   cd model
   pip install -e .


usage
-----
In this simple example, we create the classic *vesica pisces*

.. code-block:: python

     from geometor.model import *

     model = Model("vesica")
     A = model.set_point(0, 0, classes=["given"])
     B = model.set_point(1, 0, classes=["given"])

     model.construct_line(A, B)

     model.construct_circle(A, B)
     model.construct_circle(B, A)

     E = model.get_element_by_ID("E")
     F = model.get_element_by_ID("F")

     model.set_polygon([A, B, E])
     model.set_polygon([A, B, F])

     model.construct_line(E, F)

     report_summary(model)
     report_group_by_type(model)
     report_sequence(model)

     model.save("vesica.json")


dependencies
------------

**model** depends on the following Python packages:

- sympy
- rich
- jinja2
- numpy (this may now not be required)

contributing
------------

Contributions are welcome! 


Please see our Issues_ for specific opportunities.

Share thoughts in the Discussions_ forum

license
-------

**model** is licensed under the MIT License. See the `LICENSE` file for more details.

.. _Issues: https://github.com/geometor/model/issues
.. _Discussions: https://github.com/geometor/model/discussions

.. _explorer: https://github.com/geometor/explorer
.. _`Sympy Expressions`: https://docs.sympy.org/latest/tutorials/intro-tutorial/basic_operations.html
.. _`Sympy Geometry`: https://docs.sympy.org/latest/modules/geometry/index.html
.. _`Sympy`: https://docs.sympy.org
.. _GEOMETOR: https://geometor.com
   .. _`Project's Website`: https://geometor.github.io/model
