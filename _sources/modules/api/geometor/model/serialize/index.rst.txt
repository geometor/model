geometor.model.serialize
========================

.. py:module:: geometor.model.serialize

.. autoapi-nested-parse::

   The :mod:`geometor.model.serialize` module provides serialization functions for the Model class.



Classes
-------

.. autoapisummary::

   geometor.model.serialize.SerializeMixin


Functions
---------

.. autoapisummary::

   geometor.model.serialize.load_model


Module Contents
---------------

.. py:class:: SerializeMixin

   Mixin for the Model class containing serialization operations.


   .. py:method:: save(file_path)

      Saves a Model object to a JSON file as a list of elements.



.. py:function:: load_model(file_path, logger=None)

   Loads a model from a JSON file and returns a new Model instance.


