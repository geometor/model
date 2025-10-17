import os
import tempfile
from geometor.model import Model, save_model, load_model

def compare_models(m1, m2):
    """
    A simple utility to compare two models based on their browser dict representation.
    This is a basic check and might need to be more comprehensive.
    """
    dict1 = m1.to_browser_dict()
    dict2 = m2.to_browser_dict()

    # Sort elements for consistent comparison
    dict1['elements'].sort(key=lambda x: x['ID'])
    dict2['elements'].sort(key=lambda x: x['ID'])

    if dict1 == dict2:
        print("✅ Models are identical.")
        return True
    else:
        print("❌ Models are NOT identical.")
        # For debugging, print the differences
        import json
        print("--- Model 1 ---")
        print(json.dumps(dict1, indent=2))
        print("--- Model 2 ---")
        print(json.dumps(dict2, indent=2))
        return False

# 1. Create an initial model
print("Step 1: Creating the initial model...")
model_original = Model("Original")
A = model_original.set_point(0, 0, classes=["given"])
B = model_original.set_point(1, 0, classes=["given"])
l1 = model_original.construct_line(A, B)
c1 = model_original.construct_circle(A, B)
c2 = model_original.construct_circle(B, A)
print("Initial model created.")
print("-" * 20)

# 2. Save the model to a temporary file
tmp_dir = tempfile.gettempdir()
file_path = os.path.join(tmp_dir, "test_model.json")
print(f"Step 2: Saving model to {file_path}...")
save_model(model_original, file_path)
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

