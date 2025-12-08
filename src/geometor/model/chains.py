"""Provides the Chain class for analyzing connected golden sections.

This module defines the `Chain` class, which facilitates the study of sequences of connected geometric sections. It offers tools for extracting segments and points, analyzing the flow of segment lengths, and exploring symmetries within the structure.
"""

import sympy as sp
import sympy.geometry as spg

from geometor.model.sections import Section
from geometor.model.utils import clean_expr

__all__ = ["Chain"]


class Chain:
    """A class representing a chain of connected golden sections.
    
    The Chain class is designed to analyze the progression and properties of connected geometric sections. It characterizes the "flow" of the chain by comparing consecutive segment lengths and provides methods to extract segments, points, and symbolic lengths, as well as to identify lines of symmetry.
    """

    def __init__(self, sections: list[Section]) -> None:
        """Initializes a Chain object with a list of connected sections.
        
        This constructor accepts a list of Section objects that form the chain. It automatically triggers the extraction of unique segments and points from these sections to populate the chain's internal state.

        Args:
            sections: A list of Section objects representing a chain of connected golden sections.
        """
        self.sections = sections
        self.segments = self.extract_segments()
        self.points = self.extract_points()

    def extract_segments(self) -> list[spg.Segment]:
        """Extracts unique segments from the chain.
        
        This method iterates through all sections in the chain and collects every unique segment involved. It ensures that no duplicate segments are stored in the chain's segment list.

        Returns:
            A list containing the unique segments in the chain.
        """
        segments = []
        for section in self.sections:
            for segment in section.segments:
                if not any(segment.equals(existing) for existing in segments):
                    segments.append(segment)
        return segments

    def extract_points(self) -> list[spg.Point]:
        """Extracts unique points from the chain while maintaining order.
        
        This method compiles a list of all unique points used to define the sections in the chain. The order of appearance is preserved to maintain the geometric flow of the chain.

        Returns:
             A list containing the ordered unique points from the chain.
        """
        points = {}
        for section in self.sections:
            for point in section.points:
                points[point] = None
        return list(points.keys())

    @property
    def lengths(self) -> list[sp.Expr]:
        """Extract the symbolic lengths of the segments in the chain.
        
        This property returns the lengths of all segments in the chain as symbolic expressions, ensuring exact mathematical representation.

        Returns:
            A list containing the symbolic lengths of each segment in the chain.
        """
        return [clean_expr(segment.length) for segment in self.segments]

    @property
    def numerical_lengths(self) -> list[float]:
        """Calculate and extract the numerical lengths of the segments in the chain.
        
        This property evaluates the symbolic lengths of the segments to floating-point numbers. It is useful for numerical analysis and comparisons where symbolic exactness is not required.

        Returns:
            A list containing the evaluated numerical lengths of each segment in the chain.
        """
        return [float(segment.length.evalf()) for segment in self.segments]

    @property
    def flow(self) -> list[str]:
        """Determine the flow of the segments in the chain by comparing the lengths of consecutive segments.
        
        This property analyzes the relative lengths of adjacent segments to produce a string representation of the chain's "flow" (e.g., using '<' and '>'). This visualization helps in understanding the growth or shrinkage patterns within the chain.

        Returns:
             A list of symbols representing the flow of segment lengths. '>' indicates that the previous segment is longer, '<' indicates that the next segment is longer.
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
        """Creates and returns Fibonacci-style IDs for each segment based on their lengths.
        
        This property generates symbolic identifiers (like 'a', 'b', 'a+b') for segments, mirroring the additive properties of Fibonacci sequences. It is particularly relevant when analyzing chains constructed with golden ratio proportions.

        Returns:
             A list of strings where each string is a Fibonacci-style ID corresponding to a segment.
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
