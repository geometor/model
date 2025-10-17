# GEOMETOR Model

A Python library for creating and manipulating geometric constructions, providing a foundation for applications like the GEOMETOR Explorer.

## Key Modules (`src/geometor/model/`)

-   **`__init__.py`**: Main `Model` class, now a `dict` subclass with an event system.
-   **`element.py`**: Core `Element` class.
-   **`_points.py`**: `Point` class and functions.
-   **`_lines.py`**: `Line` class and functions.
-   **`_circles.py`**: `Circle` class and functions.
-   **`_segments.py`**: `Segment` class and functions.
-   **`_polygons.py`**: `Polygon` class and functions, including `_set_polygon_by_IDs`.
-   **`_delete.py`**: Functions for deleting elements and finding dependents.
-   **`_serialize.py`**: JSON serialization and deserialization.
-   **`chains.py`**: Logic for connected segments.
-   **`sections.py`**: Logic for line sections.
-   **`wedges.py`**: Logic for wedges (angles).
-   **`reports.py`**: Reporting and analysis.
-   **`helpers.py`**: Helper functions.
-   **`utils.py`**: Utility functions.

## Development Plan

See `ROADMAP.md`.
