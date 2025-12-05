import pytest
from sympy import Symbol

from geometor.model import Model
from geometor.model.polynomials import Polynomial


def test_polynomial_creation():
    coeffs = [1, -1, -1]  # x^2 - x - 1
    poly_el = Polynomial(coeffs, name="golden_poly")
    assert isinstance(poly_el, Polynomial)
    assert str(poly_el) == "Polynomial(x**2 - x - 1)"
    assert poly_el.ID == "golden_poly"
    assert poly_el.degree() == 2
    assert poly_el.all_coeffs() == [1, -1, -1]


def test_add_polynomial_to_model():
    model = Model("test_model")
    coeffs = [1, -1, -1]  # x^2 - x - 1
    poly_el = model.add_poly(coeffs, name="golden_poly_in_model")

    assert isinstance(poly_el, Polynomial)
    assert poly_el.ID == "golden_poly_in_model"
    assert model[poly_el.equation()] == poly_el
    assert len(model) == 1


def test_polynomial_evaluation():
    coeffs = [1, -1, -1]  # x^2 - x - 1
    poly_el = Polynomial(coeffs)
    assert poly_el.eval(0) == -1
    assert poly_el.eval(1) == -1
    assert poly_el.eval(2) == 1


def test_polynomial_roots():
    coeffs = [1, -1, -1]  # x^2 - x - 1
    poly_el = Polynomial(coeffs)
    roots = poly_el.real_roots()
    # The golden ratio and its conjugate
    assert len(roots) == 2
    assert roots[0].evalf() == pytest.approx((1 - 5**0.5) / 2)
    assert roots[1].evalf() == pytest.approx((1 + 5**0.5) / 2)
