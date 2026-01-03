"""
constructs level-3 geometry:
creates a line and two circles for every pair of points from level-2
WARNING: This involves ~20,000 combinations and may take a long time.
"""

from geometor.model import *
from itertools import combinations
import time

def run():
    start_time = time.time()
    model = Model("level-3")
    pt_A = model.set_point(0, 0, classes=["given"])
    pt_B = model.set_point(1, 0, classes=["given"])

    def fundamental(pt_1: str, pt_2: str):
        model.construct_line(pt_1, pt_2)
        model.construct_circle(pt_1, pt_2)
        model.construct_circle(pt_2, pt_1)

    print("--- Structure: Level 1 ---")
    fundamental(pt_A, pt_B)
    
    print(f"Points after Level 1: {len(model.points)}")
    total_combinations = len(model.points) * (len(model.points) - 1) // 2
    print(f"Iterating {total_combinations} pairs...")

    print("--- Structure: Level 2 ---")
    count = 0
    for p1, p2 in combinations(model.points, 2):
        fundamental(p1, p2)
        count += 1
        print(f"LEVEL-2 {count} / {total_combinations}")
        print()
        
    elapsed = time.time() - start_time
    print("LEVEL-2 complete!")
    print(f"Completed in {elapsed:.2f} seconds")
    print(f"Points after Level 2: {len(model.points)}")
    
    print("--- Structure: Level 3 ---")
    total_combinations = len(model.points) * (len(model.points) - 1) // 2
    print(f"Iterating {total_combinations} pairs...")
    
    count = 0
    for p1, p2 in combinations(model.points, 2):
        fundamental(p1, p2)
        count += 1
        print(f"LEVEL-3 {count} / {total_combinations}")
        print()

    model.report_summary()
    model.report_group_by_type()
    model.report_sequence()

    model.save("level-3.json")
    
    print("LEVEL-3 complete!")
    elapsed = time.time() - start_time
    print(f"Completed in {elapsed:.2f} seconds")


if __name__ == "__main__":
    run()
