geometor.model.segments
=======================

.. py:module:: geometor.model.segments

.. autoapi-nested-parse::

   The :mod:`geometor.model.segments` module provides segment construction and manipulation for the Model class.



Classes
-------

.. autoapisummary::

   geometor.model.segments.SegmentsMixin


Module Contents
---------------

.. py:class:: SegmentsMixin

   Mixin for the Model class containing segment construction operations.


   .. py:method:: set_segment_by_IDs(pt_1_ID: str, pt_2_ID: str, classes: list = None, ID: str = '') -> sympy.geometry.Segment

      find points by ID and use them with :meth:`Model.set_segment`



   .. py:method:: set_segment(pt_1: sympy.geometry.Point, pt_2: sympy.geometry.Point, classes=[], ID='') -> sympy.geometry.Segment

      set segment (list of points) for demonstration in the model



