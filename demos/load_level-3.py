"""
loads interim level-3 generation
search for golden sections
"""

from geometor.model import *
from geometor.divine.golden import *
from itertools import combinations


def run():
    model = load_model("level-3.json")
    model.report_summary()

    print()
    print("\nfind golden sections in model: \n")
    sections, sections_by_line = find_golden_sections_in_model(model)
    print(f"sections: {len(sections)}")
    for section in sections:
        #  print(section.lengths)
        #  print(section.ratio)
        #  print(section.min_length)
        #  #  print(section.points)
        model.set_section(section.points, classes=["golden"])
        print(section.get_IDs(model))

    model.save("level-3-divine.json")
    model.report_summary()

    


if __name__ == "__main__":
    run()
