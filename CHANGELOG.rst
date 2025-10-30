changelog
=========

0.3.1
-----
*2025-10-30*

**fixed**

.. + Fixed a recursion error in `_get_ancestors_IDs` by adding cycle detection.

0.3.0
-----
*2025-10-27*

**added**

.. + Improved logging and output for better debugging and user feedback.

0.2.6
-----
*2025-10-25*

**added**

.. + Cleaned algebraic expressions for lengths to simplify complex mathematical representations.

**fixed**

.. + Handled polygons in ancestor search to prevent errors and improve reliability.
.. + Added a missing return statement to ensure correct functionality.

0.2.5
-----
*2025-10-23*

**fixed**

.. + Fixed serialization of `Wedge` objects, ensuring models can be saved and loaded correctly.
.. + Correctly serialized element classes to handle sets, improving data integrity.

0.2.4
-----
*2025-10-23*

**fixed**

.. + Fixed serialization of `Section` objects, ensuring models can be saved and loaded correctly.

0.2.3
-----
*2025-10-22*

**added**

.. + Added `guide` property to model elements to exclude them from intersection calculations and analysis.

**fixed**

.. + Persisted `guide` property to ensure it is saved and loaded correctly.
.. + Ensured delete only removes chronological dependents to prevent unintended data loss.
.. + Improved model loading speed and serialization stability for a more reliable user experience.

0.2.2
-----
*2025-10-22*

**changed**

.. + Refactored logging for better performance and readability.

0.2.1
-----
*2025-10-20*

**changed**

.. + Replaced the event-driven system with a synchronous analysis hook to simplify the architecture and ensure correct execution order.
.. + Decoupled all logging from the model library; logging is now handled by the calling application.

0.2.0
-----
*2025-10-20*

**changed**

.. + Bumped version to 0.2.0.
.. + Optimized golden section check for better performance.
.. + Standardized on 'ID' instead of 'label' for element identification.
.. + Refactored the `Model` class and added delete functionality.
.. + Added an event system and refactored the `Section` representation.

0.1.0 
-----
*2023-11-15*

**fixed**

.. + Fixed bug in data processing (`#42 <https://github.com/example/repo/issues/42>`_)
.. + Improved error handling in API calls

**added**

.. + Fixed bug in data processing (`#42 <https://github.com/example/repo/issues/42>`_)
.. + Improved error handling in API calls

**changed**

.. + Fixed bug in data processing (`#42 <https://github.com/example/repo/issues/42>`_)
.. + Improved error handling in API calls