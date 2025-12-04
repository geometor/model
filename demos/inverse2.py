"""
test script for geometor package
"""

from geometor.model import *


def run():
    # rational number to test
    n = sp.Rational(3, 1)

    model = Model("inverse")
    A = model.set_point(0, 0, classes=["given"])
    B = model.set_point(1, 0, classes=["given"])
    C = model.set_point(n, 0, classes=["given", "red"])
    D = model.set_point(0, 1, classes=["given"])

    # baseline
    model.construct_line(A, B)

    # unit circle
    model.construct_circle(A, B)

    E = model.get_element_by_ID("E")
    #  model[C].ID = 'C'

    # perpendicular
    model.construct_line(A, D)

    # diagonal
    model.construct_line(D, C)

    G = model.get_element_by_ID("G")

    model.construct_circle(E, G, classes=["green"])

    J = model.get_element_by_ID("J")

    model.construct_line(D, J)

    N = model.get_element_by_ID("N")
    model[N].classes["red"] = ""

    report_summary(model)

    #  sequencer = Sequencer(model)
    #  sequencer.plot_sequence()


if __name__ == "__main__":
    run()
