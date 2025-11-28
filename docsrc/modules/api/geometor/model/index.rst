geometor.model
==============

.. py:module:: geometor.model

.. autoapi-nested-parse::

   The Model module provides a set of tools for constructing geometric models.
   It relies heavily on sympy for providing the algebraic infrastructure
   the functions here are for creating the abstract model, not the rendering
   see the Render module for plotting with matplotlib

   This module provides the `Model` class, which is used to represent a geometric model
   in 2D space. The `Model` class is based on the `list` data structure, and can contain
   points, lines, circles, polygons, and segments.



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

   geometor.model.Point
   geometor.model.Line
   geometor.model.Circle
   geometor.model.Polygon
   geometor.model.Segment
   geometor.model.GeometryObject


Classes
-------

.. autoapisummary::

   geometor.model.Element
   geometor.model.Wedge
   geometor.model.Section
   geometor.model.Chain
   geometor.model.Element
   geometor.model.Polynomial
   geometor.model.Model


Functions
---------

.. autoapisummary::

   geometor.model.load_model


Package Contents
----------------

.. py:data:: Point

.. py:data:: Line

.. py:data:: Circle

.. py:data:: Polygon

.. py:data:: Segment

.. py:class:: Element(sympy_obj, parents: list | None = None, classes: list[str] | None = None, ID: str = '', guide: bool = False)

   a container for special attributes of an element of a model that are
   not supported by the SymPy elements

   :param - ``sympy_obj``: The sympy object representing the geometric entity.
   :param - ``parents``: A list of parent elements (default is None).
   :type - ``parents``: list[objects]
   :param - ``classes``: A list of class labels (default is None).
   :type - ``classes``: list[str]
   :param - ``ID``:
                    - A string ID for the element
                    - if ID is none, a ID is generated
                    - is used as a reference in reports and plots
   :type - ``ID``: str

   .. attribute:: - ``ID``

      name used in presentation and reports

      :type: :class:`python:str`

   .. attribute:: - ``classes``

      dict with strings for class name

      :type: dict

   .. attribute:: - ``parents``

      dict with keys as parent sympy objects

      :type: dict


   .. py:attribute:: object


   .. py:attribute:: parents


   .. py:attribute:: classes


   .. py:attribute:: ID
      :value: ''



   .. py:attribute:: guide
      :value: False



   .. py:property:: length

      Returns the cleaned length of the element.
      For polygons, it returns the list of cleaned side lengths.


.. py:class:: Wedge(points: list[sympy.geometry.Point])

   .. py:attribute:: points


   .. py:attribute:: pt_center


   .. py:attribute:: pt_radius


   .. py:attribute:: pt_sweep_start


   .. py:attribute:: pt_sweep_end


   .. py:attribute:: sweep_ray


   .. py:attribute:: start_ray


   .. py:method:: __repr__()


   .. py:property:: circle
      :type: sympy.geometry.Circle



   .. py:property:: radians
      :type: sympy.Expr



   .. py:property:: degrees
      :type: sympy.Expr



   .. py:property:: ratio
      :type: sympy.Expr



   .. py:property:: area
      :type: sympy.Expr



   .. py:property:: arc_length
      :type: sympy.Expr



   .. py:property:: perimeter
      :type: sympy.Expr



.. py:class:: Section(points: list[sympy.geometry.Point])

   .. py:attribute:: points


   .. py:attribute:: segments


   .. py:attribute:: clean_expr


   .. py:method:: __eq__(other)


   .. py:method:: __hash__()


   .. py:method:: __repr__()


   .. py:method:: get_IDs(model) -> list[str]

      returns a list of IDs



   .. py:property:: ratio
      :type: sympy.Expr


      returns the ratio of the symbolic lengths of each segment


   .. py:property:: lengths
      :type: list[sympy.Expr]



   .. py:property:: floats
      :type: list[float]



   .. py:property:: is_golden
      :type: bool



   .. py:property:: min_length
      :type: sympy.Expr



   .. py:property:: min_float
      :type: float



   .. py:property:: min_segment
      :type: sympy.geometry.Segment



   .. py:property:: max_length
      :type: sympy.Expr



   .. py:property:: max_float
      :type: float



   .. py:property:: max_segment
      :type: sympy.geometry.Segment



.. py:class:: Chain(sections: list[geometor.model.sections.Section])

   A class representing a chain of connected golden sections,
   facilitating the extraction of segments, points, and lengths, as well as
   analyzing the flow and symmetry within the chain.

   Each chain’s flow is characterized by the comparative lengths of
   consecutive segments, represented symbolically to understand the
   progression and transitions in segment lengths. Furthermore, this module
   empowers users to explore symmetry lines within chains, unveiling a subtle,
   profound aspect of geometric harmony.



   .. py:attribute:: sections


   .. py:attribute:: segments
      :value: []



   .. py:attribute:: points
      :value: []



   .. py:method:: extract_segments() -> list[sympy.geometry.Segment]

      Extracts unique segments from the chain.

      :returns: A list containing the unique segments in the chain.
      :rtype: - :class:`list[spg.Segment]`



   .. py:method:: extract_points() -> list[sympy.geometry.Point]

      Extracts unique points from the chain while maintaining order.

      :returns: A list containing the ordered unique points from the chain.
      :rtype: - :class:`list[spg.Point]`



   .. py:property:: lengths
      :type: list[sympy.Expr]


      Extract the symbolic lengths of the segments in the chain.

      :returns: A list containing the symbolic lengths of each segment in the chain.
      :rtype: - :class:`list[sp.Expr]`


   .. py:property:: numerical_lengths
      :type: list[float]


      Calculate and extract the numerical lengths of the segments in the chain.

      :returns: A list containing the evaluated numerical lengths of each
                segment in the chain.
      :rtype: - :class:`list[float]`


   .. py:property:: flow
      :type: list[str]


      Determine the flow of the segments in the chain by comparing the lengths
      of consecutive segments.

      :returns: A list of symbols representing the flow of segment lengths. '>'
                indicates that the previous segment is longer, '<' indicates
                that the next segment is longer.
      :rtype: - :class:`list[str]`


   .. py:method:: count_symmetry_lines() -> int


   .. py:property:: fibonacci_IDs
      :type: list[str]


      Creates and returns Fibonacci-style IDs for each segment based on
      their lengths.

      :returns: A list of strings where each string is a Fibonacci-style
                ID corresponding to a segment.
      :rtype: - :class:`list[str]`


.. py:class:: Element(sympy_obj, parents: list | None = None, classes: list[str] | None = None, ID: str = '', guide: bool = False)

   a container for special attributes of an element of a model that are
   not supported by the SymPy elements

   :param - ``sympy_obj``: The sympy object representing the geometric entity.
   :param - ``parents``: A list of parent elements (default is None).
   :type - ``parents``: list[objects]
   :param - ``classes``: A list of class labels (default is None).
   :type - ``classes``: list[str]
   :param - ``ID``:
                    - A string ID for the element
                    - if ID is none, a ID is generated
                    - is used as a reference in reports and plots
   :type - ``ID``: str

   .. attribute:: - ``ID``

      name used in presentation and reports

      :type: :class:`python:str`

   .. attribute:: - ``classes``

      dict with strings for class name

      :type: dict

   .. attribute:: - ``parents``

      dict with keys as parent sympy objects

      :type: dict


   .. py:attribute:: object


   .. py:attribute:: parents


   .. py:attribute:: classes


   .. py:attribute:: ID
      :value: ''



   .. py:attribute:: guide
      :value: False



   .. py:property:: length

      Returns the cleaned length of the element.
      For polygons, it returns the list of cleaned side lengths.


.. py:class:: Polynomial(coeffs, name='', classes=None, group=None)

   Bases: :py:obj:`geometor.model.element.Element`


   A polynomial element defined by its coefficients.


   .. py:attribute:: x


   .. py:attribute:: y


   .. py:attribute:: coeffs


   .. py:attribute:: poly


   .. py:method:: __str__()


   .. py:method:: __repr__()


   .. py:method:: equation()


   .. py:method:: eval(val)


   .. py:method:: degree()


   .. py:method:: all_coeffs()


   .. py:method:: real_roots()


   .. py:method:: intersection(other)


   .. py:attribute:: object


   .. py:attribute:: parents


   .. py:attribute:: classes


   .. py:attribute:: ID
      :value: ''



   .. py:attribute:: guide
      :value: False



   .. py:property:: length

      Returns the cleaned length of the element.
      For polygons, it returns the list of cleaned side lengths.


.. py:function:: load_model(file_path, logger=None)

   Loads a model from a JSON file and returns a new Model instance.


.. py:class:: Model(name: str = '', logger=None)

   Bases: :py:obj:`dict`, :py:obj:`geometor.model.points.PointsMixin`, :py:obj:`geometor.model.lines.LinesMixin`, :py:obj:`geometor.model.circles.CirclesMixin`, :py:obj:`geometor.model.polygons.PolygonsMixin`, :py:obj:`geometor.model.segments.SegmentsMixin`, :py:obj:`geometor.model.polynomials.PolynomialsMixin`, :py:obj:`geometor.model.serialize.SerializeMixin`, :py:obj:`geometor.model.delete.DeleteMixin`, :py:obj:`geometor.model.sections.SectionsMixin`, :py:obj:`geometor.model.wedges.WedgesMixin`, :py:obj:`geometor.model.ancestors.AncestorsMixin`


   A collection of geometric elements, including points, lines, circles, and
   polygons, represented using the `sympy.geometry` library.


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

      control types for keys and values



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

      Find x, y limits from points and circles of the model



   .. py:attribute:: get_element_by_ID


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



   .. py:method:: construct_line_by_IDs(pt_1_ID: str, pt_2_ID: str, classes: list = None, ID: str = '') -> sympy.geometry.Line

      find points by ID and use them with :meth:`Model.construct_line`



   .. py:method:: construct_line(pt_1: sympy.geometry.Point, pt_2: sympy.geometry.Point, classes: list = None, ID: str = '', guide: bool = False) -> sympy.geometry.Line

      Constructs a :class:`Line <sympy.geometry.line.Line>` from two points and
      adds it to the :class:`Model <geometor.model.model.Model>`



   .. py:method:: construct_circle_by_IDs(pt_1_ID: str, pt_2_ID: str, classes: list = None, ID: str = '') -> sympy.geometry.Line

      find points by ID and use them with :meth:`Model.construct_line`



   .. py:method:: construct_circle(pt_center: sympy.geometry.Point, pt_radius: sympy.geometry.Point, classes: list = None, ID: str = '', guide: bool = False) -> sympy.geometry.Circle

      Constructs a Circle from two points and adds it to the model.



   .. py:method:: set_polygon_by_IDs(poly_pts_IDs: list[str], classes: list = None, ID: str = '') -> sympy.geometry.Polygon

      find points by ID and use them with :meth:`Model.set_polygon`



   .. py:method:: set_polygon(poly_pts: list[sympy.geometry.Point], classes=[], ID='') -> sympy.geometry.Polygon

      set polygon (list of 3 or more points)



   .. py:method:: set_segment_by_IDs(pt_1_ID: str, pt_2_ID: str, classes: list = None, ID: str = '') -> sympy.geometry.Segment

      find points by ID and use them with :meth:`Model.set_segment`



   .. py:method:: set_segment(pt_1: sympy.geometry.Point, pt_2: sympy.geometry.Point, classes=[], ID='') -> sympy.geometry.Segment

      set segment (list of points) for demonstration in the model



   .. py:method:: poly(coeffs: list, name: str = '', classes: list = [], group: str = '') -> Polynomial

      Create a Polynomial element.



   .. py:method:: add_poly(coeffs: list, name: str = '', classes: list = [], group: str = '') -> Polynomial

      Create and add a Polynomial element to the model.



   .. py:method:: save(file_path)

      Saves a Model object to a JSON file as a list of elements.



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



   .. py:method:: set_section_by_IDs(points_IDs: list[str], classes: list = None, ID: str = '') -> Section

      find points by ID and use them with :meth:`Model.set_section`



   .. py:method:: set_section(points: list[sympy.geometry.Point], classes=[], ID='') -> Section

      set section (list of 3 points on a line)



   .. py:method:: set_wedge(pt_center: sympy.geometry.Point, pt_radius: sympy.geometry.Point, pt_sweep_start: sympy.geometry.Point, pt_sweep_end: sympy.geometry.Point, direction='clockwise', classes: list = None, ID: str = '') -> Wedge

      sets a Wedge from 3 points and adds it to the model.

      operations
      ~~~~~~~~~~
      - create an instance of :class:`geometor.model.Wedge`
      - create a ``details`` object from :class:`Element`
      - add parents to details
          initial parents are the two starting points
      - check for duplicates in in the ``model``
      - find intersection points for new element with all precedng elements
      - Add ``circle`` to the model.

      :param - ``pt_center``:
      :type - ``pt_center``: :class:`sympy.geometry.point.Point` : point for circle center
      :param - ``pt_radius``:
      :type - ``pt_radius``: :class:`sympy.geometry.point.Point` : point to mark radius
      :param - ``pt_end``:
      :type - ``pt_end``: :class:`sympy.geometry.point.Point` : A SymPy Point marking the sweep of the wedge
      :param - ``classes``:
      :type - ``classes``: :class:`list` *optional* : A list of string names for classes defining a set of styles. Defaults to None.
      :param - ``ID``:
      :type - ``ID``: :class:`str` *optional* : A text ID for use in plotting and reporting. Defaults to an empty string.

      :returns: The portion of a circle
      :rtype: - :class:`Wedge`

      .. rubric:: Example

      >>> from geometor.elements import *
      >>> model = Model("demo")
      >>> A = model.set_point(0, 0, classes=["given"], ID="A")
      >>> B = model.set_point(1, 0, classes=["given"], ID="B")
      >>> model.construct_circle(A, B)
      >>> model.construct_circle(B, A)
      >>> model._set_wedge_by_IDs('A', 'B', 'C')
      <Wedge object ...>

      .. rubric:: Notes

      SymPy defines a circle as a center point and a radius length, so the radius length is calculated for the spg.Circle.



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



.. py:data:: GeometryObject

