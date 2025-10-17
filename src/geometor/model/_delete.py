"""
Deletion functions for the Model class.
"""
from .common import *

def _get_dependents_recursive(model, parent_element, dependents_set):
    """
    Recursively finds all elements that depend on the given parent_element.

    An element is considered a dependent if the parent_element is in its
    'parents' list. This function traverses the entire dependency tree.

    Args:
        model (Model): The model instance to search within.
        parent_element (spg.GeometryEntity): The element whose dependents are to be found.
        dependents_set (set): A set to store the found dependent elements.
    """
    for element, details in model.items():
        if parent_element in details.parents:
            if element not in dependents_set:
                dependents_set.add(element)
                # Recurse to find the children of this newly found dependent
                _get_dependents_recursive(model, element, dependents_set)


def get_dependents(self, element_or_ID):
    """
    Finds and returns a set of all elements that depend on the given element.

    This method is for checking dependencies without performing any deletion.

    Args:
        element_or_ID (spg.GeometryEntity or str): The element object or its
            ID to check for dependents.

    Returns:
        set: A set of dependent elements. Returns an empty set if the element
             is not found or has no dependents.
    """
    if isinstance(element_or_ID, str):
        element_to_check = self.get_element_by_ID(element_or_ID)
        if not element_to_check:
            console.print(f"[bold red]Error:[/bold red] Element with ID '{element_or_ID}' not found.")
            return set()
    else:
        element_to_check = element_or_ID

    if element_to_check not in self:
        console.print(f"[bold red]Error:[/bold red] Element '{element_to_check}' not found in the model.")
        return set()

    dependents = set()
    _get_dependents_recursive(self, element_to_check, dependents)
    return dependents


def delete_element(self, element_or_ID):
    """
    Deletes an element and performs a cascading delete of all its dependents.

    This method removes the specified element and any other elements that were
    constructed from it, directly or indirectly.

    Args:
        element_or_ID (spg.GeometryEntity or str): The element object or its
            ID to be deleted.
    """
    if isinstance(element_or_ID, str):
        element_to_delete = self.get_element_by_ID(element_or_ID)
        if not element_to_delete:
            console.print(f"[bold red]Error:[/bold red] Element with ID '{element_or_ID}' not found.")
            return
    else:
        element_to_delete = element_or_ID

    if element_to_delete not in self:
        # This can happen if the object exists but isn't in this specific model
        console.print(f"[bold red]Error:[/bold red] Element '{element_to_delete}' not found in the model.")
        return

    # 1. Recursively find all dependents
    dependents = set()
    _get_dependents_recursive(self, element_to_delete, dependents)

    # 2. The full set to remove includes the initial element
    elements_to_remove = dependents | {element_to_delete}

    # 3. Remove all identified elements from the model
    for el in elements_to_remove:
        if el in self:
            del self[el]

    console.print(f"Deleted {len(elements_to_remove)} element(s) including dependents.")

