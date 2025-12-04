# GEOMETOR Model

A Python library for creating and manipulating geometric constructions.

## Overview

The `model` library provides the foundation for other GEOMETOR applications. It defines the core data structures for geometric elements (points, lines, circles) and provides a rich API for creating, modifying, and analyzing constructions.

## Index

-   `__init__.py`: Main `Model` class, a `dict` subclass with a synchronous analysis hook.
-   `element.py`: The core `Element` class for all geometric objects.
-   `points.py`: `Point` class and related functions.
-   `lines.py`: `Line` class and related functions.
-   `circles.py`: `Circle` class and related functions.
-   `polynomials.py`: `Polynomial` class and related functions.
-   `polygons.py`: `Polygon` class and related functions.
-   `serialize.py`: JSON serialization and deserialization for the model.
-   `reports.py`: Reporting functionality and `ReportMixin`.
-   `colors.py`: Color definitions and utilities.
-   `ancestors.py`: Ancestor retrieval functions.
-   `chains.py`: Chain analysis.
-   `sections.py`: Section analysis.
-   `wedges.py`: Wedge analysis.
-   `delete.py`: Deletion logic.
