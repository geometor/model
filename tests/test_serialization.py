import os
import tempfile

from geometor.model import Model, load_model


def compare_models(m1, m2):
    """
    Compares two Model objects to see if they are equivalent by checking their internal structure.
    """
    # 1. Compare element counts
    if len(m1) != len(m2):
        print(f"❌ Models have different number of elements: {len(m1)} vs {len(m2)}")
        return False

    # 2. Create maps from ID to element for easy lookup
    map1 = {el.ID: (key, el) for key, el in m1.items()}
    map2 = {el.ID: (key, el) for key, el in m2.items()}

    # 3. Compare the set of IDs
    if map1.keys() != map2.keys():
        print(f"❌ Models have different element IDs.")
        print(f"--- Model 1 IDs: {sorted(map1.keys())}")
        print(f"--- Model 2 IDs: {sorted(map2.keys())}")
        return False

    # 4. Compare each element's properties
    for ID in sorted(map1.keys()):
        key1, el1 = map1[ID]
        key2, el2 = map2[ID]

        # Compare string representation of the sympy object
        if str(key1) != str(key2):
            print(f"❌ Mismatch in sympy object for element {ID}:")
            print(f"  M1: {str(key1)}")
            print(f"  M2: {str(key2)}")
            return False

        # Compare classes
        if el1.classes.keys() != el2.classes.keys():
            print(
                f"❌ Mismatch in classes for element {ID}: {el1.classes.keys()} vs {el2.classes.keys()}"
            )
            return False

        # Compare parents by their IDs
        parents1_ids = sorted([m1[p].ID for p in el1.parents.keys()])
        parents2_ids = sorted([m2[p].ID for p in el2.parents.keys()])
        if parents1_ids != parents2_ids:
            print(
                f"❌ Mismatch in parents for element {ID}: {parents1_ids} vs {parents2_ids}"
            )
            return False

        # Compare pt_radius for circles by ID
        from geometor.model.element import CircleElement

        if isinstance(el1, CircleElement):
            if not isinstance(el2, CircleElement):
                print(
                    f"❌ Type mismatch for element {ID}: CircleElement vs {type(el2)}"
                )
                return False
            if m1[el1.pt_radius].ID != m2[el2.pt_radius].ID:
                print(f"❌ Mismatch in pt_radius for circle {ID}")
                return False

    print("✅ Models are identical.")
    return True


# 1. Create an initial model
print("Step 1: Creating the initial model...")
model_original = Model("Original")
A = model_original.set_point(0, 0, classes=["given"])
B = model_original.set_point(1, 0, classes=["given"])
l1 = model_original.construct_line(A, B)
c1 = model_original.construct_circle(A, B)
c2 = model_original.construct_circle(B, A)
C = model_original.get_element_by_ID("C")
model_original.set_section([C, A, B])
print("Initial model created.")
print("-" * 20)

# 2. Save the model to a temporary file
tmp_dir = tempfile.gettempdir()
file_path = os.path.join(tmp_dir, "test_model.json")
print(f"Step 2: Saving model to {file_path}...")
model_original.save(file_path)
print("Model saved.")
print("-" * 20)

# 3. Load the model into a new instance
print("Step 3: Loading model into a new instance...")
model_reloaded = load_model(file_path)
model_reloaded.name = "Reloaded"
print("Model reloaded.")
print("-" * 20)

# 4. Compare the original and reloaded models
print("Step 4: Comparing original and reloaded models...")
compare_models(model_original, model_reloaded)
print("-" * 20)

# 5. Add a new element to both models
print("Step 5: Adding a new, identical element to both models...")
E_orig = model_original.get_element_by_ID("E")
F_orig = model_original.get_element_by_ID("F")
model_original.construct_line(E_orig, F_orig)
print(" -> New line added to original model.")

E_reload = model_reloaded.get_element_by_ID("E")
F_reload = model_reloaded.get_element_by_ID("F")
model_reloaded.construct_line(E_reload, F_reload)
print(" -> New line added to reloaded model.")
print("-" * 20)

# 6. Compare the models again
print("Step 6: Comparing models after modification...")
compare_models(model_original, model_reloaded)
print("-" * 20)

# Cleanup
os.remove(file_path)
print(f"Cleaned up temporary file: {file_path}")
