geometor.model.circles
======================

.. py:module:: geometor.model.circles

.. autoapi-nested-parse::

   circle functions for Model class



Classes
-------

.. autoapisummary::

   geometor.model.circles.CirclesMixin


Module Contents
---------------

.. py:class:: CirclesMixin

   Mixin for the Model class containing circle construction operations.


   .. py:method:: construct_circle_by_IDs(pt_1_ID: str, pt_2_ID: str, classes: list = None, ID: str = '') -> sympy.geometry.Line

      find points by ID and use them with :meth:`Model.construct_line`



   .. py:method:: construct_circle(pt_center: sympy.geometry.Point, pt_radius: sympy.geometry.Point, classes: list = None, ID: str = '', guide: bool = False) -> sympy.geometry.Circle

      Constructs a Circle from two points and adds it to the model.



