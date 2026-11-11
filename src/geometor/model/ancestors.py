"""Provides ancestor retrieval functions for the :class:`geometor.model.Model` class.

We follow the causal chain of parents for the element.
"""

from __future__ import annotations

import sympy.geometry as spg
from sympy.geometry.entity import GeometryEntity


class AncestorsMixin:
    """Mixin for the Model class containing ancestor retrieval operations.

    get ancestors as IDs or elements
    """

    def get_ancestors_IDs(self, element: GeometryEntity) -> dict[str, dict]:
        """Retrieve the IDs of the ancestors for the given element.

        The method recursively traverses the parent elements of the given element
        and constructs a nested dictionary with IDs representing the ancestor tree.

        Args:
            element: sympy.geometry object
                The element for which the ancestors' IDs are to be retrieved.

        Returns:
            dict: A nested dictionary representing the IDs of the ancestors.
        """
        from geometor.model.invariants import Angle
        from geometor.model.sections import Section
        from geometor.model.wedges import Wedge

        visited: set[str] = set()

        def _recursive_get(el: GeometryEntity) -> dict[str, dict]:
            if el not in self:
                return {}
            element_id = self[el].ID
            if element_id in visited:
                return {}  # Cycle guard

            visited.add(element_id)
            ancestors: dict[str, dict] = {element_id: {}}

            if isinstance(el, (Section, Angle, Wedge)):
                for pt in el.points:
                    ancestors[element_id].update(_recursive_get(pt))
                return ancestors

            if isinstance(el, spg.Polygon):
                for pt in el.vertices:
                    ancestors[element_id].update(_recursive_get(pt))
                return ancestors

            if "given" in self[el].classes:
                return ancestors

            parents = list(self[el].parents.keys())[:2] if self[el].parents else []
            for parent in parents:
                ancestors[element_id].update(_recursive_get(parent))

            return ancestors

        return _recursive_get(element)

    def get_ancestors(self, element: GeometryEntity) -> dict[GeometryEntity, dict]:
        """Retrieve the causal ancestors for the given element as a nested dictionary."""
        visited: set[GeometryEntity] = set()

        def _recursive_el(el: GeometryEntity) -> dict[GeometryEntity, dict]:
            if el not in self or el in visited:
                return {}
            visited.add(el)
            ancestors: dict[GeometryEntity, dict] = {el: {}}

            if "given" in self[el].classes:
                return ancestors

            parents = list(self[el].parents.keys())[:2] if self[el].parents else []
            for parent in parents:
                ancestors[el].update(_recursive_el(parent))

            return ancestors

        return _recursive_el(element)
