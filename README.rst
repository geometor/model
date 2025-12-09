GEOMETOR • model
================

.. image:: https://img.shields.io/pypi/v/geometor-model.svg
   :target: https://pypi.python.org/pypi/geometor-model
.. image:: https://img.shields.io/github/license/geometor/model.svg
   :target: https://github.com/geometor/model/blob/main/LICENSE

**The symbolic heart of the GEOMETOR project.**

Overview
--------

``geometor.model`` is a Python library for defining and verifying geometric constructions with symbolic accuracy. It treats geometry not as a visual approximation, but as a rigorous system of information and operations.

In this system:

- **Points** represent *information*. They are exact algebraic locations.
- **Lines** and **Circles** represent *operations* performed on that information.
- **Intersections** are the *consequences* of operations, yielding new information (Points).

We leverage `SymPy <https://www.sympy.org>`_ to ensure that every coordinate and radius is an exact algebraic expression, allowing us to find deep relationships that floating-point arithmetic would miss.

Key Features
------------

- **Symbolic Precision**: No rounding errors. $\sqrt{2}$ is $\sqrt{2}$, not $1.414...$.
- **Ancestry Tracking**: Every element knows its parents. We can trace the lineage of any point back to the starting axioms.
- **Automatic Intersection**: The model automatically calculates all intersection points whenever a new line or circle is added.
- **Serialization**: Models can be saved to JSON and shared with other tools like `geometor.explorer`.

Installation
------------

.. code-block:: bash

    pip install geometor-model

Command Line Interface
----------------------

The ``geometor.model`` package includes a robust CLI for interactive construction and scripting (REPL).

Start the session:

.. code-block:: bash

    python -m geometor.model

Sample commands:

.. code-block:: text

    > A = 0, 0      # Set point A
    > B = 1, 0      # Set point B
    > ( A B )       # Circle centered at A passing through B
    > [ A B ]       # Line through A and B

For full details, see the `CLI Usage <https://geometor.github.io/model/usage/cli.html>`_ documentation.

Usage
-----

.. code-block:: python

    from geometor.model import Model

    # Initialize a new model
    model = Model("vesica")

    # Define two starting points
    A = model.set_point(0, 0, classes=["given"])
    B = model.set_point(1, 0, classes=["given"])

    # Construct the Vesica Piscis
    model.construct_circle(A, B)
    model.construct_circle(B, A)

    # The model now automatically contains the intersections of these circles
    print(model.points)

Resources
---------

- **Documentation**: https://geometor.github.io/model
- **Source Code**: https://github.com/geometor/model
- **Issues**: https://github.com/geometor/model/issues

Related Projects
----------------

- `GEOMETOR Explorer <https://github.com/geometor/explorer>`_: Interactive visualization environment.
- `GEOMETOR Divine <https://github.com/geometor/divine>`_: Golden ratio analysis engine.
