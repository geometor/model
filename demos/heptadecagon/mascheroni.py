"""Mohr–Mascheroni compass-only construction of the regular heptadecagon (zero straightedge lines).

Starting strictly from O(0, 0) and V0(1, 0), every point is constructed exclusively via
collapsible Euclidean circles ``model.construct_circle(center_pt, radius_pt)`` with
``len(model.lines) == 0``:

1. **Napoleon & Orthogonal Seed**: Hexagonal stepping around C0 = (O, V0) yields W(-1, 0) and
   R_up(0, √3), establishing the inversion circle C_root3 = (O, R_up) of squared radius 3.
   Napoleon's circles (V0, T2) ∩ (W, T1) give N_up(0, √2), from which (O, N_up) ∩ (V0, O) gives
   Gaussian integer corners (1, ±1) and unit poles A(0, 1), A_s(0, -1).
2. **Integer Mirror Lattice & Seed Inversion**: Compass reflections build integer mirrors at
   y = ±2, y = ±3, and X_m4(-4, 0), whose inverse in C_root3 is H0(-3/4, 0).
3. **Reflected Carlyle Circle Pairs (k = 3 Scale)**: Three applications of a 6-circle symmetric
   Carlyle reflection gadget solve x^2 - 2*c*x - 9 = 0 on the x-axis, producing 3-scaled Gauss
   half-8-periods (H1_hat, H2_hat) and 4-periods (W1_hat..W4_hat).
4. **Scaled 2-Periods & Inversion Projection**: A 7-circle Mascheroni midpoint locates M4_up,
   and symmetric circles (M4_up, A_3) ∩ (M4_dn, A_3s) cut the x-axis at Z1_hat = (6*cos(2π/17), 0)
   and Z4_hat = (6*cos(8π/17), 0). Inverting Z1_hat in C_root3 gives P1 = (1/(2*cos(2π/17)), 0),
   and (P1, O) ∩ C0 lands directly on V1 and V16 with zero straightedge lines.
"""

from __future__ import annotations

import logging

import sympy.geometry as spg

from geometor.model import Model
from geometor.model.element import Struct, exact_intersect

from .algebra import canonicalize_17
from .richmond import _claim_id


def construct_mascheroni_heptadecagon(
    *,
    quiet: bool = True,
    add_sides: bool = False,
) -> tuple[Model, dict[str, spg.Point], list[spg.Point]]:
    """Construct the regular heptadecagon using strictly compass circles (zero lines).

    Args:
        quiet: Suppress verbose Rich step-by-step logging during construction.
        add_sides: Optionally add the 17 polygon boundary segments ``/ V0 V1 /`` ... ``/ V16 V0 /``
            after all 17 vertices have been constructed purely by circles. Defaults to ``False`` so
            the model contains strictly points and circles.

    Returns:
        A tuple ``(model, milestones, vertices)`` where:
        - ``model`` is the populated compass-only :class:`geometor.model.Model` (``len(model.lines) == 0``),
        - ``milestones`` maps key Mascheroni milestones to exact ``Point2D``s,
        - ``vertices`` is the ordered list ``[V0, V1, ..., V16]`` of all 17 exact vertices.
    """
    logger = logging.getLogger("geometor.model.heptadecagon.mascheroni")
    if quiet:
        logger.setLevel(logging.WARNING)
        logger.handlers.clear()
        logger.addHandler(logging.NullHandler())

    model = Model("heptadecagon_mascheroni", logger=logger)
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

    def _pick_other(pts: list[spg.Point], known_pt: spg.Point) -> spg.Point:
        kx, ky = float(known_pt.x.evalf()), float(known_pt.y.evalf())
        return next(
            p
            for p in pts
            if abs(float(p.x.evalf()) - kx) > 1e-6
            or abs(float(p.y.evalf()) - ky) > 1e-6
        )

    def _style_point(
        pt: spg.Point,
        *,
        result_id: str = "",
        result_guide: bool = True,
        result_classes: list[str] | None = None,
    ) -> spg.Point:
        model[pt].guide = result_guide
        if result_id:
            _claim_id(model, pt, result_id)
        if result_classes is not None:
            model[pt].classes = {c: "" for c in result_classes}
        return pt

    def _reflect_across_pts(
        p_target: spg.Point,
        m1: spg.Point,
        m2: spg.Point,
        *,
        circle_classes: list[str] | None = None,
        result_id: str = "",
        result_guide: bool = True,
        result_classes: list[str] | None = None,
    ) -> spg.Point:
        """Reflect ``p_target`` across the virtual axis through ``m1, m2`` using 2 circles."""
        cls = circle_classes or ["guide"]
        c1 = model.construct_circle(m1, p_target, classes=cls, guide=True)
        c2 = model.construct_circle(m2, p_target, classes=cls, guide=True)
        hits = _add_intersection_points(c1, c2, guide=True, classes=["guide"])
        res = _pick_other(hits, p_target)
        return _style_point(
            res,
            result_id=result_id,
            result_guide=result_guide,
            result_classes=result_classes,
        )

    def _invert_in_circle(
        pt: spg.Point,
        c_inv: spg.Circle,
        center_pt: spg.Point,
        *,
        circle_classes: list[str] | None = None,
        result_id: str = "",
        result_guide: bool = True,
        result_classes: list[str] | None = None,
    ) -> spg.Point:
        """Invert ``pt`` in ``c_inv`` (centered at ``center_pt``) using 3 collapsible circles."""
        cls = circle_classes or ["inversion"]
        c_po = model.construct_circle(pt, center_pt, classes=cls, guide=True)
        u_pts = _add_intersection_points(c_po, c_inv, guide=True, classes=["guide"])
        c_u1 = model.construct_circle(u_pts[0], center_pt, classes=["guide"], guide=True)
        c_u2 = model.construct_circle(u_pts[1], center_pt, classes=["guide"], guide=True)
        inv_hits = _add_intersection_points(c_u1, c_u2, guide=True, classes=["guide"])
        res = _pick_other(inv_hits, center_pt)
        return _style_point(
            res,
            result_id=result_id,
            result_guide=result_guide,
            result_classes=result_classes,
        )

    def _mascheroni_midpoint(
        p1: spg.Point,
        p2: spg.Point,
        *,
        result_id: str = "",
        result_guide: bool = True,
        result_classes: list[str] | None = None,
    ) -> spg.Point:
        """Construct the exact midpoint ``(p1 + p2) / 2`` using 7 collapsible circles."""
        c_q = model.construct_circle(p2, p1, classes=["guide"], guide=True)
        c_p = model.construct_circle(p1, p2, classes=["guide"], guide=True)
        s1 = _add_intersection_points(c_q, c_p, guide=True, classes=["guide"])[0]
        c_s1 = model.construct_circle(s1, p2, classes=["guide"], guide=True)
        s2 = _pick_other(
            _add_intersection_points(c_q, c_s1, guide=True, classes=["guide"]), p1
        )
        c_s2 = model.construct_circle(s2, p2, classes=["guide"], guide=True)
        p_double = _pick_other(
            _add_intersection_points(c_q, c_s2, guide=True, classes=["guide"]), s1
        )
        return _invert_in_circle(
            p_double,
            c_p,
            p1,
            result_id=result_id,
            result_guide=result_guide,
            result_classes=result_classes,
        )

    # --- Step 0: Given O(0, 0) and V0(1, 0) ---
    O = model.set_point(0, 0, ID="O", classes=["given"])
    V0 = model.set_point(1, 0, ID="V0", classes=["given", "vertex"])

    # --- Step 1: Unit circle C0, R=√3 inversion circle C_root3, Napoleon √2, and poles A, A_s ---
    circle_main = model.construct_circle(O, V0, ID="( O V0 )")
    c_V0_O = model.construct_circle(V0, O, classes=["mascheroni_seed"], guide=True)
    t_16 = _add_intersection_points(circle_main, c_V0_O, guide=True, classes=["guide"])
    T6, T1 = t_16[0], t_16[1]
    _claim_id(model, T6, "T6")
    _claim_id(model, T1, "T1")

    c_T1_O = model.construct_circle(T1, O, classes=["mascheroni_seed"], guide=True)
    T2 = _pick_other(
        _add_intersection_points(circle_main, c_T1_O, guide=True, classes=["guide"]), V0
    )
    _claim_id(model, T2, "T2")

    c_T2_O = model.construct_circle(T2, O, classes=["mascheroni_seed"], guide=True)
    W = _pick_other(
        _add_intersection_points(circle_main, c_T2_O, guide=True, classes=["guide"]), T1
    )
    _claim_id(model, W, "W")

    R_up = _pick_other(
        _add_intersection_points(c_T1_O, c_T2_O, guide=True, classes=["guide"]), O
    )
    _style_point(R_up, result_id="R_up", result_guide=False, result_classes=["milestone"])
    c_root3 = model.construct_circle(
        O, R_up, ID="( O R_up )", classes=["inversion_circle"], guide=True
    )

    c_nap1 = model.construct_circle(V0, T2, classes=["napoleon"], guide=True)
    c_nap2 = model.construct_circle(W, T1, classes=["napoleon"], guide=True)
    nap_pts = _add_intersection_points(c_nap1, c_nap2, guide=True, classes=["guide"])
    N_up = nap_pts[1]
    _style_point(N_up, result_id="N_up", result_guide=False, result_classes=["milestone"])

    c_sqrt2 = model.construct_circle(O, N_up, classes=["napoleon"], guide=True)
    b_pts = _add_intersection_points(c_sqrt2, c_V0_O, guide=True, classes=["guide"])
    B_1m, B_11 = b_pts[0], b_pts[1]
    _claim_id(model, B_1m, "B_1m")
    _claim_id(model, B_11, "B_11")

    c_B11_V0 = model.construct_circle(B_11, V0, classes=["guide"], guide=True)
    A = _pick_other(
        _add_intersection_points(circle_main, c_B11_V0, guide=True, classes=["guide"]),
        V0,
    )
    _style_point(A, result_id="A", result_guide=False, result_classes=["milestone"])

    c_B1m_V0 = model.construct_circle(B_1m, V0, classes=["guide"], guide=True)
    A_s = _pick_other(
        _add_intersection_points(circle_main, c_B1m_V0, guide=True, classes=["guide"]),
        V0,
    )
    _claim_id(model, A_s, "A_s")

    # --- Step 2: Integer mirror lattice y = ±2 and y = ±3 ---
    c_A_O = model.construct_circle(A, O, classes=["guide"], guide=True)
    c_B11_O = model.construct_circle(B_11, O, classes=["guide"], guide=True)
    A_2 = _pick_other(
        _add_intersection_points(c_A_O, c_B11_O, guide=True, classes=["guide"]), O
    )
    _claim_id(model, A_2, "A_2")

    A_2s = _reflect_across_pts(O, A_s, B_1m, result_id="A_2s")

    c_A2_A = model.construct_circle(A_2, A, classes=["guide"], guide=True)
    B_12 = _pick_other(
        _add_intersection_points(c_A2_A, c_B11_V0, guide=True, classes=["guide"]), A
    )
    _claim_id(model, B_12, "B_12")

    c_A2s_As = model.construct_circle(A_2s, A_s, classes=["guide"], guide=True)
    B_12s = _pick_other(
        _add_intersection_points(c_A2s_As, c_B1m_V0, guide=True, classes=["guide"]), A_s
    )
    _claim_id(model, B_12s, "B_12s")

    c_B12_A = model.construct_circle(B_12, A, classes=["guide"], guide=True)
    A_3 = _pick_other(
        _add_intersection_points(c_A2_A, c_B12_A, guide=True, classes=["guide"]), A
    )
    _claim_id(model, A_3, "A_3")

    c_B12s_As = model.construct_circle(B_12s, A_s, classes=["guide"], guide=True)
    A_3s = _pick_other(
        _add_intersection_points(c_A2s_As, c_B12s_As, guide=True, classes=["guide"]), A_s
    )
    _claim_id(model, A_3s, "A_3s")

    # --- Step 3: Seed H0 = (-3/4, 0) via inversion of X_m4 = (-4, 0) in C_root3 ---
    c_W_O = model.construct_circle(W, O, classes=["guide"], guide=True)
    B_m11 = _pick_other(
        _add_intersection_points(c_W_O, c_A_O, guide=True, classes=["guide"]), O
    )
    c_Bm11_O = model.construct_circle(B_m11, O, classes=["guide"], guide=True)
    X_m2 = _pick_other(
        _add_intersection_points(c_W_O, c_Bm11_O, guide=True, classes=["guide"]), O
    )
    c_Xm2_W = model.construct_circle(X_m2, W, classes=["guide"], guide=True)
    c_Bm11_W = model.construct_circle(B_m11, W, classes=["guide"], guide=True)
    B_m21 = _pick_other(
        _add_intersection_points(c_Xm2_W, c_Bm11_W, guide=True, classes=["guide"]), W
    )
    X_m4 = _reflect_across_pts(O, X_m2, B_m21, result_id="X_m4")
    H0 = _invert_in_circle(
        X_m4,
        c_root3,
        O,
        result_id="H0",
        result_guide=False,
        result_classes=["milestone"],
    )

    # --- Step 4: Three 6-circle Mascheroni-Carlyle gadgets for x^2 - 2*c*x - 9 = 0 ---
    def _carlyle_gadget_9(
        h_pt: spg.Point, id_left: str, id_right: str
    ) -> tuple[spg.Point, spg.Point]:
        p_up = _reflect_across_pts(h_pt, A_2, B_12)
        p_dn = _reflect_across_pts(h_pt, A_2s, B_12s)
        c_up = model.construct_circle(p_up, A_s, classes=["carlyle_pair"], guide=True)
        c_dn = model.construct_circle(p_dn, A, classes=["carlyle_pair"], guide=True)
        roots = _add_intersection_points(c_up, c_dn, guide=True, classes=["milestone"])
        r_left, r_right = roots[0], roots[1]
        _style_point(
            r_left,
            result_id=id_left,
            result_guide=False,
            result_classes=["milestone"],
        )
        _style_point(
            r_right,
            result_id=id_right,
            result_guide=False,
            result_classes=["milestone"],
        )
        return r_left, r_right

    H2_hat, H1_hat = _carlyle_gadget_9(H0, "H2_hat", "H1_hat")
    W2_hat, W1_hat = _carlyle_gadget_9(H1_hat, "W2_hat", "W1_hat")
    W4_hat, W3_hat = _carlyle_gadget_9(H2_hat, "W4_hat", "W3_hat")

    # --- Step 5: Reflected Carlyle pair for scaled 2-periods x^2 - w1_hat*x + 3*w3_hat = 0 ---
    M_0_32 = _invert_in_circle(A_2, c_root3, O, result_id="M_3_2")
    M_2_32 = _reflect_across_pts(M_0_32, V0, B_11)
    Y3_neg = _reflect_across_pts(W3_hat, O, B_1m)
    Q_y = _reflect_across_pts(Y3_neg, M_0_32, M_2_32, result_id="Q_y")

    M4_up = _mascheroni_midpoint(
        W1_hat,
        Q_y,
        result_id="M4_up",
        result_guide=False,
        result_classes=["milestone"],
    )
    M4_dn = _reflect_across_pts(M4_up, O, V0, result_id="M4_dn")

    c_m4_up = model.construct_circle(
        M4_up, A_3, ID="( M4_up A_3 )", classes=["carlyle_pair"], guide=True
    )
    c_m4_dn = model.construct_circle(
        M4_dn, A_3s, ID="( M4_dn A_3s )", classes=["carlyle_pair"], guide=True
    )
    z_pts = _add_intersection_points(c_m4_up, c_m4_dn, guide=True, classes=["milestone"])
    Z4_hat, Z1_hat = z_pts[0], z_pts[1]
    _style_point(
        Z4_hat, result_id="Z4_hat", result_guide=False, result_classes=["milestone"]
    )
    _style_point(
        Z1_hat, result_id="Z1_hat", result_guide=False, result_classes=["milestone"]
    )

    # --- Step 6: Inversion in C_root3 to P1 = (1/(2*cos(2π/17)), 0) & pure-compass stepping ---
    P1 = _invert_in_circle(
        Z1_hat,
        c_root3,
        O,
        circle_classes=["inversion"],
        result_id="P1",
        result_guide=False,
        result_classes=["milestone"],
    )
    c_P1_O = model.construct_circle(
        P1, O, ID="( P1 O )", classes=["carlyle_pair"], guide=True
    )
    v_1_16 = _add_intersection_points(
        circle_main, c_P1_O, guide=True, classes=["vertex"]
    )
    V16, V1 = v_1_16[0], v_1_16[1]
    _style_point(V1, result_id="V1", result_guide=False, result_classes=["vertex"])
    _style_point(V16, result_id="V16", result_guide=False, result_classes=["vertex"])

    vertices_map: dict[int, spg.Point] = {0: V0, 1: V1, 16: V16}
    for k in range(1, 15):
        p_ctr = vertices_map[k]
        p_rad = vertices_map[k - 1]
        c_step = model.construct_circle(
            p_ctr, p_rad, classes=["compass_step"], guide=True
        )
        hits = _add_intersection_points(circle_main, c_step, guide=True)
        nxt_pt = _pick_other(hits, p_rad)
        _style_point(
            nxt_pt,
            result_id=f"V{k + 1}",
            result_guide=False,
            result_classes=["vertex"],
        )
        vertices_map[k + 1] = nxt_pt

    vertices = [vertices_map[k] for k in range(17)]

    assert len(model.lines) == 0, "Mascheroni model must contain strictly ZERO lines!"

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
    assert len(set(all_ids)) == len(all_ids), "Duplicate element IDs in Mascheroni model!"

    milestones = {
        "O": O,
        "V0": V0,
        "R_up": R_up,
        "N_up": N_up,
        "A": A,
        "H0": H0,
        "H1_hat": H1_hat,
        "H2_hat": H2_hat,
        "W1_hat": W1_hat,
        "W2_hat": W2_hat,
        "W3_hat": W3_hat,
        "W4_hat": W4_hat,
        "M4_up": M4_up,
        "Z1_hat": Z1_hat,
        "Z4_hat": Z4_hat,
        "P1": P1,
    }
    return model, milestones, vertices
