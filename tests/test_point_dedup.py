"""Tests for O(1) 3x3 spatial grid point deduplication and index consistency."""

from __future__ import annotations

import sympy as sp

from geometor.model import Model


def test_algebraically_equal_distinct_trees_deduplicate() -> None:
    """Different SymPy expression trees representing the same point collapse to one."""
    model = Model("dedup-trees", enable_logging=False)
    p1 = model.set_point(1 / sp.sqrt(2), (sp.sqrt(5) + 1) / 2 - 1, classes=["first"])
    p2 = model.set_point(sp.sqrt(2) / 2, (sp.sqrt(5) - 1) / 2, classes=["second"])

    assert p1 == p2
    assert len(model.points) == 1
    assert set(model[p1].classes) == {"first", "second"}


def test_grid_boundary_straddle_matches_and_nearby_distinct_stays_separate() -> None:
    """Points straddling a 1e-6 cell boundary still match; 1e-8 apart stay distinct."""
    model = Model("dedup-boundary", enable_logging=False)
    # 1e-6 exactly (cell 1) vs algebraically equal expression that evals slightly below 1e-6 (cell 0)
    x_exact = sp.Rational(1, 10**6)
    x_straddle = ((sp.sqrt(5) + 1) * (sp.sqrt(5) - 1) / 4) * sp.Rational(1, 10**6)
    p1 = model.set_point(x_exact, 0)
    p2 = model.set_point(x_straddle, 0)

    assert p1 == p2
    assert len(model.points) == 1

    # A distinct point 1e-8 away (same 1e-6 cell, outside 1e-9 match tolerance) must not merge
    p3 = model.set_point(x_exact + sp.Rational(1, 10**8), 0)
    assert p3 != p1
    assert len(model.points) == 2


def test_delete_and_explicit_id_claim_keep_indices_consistent() -> None:
    """Deleting points and claiming explicit IDs keep _point_grid and _used_point_ids valid."""
    model = Model("dedup-indices", enable_logging=False)
    p_a = model.set_point(0, 0, ID="A")
    p_b = model.set_point(1, 0, ID="B")
    assert len(model.points) == 2
    assert "A" in model._used_point_ids
    assert "B" in model._used_point_ids

    # Claiming ID "A" on a new point reassigns p_a and keeps all IDs unique
    p_c = model.set_point(2, 0, ID="A")
    assert model[p_c].ID == "A"
    assert model[p_a].ID != "A"
    assert len({model[p].ID for p in model.points}) == 3
    assert model._used_point_ids == {model[p].ID for p in model.points}

    # Deleting p_b removes it from _point_grid and _used_point_ids
    model.remove_by_ID("B")
    assert len(model.points) == 2
    assert "B" not in model._used_point_ids
    assert p_b not in model

    # Re-adding (1, 0) creates a fresh point cleanly
    p_b_new = model.set_point(1, 0)
    assert len(model.points) == 3
    assert p_b_new in model
