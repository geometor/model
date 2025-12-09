# GEOMETOR Model

The foundational library for the GEOMETOR initiative, providing the data structures and logic for symbolic geometric construction.

## Mission

To create a digital equivalent of the compass and straightedge that operates with absolute symbolic precision, allowing for the exploration of geometric truth without the noise of approximation.

## Core Concepts

-   **Model**: The container state. It holds lists of points, lines, circles, and segments. It manages the build process.
-   **Element**: The base class for all geometric objects. Handles unique IDs, labels, classes, and ancestry.
-   **Symbolic Engine**: Wraps SymPy functionality to handle algebraic coordinates and equations.
-   **CLI**: A text-based interface for rapid modeling and scripting (`python -m geometor.model`).

## Architecture

### Key Modules

-   `model.py` (`__init__.py`): The main entry point. Orchestrates the construction operations.
-   `elements.py`: Defines the `Element` base class.
-   `points.py`, `lines.py`, `circles.py`: Specific implementations of geometric primitives.
-   `intercepts.py`: Logic for calculating intersections between elements.
-   `serialize.py`: Handles import/export to JSON, essential for communication with the Explorer.

## Getting Started

### Installation

```bash
git clone https://github.com/geometor/model
cd model
pip install -e .
```

### Running Tests

```bash
pytest
```

### Building Documentation

```bash
cd docsrc
make html
```

## Development Workflow

1.  **Define**: Create a new construction script in `demos/` or interactively in the CLI.
2.  **Run**: Execute the script to generate the model.
3.  **Verify**: Check the algebraic properties of the resulting elements.
4.  **Export**: Save to JSON for visualization.
