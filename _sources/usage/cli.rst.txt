CLI Usage
=========

The **Geometor Model CLI** provides an interactive environment (REPL) for constructing and analyzing geometric models using a concise, text-based syntax. It is designed for rapid experimentation and scripting.

Starting the CLI
----------------

To start the CLI, run the module as a script:

.. code-block:: bash

    python -m geometor.model

You will be greeted by the Geometor CLI prompt:

.. code-block:: text

    Geometor CLI
    Commands:
      ...
    >

Command Syntax
--------------

The CLI supports a variety of commands for creating geometric elements.

Points
~~~~~~

*   **Manual Label**: Create a point with a specific label.

    .. code-block:: text

        A = 0, 0
        P1 = 1.5, -2

*   **Auto Label**: Create a point and let the model assign the next available label (A, B, C...).

    .. code-block:: text

        * 0, 0
        * 1, 0

Lines
~~~~~

*   **Connect Points**: Create a line passing through two points.

    .. code-block:: text

        [ A B ]

Circles
~~~~~~~

*   **Center & Radius**: Create a circle with a center point and a point on the circumference.

    .. code-block:: text

        ( A B )

    *Center: A, Point on Circle: B*

Polygons
~~~~~~~~

*   **Polygon from Points**: Create a polygon connecting 3 or more points.

    .. code-block:: text

        < A B C >

Linear Divisions
~~~~~~~~~~~~~~~~

*   **Segment**: Create a segment between two points.

    .. code-block:: text

        / A B /

*   **Section**: Create a section defined by three collinear points (start, inner, end).

    .. code-block:: text

        / A B C /

Wedges
~~~~~~

*   **Wedge**: Create a wedge defined by a center, a radius point, and a sweep end point.

    .. code-block:: text

        < A B C )

    *Center: A, Radius: B, Sweep to: C*
    *(Note: The sweep starts from the radius point B)*

Scripting
---------

You can pipe a file containing a list of commands directly into the CLI for batch processing.

**Example Script (`script.txt`):**

.. code-block:: text

    * 0, 0
    * 1, 0
    ( A B )
    ( B A )
    < A C B >
    exit

**Run:**

.. code-block:: bash

    python -m geometor.model < script.txt

Output
------

The CLI uses the `rich` library to provide formatted output, including:

*   **Element Details**: Coordinates, equations, and properties.
*   **Intersection Logs**: Automatically detected intersection points are logged as they are found.
*   **Tables**: Clean tabular data for complex objects like Polygons.
