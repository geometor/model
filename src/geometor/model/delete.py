"""Provides deletion functions for the Model class.

This module handles the removal of elements from the model. It includes logic to identify dependent elements (descendants) to ensure that deleting a parent element cascades correctly and maintains the integrity of the dependency graph.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sympy.geometry.entity import GeometryEntity
from rich.console import Console

console = Console()


if TYPE_CHECKING:
    pass


class DeleteMixin:
    """Mixin for the Model class containing deletion operations.
    
    This mixin equips the Model with methods to safely delete elements. It provides functionality to trace the dependency tree and recursively remove an element along with all other elements that depend on it.
    """

    def _get_dependents_recursive(
        self, parent_element: GeometryEntity, dependents_set: set[GeometryEntity]
    ) -> None:
        """Recursively finds all elements that depend on the given parent_element.
        
        This internal helper traverses the model's dependency graph starting from a specific element. It identifies every element that lists the current element as a parent, recursively populating a set of all descendants.

        Args:
            parent_element: The element whose dependents are to be found.
            dependents_set: A set to store the found dependent elements.
        """
        for element, details in self.items():
            if parent_element in details.parents:
                if element not in dependents_set:
                    dependents_set.add(element)
                    # Recurse to find the children of this newly found dependent
                    self._get_dependents_recursive(element, dependents_set)

    def get_dependents(self, element_or_ID: GeometryEntity | str) -> set[GeometryEntity]:
        """Finds and returns a set of all elements that depend on the given element.
        
        This method serves as a query tool to inspect the impact of potentially deleting an element. It resolves the input to a model element and uses recursive search to gather all downstream dependencies.

        Args:
            element_or_ID: The element object or its ID to check for dependents.

        Returns:
            A set of dependent elements. Returns an empty set if the element is not found or has no dependents.
        """
        if isinstance(element_or_ID, str):
            element_to_check = self.get_element_by_ID(element_or_ID)
            if not element_to_check:
                console.print(
                    f"[bold red]Error:[/bold red] Element with ID '{element_or_ID}' not found."
                )
                return set()
        else:
            element_to_check = element_or_ID

        if element_to_check not in self:
            console.print(
                f"[bold red]Error:[/bold red] Element '{element_to_check}' not found in the model."
            )
            return set()

        dependents = set()
        self._get_dependents_recursive(element_to_check, dependents)
        return dependents

    def delete_element(self, element_or_ID: GeometryEntity | str) -> None:
        """Deletes an element and performs a cascading delete of all its dependents.
        
        This is the primary method for removing content from the model. It verifies the existence of the target element, identifies the entire tree of dependent structures, and removes them all to prevent orphaned references in the model.

        Args:
            element_or_ID: The element object or its ID to be deleted.
        """
        if isinstance(element_or_ID, str):
            element_to_delete = self.get_element_by_ID(element_or_ID)
            if not element_to_delete:
                console.print(
                    f"[bold red]Error:[/bold red] Element with ID '{element_or_ID}' not found."
                )
                return
        else:
            element_to_delete = element_or_ID

        if element_to_delete not in self:
            # This can happen if the object exists but isn't in this specific model
            console.print(
                f"[bold red]Error:[/bold red] Element '{element_to_delete}' not found in the model."
            )
            return

        # 1. Recursively find all dependents
        dependents = set()
        self._get_dependents_recursive(element_to_delete, dependents)

        # 2. The full set to remove includes the initial element
        elements_to_remove = dependents | {element_to_delete}

        # 3. Filter out elements that came before the element to delete
        model_elements = list(self.keys())
        delete_index = model_elements.index(element_to_delete)

        final_elements_to_remove = {
            el for el in elements_to_remove if model_elements.index(el) >= delete_index
        }

        # 4. Remove all identified elements from the model
        for el in final_elements_to_remove:
            if el in self:
                del self[el]
