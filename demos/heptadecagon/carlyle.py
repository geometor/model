"""Duane W. DeTemple's (1991) Carlyle-circle construction of the regular heptadecagon.

Reference:
    Duane W. DeTemple, "Carlyle Circles and the Lemoine Simplicity of Polygon Constructions",
    The American Mathematical Monthly, Vol. 98, No. 2 (Feb. 1991), pp. 97-108.

Solves Gauss's 3-step chain of quadratic period equations geometrically via four Carlyle
circles (C1, C2, C3, C4), arriving directly at the quadratic-residue vertices V1, V16 and
V4, V13 before stepping the side length |V0 V1| around the unit circle.
"""

from __future__ import annotations

import logging

import sympy.geometry as spg

from geometor.model import Model
from geometor.model.element import Struct, exact_intersect

from .algebra import canonicalize_17
from .richmond import _claim_id


def construct_carlyle_heptadecagon(
    *,
    quiet: bool = True,
    add_sides: bool = True,
) -> tuple[Model, dict[str, spg.Point], list[spg.Point]]:
    """Construct the regular heptadecagon via DeTemple's (1991) 4-Carlyle-circle method.

    Args:
        quiet: Suppress verbose Rich step-by-step logging during construction.
        add_sides: Add the 17 boundary segments ``/ V0 V1 /`` ... ``/ V16 V0 /``.

    Returns:
        A tuple ``(model, milestones, vertices)`` where:
        - ``model`` is the populated :class:`geometor.model.Model`,
        - ``milestones`` maps DeTemple's Carlyle period points
          (``O, V0, A, M1, H1, H2, W1, W2, W3, W4, Y3, M4, Z1, Z4``) to exact ``Point2D``s,
        - ``vertices`` is the ordered list ``[V0, V1, ..., V16]`` of all 17 exact vertices.
    """
    logger = logging.getLogger("geometor.model.heptadecagon.carlyle")
    if quiet:
        logger.setLevel(logging.WARNING)
        logger.handlers.clear()
        logger.addHandler(logging.NullHandler())

    model = Model("heptadecagon_carlyle", logger=logger)
    model.set_simplifier(canonicalize_17)

    guide_idx = 0

    def _next_guide_id() -> str:
        nonlocal guide_idx
        guide_idx += 1
        return f"g{guide_idx}"

    def _add_intersection_points(
        s1: Struct,
        s2: Struct,
        *,
        guide: bool = False,
        classes: list[str] | None = None,
        single_id: str = "",
    ) -> list[spg.Point]:
        raw_pts = exact_intersect(s1, s2)
        added: list[spg.Point] = []
        for idx, raw in enumerate(raw_pts):
            pts_before = len(model.points)
            explicit_id = (
                single_id if (single_id and len(raw_pts) == 1 and idx == 0) else ""
            )
            init_classes = (
                [c for c in (classes or []) if c != "guide"]
                if guide
                else list(classes or [])
            )
            pt = model.set_point(
                raw.x,
                raw.y,
                parents=[s1, s2],
                classes=init_classes,
                ID=explicit_id,
                guide=guide,
            )
            is_new = len(model.points) > pts_before
            if is_new and guide:
                if not explicit_id:
                    _claim_id(model, pt, _next_guide_id())
                if classes and "guide" in classes:
                    model[pt].classes["guide"] = ""
            model[s1].parents[pt] = ""
            model[s2].parents[pt] = ""
            added.append(pt)
        return added

    def _construct_bisector_line(
        p1: spg.Point,
        p2: spg.Point,
        *,
        guide_line: bool = True,
        line_classes: list[str] | None = None,
        line_id: str = "",
    ) -> spg.Line:
        c1 = model.construct_circle(p1, p2, classes=["guide"], guide=True)
        c2 = model.construct_circle(p2, p1, classes=["guide"], guide=True)
        poles = _add_intersection_points(c1, c2, guide=True, classes=["guide"])
        cls = list(line_classes) if line_classes is not None else ["bisector"]
        return model.construct_line(
            poles[0], poles[1], classes=cls, ID=line_id, guide=guide_line
        )

    # --- Step 0: Given O(0, 0) and V0(1, 0) ---
    O = model.set_point(0, 0, ID="O", classes=["given"])
    V0 = model.set_point(1, 0, ID="V0", classes=["given", "vertex"])

    # --- Step 1: Orthogonal axes and unit circle ---
    line_OV = model.construct_line(O, V0, ID="[ O V0 ]")
    circle_main = model.construct_circle(O, V0, ID="( O V0 )")
    W_opp = next(p for p in model.points if float(p.x.evalf()) < -0.5)
    _claim_id(model, W_opp, "W")

    line_OA = _construct_bisector_line(
        W_opp, V0, guide_line=False, line_classes=["bisector"], line_id="[ O A ]"
    )
    A_south = next(p for p in model.points if abs(float(p.y.evalf()) + 1.0) < 1e-9)
    A = next(p for p in model.points if abs(float(p.y.evalf()) - 1.0) < 1e-9)
    _claim_id(model, A_south, "A_s")
    _claim_id(model, A, "A")
    model[A].classes["milestone"] = ""

    # --- Step 2: Carlyle Circle C1 for half-8-periods u^2 + (1/2)u - 1 = 0 ---
    bis_WO = _construct_bisector_line(W_opp, O, guide_line=True)
    M_WO = _add_intersection_points(
        line_OV, bis_WO, guide=True, classes=["guide"], single_id="M_WO"
    )[0]
    bis_MWO = _construct_bisector_line(M_WO, O, guide_line=True)
    M1 = _add_intersection_points(
        line_OV, bis_MWO, guide=False, classes=["milestone"], single_id="M1"
    )[0]

    c_carlyle_1 = model.construct_circle(
        M1, A, ID="( M1 A )", classes=["carlyle"], guide=True
    )
    pts_h = _add_intersection_points(line_OV, c_carlyle_1, guide=True, classes=["milestone"])
    H2, H1 = pts_h[0], pts_h[1]
    model[H1].guide = False
    model[H2].guide = False
    _claim_id(model, H1, "H1")
    _claim_id(model, H2, "H2")

    # --- Step 3: Carlyle Circles C2 & C3 for Gauss's 4-periods w^2 - 2*u_i*w - 1 = 0 ---
    c_carlyle_2 = model.construct_circle(
        H1, A, ID="( H1 A )", classes=["carlyle"], guide=True
    )
    pts_w12 = _add_intersection_points(line_OV, c_carlyle_2, guide=True, classes=["milestone"])
    W2, W1 = pts_w12[0], pts_w12[1]
    model[W1].guide = False
    model[W2].guide = False
    _claim_id(model, W1, "W1")
    _claim_id(model, W2, "W2")

    c_carlyle_3 = model.construct_circle(
        H2, A, ID="( H2 A )", classes=["carlyle"], guide=True
    )
    pts_w34 = _add_intersection_points(line_OV, c_carlyle_3, guide=True, classes=["milestone"])
    W4, W3 = pts_w34[0], pts_w34[1]
    model[W3].guide = False
    model[W4].guide = False
    _claim_id(model, W3, "W3")
    _claim_id(model, W4, "W4")

    # --- Step 4: Carlyle Circle C4 for 2-periods z^2 - w1*z + w3 = 0 ---
    c_OW3 = model.construct_circle(O, W3, ID="( O W3 )", classes=["guide"], guide=True)
    pts_y3 = _add_intersection_points(line_OA, c_OW3, guide=True, classes=["guide"])
    Y3 = next(p for p in pts_y3 if float(p.y.evalf()) > 0)
    model[Y3].guide = False
    _claim_id(model, Y3, "Y3")
    model[Y3].classes = {"milestone": ""}

    bis_OW1 = _construct_bisector_line(
        O, W1, guide_line=True, line_classes=["carlyle_line"]
    )
    bis_AY3 = _construct_bisector_line(
        A, Y3, guide_line=True, line_classes=["carlyle_line"]
    )
    M4 = _add_intersection_points(
        bis_OW1, bis_AY3, guide=False, classes=["milestone"], single_id="M4"
    )[0]

    c_carlyle_4 = model.construct_circle(
        M4, A, ID="( M4 A )", classes=["carlyle"], guide=True
    )
    pts_z = _add_intersection_points(line_OV, c_carlyle_4, guide=True, classes=["milestone"])
    Z4, Z1 = pts_z[0], pts_z[1]
    model[Z1].guide = False
    model[Z4].guide = False
    _claim_id(model, Z1, "Z1")
    _claim_id(model, Z4, "Z4")

    # --- Step 5: Perpendicular bisectors of O-Z1 and O-Z4 hit unit circle at V1, V16 & V4, V13 ---
    perp_Z1 = _construct_bisector_line(
        O, Z1, guide_line=True, line_classes=["carlyle_line"], line_id="[ X1 V1 ]"
    )
    pts_v1 = _add_intersection_points(perp_Z1, circle_main, guide=True, classes=["vertex"])
    V16, V1 = pts_v1[0], pts_v1[1]
    model[V1].guide = False
    model[V16].guide = False
    _claim_id(model, V1, "V1")
    _claim_id(model, V16, "V16")

    perp_Z4 = _construct_bisector_line(
        O, Z4, guide_line=True, line_classes=["carlyle_line"], line_id="[ X4 V4 ]"
    )
    pts_v4 = _add_intersection_points(perp_Z4, circle_main, guide=True, classes=["vertex"])
    V13, V4 = pts_v4[0], pts_v4[1]
    model[V4].guide = False
    model[V13].guide = False
    _claim_id(model, V4, "V4")
    _claim_id(model, V13, "V13")

    # --- Step 6: Step |V0 V1| around the unit circle for the remaining vertices ---
    vertices_map: dict[int, spg.Point] = {
        0: V0,
        1: V1,
        4: V4,
        13: V13,
        16: V16,
    }

    def _compass_step(center_idx: int, radius_idx: int, target_idx: int) -> None:
        p_ctr = vertices_map[center_idx]
        p_rad = vertices_map[radius_idx]
        c_step = model.construct_circle(
            p_ctr, p_rad, classes=["compass_step"], guide=True
        )
        hits = _add_intersection_points(circle_main, c_step, guide=True)
        chosen = next(
            p
            for p in hits
            if abs(float(p.x.evalf() - p_rad.x.evalf())) > 1e-6
            or abs(float(p.y.evalf() - p_rad.y.evalf())) > 1e-6
        )
        model[chosen].guide = False
        _claim_id(model, chosen, f"V{target_idx}")
        model[chosen].classes = {"vertex": ""}
        vertices_map[target_idx] = chosen

    _compass_step(1, 0, 2)
    _compass_step(2, 1, 3)
    _compass_step(4, 3, 5)
    _compass_step(5, 4, 6)
    _compass_step(6, 5, 7)
    _compass_step(7, 6, 8)
    _compass_step(8, 7, 9)
    _compass_step(9, 8, 10)
    _compass_step(10, 9, 11)
    _compass_step(11, 10, 12)
    _compass_step(13, 12, 14)
    _compass_step(14, 13, 15)

    vertices = [vertices_map[k] for k in range(17)]

    if add_sides:
        for k in range(17):
            nxt = (k + 1) % 17
            model.set_segment(
                vertices[k],
                vertices[nxt],
                classes=["heptadecagon"],
                ID=f"/ V{k} V{nxt} /",
            )

    all_ids = [el.ID for el in model.values()]
    assert len(set(all_ids)) == len(all_ids), "Duplicate element IDs in Carlyle model!"

    milestones = {
        "O": O,
        "V0": V0,
        "A": A,
        "M1": M1,
        "H1": H1,
        "H2": H2,
        "W1": W1,
        "W2": W2,
        "W3": W3,
        "W4": W4,
        "Y3": Y3,
        "M4": M4,
        "Z1": Z1,
        "Z4": Z4,
    }
    return model, milestones, vertices
