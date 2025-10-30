changelog
=========

0.3.1
-----
*2025-10-30*

**fixed**

.. + Fixed a recursion error in `_get_ancestors_IDs` by adding cycle detection.

0.2.5
-----
*2025-10-23*

**fixed**

.. + Fixed serialization of `Wedge` objects, ensuring models can be saved and loaded correctly.

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

0.2.1
-----
*2025-10-20*

**changed**

.. + Replaced the event-driven system with a synchronous analysis hook to simplify the architecture and ensure correct execution order.
.. + Decoupled all logging from the model library; logging is now handled by the calling application.

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
