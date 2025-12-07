"""
constructs the classic 'vesica pisces'
"""

from geometor.model import *


def run():
    model = Model("vesica")
    A = model.set_point(0, 0, classes=["given"])
    B = model.set_point(1, 0, classes=["given"])

    model.construct_line(A, B)

    model.construct_circle(A, B)
    model.construct_circle(B, A)

    E = model.get_element_by_ID("E")
    F = model.get_element_by_ID("F")

    model.set_polygon([A, B, E])
    model.set_polygon([A, B, F])

    model.construct_line(E, F)

    model.report_summary()
    model.report_group_by_type()
    model.report_sequence()

    model.save("vesica.json")


if __name__ == "__main__":
    run()
