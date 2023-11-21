


# GEOMETOR • model


`geometor.model` is the foundational library for the [GEOMETOR](https://geometor.com) initiative.


![_images/splash.png](_images/splash.png)
At the core of the module is the `Model` class which establishes the field
and methods of operation for creating the geometric constructions while maintaining integrity.


The **field** might be easy to consider as a Cartesian grid. But in reality, it
is an ordered set of information and operations. Points are the information.
Lines and circles are the operations.


In our system, all geometric elements of the `Model` are defined as [Sympy Geometry](https://docs.sympy.org/latest/modules/geometry/index.html)
objects. This means a `Point` can be defined as a pair of any algebraic
[Sympy Expressions](https://docs.sympy.org/latest/tutorials/intro-tutorial/basic_operations.html) that can be evaluated into a floating point value.


`Line` and `Circle` are each defined by two points. So each construction
must begin with at least two given points at the start. As lines and circles
are added, intersection points are discovered with previous lines and circles
and added to the model, so they may be used with new lines and circles.


There are three main operations of the `Model`:


* set\_point
* construct\_line
* construct\_circle


The major responsibilities of the `Model`:


* **deduplicate**


when elements are added to the model, we check to see if they already exist. This is particularly important for intersection points that often coincide with exisitng points.
* **clean values**
* discover **intersections**
* **save** to and load from json
* maintain a set of **related** info for each element:


	+ ancestral relationships
	+ establish labels for elements
	+ classes for styles


All of the plotting functionality has moved to **GEOMETOR** [render](https://github.com/geometor/render). However, there are several report functions in the this module:


* report\_summary
* report\_group\_by\_type
* report\_sequence


![_images/screenshot.png](_images/screenshot.png)

## recent logs






## contents




### mission


The mission of this `geometor.model` project is to establish a rigorous
system for defining classical geometric constructions of points, lines and
circles. But in our case, we are not using straight edge and compass. We are
creating the geometric elements as expressions in symbolic algebra thanks to
the power of the [`Sympy`\_](#id1) library.



#### goals







### usage


In this simple example, we create the classic *vesica pisces*



```
from geometor.model import \*

model = Model("vesica")
A = model.set\_point(0, 0, classes=["given"])
B = model.set\_point(1, 0, classes=["given"])

model.construct\_line(A, B)

model.construct\_circle(A, B)
model.construct\_circle(B, A)

E = model.get\_element\_by\_label("E")
F = model.get\_element\_by\_label("F")

model.set\_polygon([A, B, E])
model.set\_polygon([A, B, F])

model.construct\_line(E, F)

report\_summary(model)
report\_group\_by\_type(model)
report\_sequence(model)

model.save("vesica.json")

```




### modules


[geometor.model](index.html#document-modules/geometor.model) is the primary module of the **GEOMETOR** initiative.


It represents the foundation of our geometric exploration.




#### geometor.model


The Model module provides a set of tools for constructing geometric models.
It relies heavily on sympy for providing the algebraic infrastructure
the functions here are for creating the abstract model, not the rendering
see the Render module for plotting with matplotlib


This module provides the Model class, which is used to represent a geometric model
in 2D space. The Model class is based on the list data structure, and can contain
points, lines, circles, polygons, and segments.




*class* geometor.model.Model(*name: [str](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)") = ''*)
Bases: [`dict`](https://docs.python.org/3.9/library/stdtypes.html#dict "(in Python v3.9)")


A collection of geometric elements, including points, lines, circles, and
polygons, represented using the sympy.geometry library.


When lines and circles are added to the model, intersection points of the
new element with the preceding elements are identify and added.


When new elements or points are added to the model, we check for existing
duplicates.



##### parameters


* `name`[`str`](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)")establish name for the model instance




##### attributes


* [`name`](#geometor.model.Model.name "geometor.model.Model.name") -> [`str`](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)") *name of the model*
* [`points`](#geometor.model.Model.points "geometor.model.Model.points") -> [`list`](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)") [[`Point`](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)")]
* [`lines`](#geometor.model.Model.lines "geometor.model.Model.lines") -> [`list`](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)") [`Line`]
* [`circles`](#geometor.model.Model.circles "geometor.model.Model.circles") -> [`list`](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)") [`Circle`]
* [`structs`](#geometor.model.Model.structs "geometor.model.Model.structs") -> [`list`](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)") [Struct]returns list of structs (lines and circles) in the Model




##### methods


* [`set\_point()`](#geometor.model.Model.set_point "geometor.model.Model.set_point") -> [`Point`](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)")
* [`construct\_line()`](#geometor.model.Model.construct_line "geometor.model.Model.construct_line") -> [`Line`](https://docs.sympy.org/latest/modules/geometry/lines.html#sympy.geometry.line.Line "(in SymPy v1.12)")
* [`construct\_line\_by\_labels()`](#geometor.model.Model.construct_line_by_labels "geometor.model.Model.construct_line_by_labels") -> [`Line`](https://docs.sympy.org/latest/modules/geometry/lines.html#sympy.geometry.line.Line "(in SymPy v1.12)")
* [`construct\_circle()`](#geometor.model.Model.construct_circle "geometor.model.Model.construct_circle") -> [`Circle`](https://docs.sympy.org/latest/modules/geometry/ellipses.html#sympy.geometry.ellipse.Circle "(in SymPy v1.12)")
* [`construct\_circle\_by\_labels()`](#geometor.model.Model.construct_circle_by_labels "geometor.model.Model.construct_circle_by_labels") -> [`Circle`](https://docs.sympy.org/latest/modules/geometry/ellipses.html#sympy.geometry.ellipse.Circle "(in SymPy v1.12)")
* [`set\_segment()`](#geometor.model.Model.set_segment "geometor.model.Model.set_segment") -> [`Segment`](https://docs.sympy.org/latest/modules/geometry/lines.html#sympy.geometry.line.Segment "(in SymPy v1.12)")
* [`set\_segment\_by\_labels()`](#geometor.model.Model.set_segment_by_labels "geometor.model.Model.set_segment_by_labels") -> [`Segment`](https://docs.sympy.org/latest/modules/geometry/lines.html#sympy.geometry.line.Segment "(in SymPy v1.12)")
* [`set\_polygon()`](#geometor.model.Model.set_polygon "geometor.model.Model.set_polygon") -> [`Polygon`](https://docs.sympy.org/latest/modules/geometry/polygons.html#sympy.geometry.polygon.Polygon "(in SymPy v1.12)")
* [`set\_polygon\_by\_labels()`](#geometor.model.Model.set_polygon_by_labels "geometor.model.Model.set_polygon_by_labels") -> [`Polygon`](https://docs.sympy.org/latest/modules/geometry/polygons.html#sympy.geometry.polygon.Polygon "(in SymPy v1.12)")
* [`set\_wedge()`](#geometor.model.Model.set_wedge "geometor.model.Model.set_wedge") -> `Wedge`
* [`limits()`](#geometor.model.Model.limits "geometor.model.Model.limits") -> [`list`](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)")returns the x, y limits of the points and circle boundaries in the model
* [`get\_ancestors()`](#geometor.model.Model.get_ancestors "geometor.model.Model.get_ancestors") ->
* [`get\_ancestors\_labels()`](#geometor.model.Model.get_ancestors_labels "geometor.model.Model.get_ancestors_labels") ->
* [`get\_element\_by\_label()`](#geometor.model.Model.get_element_by_label "geometor.model.Model.get_element_by_label") ->
* [`save()`](#geometor.model.Model.save "geometor.model.Model.save") ->
* [`load()`](#geometor.model.Model.load "geometor.model.Model.load") ->
* [`point\_label\_generator()`](#geometor.model.Model.point_label_generator "geometor.model.Model.point_label_generator") -> Iterator[str]



Todo


add get\_bounds\_polygon method to Model





*property* name*: [str](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)")*
The name of the model





set\_point(*x\_val: [Expr](https://docs.sympy.org/latest/modules/core.html#sympy.core.expr.Expr "(in SymPy v1.12)")*, *y\_val: [Expr](https://docs.sympy.org/latest/modules/core.html#sympy.core.expr.Expr "(in SymPy v1.12)")*, *parents: [list](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)") | [None](https://docs.python.org/3.9/library/constants.html#None "(in Python v3.9)") = None*, *classes: [list](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)") | [None](https://docs.python.org/3.9/library/constants.html#None "(in Python v3.9)") = None*, *label: [str](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)") = ''*) → [Point](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)")
Adds a point to the model, finds duplicates, cleans values, and sets
parents and classes.



###### parameters


* `x\_val` : [`sympy.core.expr.Expr`](https://docs.sympy.org/latest/modules/core.html#sympy.core.expr.Expr "(in SymPy v1.12)"): The x-value of the point.
* `y\_val` : [`sympy.core.expr.Expr`](https://docs.sympy.org/latest/modules/core.html#sympy.core.expr.Expr "(in SymPy v1.12)"): The y-value of the point.
* `parents` : list, optional: A list of parent elements or references.
Defaults to None.
* `classes` list, optional: A list of string names for classes defining
a set of styles. Defaults to None.
* `label` str, optional: A text label for use in plotting and
reporting. Defaults to an empty string.




###### returns


* [`sympy.geometry.point.Point`](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)"): The set point.




###### example



```
>>> from geometor.model import \*
>>> model = Model("demo")
>>> model.set\_point(0, 0, classes=["given"])
<spg.Point object ...>

```




###### notes


The function simplifies the x and y values before adding, and it updates the attributes if the point is already in the model.






construct\_line(*pt\_1: [Point](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)")*, *pt\_2: [Point](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)")*, *classes: [list](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)") | [None](https://docs.python.org/3.9/library/constants.html#None "(in Python v3.9)") = None*, *label: [str](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)") = ''*) → [Line](https://docs.sympy.org/latest/modules/geometry/lines.html#sympy.geometry.line.Line "(in SymPy v1.12)")
Constructs a [`Line`](https://docs.sympy.org/latest/modules/geometry/lines.html#sympy.geometry.line.Line "(in SymPy v1.12)") from two points and
adds it to the `Model`



###### parameters


* `pt\_1` : [`sympy.geometry.point.Point`](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)") *A SymPy Point marking the
first point of the line*
* `pt\_2` : [`sympy.geometry.point.Point`](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)"): A SymPy Point marking the
second point of the line
* `classes` : list: Additional classes (optional)
* `label` : str: Label for the line (optional)




###### returns


* [`sympy.geometry.line.Line`](https://docs.sympy.org/latest/modules/geometry/lines.html#sympy.geometry.line.Line "(in SymPy v1.12)"): The constructed line




###### example



```
>>> from geometor.elements import \*
>>> model = Model("demo")
>>> A = model.set\_point(0, 0, classes=["given"], label="A")
>>> B = model.set\_point(1, 0, classes=["given"], label="B")
>>> model.construct\_line(A, B)
<spg.Line object ...>

```




###### operations


* create an instance of `spg.Line`
* create a `details` object from `Element`
* add parents to details
* check for duplicates in elements.
* find intersection points for new element with all precedng elements
* Add `line` to the model.






construct\_line\_by\_labels(*pt\_1\_label: [str](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)")*, *pt\_2\_label: [str](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)")*, *classes: [list](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)") | [None](https://docs.python.org/3.9/library/constants.html#None "(in Python v3.9)") = None*, *label: [str](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)") = ''*) → [Line](https://docs.sympy.org/latest/modules/geometry/lines.html#sympy.geometry.line.Line "(in SymPy v1.12)")
find points by label and use them with [`Model.construct\_line()`](#geometor.model.Model.construct_line "geometor.model.Model.construct_line")





construct\_circle(*pt\_center: [Point](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)")*, *pt\_radius: [Point](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)")*, *classes: [list](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)") | [None](https://docs.python.org/3.9/library/constants.html#None "(in Python v3.9)") = None*, *label: [str](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)") = ''*) → [Circle](https://docs.sympy.org/latest/modules/geometry/ellipses.html#sympy.geometry.ellipse.Circle "(in SymPy v1.12)")
Constructs a Circle from two points and adds it to the model.



###### operations


* create an instance of `sympy.geometry.ellipse.Circle`as ``circle``
* create a `details` object from `Element`
* add parents to detailsinitial parents are the two starting points
* check for duplicates in in the `model`
* find intersection points for new element with all precedng elements
* Add `circle` to the model.




###### parameters


* `pt\_center` : [`sympy.geometry.point.Point`](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)") A SymPy Point representing the circle center.
* `pt\_radius` : [`sympy.geometry.point.Point`](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)") A SymPy Point marking the length of the radius.
* `classes` : [`list`](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)") *optional* A list of string names for classes defining a set of styles. Defaults to None.
* `label` : [`str`](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)") *optional* A text label for use in plotting and reporting. Defaults to an empty string.




###### returns


* [`Circle`](https://docs.sympy.org/latest/modules/geometry/ellipses.html#sympy.geometry.ellipse.Circle "(in SymPy v1.12)"):The constructed circle.




###### example



```
>>> from geometor.elements import \*
>>> model = Model("demo")
>>> A = model.set\_point(0, 0, classes=["given"], label="A")
>>> B = model.set\_point(1, 0, classes=["given"], label="B")
>>> model.construct\_circle(A, B)
<spg.Circle object ...>

```




###### notes


SymPy defines a circle as a center point and a radius length, so the radius length is calculated for the spg.Circle.






construct\_circle\_by\_labels(*pt\_1\_label: [str](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)")*, *pt\_2\_label: [str](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)")*, *classes: [list](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)") | [None](https://docs.python.org/3.9/library/constants.html#None "(in Python v3.9)") = None*, *label: [str](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)") = ''*) → [Line](https://docs.sympy.org/latest/modules/geometry/lines.html#sympy.geometry.line.Line "(in SymPy v1.12)")
find points by label and use them with [`Model.construct\_line()`](#geometor.model.Model.construct_line "geometor.model.Model.construct_line")





set\_segment(*pt\_1: [Point](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)")*, *pt\_2: [Point](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)")*, *classes=[]*, *label=''*) → [Segment](https://docs.sympy.org/latest/modules/geometry/lines.html#sympy.geometry.line.Segment "(in SymPy v1.12)")
set segment (list of points) for demonstration in the model





set\_segment\_by\_labels(*pt\_1\_label: [str](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)")*, *pt\_2\_label: [str](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)")*, *classes: [list](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)") | [None](https://docs.python.org/3.9/library/constants.html#None "(in Python v3.9)") = None*, *label: [str](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)") = ''*) → [Line](https://docs.sympy.org/latest/modules/geometry/lines.html#sympy.geometry.line.Line "(in SymPy v1.12)")
find points by label and use them with [`Model.construct\_line()`](#geometor.model.Model.construct_line "geometor.model.Model.construct_line")





set\_polygon(*poly\_pts: [list](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)")[[sympy.geometry.point.Point](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)")]*, *classes=[]*, *label=''*) → [Polygon](https://docs.sympy.org/latest/modules/geometry/polygons.html#sympy.geometry.polygon.Polygon "(in SymPy v1.12)")
set polygon (list of 3 or more points)





set\_polygon\_by\_labels(*poly\_pts\_labels: [list](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)")[[str](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)")]*, *classes: [list](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)") | [None](https://docs.python.org/3.9/library/constants.html#None "(in Python v3.9)") = None*, *label: [str](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)") = ''*) → [Line](https://docs.sympy.org/latest/modules/geometry/lines.html#sympy.geometry.line.Line "(in SymPy v1.12)")
find points by label and use them with [`Model.construct\_line()`](#geometor.model.Model.construct_line "geometor.model.Model.construct_line")





set\_wedge(*pt\_center: [Point](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)")*, *pt\_radius: [Point](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)")*, *pt\_sweep\_start: [Point](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)")*, *pt\_sweep\_end: [Point](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)")*, *direction='clockwise'*, *classes: [list](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)") | [None](https://docs.python.org/3.9/library/constants.html#None "(in Python v3.9)") = None*, *label: [str](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)") = ''*) → [Wedge](index.html#geometor.model.wedges.Wedge "geometor.model.wedges.Wedge")
sets a Wedge from 3 points and adds it to the model.



###### operations


* create an instance of `geometor.model.Wedge`
* create a `details` object from `Element`
* add parents to detailsinitial parents are the two starting points
* check for duplicates in in the `model`
* find intersection points for new element with all precedng elements
* Add `circle` to the model.



###### parameters


* `pt\_center` : [`sympy.geometry.point.Point`](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)") : point for circle center
* `pt\_radius` : [`sympy.geometry.point.Point`](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)") : point to mark radius
* `pt\_end` : [`sympy.geometry.point.Point`](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)") : A SymPy Point marking the sweep of the wedge
* `classes` : [`list`](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)") *optional* : A list of string names for classes defining a set of styles. Defaults to None.
* `label` : [`str`](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)") *optional* : A text label for use in plotting and reporting. Defaults to an empty string.




###### returns


* `Wedge`The portion of a circle




###### example



```
>>> from geometor.elements import \*
>>> model = Model("demo")
>>> A = model.set\_point(0, 0, classes=["given"], label="A")
>>> B = model.set\_point(1, 0, classes=["given"], label="B")
>>> model.construct\_circle(A, B)
>>> model.construct\_circle(B, A)
>>> model.\_set\_wedge\_by\_labels('A', 'B', 'C')
<Wedge object ...>

```




###### notes


SymPy defines a circle as a center point and a radius length, so the radius length is calculated for the spg.Circle.







remove\_by\_label(*label: [str](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)")*) → [None](https://docs.python.org/3.9/library/constants.html#None "(in Python v3.9)")



*property* points*: [list](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)")[[sympy.geometry.point.Point](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)")]*
returns point elements from model as list





*property* structs*: [list](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)")[[sympy.geometry.line.Line](https://docs.sympy.org/latest/modules/geometry/lines.html#sympy.geometry.line.Line "(in SymPy v1.12)") | [sympy.geometry.ellipse.Circle](https://docs.sympy.org/latest/modules/geometry/ellipses.html#sympy.geometry.ellipse.Circle "(in SymPy v1.12)")]*
returns struct elements (line or circle) from model as list





*property* lines*: [list](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)")[[sympy.geometry.line.Line](https://docs.sympy.org/latest/modules/geometry/lines.html#sympy.geometry.line.Line "(in SymPy v1.12)")]*
returns line elements from model as list





*property* circles*: [list](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)")[[sympy.geometry.ellipse.Circle](https://docs.sympy.org/latest/modules/geometry/ellipses.html#sympy.geometry.ellipse.Circle "(in SymPy v1.12)")]*
returns circle elements from model as list





limits() → [tuple](https://docs.python.org/3.9/library/stdtypes.html#tuple "(in Python v3.9)")[[tuple](https://docs.python.org/3.9/library/stdtypes.html#tuple "(in Python v3.9)")[[float](https://docs.python.org/3.9/library/functions.html#float "(in Python v3.9)"), [float](https://docs.python.org/3.9/library/functions.html#float "(in Python v3.9)")], [tuple](https://docs.python.org/3.9/library/stdtypes.html#tuple "(in Python v3.9)")[[float](https://docs.python.org/3.9/library/functions.html#float "(in Python v3.9)"), [float](https://docs.python.org/3.9/library/functions.html#float "(in Python v3.9)")]]
Find x, y limits from points and circles of the model



Returns a list of x, y limits:`((x\_min, x\_max), (y\_min, y\_max))`







get\_ancestors(*element*)
Retrieves the ancestors for the given element.


The method recursively traverses the parent elements of the given element
and constructs a nested dictionary representing the ancestor tree.



###### parameters


* elementsympy.geometry objectThe element for which the ancestors are to be retrieved.




###### returns


* dict : A nested dictionary representing the ancestors.




###### example


If element A has parents B and C, and B has parent D, the method returns:
{A: {B: {D: {}}, C: {}}}






get\_ancestors\_labels(*element*) → [dict](https://docs.python.org/3.9/library/stdtypes.html#dict "(in Python v3.9)")[[str](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)"), [dict](https://docs.python.org/3.9/library/stdtypes.html#dict "(in Python v3.9)")]
Retrieves the labels of the ancestors for the given element.


The method recursively traverses the parent elements of the given element
and constructs a nested dictionary with labels representing the ancestor tree.



###### parameters


* elementsympy.geometry objectThe element for which the ancestors’ labels are to be retrieved.


returns
- dict : A nested dictionary representing the labels of the ancestors.




###### example


If element A has parents B and C, and B has parent D, the method returns:
{‘A’: {‘B’: {‘D’: {}}, ‘C’: {}}}






get\_element\_by\_label(*label: [str](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)")*)
Finds and returns the element with the given label.



###### parameters


* `label` : [`str`](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)"): The label of the desired element.




###### returns


Element or None: The element with the matching label, or None if no match is found.






save(*file\_path*)



*classmethod* load(*file\_path*)



point\_label\_generator() → [Iterator](https://docs.python.org/3.9/library/collections.abc.html#collections.abc.Iterator "(in Python v3.9)")[[str](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)")]





#### geometor.model.element


Element type
ElementDetails class
intersection functions




*class* geometor.model.element.Element(*sympy\_obj*, *parents: [list](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)") | [None](https://docs.python.org/3.9/library/constants.html#None "(in Python v3.9)") = None*, *classes: [list](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)")[[str](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)")] | [None](https://docs.python.org/3.9/library/constants.html#None "(in Python v3.9)") = None*, *label: [str](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)") = ''*)
Bases: [`object`](https://docs.python.org/3.9/library/functions.html#object "(in Python v3.9)")


a container for special attributes of an element of a model that are
not supported by the SymPy elements



##### parameters


* `sympy\_obj` :The sympy object representing the geometric entity.
* `parents`list[objects]A list of parent elements (default is None).
* `classes`list[str]A list of class labels (default is None).
* `label`str
	+ A string label for the element
	+ if label is none, a label is generated
	+ is used as a reference in reports and plots




##### attributes


* `label`[`str`](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)")name used in presentation and reports
* `classes`dictdict with strings for class name
* `parents`dictdict with keys as parent sympy objects






*class* geometor.model.element.CircleElement(*sympy\_obj: [Circle](https://docs.sympy.org/latest/modules/geometry/ellipses.html#sympy.geometry.ellipse.Circle "(in SymPy v1.12)")*, *pt\_radius: [Point](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)")*, *parents: [list](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)") | [None](https://docs.python.org/3.9/library/constants.html#None "(in Python v3.9)") = None*, *classes: [list](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)")[[str](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)")] | [None](https://docs.python.org/3.9/library/constants.html#None "(in Python v3.9)") = None*, *label: [str](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)") = ''*)
Bases: [`Element`](#geometor.model.element.Element "geometor.model.element.Element")


same as [`Element`](#geometor.model.element.Element "geometor.model.element.Element") but adds a `pt\_radius`



##### parameters


* `sympy\_obj` :The sympy object representing the geometric entity.
* `pt\_radius`spg.PointA list of parent elements (default is None).
* `parents`list[objects]A list of parent elements (default is None).
* `classes`list[str]A list of class labels (default is None).
* `label`str
	+ A string label for the element
	+ if label is none, a label is generated
	+ is used as a reference in reports and plots




##### attributes


* `label`[`str`](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)")name used in presentation and reports
* `classes`dictdict with strings for class name
* `parents`dictdict with keys as parent sympy objects






geometor.model.element.check\_existence(*self*, *struct: [Line](https://docs.sympy.org/latest/modules/geometry/lines.html#sympy.geometry.line.Line "(in SymPy v1.12)") | [Circle](https://docs.sympy.org/latest/modules/geometry/ellipses.html#sympy.geometry.ellipse.Circle "(in SymPy v1.12)")*, *existing\_structs: [list](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)")[[sympy.geometry.line.Line](https://docs.sympy.org/latest/modules/geometry/lines.html#sympy.geometry.line.Line "(in SymPy v1.12)") | [sympy.geometry.ellipse.Circle](https://docs.sympy.org/latest/modules/geometry/ellipses.html#sympy.geometry.ellipse.Circle "(in SymPy v1.12)")]*) → [tuple](https://docs.python.org/3.9/library/stdtypes.html#tuple "(in Python v3.9)")[[bool](https://docs.python.org/3.9/library/functions.html#bool "(in Python v3.9)"), [sympy.geometry.line.Line](https://docs.sympy.org/latest/modules/geometry/lines.html#sympy.geometry.line.Line "(in SymPy v1.12)") | [sympy.geometry.ellipse.Circle](https://docs.sympy.org/latest/modules/geometry/ellipses.html#sympy.geometry.ellipse.Circle "(in SymPy v1.12)")]
Check if a geometric structure exists in the model.





geometor.model.element.find\_all\_intersections(*self*, *struct: [Line](https://docs.sympy.org/latest/modules/geometry/lines.html#sympy.geometry.line.Line "(in SymPy v1.12)") | [Circle](https://docs.sympy.org/latest/modules/geometry/ellipses.html#sympy.geometry.ellipse.Circle "(in SymPy v1.12)")*) → [None](https://docs.python.org/3.9/library/constants.html#None "(in Python v3.9)")
find all intersections in the model for the given struct





geometor.model.element.find\_intersection(*test\_tuple: [tuple](https://docs.python.org/3.9/library/stdtypes.html#tuple "(in Python v3.9)")*) → [tuple](https://docs.python.org/3.9/library/stdtypes.html#tuple "(in Python v3.9)")
find intersection for two structs





#### geometor.model.wedges


wedge functions for Model class




*class* geometor.model.wedges.Wedge(*pt\_center: [Point](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)")*, *pt\_radius: [Point](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)")*, *pt\_sweep\_start: [Point](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)")*, *pt\_sweep\_end: [Point](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)")*, *direction: [str](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)") = 'clockwise'*)
Bases: [`object`](https://docs.python.org/3.9/library/functions.html#object "(in Python v3.9)")




*property* circle*: [Circle](https://docs.sympy.org/latest/modules/geometry/ellipses.html#sympy.geometry.ellipse.Circle "(in SymPy v1.12)")*



*property* radians*: [Expr](https://docs.sympy.org/latest/modules/core.html#sympy.core.expr.Expr "(in SymPy v1.12)")*



*property* degrees*: [Expr](https://docs.sympy.org/latest/modules/core.html#sympy.core.expr.Expr "(in SymPy v1.12)")*



*property* ratio*: [Expr](https://docs.sympy.org/latest/modules/core.html#sympy.core.expr.Expr "(in SymPy v1.12)")*



*property* area*: [Expr](https://docs.sympy.org/latest/modules/core.html#sympy.core.expr.Expr "(in SymPy v1.12)")*



*property* arc\_length*: [Expr](https://docs.sympy.org/latest/modules/core.html#sympy.core.expr.Expr "(in SymPy v1.12)")*



*property* perimeter*: [Expr](https://docs.sympy.org/latest/modules/core.html#sympy.core.expr.Expr "(in SymPy v1.12)")*




#### geometor.model.sections


section functions for Model class




*class* geometor.model.sections.Section(*points: [list](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)")[[sympy.geometry.point.Point](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)")]*)
Bases: [`object`](https://docs.python.org/3.9/library/functions.html#object "(in Python v3.9)")




get\_labels(*model*) → [list](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)")[[str](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)")]
returns a list of labels





*property* ratio*: [Expr](https://docs.sympy.org/latest/modules/core.html#sympy.core.expr.Expr "(in SymPy v1.12)")*
returns the ratio of the symbolic lengths of each segment





*property* lengths*: [list](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)")[[sympy.core.expr.Expr](https://docs.sympy.org/latest/modules/core.html#sympy.core.expr.Expr "(in SymPy v1.12)")]*



*property* floats*: [list](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)")[[float](https://docs.python.org/3.9/library/functions.html#float "(in Python v3.9)")]*



*property* is\_golden*: [bool](https://docs.python.org/3.9/library/functions.html#bool "(in Python v3.9)")*



*property* min\_length*: [Expr](https://docs.sympy.org/latest/modules/core.html#sympy.core.expr.Expr "(in SymPy v1.12)")*



*property* min\_float*: [float](https://docs.python.org/3.9/library/functions.html#float "(in Python v3.9)")*



*property* min\_segment*: [Segment](https://docs.sympy.org/latest/modules/geometry/lines.html#sympy.geometry.line.Segment "(in SymPy v1.12)")*



*property* max\_length*: [Expr](https://docs.sympy.org/latest/modules/core.html#sympy.core.expr.Expr "(in SymPy v1.12)")*



*property* max\_float*: [float](https://docs.python.org/3.9/library/functions.html#float "(in Python v3.9)")*



*property* max\_segment*: [Segment](https://docs.sympy.org/latest/modules/geometry/lines.html#sympy.geometry.line.Segment "(in SymPy v1.12)")*




#### geometor.model.chains




*class* geometor.model.chains.Chain(*sections: [list](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)")[[geometor.model.sections.Section](index.html#geometor.model.sections.Section "geometor.model.sections.Section")]*)
Bases: [`object`](https://docs.python.org/3.9/library/functions.html#object "(in Python v3.9)")


A class representing a chain of connected golden sections,
facilitating the extraction of segments, points, and lengths, as well as
analyzing the flow and symmetry within the chain.


Each chain’s flow is characterized by the comparative lengths of
consecutive segments, represented symbolically to understand the
progression and transitions in segment lengths. Furthermore, this module
empowers users to explore symmetry lines within chains, unveiling a subtle,
profound aspect of geometric harmony.




extract\_segments() → [list](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)")[[sympy.geometry.line.Segment](https://docs.sympy.org/latest/modules/geometry/lines.html#sympy.geometry.line.Segment "(in SymPy v1.12)")]
Extracts unique segments from the chain.



##### returns


* `list[spg.Segment]`A list containing the unique segments in the chain.






extract\_points() → [list](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)")[[sympy.geometry.point.Point](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)")]
Extracts unique points from the chain while maintaining order.



##### returns


* `list[spg.Point]`A list containing the ordered unique points from the chain.






*property* lengths*: [list](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)")[[sympy.core.expr.Expr](https://docs.sympy.org/latest/modules/core.html#sympy.core.expr.Expr "(in SymPy v1.12)")]*
Extract the symbolic lengths of the segments in the chain.



##### returns


* `list[sp.Expr]`A list containing the symbolic lengths of each segment in the chain.






*property* numerical\_lengths*: [list](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)")[[float](https://docs.python.org/3.9/library/functions.html#float "(in Python v3.9)")]*
Calculate and extract the numerical lengths of the segments in the chain.



##### returns


* `list[float]`A list containing the evaluated numerical lengths of each
segment in the chain.






*property* flow*: [list](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)")[[str](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)")]*
Determine the flow of the segments in the chain by comparing the lengths
of consecutive segments.



##### returns


* `list[str]`A list of symbols representing the flow of segment lengths. ‘>’
indicates that the previous segment is longer, ‘<’ indicates
that the next segment is longer.






count\_symmetry\_lines() → [int](https://docs.python.org/3.9/library/functions.html#int "(in Python v3.9)")



*property* fibonacci\_labels*: [list](https://docs.python.org/3.9/library/stdtypes.html#list "(in Python v3.9)")[[str](https://docs.python.org/3.9/library/stdtypes.html#str "(in Python v3.9)")]*
Creates and returns Fibonacci-style labels for each segment based on
their lengths.



##### returns


* `list[str]`A list of strings where each string is a Fibonacci-style 
label corresponding to a segment.







#### geometor.model.helpers


a few helper functions from earlier constructions


these types of operations need to be integrated into the euclid model




geometor.model.helpers.line\_get\_y(*l1*, *x*)
return y value for specific x





geometor.model.helpers.set\_given\_start\_points(*model*)
create inital two points -
establishing the unit for the field





geometor.model.helpers.set\_given\_start\_points\_zero(*model*)
create inital two points -
establishing the unit for the field





geometor.model.helpers.set\_equilateral\_poles(*model: [Model](index.html#geometor.model.Model "geometor.model.Model")*, *pt\_1: [Point](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)")*, *pt\_2: [Point](https://docs.sympy.org/latest/modules/geometry/points.html#sympy.geometry.point.Point "(in SymPy v1.12)")*, *add\_circles=True*)



geometor.model.helpers.construct\_perpendicular\_bisector(*model*, *pt\_1*, *pt\_2*, *add\_circles=True*)
perform fundamental operations for two points
and add perpendicular bisector





geometor.model.helpers.set\_midpoint(*model*, *pt\_1*, *pt\_2*, *add\_circles=True*)
perform fundamental operations for two points
and add perpendicular bisector





geometor.model.helpers.set\_given\_rect\_points(*model*, *pt*, *x\_offset*, *y\_offset*)



geometor.model.helpers.set\_given\_square\_points(*model*, *pt*, *offset*)



#### geometor.model.reports


report helper functions




geometor.model.reports.generate\_dot(*graph*, *parent=None*, *dot\_string=''*, *defined\_nodes=None*)



geometor.model.reports.report\_summary(*model*)



geometor.model.reports.report\_group\_by\_type(*model*)



geometor.model.reports.get\_colored\_label(*el*, *label*)
Get the colored label for a geometric element.





geometor.model.reports.report\_sequence(*model*)
Generate a sequential report of the model using rich Console layouts.





#### geometor.model.utils


utils




geometor.model.utils.clean\_expr(*expr*)
simplify and denest SymPy expressions





geometor.model.utils.spread(*l1: [Line](https://docs.sympy.org/latest/modules/geometry/lines.html#sympy.geometry.line.Line "(in SymPy v1.12)")*, *l2: [Line](https://docs.sympy.org/latest/modules/geometry/lines.html#sympy.geometry.line.Line "(in SymPy v1.12)")*)
calculate the spread of two lines





geometor.model.utils.compare\_points(*pt1*, *pt2*)



geometor.model.utils.point\_value(*pt*)



geometor.model.utils.sort\_points(*pts*)



geometor.model.utils.log\_init(*name*)



geometor.model.utils.print\_log(*txt=''*)



geometor.model.utils.elapsed(*start\_time*)





### demos




#### demo



```


```




#### vesica



```
"""
constructs the classic 'vesica pisces'
"""
from geometor.model import \*


def run():
    model = Model("vesica")
    A = model.set\_point(0, 0, classes=["given"])
    B = model.set\_point(1, 0, classes=["given"])

    model.construct\_line(A, B)

    model.construct\_circle(A, B)
    model.construct\_circle(B, A)

    E = model.get\_element\_by\_label("E")
    F = model.get\_element\_by\_label("F")

    model.set\_polygon([A, B, E])
    model.set\_polygon([A, B, F])

    model.construct\_line(E, F)

    report\_summary(model)
    report\_group\_by\_type(model)
    report\_sequence(model)

    model.save("vesica.json")


if \_\_name\_\_ == "\_\_main\_\_":
    run()

```






### references




#### sympy




#### matplotlib




#### textualize






### todos



Todo


add get\_bounds\_polygon method to Model



(The [*original entry*](index.html#id1) is located in /home/phiarchitect/PROJECTS/geometor/model/src/geometor/model/\_\_init\_\_.py:docstring of geometor.model.Model, line 50.)




### changelog



#### 0.1.0


*2023-11-15*


**fixed**


**added**


**changed**





### glossary



testa test item








## indices


* [Index](genindex.html)
* [Module Index](py-modindex.html)
* [Search Page](search.html)







