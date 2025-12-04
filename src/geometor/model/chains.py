"""
The :mod:`geometor.model.chains` module provides the Chain class for analyzing connected golden sections.
"""

import sympy as sp
import sympy.geometry as spg

from geometor.model.sections import Section
from geometor.model.utils import clean_expr

__all__ = ["Chain"]


class Chain:
    """
    A class representing a chain of connected golden sections,
    facilitating the extraction of segments, points, and lengths, as well as
    analyzing the flow and symmetry within the chain.

    Each chain’s flow is characterized by the comparative lengths of
    consecutive segments, represented symbolically to understand the
    progression and transitions in segment lengths. Furthermore, this module
    empowers users to explore symmetry lines within chains, unveiling a subtle,
    profound aspect of geometric harmony.

    """

    def __init__(self, sections: list[Section]):
        """
        Initializes a Chain object with a list of connected sections.

        parameters
        ----------
        - ``sections`` : :class:`list[Section]`
            A list of Section objects representing a chain of connected golden sections.
        """
        self.sections = sections
        self.segments = self.extract_segments()
        self.points = self.extract_points()

    def extract_segments(self) -> list[spg.Segment]:
        """
        Extracts unique segments from the chain.

        returns
        -------
        - :class:`list[spg.Segment]`
            A list containing the unique segments in the chain.
        """
        segments = []
        for section in self.sections:
            for segment in section.segments:
                if not any(segment.equals(existing) for existing in segments):
                    segments.append(segment)
        return segments

    def extract_points(self) -> list[spg.Point]:
        """
        Extracts unique points from the chain while maintaining order.

        returns
        -------
        - :class:`list[spg.Point]`
            A list containing the ordered unique points from the chain.
        """
        points = {}
        for section in self.sections:
            for point in section.points:
                points[point] = None
        return list(points.keys())

    @property
    def lengths(self) -> list[sp.Expr]:
        """
        Extract the symbolic lengths of the segments in the chain.

        returns
        -------
        - :class:`list[sp.Expr]`
            A list containing the symbolic lengths of each segment in the chain.
        """
        return [clean_expr(segment.length) for segment in self.segments]

    @property
    def numerical_lengths(self) -> list[float]:
        """
        Calculate and extract the numerical lengths of the segments in the chain.

        returns
        -------
        - :class:`list[float]`
            A list containing the evaluated numerical lengths of each
            segment in the chain.
        """
        return [float(segment.length.evalf()) for segment in self.segments]

    @property
    def flow(self) -> list[str]:
        """
        Determine the flow of the segments in the chain by comparing the lengths
        of consecutive segments.

        returns
        -------
        - :class:`list[str]`
            A list of symbols representing the flow of segment lengths. '>'
            indicates that the previous segment is longer, '<' indicates
            that the next segment is longer.
        """
        flow_symbols = []
        lengths = self.numerical_lengths  # Using numerical lengths for comparison

        for i in range(len(lengths) - 1):
            if lengths[i] > lengths[i + 1]:
                flow_symbols.append(">")
            elif lengths[i] < lengths[i + 1]:
                flow_symbols.append("<")
            else:
                flow_symbols.append("=")  # Equal lengths

        return "".join(flow_symbols)

    def count_symmetry_lines(self) -> int:
        symmetry_count = 0
        flow = self.flow
        flow_length = len(flow)

        # Iterate over the flow string to identify changes in direction
        for i in range(1, flow_length):
            if flow[i] != flow[i - 1]:
                symmetry_count += 1

        return symmetry_count

    @property
    def fibonacci_IDs(self) -> list[str]:
        """
        Creates and returns Fibonacci-style IDs for each segment based on
        their lengths.

        returns
        -------
        - :class:`list[str]`
            A list of strings where each string is a Fibonacci-style
            ID corresponding to a segment.
        """

        # Step 1: Define Symbols
        a, b = sp.symbols("a b")

        # Step 2: Generate Expressions
        expressions = [a, b]
        unique_lengths = sorted(set(self.numerical_lengths))
        for _ in range(2, len(unique_lengths)):
            next_expr = expressions[-1] + expressions[-2]
            expressions.append(next_expr)

        # Step 3: Mapping Expressions
        length_to_expr = {
            length: str(expr).replace(" ", "")
            for length, expr in zip(unique_lengths, expressions)
        }

        # Assign expressions to segments
        segment_expressions = [
            str(length_to_expr[length]) for length in self.numerical_lengths
        ]

        return segment_expressions
