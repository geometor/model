"""
constructs the classic 'vesica pisces'
"""

from geometor.model import *


def run():
    model = Model("wedge")
    A = model.set_point(0, 0, classes=["given"])
    B = model.set_point(1, 0, classes=["given"])

    model.construct_line(A, B)

    c1 = model.construct_circle(A, B)
    c2 = model.construct_circle(B, A)

    print(f"{c1.area=}")

    E = model.get_element_by_ID("E")
    F = model.get_element_by_ID("F")

    w = model.set_wedge(A, B, F, E)
    print(f"{w.area=}")
    print(f"{w.ratio=}")
    print(f"{w.arc_length=}")
    print(f"{w.degrees=}")
    #  model.set_polygon([A, B, E])
    #  model.set_polygon([A, B, F])

    #  model.construct_line(E, F)

    #  report_summary(model)
    #  report_group_by_type(model)
    #  report_sequence(model)

    #  model.save("vesica.json")


if __name__ == "__main__":
    run()
