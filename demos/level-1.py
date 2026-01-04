"""
constructs the classic 'vesica pisces'
"""

from geometor.model import *


def run():
    model = Model("level-1")
    model.set_point(0, 0, classes=["given"])
    model.set_point(1, 0, classes=["given"])

    def fundamental(pt_1: str, pt_2: str):
        model.parse_command(f"[{pt_1} {pt_2}]")
        model.parse_command(f"({pt_1} {pt_2})")
        model.parse_command(f"({pt_2} {pt_1})")

    fundamental("A", "B")

    model.save("level-1a.json")

    model = load_model("level-1a.json")

    model.report_summary()
    model.report_group_by_type()
    model.report_sequence()


if __name__ == "__main__":
    run()
