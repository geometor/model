**Symbolic compass-and-straightedge construction engine for the GEOMETOR ecosystem.**

``geometor.model`` is the foundational library for the `GEOMETOR <https://geometor.com>`_ initiative. At the core of the module is the ``Model`` class, which establishes an exact symbolic field (`SymPy <https://docs.sympy.org>`_) for creating, analyzing, and serializing geometric constructions.

----

Core Principles
---------------

- **Points as Information**: Every ``Point`` is defined as a pair of exact algebraic SymPy expressions (`x`, `y`) rather than floating-point approximations.
- **Lines & Circles as Operations**: Each ``Line`` (`[ A B ]`) and ``Circle`` (`( A B )`) is constructed from two existing points.
- **Intersections as Consequences**: Whenever a new line or circle is constructed, ``Model`` automatically solves for all intersection points with existing primitives, simplifies and deduplicates algebraic coordinates, and records parent ancestry.
- **Structures & Measurements**: Segments (`/ A B /`), Polygons (`< A B C >`), and Wedges/Angles (`< B A C )`) attach directly to model points.

----

Ecosystem Integration
---------------------

``geometor.model`` powers the symbolic constructions across the entire GEOMETOR platform and coordinates directly with ``photon-platform/publish``:

- `GEOMETOR • explorer <https://geometor.github.io/explorer>`_: Interactive web workbench, animation timeline, and golden-ratio analyzer over serialized ``geometor.model`` JSON files.
- `GEOMETOR • elements <https://geometor.github.io/elements>`_: Executable `g1.py` construction scripts and interactive step-by-step SVG diagrams across the 525-node G-Index.
- `GEOMETOR • etc <https://geometor.github.io/etc>`_: Composable triangle-center constructions (`model.py` and `x-NNNNN.json`) across four reference triangles in the *Encyclopedia of Triangle Centers*.
- `PHOTON • publish <https://photon-platform.github.io/publish>`_: Renders ``geometor.model`` symbolic indications via `:g:` and `:eq:` roles with bidirectional SVG highlighting in the Book Codex theme.

.. image:: /_static/screenshot.png
