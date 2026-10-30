GEOMETOR • model
================

.. image:: https://img.shields.io/pypi/v/geometor-model.svg
   :target: https://pypi.python.org/pypi/geometor-model
.. image:: https://img.shields.io/github/license/geometor/model.svg
   :target: https://github.com/geometor/model/blob/main/LICENSE

**Symbolic compass-and-straightedge construction engine for the GEOMETOR ecosystem.**

Overview
--------

``geometor.model`` is the foundational symbolic algebra engine for defining, constructing, and verifying geometric systems with exact precision. Powered by `SymPy <https://www.sympy.org>`_, it treats constructive geometry as an ordered deductive system of information and operations:

- **Points** represent *information*—exact algebraic coordinates ($\sqrt{2}$, $\varphi = \frac{1+\sqrt{5}}{2}$, etc.) without floating-point approximation noise.
- **Lines** and **Circles** represent *operations* performed on pairs of existing points.
- **Intersections** are the *consequences* of operations, automatically computed, simplified, deduplicated, and added to the model with full ancestral lineage.
- **Segments**, **Wedges/Angles**, and **Polygons** represent derived structural measurements and regions.

Role Across the GEOMETOR Ecosystem & Coordination with ``publish``
------------------------------------------------------------------

``geometor.model`` powers the executable constructions and interactive SVG diagrams across all GEOMETOR repositories:

- **`geometor/elements <https://github.com/geometor/elements>`_**: Every proposition in the G-Index (`G.1`–`G.525`) includes a standalone ``geometor.model`` Python script (`g1.py`) rendered in the **Code** track of the Book Codex.
- **`geometor/etc <https://github.com/geometor/etc>`_**: Every triangle center (`X(1)`–`X(1000)+`) is constructed via composable ``geometor.model`` operations (`model.py`), serialized to JSON (`x-NNNNN.json`), and rendered into two-layer SVGs across four reference triangles.
- **`geometor/explorer <https://github.com/geometor/explorer>`_**: Provides the interactive Flask/SVG web workbench and live CLI over ``geometor.model`` JSON states.
- **`photon-platform/publish <https://github.com/photon-platform/publish>`_**: Connects ``geometor.model`` element labels and symbolic indications (`[ A B ]`, `/ A B /`, `( A B C )`, `< B A C )`, `< A B C >`, `A`) to `:g:` and `:eq:` roles in Sphinx documentation with bidirectional SVG highlighting and step-by-step construction playback.

Key Features
------------

- **Exact Symbolic Precision**: Every coordinate, radius, line equation, and spread is maintained as an exact SymPy algebraic expression.
- **Ancestry & Dependency Tracking**: Every constructed element records its parent primitives, enabling automatic dependency tree extraction (`ancestors`) and step-by-step playback.
- **Automatic Intersection Discovery & Deduplication**: Adding a line or circle automatically computes all intersections with existing primitives and merges coincident algebraic points.
- **JSON Serialization & Interactive CLI**: Save and load complete model histories to/from JSON (`serialize.py`) or build models interactively via `python3 -m geometor.model`.

Installation & Usage
--------------------

.. code-block:: bash

   pip install geometor-model

Python API:

.. code-block:: python

   from geometor.model import Model

   model = Model("equilateral")
   A = model.set_point(0, 0, classes=["given"], label="A")
   B = model.set_point(1, 0, classes=["given"], label="B")

   model.construct_circle(A, B)
   model.construct_circle(B, A)

   # Intersections C and D are automatically discovered and labeled
   for pt in model.points:
       print(pt.label, pt.x, pt.y)

Documentation & Deployment
--------------------------

Built with `photon-platform/publish <https://github.com/photon-platform/publish>`_ in the unified Classical Scriptorium Book Codex theme:

.. code-block:: bash

   publish test

Resources
---------

- **Documentation**: https://geometor.github.io/model
- **Source Code**: https://github.com/geometor/model
- **Issues**: https://github.com/geometor/model/issues
