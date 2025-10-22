from geometor.model import Model

# Create a new model
model = Model()

# Add some initial points
A = model.set_point(0, 0, classes=["given"])
B = model.set_point(1, 0, classes=["given"])

# Add a line
l1 = model.construct_line(A, B)

# Add a circle
c1 = model.construct_circle(A, B)

# Print the model before deletion
print("Model before deletion:")
for el in model:
    print(f"- {model[el].ID}: {el}")

# Delete the circle
model.delete_element(c1)

# Print the model after deleting the circle
print("\nModel after deleting the circle:")
for el in model:
    print(f"- {model[el].ID}: {el}")

# Add the circle back
c1 = model.construct_circle(A, B)

# Delete the line
model.delete_element(l1)

# Print the model after deleting the line
print("\nModel after deleting the line:")
for el in model:
    print(f"- {model[el].ID}: {el}")
