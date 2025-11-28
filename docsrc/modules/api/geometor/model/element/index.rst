geometor.model.element
======================

.. py:module:: geometor.model.element

.. autoapi-nested-parse::

   Element type
   ElementDetails class
   intersection functions



Attributes
----------

.. autoapisummary::

   geometor.model.element.Struct


Classes
-------

.. autoapisummary::

   geometor.model.element.Element
   geometor.model.element.CircleElement


Module Contents
---------------

.. py:data:: Struct

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


.. py:class:: CircleElement(sympy_obj: sympy.geometry.Circle, pt_radius: sympy.geometry.Point, parents: list | None = None, classes: list[str] | None = None, ID: str = '', guide: bool = False)

   Bases: :py:obj:`Element`


   same as :class:`Element` but adds a ``pt_radius``

   :param - ``sympy_obj``: The sympy object representing the geometric entity.
   :param - ``pt_radius``: A list of parent elements (default is None).
   :type - ``pt_radius``: spg.Point
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


   .. py:attribute:: pt_radius


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


