from sympy import solve, symbols
from sympy.geometry import Line, Point

t1, t2 = symbols("t1 t2")
P1, P2 = Point(0, 0), Point(4, 4)
P3, P4 = Point(0, 4), Point(4, 0)

L1 = Line(P1, P2)
L2 = Line(P3, P4)

# Define arbitrary points on L1 and L2
arbitrary_point_L1 = L1.arbitrary_point(t1)
arbitrary_point_L2 = L2.arbitrary_point(t2)

L3 = Line(arbitrary_point_L1, arbitrary_point_L2)

print(L3)
