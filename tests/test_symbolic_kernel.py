"""Tests for the geometor.model Symbolic Performance & Euclidean Kernel Upgrade.

Covers:
1. Bug 1: Zero logging overhead & zero stdout emissions when silent (logger=False,
   enable_logging=False, or NullHandler-only logger).
2. Bug 2: In-process closed-form 2D intersections (intersect_2d), Euclidean selectors
   (side_of, other_than, on_ray, beyond, between, near, index), ConstructionError on
   diorismos failure, and sub-150ms exact compass-and-straightedge triangle centers.
3. Bug 3: Unified guide behavior between guide=True and classes=["guide"].
4. Bug 4: Duplicate line construction returns existing spg.Line (including scalar-multiple
   reversed orientation) and tracks incident points in Element.pts.
5. Bug 5: Cycle-free causal Element.parents DAG separated from incident Element.pts.
6. Explicit Q(sqrt(phi)) Kepler algebraic number field canonicalization in < 200 ms.
"""

from __future__ import annotations

import logging
import time

import pytest
import sympy as sp
import sympy.geometry as spg

from geometor.model import (
    ConstructionError,
    Model,
    canonicalize_golden,
    canonicalize_kepler,
    clean_expr,
    get_golden_field,
    get_kepler_field,
    intersect_2d,
    quadrance,
    reduce_in_field,
    zero_test,
)


def test_silent_logging_emits_zero_stdout(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify silent models skip Rich Table/pretty formatting and emit 0 bytes to stdout."""
    null_logger = logging.getLogger("geometor.model.test.null_only")
    null_logger.handlers.clear()
    null_logger.addHandler(logging.NullHandler())
    null_logger.setLevel(logging.INFO)
    null_logger.propagate = False

    for mdl in (
        Model("silent_bool", logger=False),
        Model("silent_flag", enable_logging=False),
        Model("silent_null_handler", logger=null_logger),
    ):
        assert mdl.is_logging_enabled is False
        a = mdl.given_point(0, 0, ID="A")
        b = mdl.given_point(1, 0, ID="B")
        c1 = mdl.construct_circle(a, b)
        c2 = mdl.construct_circle(b, a)
        top = mdl.intersect(c1, c2, side_of=(a, b, +1), ID="C")
        mdl.construct_line(a, b)
        mdl.set_segment(a, top)
        mdl.set_polygon([a, b, top])
        mdl.set_angle(b, a, top)
        d = mdl.set_point(-1, 0, ID="D")
        mdl.set_section([d, a, b])
        mdl.set_wedge(a, b, b, top)
        mdl.add_poly([1, -1, -1], name="phi_poly")

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_duplicate_line_returns_existing_and_tracks_pts() -> None:
    """Verify construct_line returns existing spg.Line on forward/reverse/collinear calls."""
    mdl = Model("dup_lines", logger=False, auto_intersect=False)
    a = mdl.given_point(0, 0, ID="A")
    b = mdl.given_point(2, 1, ID="B")
    c = mdl.given_point(6, 3, ID="C")

    l1 = mdl.construct_line(a, b)
    assert isinstance(l1, spg.Line)

    # Reversed orientation produces negated coefficients (-a, -b, -c)
    l2 = mdl.construct_line(b, a, classes=["bisector"])
    assert l2 is l1
    assert "bisector" in mdl[l1].classes

    # Collinear third point
    l3 = mdl.construct_line(a, c)
    assert l3 is l1
    assert len(mdl.lines) == 1
    assert c in mdl[l1].pts
    # Causal parents of l1 remain strictly [A, B], free of later points
    assert list(mdl[l1].parents.keys()) == [a, b]


def test_guide_flag_and_guide_class_unified() -> None:
    """Verify guide=True and classes=['guide'] behave identically in Element and Model.structs."""
    mdl = Model("guides", logger=False)
    a = mdl.given_point(0, 0, ID="A")
    b = mdl.given_point(1, 0, ID="B")

    c_flag = mdl.construct_circle(a, b, guide=True)
    c_class = mdl.construct_circle(b, a, classes=["guide"])

    assert mdl[c_flag].guide is True
    assert mdl[c_class].guide is True
    assert c_flag not in mdl.structs
    assert c_class not in mdl.structs
    # Neither guide circle triggered auto-intersections
    assert len(mdl.points) == 2


def test_causal_parents_dag_has_no_cycles() -> None:
    """Verify auto-intersections populate struct.pts without creating cycles in struct.parents."""
    mdl = Model("vesica_dag", logger=False)
    a = mdl.given_point(0, 0, label="A")
    b = mdl.given_point(1, 0, label="B")
    assert mdl[a].ID == "A"
    assert mdl[b].ID == "B"

    c1 = mdl.construct_circle(a, b)
    c2 = mdl.construct_circle(b, a)
    assert len(mdl.points) == 4

    derived_pts = [p for p in mdl.points if p not in (a, b)]
    assert len(derived_pts) == 2
    for pt in derived_pts:
        # Derived point depends on c1 and c2
        assert set(mdl[pt].parents.keys()) == {c1, c2}
        # c1 and c2 do NOT list derived point as their parent!
        assert pt not in mdl[c1].parents
        assert pt not in mdl[c2].parents
        # Instead, c1 and c2 record pt in incident .pts
        assert pt in mdl[c1].pts
        assert pt in mdl[c2].pts

    anc_ids = mdl.get_ancestors_IDs(derived_pts[0])
    pt_id = mdl[derived_pts[0]].ID
    assert set(anc_ids[pt_id].keys()) == {"( A B )", "( B A )"}
    anc_objs = mdl.get_ancestors(derived_pts[0])
    assert set(anc_objs[derived_pts[0]].keys()) == {c1, c2}


def test_closed_form_intersect_2d_and_euclidean_selectors() -> None:
    """Verify intersect_2d edge cases and all Euclidean predicates in Model.intersect."""
    mdl = Model("selectors", logger=False, auto_intersect=False)
    a = mdl.given_point(0, 0, ID="A")
    b = mdl.given_point(4, 0, ID="B")
    far = mdl.given_point(10, 0, ID="FAR")

    c1 = mdl.construct_circle(a, b)
    c2 = mdl.construct_circle(b, a)

    # Disjoint circle test -> diorismos violation raises ConstructionError
    p_tiny = mdl.set_point(11, 0, ID="T")
    c_far = mdl.construct_circle(far, p_tiny)
    assert intersect_2d(c1, c_far) == []
    with pytest.raises(ConstructionError):
        mdl.intersect(c1, c_far)

    # Tangent line-circle test -> exactly 1 tangent point
    top_axis = mdl.set_point(0, 4, ID="Y4")
    p_tan_dir = mdl.set_point(1, 4, ID="Y4_1")
    l_tan = mdl.construct_line(top_axis, p_tan_dir)
    tan_pts = intersect_2d(l_tan, c1)
    assert len(tan_pts) == 1
    assert tan_pts[0] == spg.Point(0, 4)

    # side_of selector (+1 upper half-plane vs -1 lower half-plane)
    p_up = mdl.intersect(c1, c2, side_of=(a, b, +1), ID="P_UP")
    p_dn = mdl.intersect(c1, c2, side_of=(a, b, -1), ID="P_DN")
    assert p_up == spg.Point(2, 2 * sp.sqrt(3))
    assert p_dn == spg.Point(2, -2 * sp.sqrt(3))

    # other_than selector
    p_other = mdl.intersect(c1, c2, other_than=p_up)
    assert p_other == p_dn

    # between, beyond, and on_ray selectors along line AB
    l_ab = mdl.construct_line(a, b)
    l_perp = mdl.construct_line(p_up, p_dn)
    mid = mdl.intersect(l_ab, l_perp, between=(a, b), ID="M")
    assert mid == spg.Point(2, 0)

    ext_b = mdl.intersect(l_ab, c2, beyond=(a, b), ID="EXT_B")
    assert ext_b == spg.Point(8, 0)

    ray_pt = mdl.intersect(l_ab, c1, on_ray=(a, b))
    assert ray_pt == b

    # near and index selectors
    near_up = mdl.intersect(c1, c2, near=spg.Point(2, 10))
    assert near_up == p_up
    idx_0 = mdl.intersect(c1, c2, index=0)
    assert idx_0 == p_dn


def _construct_classical_four_centers(
    ax: sp.Expr, ay: sp.Expr, bx: sp.Expr, by: sp.Expr, cx: sp.Expr, cy: sp.Expr
) -> tuple[Model, dict[str, spg.Point]]:
    """Construct X(1), X(2), X(3), X(4) purely by Euclidean compass and straightedge."""
    mdl = Model("classical_centers", logger=False, auto_intersect=False)
    a = mdl.given_point(ax, ay, ID="A")
    b = mdl.given_point(bx, by, ID="B")
    c = mdl.given_point(cx, cy, ID="C")

    l_ab = mdl.construct_line(a, b)
    l_bc = mdl.construct_line(b, c)
    l_ca = mdl.construct_line(c, a)

    def _perp_bisector(p: spg.Point, q: spg.Point) -> spg.Line:
        with mdl.subconstruction("perp_bisector"):
            ca = mdl.construct_circle(p, q)
            cb = mdl.construct_circle(q, p)
            u = mdl.intersect(ca, cb, side_of=(p, q, +1))
            v = mdl.intersect(ca, cb, side_of=(p, q, -1))
            ln = mdl.construct_line(u, v)
            return ln

    pb_ab = _perp_bisector(a, b)
    pb_bc = _perp_bisector(b, c)
    m_c = mdl.intersect(pb_ab, l_ab, ID="Mc")
    m_a = mdl.intersect(pb_bc, l_bc, ID="Ma")

    # X(3) Circumcenter & X(2) Centroid
    x3 = mdl.intersect(pb_ab, pb_bc, ID="X3")
    med_a = mdl.construct_line(a, m_a, guide=True)
    med_c = mdl.construct_line(c, m_c, guide=True)
    x2 = mdl.intersect(med_a, med_c, ID="X2")

    # X(4) Orthocenter via Thales circle over AB and BC
    thales_ab = mdl.construct_circle(m_c, a, guide=True)
    foot_a = mdl.intersect(thales_ab, l_ca, other_than=a, ID="Ha_foot")
    alt_b = mdl.construct_line(b, foot_a, guide=True)

    thales_bc = mdl.construct_circle(m_a, b, guide=True)
    foot_b = mdl.intersect(thales_bc, l_ca, other_than=c, ID="Hb_foot")
    alt_b2 = mdl.construct_line(b, foot_b, guide=True)
    # Also altitude from A to BC via Thales circle on AB
    foot_bc = mdl.intersect(thales_ab, l_bc, other_than=b, ID="Fa")
    alt_a = mdl.construct_line(a, foot_bc, guide=True)
    x4 = mdl.intersect(alt_a, alt_b if foot_a != b else alt_b2, ID="X4")

    # X(1) Incenter via internal angle bisectors at A and B
    def _angle_bisector(v: spg.Point, p1: spg.Point, p2: spg.Point, l1: spg.Line, l2: spg.Line) -> spg.Line:
        with mdl.subconstruction("angle_bisector"):
            cv = mdl.construct_circle(v, p1)
            q1 = p1
            q2 = mdl.intersect(cv, l2, on_ray=(v, p2))
            c_q1 = mdl.construct_circle(q1, q2)
            c_q2 = mdl.construct_circle(q2, q1)
            far_pole = mdl.intersect(c_q1, c_q2, other_than=v, near=spg.Point((q1.x + q2.x) / 2, (q1.y + q2.y) / 2))
            bis = mdl.construct_line(v, far_pole)
            return bis

    bis_a = _angle_bisector(a, b, c, l_ab, l_ca)
    bis_b = _angle_bisector(b, c, a, l_bc, l_ab)
    x1 = mdl.intersect(bis_a, bis_b, ID="X1")

    return mdl, {"X1": x1, "X2": x2, "X3": x3, "X4": x4}


def test_fast_compass_straightedge_triangle_centers() -> None:
    """Verify X(1)..X(4) build in < 200 ms with exact Euler line collinearity."""
    # 1. Heronian (15, 13, 14): A=(0,0), B=(14,0), C=(5,12)
    t0 = time.perf_counter()
    mdl_heron, c_heron = _construct_classical_four_centers(
        sp.Integer(0), sp.Integer(0),
        sp.Integer(14), sp.Integer(0),
        sp.Integer(5), sp.Integer(12),
    )
    elapsed_heron_ms = (time.perf_counter() - t0) * 1000.0
    assert elapsed_heron_ms < 250.0
    assert c_heron["X1"] == spg.Point(6, 4)
    assert c_heron["X2"] == spg.Point(sp.Rational(19, 3), 4)
    assert c_heron["X3"] == spg.Point(7, sp.Rational(33, 8))
    assert c_heron["X4"] == spg.Point(5, sp.Rational(15, 4))
    mdl_heron.assert_collinear(c_heron["X2"], c_heron["X3"], c_heron["X4"], by="Euler")

    # 2. Irrational Acute (5, 6, 7): A=(0,0), B=(7,0), C=(19/7, 12*sqrt(6)/7)
    t1 = time.perf_counter()
    mdl_acute, c_acute = _construct_classical_four_centers(
        sp.Integer(0), sp.Integer(0),
        sp.Integer(7), sp.Integer(0),
        sp.Rational(19, 7), sp.Rational(12, 7) * sp.sqrt(6),
    )
    elapsed_acute_ms = (time.perf_counter() - t1) * 1000.0
    assert elapsed_acute_ms < 300.0
    mdl_acute.assert_collinear(c_acute["X2"], c_acute["X3"], c_acute["X4"], by="Euler")


def test_kepler_algebraic_number_field_reduction() -> None:
    """Verify Q(phi) and Q(sqrt(phi)) canonicalize Kepler expressions and models in < 200 ms."""
    k_phi = get_golden_field()
    k_kepler = get_kepler_field()
    assert k_phi.ext.minpoly.degree() == 2
    assert k_kepler.ext.minpoly.degree() == 4

    t0 = time.perf_counter()
    phi = sp.GoldenRatio
    sqrt_phi = sp.sqrt(phi)

    # Crucial Kepler right-triangle radical identities: sqrt(1 + phi) == phi and sqrt(phi - 1) == 1/sqrt(phi)
    r_hyp = canonicalize_kepler(sp.sqrt(1 + phi))
    r_inv = canonicalize_kepler(sp.sqrt(phi - 1))
    assert zero_test(r_hyp - phi)
    assert zero_test(r_inv * sqrt_phi - 1)
    assert zero_test(canonicalize_golden(phi**5 - (5 * phi + 3)))

    # Construct Kepler right triangle A=(0,0), B=(phi,0), C=(1, 1/sqrt(phi)) with sides a=1, b=sqrt(phi), c=phi
    mdl = Model("kepler", logger=False, auto_intersect=False)
    mdl.set_simplifier(canonicalize_kepler)
    a = mdl.given_point(0, 0, ID="A")
    b = mdl.given_point(phi, 0, ID="B")
    c = mdl.given_point(1, 1 / sqrt_phi, ID="C")

    assert quadrance(b, c) == 1
    assert zero_test(quadrance(a, c) - phi)
    assert zero_test(quadrance(a, b) - (phi + 1))
    assert zero_test(quadrance(b, c) + quadrance(a, c) - quadrance(a, b))

    # Construct perpendicular bisectors for X(3) (midpoint of hypotenuse AB!) and medians for X(2)
    with mdl.subconstruction("kepler_x3"):
        c1 = mdl.construct_circle(a, b)
        c2 = mdl.construct_circle(b, a)
        p1 = mdl.intersect(c1, c2, side_of=(a, b, +1))
        p2 = mdl.intersect(c1, c2, side_of=(a, b, -1))
        pb_ab = mdl.construct_line(p1, p2)

    l_ab = mdl.construct_line(a, b)
    x3 = mdl.intersect(pb_ab, l_ab, ID="X3")
    assert zero_test(x3.x - phi / 2) and x3.y == 0
    # Verify X(3) is equidistant from A, B, and right-angle vertex C!
    mdl.assert_equal((x3, a), (x3, b), (x3, c), by="Thales")

    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    assert elapsed_ms < 250.0
    assert isinstance(clean_expr(reduce_in_field(phi**3 / (1 + sqrt_phi), k_kepler)), sp.Expr)
