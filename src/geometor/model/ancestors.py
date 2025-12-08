"""Provides ancestor retrieval functions for the :class:`geometor.model.Model` class.

We follow the chain of parents for the element. 
"""

from __future__ import annotations

import sympy.geometry as spg
from sympy.geometry.entity import GeometryEntity


class AncestorsMixin:
    """Mixin for the Model class containing ancestor retrieval operations.

    get ancestors as IDs or elements
    """

    def get_ancestors_IDs(self, element: GeometryEntity) -> dict[str, dict]:
        """Retrieves the IDs of the ancestors for the given element.

        The method recursively traverses the parent elements of the given element
        and constructs a nested dictionary with IDs representing the ancestor tree.

        Args:
            element: sympy.geometry object
                The element for which the ancestors' IDs are to be retrieved.

        Returns:
            dict: A nested dictionary representing the IDs of the ancestors.

        **example**

        If element A has parents B and C, and B has parent D, the method returns:

            {'A': {'B': {'D': {}}, 'C': {}}}

        """
        visited = set()

        def _recursive_get(el: GeometryEntity) -> dict[str, dict]:
            from geometor.model.sections import Section

            element_id = self[el].ID
            if element_id in visited:
                return {}  # Cycle detected

            visited.add(element_id)

            ancestors = {element_id: {}}

            if isinstance(el, Section):
                for pt in el.points:
                    ancestors[element_id].update(_recursive_get(pt))
                return ancestors

            if isinstance(el, spg.Polygon):
                for pt in el.vertices:
                    ancestors[element_id].update(_recursive_get(pt))
                return ancestors

            if "given" in self[el].classes:
                return ancestors

            # Check if the element has parents
            parents = []
            if self[el].parents:
                # Consider only the first two parents
                parents = list(self[el].parents.keys())[:2]

            for parent in parents:
                ancestors[element_id].update(_recursive_get(parent))

            return ancestors

        return _recursive_get(element)

    def get_ancestors(self, element: GeometryEntity) -> dict[GeometryEntity, dict]:
        """Retrieves the ancestors for the given element.

        The method recursively traverses the parent elements of the given element
        and constructs a nested dictionary representing the ancestor tree.

        Args:
            element : sympy.geometry object
                The element for which the ancestors are to be retrieved.

        Returns:
            dict : A nested dictionary representing the ancestors.

        **example**

        If element A has parents B and C, and B has parent D, the method returns:

            {A: {B: {D: {}}, C: {}}}

        """
        ancestors = {element: {}}

        if "given" in self[element].classes:
            return ancestors

        # Check if the element has parents
        parents = []
        if self[element].parents:
            # Consider only the first two parents
            parents = list(self[element].parents.keys())[:2]

        for parent in parents:
            ancestors[element].update(self.get_ancestors(parent))

        return ancestors
