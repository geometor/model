import pytest
import os
from sympy import Symbol
from geometor.model import Model
from geometor.model._polynomials import Polynomial
from geometor.model._serialize import save_model, load_model

@pytest.fixture
def setup_model_with_polynomial():
    model = Model("test_model")
    # Create a polynomial: x^2 + 2x + 1
    poly = Polynomial([1, 2, 1], name="P1")
    model.add_poly(poly.coeffs, name=poly.ID)
    return model

def test_polynomial_serialization(setup_model_with_polynomial, tmp_path):
    model = setup_model_with_polynomial
    file_path = tmp_path / "test_model.json"

    # Save the model
    save_model(model, file_path)

    # Load the model
    loaded_model = load_model(file_path)

    assert loaded_model.name == model.name
    assert len(loaded_model) == len(model)

    # Verify the polynomial
    original_poly_element = model.get_element_by_ID("P1")
    loaded_poly_element = loaded_model.get_element_by_ID("P1")

    assert isinstance(loaded_poly_element, Polynomial)
    assert loaded_poly_element.ID == original_poly_element.ID
    assert loaded_poly_element.classes == original_poly_element.classes
    assert loaded_poly_element.coeffs == original_poly_element.coeffs
    assert loaded_poly_element.object == original_poly_element.object

    # Clean up the created file
    os.remove(file_path)
