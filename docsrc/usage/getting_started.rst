:order: 2

getting started
===============

To start using ``geometor.model``, you need to create a ``Model`` instance. This object will hold all your geometric elements and manage their relationships.

.. code-block:: python

   from geometor.model import Model

   # Initialize a new model
   model = Model("my_first_construction")

From here, you can start adding points and constructing elements.

.. code-block:: python

   # Add two starting points
   A = model.set_point(0, 0, classes=["given"])
   B = model.set_point(1, 0, classes=["given"])

   # Construct a line connecting them
   line_AB = model.construct_line(A, B)

   # Construct a circle centered at A passing through B
   circle_A = model.construct_circle(A, B)
