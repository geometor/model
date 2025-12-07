geometor.model
==============

.. py:module:: geometor.model

.. autoapi-nested-parse::

   The :mod:`geometor.model` module provides the core data structures and logic for constructing geometric models in 2D space.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /modules/api/geometor/model/__main__/index
   /modules/api/geometor/model/ancestors/index
   /modules/api/geometor/model/chains/index
   /modules/api/geometor/model/circles/index
   /modules/api/geometor/model/colors/index
   /modules/api/geometor/model/delete/index
   /modules/api/geometor/model/element/index
   /modules/api/geometor/model/helpers/index
   /modules/api/geometor/model/lines/index
   /modules/api/geometor/model/model/index
   /modules/api/geometor/model/points/index
   /modules/api/geometor/model/polygons/index
   /modules/api/geometor/model/polynomials/index
   /modules/api/geometor/model/reports/index
   /modules/api/geometor/model/sections/index
   /modules/api/geometor/model/segments/index
   /modules/api/geometor/model/serialize/index
   /modules/api/geometor/model/utils/index
   /modules/api/geometor/model/wedges/index


Attributes
----------

.. autoapisummary::

   geometor.model.GeometryObject


Classes
-------

.. autoapisummary::

   geometor.model.Model


Functions
---------

.. autoapisummary::

   geometor.model.load_model


Package Contents
----------------

.. py:function:: load_model(file_path, logger=None)

   Loads a model from a JSON file and returns a new Model instance.


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


