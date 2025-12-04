geometor.model.ancestors
========================

.. py:module:: geometor.model.ancestors

.. autoapi-nested-parse::

   The :mod:`geometor.model.ancestors` module provides ancestor retrieval functions for the Model class.



Classes
-------

.. autoapisummary::

   geometor.model.ancestors.AncestorsMixin


Module Contents
---------------

.. py:class:: AncestorsMixin

   Mixin for the Model class containing ancestor retrieval operations.


   .. py:method:: get_ancestors_IDs(element) -> dict[str, dict]

      Retrieves the IDs of the ancestors for the given element.

      The method recursively traverses the parent elements of the given element
      and constructs a nested dictionary with IDs representing the ancestor tree.

      :param - element: The element for which the ancestors' IDs are to be retrieved.
      :type - element: sympy.geometry object
      :param returns:
      :param - dict:
      :type - dict: A nested dictionary representing the IDs of the ancestors.

      .. rubric:: Example

      If element A has parents B and C, and B has parent D, the method returns:
      {'A': {'B': {'D': {}}, 'C': {}}}



   .. py:method:: get_ancestors(element)

      Retrieves the ancestors for the given element.

      The method recursively traverses the parent elements of the given element
      and constructs a nested dictionary representing the ancestor tree.

      :param - element: The element for which the ancestors are to be retrieved.
      :type - element: sympy.geometry object

      :returns: **- dict**
      :rtype: A nested dictionary representing the ancestors.

      .. rubric:: Example

      If element A has parents B and C, and B has parent D, the method returns:
      {A: {B: {D: {}}, C: {}}}



