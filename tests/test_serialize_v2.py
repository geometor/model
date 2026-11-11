"""Tests for model.json schema v2 serialization and v1 backward compatibility."""

from __future__ import annotations

import json
from pathlib import Path

import sympy as sp

from geometor.model import Angle, Model, load_model


def test_serialize_v2_round_trip_with_symbolic_steps_and_angles(tmp_path: Path) -> None:
    """Verify schema_version 2 exports symbolic metadata, pts, markers, Angle, and steps."""
    mdl = Model("euclid_i1_v2", logger=False, auto_intersect=False)
    a = mdl.given_point(0, 0, ID="A")
    b = mdl.given_point(1, 0, ID="B")
    c1 = mdl.construct_circle(a, b, intersect=False, by="Post.3")
    c2 = mdl.construct_circle(b, a, intersect=False, by="Post.3")
    c = mdl.intersect(c1, c2, side_of=(a, b, +1), ID="C", by="I.1")

    s_ab = mdl.set_segment(a, b, by="Post.1")
    s_ac = mdl.set_segment(a, c, by="Post.1")
    s_bc = mdl.set_segment(b, c, by="Post.1")
    tri = mdl.set_polygon([a, b, c])
    ang_a = mdl.set_angle(b, a, c, by="Def.8")
    assert isinstance(ang_a, Angle)

    mdl.assert_equal(s_ab, s_ac, s_bc, by="C.N.1")
    mdl.conclude(tri, kind="qef", by="I.1")

    out_path = tmp_path / "model_v2.json"
    mdl.save(out_path)

    raw = json.loads(out_path.read_text(encoding="utf-8"))
    assert raw["schema_version"] == 2
    assert len(raw["steps"]) == len(mdl.steps)
    assert raw["elements"]["C"]["symbolic"]["kind"] == "point"
    assert len(raw["elements"]["C"]["symbolic"]["latex_coords"]) == 2
    assert raw["elements"]["< B A C )"]["symbolic"]["kind"] == "angle"
    assert raw["elements"]["< B A C )"]["symbolic"]["latex_spread"] == r"\frac{3}{4}"
    assert raw["elements"]["/ A B /"]["markers"] == [{"marker": "tick", "tick_group": 1}]
    assert "C" in raw["elements"]["( A B )"]["pts"]

    reloaded = load_model(out_path, logger=False)
    assert len(reloaded) == len(mdl)
    assert len(reloaded.steps) == len(mdl.steps)
    assert reloaded.steps[-1].kind == "conclude"
    assert reloaded.steps[-1].action == "qef"

    rel_ang = reloaded.get_element_by_ID("< B A C )")
    assert isinstance(rel_ang, Angle)
    assert rel_ang.spread == sp.Rational(3, 4)

    rel_c1 = reloaded.get_element_by_ID("( A B )")
    rel_c = reloaded.get_element_by_ID("C")
    assert rel_c in reloaded[rel_c1].pts
    assert reloaded[reloaded.get_element_by_ID("/ A B /")].markers == [
        {"marker": "tick", "tick_group": 1}
    ]


def test_backward_compatibility_with_v1_model_json(tmp_path: Path) -> None:
    """Verify load_model seamlessly loads legacy v1 JSON files lacking schema_version/steps/pts."""
    v1_payload = {
        "name": "legacy_v1_vesica",
        "use_point_subscript": False,
        "last_point_id": "C",
        "elements": {
            "A": {
                "sympy_obj": "Point2D(Integer(0), Integer(0))",
                "ID": "A",
                "classes": ["given"],
                "parents": [],
                "guide": False,
            },
            "B": {
                "sympy_obj": "Point2D(Integer(1), Integer(0))",
                "ID": "B",
                "classes": ["given"],
                "parents": [],
                "guide": False,
            },
            "[ A B ]": {
                "sympy_obj": "Line2D(Point2D(Integer(0), Integer(0)), Point2D(Integer(1), Integer(0)))",
                "ID": "[ A B ]",
                "classes": ["guide"],
                "parents": ["A", "B"],
                "guide": False,
            },
            "( A B )": {
                "sympy_obj": "Circle(Point2D(Integer(0), Integer(0)), Integer(1))",
                "ID": "( A B )",
                "classes": [],
                "parents": ["A", "B"],
                "guide": False,
                "pt_radius": "B",
            },
        },
    }
    v1_file = tmp_path / "legacy_v1.json"
    v1_file.write_text(json.dumps(v1_payload, indent=2), encoding="utf-8")

    loaded = load_model(v1_file, logger=False)
    assert loaded.name == "legacy_v1_vesica"
    assert len(loaded) == 4
    assert loaded.steps == []
    # Note: legacy "[ A B ]" had classes=["guide"] and guide=False -> unified to guide=True!
    line_ab = loaded.get_element_by_ID("[ A B ]")
    assert loaded[line_ab].guide is True
    assert line_ab not in loaded.structs
