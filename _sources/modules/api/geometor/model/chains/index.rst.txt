geometor.model.chains
=====================

.. py:module:: geometor.model.chains


Classes
-------

.. autoapisummary::

   geometor.model.chains.Chain


Module Contents
---------------

.. py:class:: Chain(sections: list[geometor.model.sections.Section])

   A class representing a chain of connected golden sections,
   facilitating the extraction of segments, points, and lengths, as well as
   analyzing the flow and symmetry within the chain.

   Each chain’s flow is characterized by the comparative lengths of
   consecutive segments, represented symbolically to understand the
   progression and transitions in segment lengths. Furthermore, this module
   empowers users to explore symmetry lines within chains, unveiling a subtle,
   profound aspect of geometric harmony.



   .. py:attribute:: sections


   .. py:attribute:: segments
      :value: []



   .. py:attribute:: points
      :value: []



   .. py:method:: extract_segments() -> list[sympy.geometry.Segment]

      Extracts unique segments from the chain.

      :returns: A list containing the unique segments in the chain.
      :rtype: - :class:`list[spg.Segment]`



   .. py:method:: extract_points() -> list[sympy.geometry.Point]

      Extracts unique points from the chain while maintaining order.

      :returns: A list containing the ordered unique points from the chain.
      :rtype: - :class:`list[spg.Point]`



   .. py:property:: lengths
      :type: list[sympy.Expr]


      Extract the symbolic lengths of the segments in the chain.

      :returns: A list containing the symbolic lengths of each segment in the chain.
      :rtype: - :class:`list[sp.Expr]`


   .. py:property:: numerical_lengths
      :type: list[float]


      Calculate and extract the numerical lengths of the segments in the chain.

      :returns: A list containing the evaluated numerical lengths of each
                segment in the chain.
      :rtype: - :class:`list[float]`


   .. py:property:: flow
      :type: list[str]


      Determine the flow of the segments in the chain by comparing the lengths
      of consecutive segments.

      :returns: A list of symbols representing the flow of segment lengths. '>'
                indicates that the previous segment is longer, '<' indicates
                that the next segment is longer.
      :rtype: - :class:`list[str]`


   .. py:method:: count_symmetry_lines() -> int


   .. py:property:: fibonacci_IDs
      :type: list[str]


      Creates and returns Fibonacci-style IDs for each segment based on
      their lengths.

      :returns: A list of strings where each string is a Fibonacci-style
                ID corresponding to a segment.
      :rtype: - :class:`list[str]`


