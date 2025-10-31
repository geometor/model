"""
Polynomial element for geometor.model
"""
from .element import Element
from sympy import Poly, Symbol, sympify

class Polynomial(Element):
    """
    A polynomial element defined by its coefficients.
    """
    def __init__(self, coeffs, name="", classes=None, group=None):
        if classes is None:
            classes = []
        if group:
            classes.append(group)

        self.x = Symbol('x')
        self.y = Symbol('y')
        self.coeffs = [sympify(c) for c in coeffs]
        # sympy Poly expects coeffs from highest to lowest degree
        self.poly = Poly(self.coeffs, self.x) 
        
        super().__init__(self.poly.as_expr(), ID=name, classes=classes)

    def __str__(self):
        return f"Polynomial({self.poly.as_expr()})"

    def __repr__(self):
        return f"Polynomial({self.poly.as_expr()})"

    def equation(self):
        return self.poly.as_expr()

    def eval(self, val):
        return self.poly.eval(val)

    def degree(self):
        return self.poly.degree()

    def all_coeffs(self):
        return self.poly.all_coeffs()

    def real_roots(self):
        return self.poly.real_roots()

    def intersection(self, other):
        from ._lines import Line
        from ._circles import Circle
        from ._points import Point

        intersections = []
        if isinstance(other, Polynomial):
            # Solve for x where self.poly.as_expr() == other.poly.as_expr()
            solutions = sp.solve(self.poly.as_expr() - other.poly.as_expr(), self.x)
            for sol_x in solutions:
                if sol_x.is_real:
                    sol_y = self.poly.as_expr().subs(self.x, sol_x)
                    intersections.append(Point(sol_x, sol_y))
        elif isinstance(other, (Line, Circle)):
            # For intersection with Line or Circle, we need to solve a system of equations
            # The Line/Circle object has an .equation() method that returns its SymPy expression
            # We need to substitute y in the polynomial equation with the line/circle equation
            # This is more complex and might require different solving strategies depending on the other object
            # For now, let's assume simple cases or focus on polynomial-polynomial intersection
            # A more robust solution would involve SymPy's solve_intersections or similar
            # For a line y = mx + c, substitute y in the polynomial
            # For a circle (x-h)^2 + (y-k)^2 = r^2, substitute y from polynomial into circle equation
            # This is a placeholder for more complex intersection logic
            if isinstance(other, Line):
                # Assuming line equation is of the form A*x + B*y + C = 0
                # We need to express y in terms of x or vice versa from the line equation
                # For simplicity, let's assume the line equation can be solved for y
                line_eq = other.equation()
                y_line = sp.solve(line_eq, self.y) # Assuming self.y is defined as Symbol('y') in Polynomial
                if y_line:
                    # Substitute y in polynomial with y_line[0]
                    poly_expr_y = self.poly.as_expr().subs(self.y, y_line[0])
                    solutions_x = sp.solve(poly_expr_y, self.x)
                    for sol_x in solutions_x:
                        if sol_x.is_real:
                            sol_y = y_line[0].subs(self.x, sol_x)
                            intersections.append(Point(sol_x, sol_y))
            elif isinstance(other, Circle):
                # This is significantly more complex and will require a dedicated solver
                # For now, we'll return an empty list for polynomial-circle intersections
                pass
        
        return intersections
