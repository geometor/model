"""Tests for Rational Trigonometry Invariants, Composable @proposition Lemmas, and Proof Verifier.

Covers:
1. Wildberger quadrance, line_spread, cross, vertex_spread, orientation, cross_ratio,
   is_harmonic, and first-class Angle elements.
2. Composable @proposition architecture:
   - Euclid I.1 -> Euclid I.2 (segment transfer at an arbitrary given point),
   - Euclid I.1 x 3 -> ETC X(13) First Fermat Point concurrency & concyclicity proof.
3. Exact SymPy proof assertions catching spoofed pixel coordinates (e.g., G.31 / Euclid I.9
   spoofed coordinates where 1444 != 1450) and supplementary acute/obtuse spread mismatches.
"""

from __future__ import annotations

import pytest
import sympy as sp
import sympy.geometry as spg

from geometor.model import (
    Angle,
    Model,
    ProofAssertionError,
    cross,
    cross_ratio,
    is_harmonic,
    line_spread,
    orientation,
    proposition,
    quadrance,
    vertex_spread,
    zero_test,
)
from geometor.model.utils import spread as legacy_utils_spread


def test_rational_trigonometry_invariants_and_harmonic_range() -> None:
    """Verify exact quadrance, spread, cross, Angle, and projective harmonic cross-ratio."""
    mdl = Model("invariants", logger=False, auto_intersect=False)
    a = mdl.given_point(0, 0, ID="A")
    b = mdl.given_point(2, 0, ID="B")
    c = mdl.given_point(1, sp.sqrt(3), ID="C")
    d_obtuse = mdl.given_point(-1, sp.sqrt(3), ID="D_obt")

    # Equilateral triangle side quadrances == 4 and vertex spreads == 3/4
    seg_ab = mdl.set_segment(a, b)
    assert quadrance(seg_ab) == 4
    assert quadrance(a, c) == 4
    assert quadrance(b, c) == 4

    assert vertex_spread(b, a, c) == sp.Rational(3, 4)
    assert vertex_spread(c, b, a) == sp.Rational(3, 4)
    assert vertex_spread(a, c, b) == sp.Rational(3, 4)

    l_ab = mdl.construct_line(a, b)
    l_ac = mdl.construct_line(a, c)
    assert line_spread(l_ab, l_ac) == sp.Rational(3, 4)
    assert cross(l_ab, l_ac) == sp.Rational(1, 4)
    # Verify legacy utils.spread denominator bug is fixed too
    assert legacy_utils_spread(l_ab, l_ac) == sp.Rational(3, 4)
    assert orientation(a, b, c) == 1
    assert orientation(a, c, b) == -1

    ang_acute = mdl.set_angle(b, a, c)
    ang_obtuse = mdl.set_angle(b, a, d_obtuse)
    assert isinstance(ang_acute, Angle)
    assert mdl[ang_acute].ID == "< B A C )"
    assert ang_acute.spread == sp.Rational(3, 4)
    assert ang_obtuse.spread == sp.Rational(3, 4)
    assert ang_acute.dot_sign == 1
    assert ang_obtuse.dot_sign == -1
    assert ang_acute.is_right is False

    # Un-signed spread equality passes (both 3/4), signed spread equality rejects 60° vs 120°!
    mdl.assert_spread_equal(ang_acute, ang_obtuse, signed=False)
    with pytest.raises(ProofAssertionError):
        mdl.assert_spread_equal(ang_acute, ang_obtuse, signed=True)

    # Projective cross-ratio and harmonic conjugate test along an oblique line:
    # A=(0,0), B=(6,3), internal divider C=(2,1) (ratio 1:2), external divider D=(-6,-3) (ratio -1:2)
    p_a = spg.Point(0, 0)
    p_b = spg.Point(6, 3)
    p_c = spg.Point(2, 1)
    p_d = spg.Point(-6, -3)
    assert cross_ratio(p_a, p_b, p_c, p_d) == -1
    assert is_harmonic(p_a, p_b, p_c, p_d) is True
    assert is_harmonic(p_a, p_b, p_c, spg.Point(4, 2)) is False


@proposition("I.1", g_id="G.17", kind="problem", title="Equilateral Triangle")
def construct_equilateral_triangle(
    model: Model,
    a: spg.Point,
    b: spg.Point,
    *,
    side: int = 1,
    apex_id: str = "",
) -> tuple[spg.Point, spg.Polygon]:
    """Construct an equilateral triangle on segment AB (Euclid Elements I.1)."""
    c1 = model.construct_circle(a, b, intersect=False, by="Post.3")
    c2 = model.construct_circle(b, a, intersect=False, by="Post.3")
    apex = model.intersect(c1, c2, side_of=(a, b, side), ID=apex_id, by="I.1")
    s_ca = model.set_segment(apex, a, by="Post.1")
    s_cb = model.set_segment(apex, b, by="Post.1")
    s_ab = model.set_segment(a, b)
    tri = model.set_polygon([a, b, apex])
    model.assert_equal(s_ab, s_ca, by="Def.15")
    model.assert_equal(s_ab, s_cb, by="Def.15")
    model.assert_equal(s_ca, s_cb, s_ab, by="C.N.1")
    return apex, tri


def test_composable_propositions_euclid_i1_into_i2() -> None:
    """Verify Euclid I.2 composes I.1 cleanly without guide pollution and proves |AL| == |BC|."""
    mdl = Model("Euclid_I_2", logger=False, auto_intersect=False)

    # Act I: Enunciation / Givens — arbitrary point A and arbitrary segment BC
    a = mdl.given_point(0, 0, ID="A")
    b = mdl.given_point(2, 1, ID="B")
    c = mdl.given_point(5, 3, ID="C")
    seg_bc = mdl.set_segment(b, c, classes=["given"], ID="/ B C /")

    # Act II: Construction — invoke I.1 as a scoped sub-construction on AB!
    d, _ = construct_equilateral_triangle(mdl, a, b, side=+1, apex_id="D")

    # Auxiliary circles constructed inside I.1 are automatically marked guide=True!
    assert len(mdl.structs) == 0
    assert any(st.parent_scope == "G.17" for st in mdl.steps)

    line_da = mdl.construct_line(d, a, intersect=False, by="Post.2")
    line_db = mdl.construct_line(d, b, intersect=False, by="Post.2")

    c_bc = mdl.construct_circle(b, c, intersect=False, by="Post.3")
    g_pt = mdl.intersect(line_db, c_bc, beyond=(d, b), ID="G", by="Post.2")

    c_dg = mdl.construct_circle(d, g_pt, intersect=False, by="Post.3")
    l_pt = mdl.intersect(line_da, c_dg, beyond=(d, a), ID="L", by="Post.2")

    seg_al = mdl.set_segment(a, l_pt, ID="/ A L /")

    # Act III: Demonstration — exact SymPy verification of |AL| == |BC|!
    mdl.assert_equal((b, c), (b, g_pt), by="Def.15")
    mdl.assert_equal((d, l_pt), (d, g_pt), by="Def.15")
    mdl.assert_equal((d, a), (d, b), by="I.1")
    mdl.assert_equal(seg_al, seg_bc, by="C.N.3")
    qed = mdl.conclude(seg_al, kind="qef", by="I.2")

    assert "result" in mdl[seg_al].classes
    assert qed.action == "qef"
    assert zero_test(quadrance(seg_al) - quadrance(seg_bc))


def test_composable_fermat_point_x13_from_euclid_i1() -> None:
    """Construct First Fermat Point X(13) by applying @proposition('I.1') outward on all 3 sides."""
    mdl = Model("Fermat_X13", logger=False, auto_intersect=False)
    # Acute triangle (5, 6, 7) oriented counter-clockwise: A=(0,0), B=(7,0), C=(19/7, 12*sqrt(6)/7)
    a = mdl.given_point(0, 0, ID="A")
    b = mdl.given_point(7, 0, ID="B")
    c = mdl.given_point(sp.Rational(19, 7), sp.Rational(12, 7) * sp.sqrt(6), ID="C")

    # Outward relative to CCW triangle ABC means side=-1 for (A->B), (B->C), (C->A)!
    z_apex, _ = construct_equilateral_triangle(mdl, a, b, side=-1, apex_id="Z")
    x_apex, _ = construct_equilateral_triangle(mdl, b, c, side=-1, apex_id="X")
    y_apex, _ = construct_equilateral_triangle(mdl, c, a, side=-1, apex_id="Y")

    # All three Fermat segments |AX| == |BY| == |CZ| are equal by SAS congruence (I.4)!
    mdl.assert_equal((a, x_apex), (b, y_apex), (c, z_apex), by="I.4")

    line_ax = mdl.construct_line(a, x_apex, intersect=False)
    line_by = mdl.construct_line(b, y_apex, intersect=False)
    line_cz = mdl.construct_line(c, z_apex, intersect=False)

    fermat = mdl.intersect(line_ax, line_by, ID="X13")
    # Exact concurrency on the third Fermat line [C Z] and concyclicity on all 3 outer circumcircles!
    mdl.assert_incident(fermat, line_cz, by="X(13) concurrency")
    mdl.assert_concyclic(a, b, z_apex, fermat, by="III.22")
    mdl.assert_concyclic(b, c, x_apex, fermat, by="III.22")
    mdl.assert_concyclic(c, a, y_apex, fermat, by="III.22")
    mdl.conclude(fermat, kind="qed", by="X(13)")
    assert "result" in mdl[fermat].classes


def test_proof_assertions_and_spoofed_pixel_detection() -> None:
    """Verify ProofAssertionError catches spoofed coordinates and verifies valid theorems."""
    # 1. Catch spoofed pixel coordinates from legacy G.31 (Euclid I.9 angle bisector):
    # Legacy script hardcoded D=(33,-72), E=(71,-72), F=(52,-105):
    # Q(D, F) = 19^2 + 33^2 = 1450, Q(E, F) = 19^2 + 33^2 = 1450, BUT Q(D, E) = 38^2 = 1444 != 1450!
    spoof_mdl = Model("spoof_i9", logger=False, auto_intersect=False)
    d_pt = spoof_mdl.given_point(33, -72, ID="D")
    e_pt = spoof_mdl.given_point(71, -72, ID="E")
    f_pt = spoof_mdl.given_point(52, -105, ID="F")

    spoof_mdl.assert_equal((d_pt, f_pt), (e_pt, f_pt), by="isosceles_approx")
    with pytest.raises(ProofAssertionError, match="1444"):
        spoof_mdl.assert_equal((d_pt, e_pt), (d_pt, f_pt), by="I.1")

    # 2. Verify perpendicular, parallel, congruent, and area_equal assertions on exact square/triangles
    mdl = Model("exact_theorems", logger=False, auto_intersect=False)
    p0 = mdl.given_point(0, 0, ID="P0")
    p1 = mdl.given_point(4, 0, ID="P1")
    p2 = mdl.given_point(4, 3, ID="P2")
    p3 = mdl.given_point(0, 3, ID="P3")
    p4 = mdl.given_point(2, 3, ID="P4")

    l_bot = mdl.construct_line(p0, p1, intersect=False)
    l_top = mdl.construct_line(p3, p2, intersect=False)
    l_left = mdl.construct_line(p0, p3, intersect=False)

    mdl.assert_parallel(l_bot, l_top, by="I.27")
    mdl.assert_perpendicular(l_bot, l_left, at=p0, by="Def.10")

    tri_1 = mdl.set_polygon([p0, p1, p2])
    tri_2 = mdl.set_polygon([p2, p3, p0])
    tri_shear = mdl.set_polygon([p0, p1, p4])  # Same base 4 and height 3, sheared apex!

    mdl.assert_congruent(tri_1, tri_2, by="I.34")
    mdl.assert_area_equal(tri_1, tri_shear, by="I.37")

    with pytest.raises(ProofAssertionError):
        mdl.assert_congruent(tri_1, tri_shear, by="not_congruent")
    with pytest.raises(ProofAssertionError):
        mdl.assert_parallel(l_bot, l_left)
    with pytest.raises(ProofAssertionError):
        mdl.assert_perpendicular(l_bot, l_top)
    with pytest.raises(ProofAssertionError):
        mdl.assert_collinear(p0, p1, p2)
    with pytest.raises(ProofAssertionError):
        mdl.assert_concyclic(p0, spg.Point(1, 0), spg.Point(2, 0), spg.Point(3, 0))
    with pytest.raises(ProofAssertionError):
        mdl.assert_incident(p2, l_left)
