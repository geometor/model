"""
constructs level-2 geometry:
creates a line and two circles for every pair of points
"""

from geometor.model import *
from itertools import combinations
from geometor.divine.golden import find_golden_sections_in_model

def run():
    model = Model("level-2", use_point_subscript=True)
    pt_A = model.set_point(-1/2, 0, classes=["given"])
    pt_B = model.set_point(1/2, 0, classes=["given"])

    def fundamental(pt_1: str, pt_2: str):
        model.construct_line(pt_1, pt_2)
        model.construct_circle(pt_1, pt_2)
        model.construct_circle(pt_2, pt_1)

    
    # establish Level 1.
    fundamental(pt_A, pt_B)
    
    # run the combination on ALL points found so far.
    for pt_1, pt_2 in combinations(model.points, 2):
        fundamental(pt_1, pt_2)

    model.save("level-2.json")

    print()
    print("\nfind golden sections in model: \n")
    sections, sections_by_line = find_golden_sections_in_model(model)
    print(f"sections: {len(sections)}")
    for section in sections:
        model.set_section(section.points, classes=["golden"])
        print(section.get_IDs(model))


    model.report_sequence()
    model.report_group_by_type()
    model.report_summary()

    
    model.save("level-2-divine.json")


if __name__ == "__main__":
    run()
