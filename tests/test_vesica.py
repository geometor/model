from geometor.model import Model


def test_vesica_construction():
    model = Model("vesica")

    # Start with two points
    A = model.set_point(0, 0, classes=["start"])
    B = model.set_point(1, 0, classes=["start"])

    # Construct circles
    c1 = model.construct_circle(A, B)
    c2 = model.construct_circle(B, A)

    # Find intersections
    # Intersections are automatically found and added to the model during construction
    # We expect 4 points total: A, B, and the two intersections C and D
    assert len(model.points) == 4

    # Get the intersection points (the ones that are not A or B)
    intersections = [p for p in model.points if not (p.equals(A) or p.equals(B))]
    assert len(intersections) == 2

    # Add line connecting intersections
    # Assuming standard labeling A, B, C, D...
    # C and D should be the intersection points
    # Note: The order of C and D might vary, but they are the next points generated
    # We can try to fetch them by label if the generator is deterministic

    # In __main__.py, it fetches E and F. Let's see what labels we get.
    # A, B are set.
    # Circles create intersections.
    # If we rely on the points list filter we did before:
    intersections = [p for p in model.points if not (p.equals(A) or p.equals(B))]
    C = intersections[0]
    D = intersections[1]

    l1 = model.construct_line(C, D)

    # Verify line is perpendicular bisector of AB
    # l1 is a sympy Line object (or subclass)
    # sympy Line has a slope property
    assert l1.slope == float("inf") or l1.is_vertical
