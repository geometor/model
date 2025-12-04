geometor.model.reports
======================

.. py:module:: geometor.model.reports

.. autoapi-nested-parse::

   The :mod:`geometor.model.reports` module provides reporting functions for the Model class.



Classes
-------

.. autoapisummary::

   geometor.model.reports.ReportMixin


Functions
---------

.. autoapisummary::

   geometor.model.reports.generate_dot
   geometor.model.reports.get_colored_ID


Module Contents
---------------

.. py:function:: generate_dot(graph, parent=None, dot_string='', defined_nodes=None)

.. py:class:: ReportMixin

   Mixin for the Model class containing report generation methods.


   .. py:method:: report_summary()


   .. py:method:: report_group_by_type()


   .. py:method:: report_sequence()

      Generate a sequential report of the model using rich Console layouts.



.. py:function:: get_colored_ID(el, ID, classes=None)

   Get the colored ID for a geometric element.


