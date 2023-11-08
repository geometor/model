"""
wedge functions for Model class
"""

from geometor.model.common import *

from geometor.model.element import (
    Element,
    CircleElement,
    find_all_intersections,
    check_existence,
)


class Wedge:
    def __init__(
        self, pt_center, pt_radius, pt_sweep_start, pt_sweep_end, direction="clockwise"
    ):
        #  super().__init__(*args)
        self._circle = spg.Circle(pt_center, pt_center.distance(pt_radius))

        self.pt_center = pt_center
        self.pt_radius = pt_radius
        self.sweep_ray = spg.Ray(pt_center, pt_sweep_end)
        self.start_ray = spg.Ray(
            pt_center, pt_sweep_start if pt_sweep_start else radius_point
        )

        self.start_point, self.end_point = self._find_arc_endpoints()
        self.direction = direction

        self.points = [pt_center, pt_radius, pt_sweep_start, pt_sweep_end]

    def _find_arc_endpoints(self):
        intersections_start = self.circle.intersection(self.start_ray)
        intersections_sweep = self.circle.intersection(self.sweep_ray)

        # Ensure the rays intersect the circle
        if intersections_start and intersections_sweep:
            return intersections_start[0], intersections_sweep[0]
        else:
            raise ValueError("Rays do not intersect the circle.")

    @property
    def circle(self):
        return self._circle

    @property
    def radians(self):
        angle = self.start_ray.angle_between(self.sweep_ray)
        return angle if self.direction == "clockwise" else 2 * sp.pi - angle

    @property
    def degrees(self):
        return sp.deg(self.radians)

    @property
    def ratio(self):
        return self.radians / (2 * sp.pi)

    @property
    def area(self):
        # Using the ratio of the angle to the full circle to find the area
        return self.circle.area * self.ratio

    @property
    def arc_length(self):
        # Using the ratio of the angle to the full circle to find the arc length
        return self.circle.circumference * self.ratio

    @property
    def perimeter(self):
        # Including the two radii to form the full boundary of the wedge
        return self.arc_length + 2 * self.circle.radius


def _set_wedge_by_labels(
    model, pt_1_label: str, pt_2_label: str, classes: list = None, label: str = ""
) -> Wedge:
    """
    find points by label and use them with :meth:`Model.construct_line`
    """

    pt_1 = model.get_element_by_label(pt_1_label)
    pt_2 = model.get_element_by_label(pt_2_label)
    model.construct_circle(pt_1, pt_2, classes, label)


def _set_wedge(
    model,
    pt_center: spg.Point,
    pt_radius: spg.Point,
    pt_sweep_start: spg.Point,
    pt_sweep_end: spg.Point,
    direction="clockwise",
    classes: list = None,
    label: str = "",
) -> Wedge:
    """
    sets a Wedge from 3 points and adds it to the model.

    operations
    ----------
    - create an instance of :class:`geometor.model.Wedge`
    - create a ``details`` object from :class:`Element`
    - add parents to details
        initial parents are the two starting points
    - check for duplicates in in the ``model``
    - find intersection points for new element with all precedng elements
    - Add ``circle`` to the model.

    parameters
    ----------
    - ``pt_center`` : :class:`sympy.geometry.point.Point` : point for circle center
    - ``pt_radius`` : :class:`sympy.geometry.point.Point` : point to mark radius
    - ``pt_end`` : :class:`sympy.geometry.point.Point` : A SymPy Point marking the sweep of the wedge
    - ``classes`` : :class:`list` *optional* : A list of string names for classes defining a set of styles. Defaults to None.
    - ``label`` : :class:`str` *optional* : A text label for use in plotting and reporting. Defaults to an empty string.

    returns
    -------
    - :class:`Wedge`
        The portion of a circle

    example
    -------
        >>> from geometor.elements import *
        >>> model = Model("demo")
        >>> A = model.set_point(0, 0, classes=["given"], label="A")
        >>> B = model.set_point(1, 0, classes=["given"], label="B")
        >>> model.construct_circle(A, B)
        >>> model.construct_circle(B, A)
        >>> model._set_wedge_by_labels('A', 'B', 'C')
        <Wedge object ...>

    notes
    -----
    SymPy defines a circle as a center point and a radius length, so the radius length is calculated for the spg.Circle.

    """

    if classes is None:
        classes = {}
    # find radius length for sympy.Circle
    #  radius_len = pt_center.distance(pt_radius)

    if not isinstance(pt_center, spg.Point) or not isinstance(pt_radius, spg.Point):
        raise TypeError(
            "Both pt_center and pt_radius must be instances of sympy.geometry.point.Point"
        )

    struct = Wedge(pt_center, pt_radius, pt_sweep_start, pt_sweep_end)

    if not label:
        pt_center_label = model[pt_center].label
        pt_radius_label = model[pt_radius].label
        label = f"( {pt_center_label} {pt_radius_label} )"
        label += f"< {model[pt_sweep_start].label} {pt_center_label} {model[pt_sweep_end].label} >"

    details = CircleElement(
        struct,
        parents=[pt_center, pt_radius],
        classes=classes,
        label=label,
        pt_radius=pt_radius,
    )

    model[struct] = details
    console.print(f"[orchid1]{details.label}[/orchid1]")

    return struct
