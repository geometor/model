geometor.model.model
====================

.. py:module:: geometor.model.model

.. autoapi-nested-parse::

   provides the central :class:`geometor.model.model.Model` class.



Attributes
----------

.. autoapisummary::

   geometor.model.model.GeometryObject


Classes
-------

.. autoapisummary::

   geometor.model.model.Model


Module Contents
---------------

.. py:data:: GeometryObject

.. py:class:: Model(name: str = '', logger=None)

   Bases: :py:obj:`dict`, :py:obj:`geometor.model.points.PointsMixin`, :py:obj:`geometor.model.lines.LinesMixin`, :py:obj:`geometor.model.circles.CirclesMixin`, :py:obj:`geometor.model.polygons.PolygonsMixin`, :py:obj:`geometor.model.segments.SegmentsMixin`, :py:obj:`geometor.model.polynomials.PolynomialsMixin`, :py:obj:`geometor.model.serialize.SerializeMixin`, :py:obj:`geometor.model.reports.ReportMixin`, :py:obj:`geometor.model.delete.DeleteMixin`, :py:obj:`geometor.model.sections.SectionsMixin`, :py:obj:`geometor.model.wedges.WedgesMixin`, :py:obj:`geometor.model.ancestors.AncestorsMixin`


   The central class representing a collection of geometric elements.

   It inherits from `dict` and various Mixins to provide a rich API for
   geometric construction and analysis.


   .. py:attribute:: ID_gen


   .. py:attribute:: last_point_id
      :value: ''



   .. py:method:: log(message)


   .. py:method:: set_analysis_hook(hook_function)


   .. py:property:: new_points
      :type: list[sympy.geometry.Point]


      The new_points of the model


   .. py:method:: clear_new_points()


   .. py:property:: name
      :type: str


      The name of the model


   .. py:method:: __setitem__(key: GeometryObject, value: geometor.model.element.Element)

      Set an item in the model, enforcing type checks.

      :param key: The geometric object (GeometryObject).
      :param value: The element wrapper (Element).

      :raises TypeError: If key or value are not of the expected types.



   .. py:method:: remove_by_ID(ID: str) -> None


   .. py:property:: points
      :type: list[sympy.geometry.Point]


      returns point elements from model as list


   .. py:property:: structs
      :type: list[geometor.model.element.Struct]


      returns struct elements (line or circle) from model as list


   .. py:property:: lines
      :type: list[sympy.geometry.Line]


      returns line elements from model as list


   .. py:property:: circles
      :type: list[sympy.geometry.Circle]


      returns circle elements from model as list


   .. py:method:: limits() -> tuple[tuple[float, float], tuple[float, float]]

      Find x, y limits from points and circles of the model.

      :returns: A tuple containing ((min_x, max_x), (min_y, max_y)).
      :rtype: tuple

      :raises ValueError: If the model contains no geometric elements.



   .. py:attribute:: get_element_by_ID


