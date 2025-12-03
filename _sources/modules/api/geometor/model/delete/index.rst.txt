geometor.model.delete
=====================

.. py:module:: geometor.model.delete

.. autoapi-nested-parse::

   Deletion functions for the Model class.



Attributes
----------

.. autoapisummary::

   geometor.model.delete.console


Classes
-------

.. autoapisummary::

   geometor.model.delete.DeleteMixin


Module Contents
---------------

.. py:data:: console

.. py:class:: DeleteMixin

   Mixin for the Model class containing deletion operations.


   .. py:method:: get_dependents(element_or_ID)

      Finds and returns a set of all elements that depend on the given element.

      This method is for checking dependencies without performing any deletion.

      :param element_or_ID: The element object or its
                            ID to check for dependents.
      :type element_or_ID: spg.GeometryEntity or str

      :returns:

                A set of dependent elements. Returns an empty set if the element
                     is not found or has no dependents.
      :rtype: set



   .. py:method:: delete_element(element_or_ID)

      Deletes an element and performs a cascading delete of all its dependents.

      This method removes the specified element and any other elements that were
      constructed from it, directly or indirectly.

      :param element_or_ID: The element object or its
                            ID to be deleted.
      :type element_or_ID: spg.GeometryEntity or str



