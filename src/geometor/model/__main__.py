"""The package entry point into the application."""
from geometor.model import Model
from geometor.model.reports import *

model = Model("demo")
A = model.set_point(0, 0, classes=["given"])
B = model.set_point(1, 0, classes=["given"])
model.construct_line(A, B)
model.construct_circle(A, B)
model.construct_circle(B, A)

E = model.get_element_by_label("E")
F = model.get_element_by_label("F")
model.construct_line(E, F)

report_sequence(model)
report_group_by_type(model)
report_summary(model)
