# GEOMETOR Model: Development Roadmap

The following is a list of features and improvements planned for the GEOMETOR Model library:

### 1. Enhanced Serialization (Complete)

-   **Objective:** Improve the serialization and deserialization functionality to support more complex geometric models and metadata.
-   **Strategy:**
    -   Extend the JSON schema to include support for element classes, styles, and other metadata.
    -   Implement more robust error handling and validation for the serialization process.

### 2. Advanced Geometric Operations (In Progress)

-   **Objective:** Add support for more advanced geometric operations, such as transformations, intersections, and geometric constructions.
-   **Strategy:**
    -   Implement functions for translating, rotating, and scaling geometric elements.
    -   Develop a robust intersection engine for finding intersections between different types of geometric elements.
    -   Add support for common geometric constructions, such as perpendicular bisectors, angle bisectors, and tangents.

### 3. Improved Documentation (In Progress)

-   **Objective:** Improve the documentation for the library to make it easier for developers to use and understand.
-   **Strategy:**
    -   Add more detailed docstrings to all classes and functions.
    -   Create a comprehensive set of tutorials and examples to demonstrate how to use the library.
    -   Generate API documentation using a tool like Sphinx.

### 4. Event System

-   **Objective:** Provide a flexible event system to allow for real-time monitoring and interaction with the geometric model.
-   **Strategy:**
    -   Implement a pub/sub event system for broadcasting model events, such as `point_added`, `line_added`, etc.
    -   Integrate the event system with the `explorer` UI to provide real-time updates and feedback.
    -   Use the event system to trigger analysis and validation of the model as it is being constructed.

### 5. Known Issues

-   **`divine` analysis on loaded models:** When a model is loaded from a file, adding new intersection points does not trigger a `divine` analysis. This works as expected for new constructions.
