# GEOMETOR Model

A Python library for creating and manipulating geometric constructions.

## Overview

The `model` library provides the foundation for other GEOMETOR applications. It defines the core data structures for geometric elements (points, lines, circles) and provides a rich API for creating, modifying, and analyzing constructions.

## Index

-   `__init__.py`: Main `Model` class, a `dict` subclass with a synchronous analysis hook.
-   `element.py`: The core `Element` class for all geometric objects.
-   `_points.py`: `Point` class and related functions.
-   `_lines.py`: `Line` class and related functions.
-   `_circles.py`: `Circle` class and related functions.
-   `_polygons.py`: `Polygon` class and related functions.
-   `_serialize.py`: JSON serialization and deserialization for the model.
