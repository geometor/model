:navigation: header
:order: 20

=====
usage
=====

``geometor.model`` provides the symbolic compass-and-straightedge construction engine and golden-section analyzer for the GEOMETOR ecosystem.

Quickstart
----------

.. code-block:: python

   from geometor.model import Model

   model = Model("equilateral")
   A = model.set_point(0, 0, classes=["given"])
   B = model.set_point(1, 0, classes=["given"])
   model.construct_line(A, B)
   c1 = model.construct_circle(A, B)
   c2 = model.construct_circle(B, A)

Guides
------

.. collection::
   :sort: order
