usage
=====

In this simple example, we create the classic *vesica pisces*

.. code-block:: python

     from geometor.model import *

     model = Model("vesica")
     A = model.set_point(0, 0, classes=["given"])
     B = model.set_point(1, 0, classes=["given"])

     model.construct_line(A, B)

     model.construct_circle(A, B)
     model.construct_circle(B, A)

     E = model.get_element_by_label("E")
     F = model.get_element_by_label("F")

     model.set_polygon([A, B, E])
     model.set_polygon([A, B, F])

     model.construct_line(E, F)

     report_summary(model)
     report_group_by_type(model)
     report_sequence(model)

     model.save("vesica.json")


