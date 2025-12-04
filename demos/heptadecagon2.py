"""
constructs the classic 'vesica pisces'
"""

from geometor.model import *


def run():
    model = Model("heptadecagon")
    A = model.set_point(0, 0, classes=["given"])
    B = model.set_point(1, 0, classes=["given"])

    model.construct_line(A, B)

    model.construct_circle(A, B)
    C = model.get_element_by_ID("C")

    model.construct_circle(B, A)

    E = model.get_element_by_ID("E")
    F = model.get_element_by_ID("F")
    model.construct_line(E, F)

    model.construct_circle(B, C)
    model.construct_circle(C, B)

    G = model.get_element_by_ID("P")
    H = model.get_element_by_ID("Q")
    model.construct_line(G, H)

    #  report_group_by_type(model)
    report_sequence(model)
    report_summary(model)

    #  sequencer = Sequencer(model)
    #  sequencer.plot_sequence()

    #  plt.show()


if __name__ == "__main__":
    run()
