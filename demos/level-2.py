"""
constructs level-2 geometry:
creates a line and two circles for every pair of points
"""

from geometor.model import *
from itertools import combinations


def run():
    model = Model("level-2")
    pt_A = model.set_point(0, 0, classes=["given"])
    pt_B = model.set_point(1, 0, classes=["given"])

    def fundamental(pt_1: str, pt_2: str):
        model.construct_line(pt_1, pt_2)
        model.construct_circle(pt_1, pt_2)
        model.construct_circle(pt_2, pt_1)

    
    # establish Level 1.
    fundamental(pt_A, pt_B)
    
    # run the combination on ALL points found so far.
    for pt_1, pt_2 in combinations(model.points, 2):
        # We already did A, B w/ fundamental, but model handles redundancy
        fundamental(pt_1, pt_2)

    model.save("level-2.json")

    model.report_sequence()
    model.report_group_by_type()
    model.report_summary()

    


if __name__ == "__main__":
    run()
