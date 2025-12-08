GEOMETOR • model
================

.. image:: https://img.shields.io/pypi/v/geometor-model.svg
   :target: https://pypi.python.org/pypi/geometor-model
.. image:: https://img.shields.io/github/license/geometor/model.svg
   :target: https://github.com/geometor/model/blob/main/LICENSE

A symbolic engine for defining and verifying geometric constructions.

Overview
--------

**geometor.model** is the foundational library for the GEOMETOR initiative. It establishes a rigorous system for defining classical geometric constructions using symbolic algebra.

In this system:
- **Points** are information.
- **Lines** and **Circles** are operations.

We leverage the power of `SymPy`_ to define elements as exact algebraic expressions rather than floating-point approximations.

Key Features
------------

- **Symbolic Precision**: All elements are defined using symbolic algebra.
- **Intersection Discovery**: Automatically finds intersection points as new lines and circles are added.
- **Ancestral Tracking**: Maintains the history and dependencies of every element.
- **Serialization**: Save and load models to JSON for analysis and visualization.

Usage
-----

.. code-block:: python

    from geometor.model import *

    # Initialize model
    model = Model("vesica")

    # Set given points
    A = model.set_point(0, 0, classes=["given"])
    B = model.set_point(1, 0, classes=["given"])

    # Construct lines and circles
    model.construct_line(A, B)
    model.construct_circle(A, B)
    model.construct_circle(B, A)

    # Analyze
    model.report_summary()

Resources
---------

- **Documentation**: https://geometor.github.io/model
- **Source Code**: https://github.com/geometor/model
- **Issues**: https://github.com/geometor/model/issues

Related Projects
----------------

- `GEOMETOR Explorer <https://github.com/geometor/explorer>`_: Interactive visualization.
- `GEOMETOR Divine <https://github.com/geometor/divine>`_: Golden ratio analysis.
- `GEOMETOR.com <https://geometor.com`: the center of everything

.. _SymPy: https://www.sympy.org
