"""Tests for all three exact symbolic regular heptadecagon constructions in geometor.model."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import sympy as sp
import sympy.geometry as spg

from geometor.model import load_model

# Allow importing demos/heptadecagon from the repository root
_DEMOS_DIR = str(Path(__file__).resolve().parents[1] / "demos")
if _DEMOS_DIR not in sys.path:
    sys.path.insert(0, _DEMOS_DIR)

from heptadecagon.algebra import (
    A_MINUS,
    A_PLUS,
    R1,
    R2,
    R3,
    SQRT17,
    canonicalize_17,
)
from heptadecagon.carlyle import construct_carlyle_heptadecagon
from heptadecagon.mascheroni import construct_mascheroni_heptadecagon
from heptadecagon.report import QUAD_RESIDUES_17
from heptadecagon.richmond import construct_richmond_heptadecagon


def test_richmond_heptadecagon_symbolic_identities(tmp_path: Path) -> None:
    """Verify exact milestones, all 17 vertices, Gauss periods, chord laws, and JSON round-trip."""
    model, milestones, vertices = construct_richmond_heptadecagon(
        quiet=True, add_sides=True
    )

    # 1. Exact Richmond axial milestones
    assert milestones["O"].x == 0 and milestones["O"].y == 0
    assert milestones["V0"].x == 1 and milestones["V0"].y == 0
    assert milestones["A"].x == 0 and milestones["A"].y == 1
    assert milestones["B"].x == 0 and milestones["B"].y == sp.Rational(1, 4)
    assert milestones["S"].x == (-1 + SQRT17) / 16
    assert milestones["C"].x == (-1 - SQRT17 + A_PLUS) / 16
    assert milestones["D"].x == (-1 + SQRT17 - A_MINUS) / 16
    assert canonicalize_17(milestones["E"].y ** 2 + milestones["D"].x) == 0
    assert milestones["F"].x == (-1 - SQRT17 + A_PLUS + 2 * R3) / 16
    assert milestones["G"].x == (-1 - SQRT17 + A_PLUS - 2 * R3) / 16

    # 2. All 17 vertices lie on the exact unit circle and match (cos(2*pi*k/17), sin(2*pi*k/17))
    assert len(vertices) == 17
    assert vertices[1].x == (-1 + SQRT17 + A_MINUS + 2 * R1) / 16

    for k, v in enumerate(vertices):
        assert canonicalize_17(v.x**2 + v.y**2) == 1
        ang = 2 * math.pi * k / 17
        assert math.isclose(float(v.x.evalf()), math.cos(ang), abs_tol=1e-14)
        assert math.isclose(float(v.y.evalf()), math.sin(ang), abs_tol=1e-14)

    # Conjugate reflection symmetry V_{17-k} == (x_k, -y_k)
    for k in range(1, 9):
        assert vertices[17 - k].x == vertices[k].x
        assert vertices[17 - k].y == -vertices[k].y

    # 3. Gauss's 8-term quadratic residue & non-residue period sums
    qr_sum = canonicalize_17(sum(vertices[k].x for k in QUAD_RESIDUES_17))
    nr_sum = canonicalize_17(
        sum(vertices[k].x for k in range(1, 17) if k not in QUAD_RESIDUES_17)
    )
    assert qr_sum == (-1 + SQRT17) / 2
    assert nr_sum == (-1 - SQRT17) / 2
    assert canonicalize_17(sum(v.x for v in vertices)) == 0

    # 4. All 17 polygon sides have identical exact squared length
    side_sq = canonicalize_17(2 - 2 * vertices[1].x)
    for k in range(17):
        va, vb = vertices[k], vertices[(k + 1) % 17]
        d_sq = canonicalize_17((va.x - vb.x) ** 2 + (va.y - vb.y) ** 2)
        assert d_sq == side_sq

    # 5. Exact chord identities: sum_{m=1}^8 d_m^2 == 17 and prod_{m=1}^8 d_m^2 == 17
    chord_sqs = [canonicalize_17(2 - 2 * vertices[m].x) for m in range(1, 9)]
    assert canonicalize_17(sum(chord_sqs)) == 17
    prod_sq = sp.Integer(1)
    for csq in chord_sqs:
        prod_sq = canonicalize_17(prod_sq * csq)
    assert prod_sq == 17

    # 6. Lossless JSON serialization round-trip
    json_file = tmp_path / "heptadecagon.json"
    model.save(str(json_file))
    reloaded = load_model(str(json_file))
    assert len(reloaded) == len(model)
    orig_ids = {el.ID for el in model.values()}
    reload_ids = {el.ID for el in reloaded.values()}
    assert orig_ids == reload_ids
    for k in range(17):
        pt_rel = reloaded.get_element_by_ID(f"V{k}")
        assert pt_rel == vertices[k]


def test_carlyle_and_mascheroni_constructions(tmp_path: Path) -> None:
    """Verify DeTemple's Carlyle-circle model and Mohr-Mascheroni compass-only model."""
    m_carl, mile_carl, v_carl = construct_carlyle_heptadecagon(
        quiet=True, add_sides=True
    )
    m_masch, mile_masch, v_masch = construct_mascheroni_heptadecagon(
        quiet=True, add_sides=False
    )

    # 1. Exact vertex equivalence between Carlyle and Mascheroni
    assert len(v_carl) == 17
    assert v_carl == v_masch
    assert v_carl[1].x == (-1 + SQRT17 + A_MINUS + 2 * R1) / 16
    assert v_carl[4].x == (-1 + SQRT17 + A_MINUS - 2 * R1) / 16

    # 2. DeTemple Carlyle period milestones
    assert mile_carl["M1"].x == sp.Rational(-1, 4)
    assert mile_carl["H1"].x == (-1 + SQRT17) / 4
    assert mile_carl["H2"].x == (-1 - SQRT17) / 4
    assert mile_carl["W1"].x == (-1 + SQRT17 + A_MINUS) / 4
    assert mile_carl["W2"].x == (-1 + SQRT17 - A_MINUS) / 4
    assert mile_carl["W3"].x == (-1 - SQRT17 + A_PLUS) / 4
    assert mile_carl["W4"].x == (-1 - SQRT17 - A_PLUS) / 4
    assert mile_carl["Z1"].x == 2 * v_carl[1].x
    assert mile_carl["Z4"].x == 2 * v_carl[4].x

    # 3. Strict Mohr-Mascheroni compass-only invariants (zero lines, zero segments)
    assert len(m_masch.lines) == 0
    assert all(isinstance(s, spg.Circle) for s in m_masch.structs)
    assert not any(isinstance(el, (spg.Line, spg.Segment)) for el in m_masch)

    assert mile_masch["R_up"] == spg.Point(0, sp.sqrt(3))
    assert mile_masch["N_up"] == spg.Point(0, sp.sqrt(2))
    assert mile_masch["H0"].x == sp.Rational(-3, 4)
    assert mile_masch["H1_hat"].x == 3 * mile_carl["H1"].x
    assert mile_masch["W1_hat"].x == 3 * mile_carl["W1"].x
    assert mile_masch["W3_hat"].x == 3 * mile_carl["W3"].x
    assert mile_masch["Z1_hat"].x == 6 * v_masch[1].x
    assert mile_masch["P1"].x == (
        4 + 2 * SQRT17 + A_MINUS + A_PLUS - 2 * R2 - 2 * R3
    ) / 8
    assert canonicalize_17(2 * mile_masch["P1"].x * v_masch[1].x) == 1

    # 4. Lossless JSON round-trip for both models
    for name, mdl in [("carlyle", m_carl), ("mascheroni", m_masch)]:
        jpath = tmp_path / f"heptadecagon_{name}.json"
        mdl.save(str(jpath))
        rel = load_model(str(jpath))
        assert len(rel) == len(mdl)
        assert len(rel.lines) == len(mdl.lines)
