geometor.model.points
=====================

.. py:module:: geometor.model.points

.. autoapi-nested-parse::

   The :mod:`geometor.model.points` module provides point construction and manipulation for the Model class.



Classes
-------

.. autoapisummary::

   geometor.model.points.PointsMixin


Module Contents
---------------

.. py:class:: PointsMixin

   Mixin for the Model class containing point construction operations.


   .. py:method:: point_ID_generator() -> collections.abc.Iterator[str]


   .. py:method:: set_point(x_val: sympy.Expr, y_val: sympy.Expr, parents: list = None, classes: list = None, ID: str = '', guide: bool = False) -> sympy.geometry.Point

      Adds a point to the model, finds duplicates, cleans values, and sets
      parents and classes.

      :param - ``x_val``:
      :type - ``x_val``: :class:`sympy.core.expr.Expr`: The x-value of the point.
      :param - ``y_val``:
      :type - ``y_val``: :class:`sympy.core.expr.Expr`: The y-value of the point.
      :param - ``parents``: Defaults to None.
      :type - ``parents``: list, optional: A list of parent elements or references.
      :param - ``classes`` list: a set of styles. Defaults to None.
      :type - ``classes`` list: A list of string names for classes defining
      :param optional: a set of styles. Defaults to None.
      :type optional: A list of string names for classes defining
      :param - ``ID`` str: reporting. Defaults to an empty string.
      :type - ``ID`` str: A text ID for use in plotting and
      :param optional: reporting. Defaults to an empty string.
      :type optional: A text ID for use in plotting and

      :returns: **- :class:`sympy.geometry.point.Point`**
      :rtype: The set point.

      .. rubric:: Example

      >>> from geometor.model import *
      >>> model = Model("demo")
      >>> model.set_point(0, 0, classes=["given"])
      <spg.Point object ...>

      .. rubric:: Notes

      The function simplifies the x and y values before adding, and it updates the attributes if the point is already in the model.



