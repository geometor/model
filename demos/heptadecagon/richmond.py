"""H. W. Richmond's (1893) compass-and-straightedge construction of the regular heptadecagon.

Follows the classical construction documented at:
    https://mathpages.com/home/kmath487.htm

Every element is constructed strictly from the two initial given points O(0, 0) and V0(1, 0)
via Euclidean straightedge lines and compass circles, preserving the full ancestral DAG in
``geometor.model.Model`` while marking auxiliary scaffolding with ``guide=True``.
"""

from __future__ import annotations

import logging

import sympy.geometry as spg

from geometor.model import Model
from geometor.model.element import Struct, exact_intersect

from .algebra import canonicalize_17


def _claim_id(model: Model, pt: spg.Point, new_id: str) -> None:
    """Assign a unique explicit ID to ``pt``, re-labeling any prior holder if needed."""
    used = {el.ID for el in model.values() if el.ID}
    used.add(new_id)
    for other_pt in model.points:
        if other_pt != pt and model[other_pt].ID == new_id:
            while True:
                cand = next(model.ID_gen)
                model.last_point_id = cand
                if cand not in used:
                    model[other_pt].ID = cand
                    used.add(cand)
                    break
    model[pt].ID = new_id


def construct_richmond_heptadecagon(
    *,
    quiet: bool = True,
    add_sides: bool = True,
) -> tuple[Model, dict[str, spg.Point], list[spg.Point]]:
    """Construct the complete regular heptadecagon model via H. W. Richmond's (1893) method.

    Args:
        quiet: Suppress verbose Rich step-by-step logging during construction.
        add_sides: Add the 17 boundary segments ``/ V0 V1 /`` ... ``/ V16 V0 /``.

    Returns:
        A tuple ``(model, milestones, vertices)`` where:
        - ``model`` is the populated :class:`geometor.model.Model`,
        - ``milestones`` maps Richmond's key geometric labels (``O, V0, A, B, S, C, D, E, F, G``)
          to their exact ``sympy.geometry.Point2D`` instances,
        - ``vertices`` is the ordered list ``[V0, V1, ..., V16]`` of all 17 exact vertices.
    """
    logger = logging.getLogger("geometor.model.heptadecagon")
    if quiet:
        logger.setLevel(logging.WARNING)
        logger.handlers.clear()
        logger.addHandler(logging.NullHandler())

    model = Model("heptadecagon", logger=logger)
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

    # --- Step 0: Given center O(0, 0) and initial vertex V0(1, 0) ---
    O = model.set_point(0, 0, ID="O", classes=["given"])
    V0 = model.set_point(1, 0, ID="V0", classes=["given", "vertex"])

    # --- Step 1: Main unit circle and orthogonal axes OV0 (horizontal) & OA (vertical) ---
    line_OV = model.construct_line(O, V0, ID="[ O V0 ]")
    circle_main = model.construct_circle(O, V0, ID="( O V0 )")
    # Antipode (-1, 0) was auto-created by circle_main ∩ line_OV
    W_opp = next(p for p in model.points if float(p.x.evalf()) < -0.5)
    _claim_id(model, W_opp, "W")

    # Vertical diameter line OA via perpendicular bisector of W(-1, 0) and V0(1, 0)
    line_OA = _construct_bisector_line(
        W_opp, V0, guide_line=False, line_classes=["bisector"], line_id="[ O A ]"
    )
    A_south = next(p for p in model.points if abs(float(p.y.evalf()) + 1.0) < 1e-9)
    A = next(p for p in model.points if abs(float(p.y.evalf()) - 1.0) < 1e-9)
    _claim_id(model, A_south, "A_s")
    _claim_id(model, A, "A")
    model[A].classes["milestone"] = ""

    # --- Step 2: Locate B on OA such that OB = 1/4 OA ---
    bis_OA = _construct_bisector_line(O, A, guide_line=True)
    M_OA = _add_intersection_points(
        line_OA, bis_OA, guide=False, classes=["milestone"], single_id="M_OA"
    )[0]

    bis_OM = _construct_bisector_line(O, M_OA, guide_line=True)
    B = _add_intersection_points(
        line_OA, bis_OM, guide=False, classes=["milestone"], single_id="B"
    )[0]

    # --- Step 3: Locate C on OV0 such that ∠OBC = 1/4 ∠OBV0 ---
    line_BV0 = model.construct_line(B, V0, classes=["richmond"], guide=True)
    c_BO = model.construct_circle(B, O, classes=["guide"], guide=True)

    # First angle bisection: ∠OBV0 -> ∠OBS = 1/2 ∠OBV0 (gives S = (-1 + √17)/16 on OV0!)
    pts_bv0 = _add_intersection_points(line_BV0, c_BO, guide=True, classes=["guide"])
    P1 = next(p for p in pts_bv0 if float(p.x.evalf()) > 0)
    _claim_id(model, P1, "P1")

    line_BS = _construct_bisector_line(O, P1, guide_line=True)
    S = _add_intersection_points(
        line_OV, line_BS, guide=False, classes=["milestone"], single_id="S"
    )[0]

    # Second angle bisection: ∠OBS -> ∠OBC = 1/4 ∠OBV0
    pts_bs = _add_intersection_points(line_BS, c_BO, guide=True, classes=["guide"])
    P2 = next(p for p in pts_bs if float(p.x.evalf()) > 0)
    _claim_id(model, P2, "P2")

    line_BC = _construct_bisector_line(O, P2, guide_line=True, line_classes=["richmond"])
    C = _add_intersection_points(
        line_OV, line_BC, guide=False, classes=["milestone"], single_id="C"
    )[0]

    # --- Step 4: Locate D on OV0 extended such that ∠DBC = 45° ---
    pts_bc = _add_intersection_points(line_BC, c_BO, guide=True, classes=["guide"])
    Q1 = next(p for p in pts_bc if float(p.x.evalf()) > 0)
    Q2 = next(p for p in pts_bc if float(p.x.evalf()) < 0)
    _claim_id(model, Q1, "Q1")
    _claim_id(model, Q2, "Q2")

    # Perpendicular to BC at B (since B is midpoint of chord-diameter Q1 Q2 on c_BO)
    perp_BC = _construct_bisector_line(Q1, Q2, guide_line=True)
    pts_perp = _add_intersection_points(perp_BC, c_BO, guide=True, classes=["guide"])
    Q3 = next(p for p in pts_perp if float(p.x.evalf()) < 0)
    _claim_id(model, Q3, "Q3")

    # Bisect the 90° angle ∠Q3 B Q1 to obtain the 45° ray BD
    line_BD = _construct_bisector_line(Q3, Q1, guide_line=True, line_classes=["richmond"])
    D = _add_intersection_points(
        line_OV, line_BD, guide=False, classes=["milestone"], single_id="D"
    )[0]

    # --- Step 5: Circle on diameter D V0 cuts OA at E ---
    bis_DV0 = _construct_bisector_line(D, V0, guide_line=True)
    M_DV = _add_intersection_points(
        line_OV, bis_DV0, guide=True, classes=["guide"], single_id="M_DV"
    )[0]

    c_DV = model.construct_circle(M_DV, V0, ID="( M_DV V0 )", classes=["richmond"], guide=True)
    pts_e = _add_intersection_points(line_OA, c_DV, guide=True, classes=["guide"])
    E = next(p for p in pts_e if float(p.y.evalf()) > 0)
    model[E].guide = False
    _claim_id(model, E, "E")
    model[E].classes = {"milestone": ""}

    # --- Step 6: Circle centered at C through E cuts OV0 at F and G ---
    c_CE = model.construct_circle(C, E, ID="( C E )", classes=["richmond"], guide=True)
    pts_fg = _add_intersection_points(line_OV, c_CE, guide=True, classes=["milestone"])
    # pts_fg is sorted ascending by x: G (cos 10π/17 < 0) first, F (cos 6π/17 > 0) second
    G, F = pts_fg[0], pts_fg[1]
    model[G].guide = False
    model[F].guide = False
    _claim_id(model, G, "G")
    _claim_id(model, F, "F")

    # --- Step 7: Perpendiculars to OV0 at F and G strike main circle at V3, V14 and V5, V12 ---
    c_FO = model.construct_circle(F, O, classes=["guide"], guide=True)
    f_span = _add_intersection_points(line_OV, c_FO, guide=True, classes=["guide"])
    perp_F = _construct_bisector_line(
        f_span[0], f_span[1], guide_line=True, line_classes=["richmond"], line_id="[ F V3 ]"
    )
    pts_v3 = _add_intersection_points(perp_F, circle_main, guide=True, classes=["vertex"])
    V14, V3 = pts_v3[0], pts_v3[1]
    model[V3].guide = False
    model[V14].guide = False
    _claim_id(model, V3, "V3")
    _claim_id(model, V14, "V14")

    c_GO = model.construct_circle(G, O, classes=["guide"], guide=True)
    g_span = _add_intersection_points(line_OV, c_GO, guide=True, classes=["guide"])
    perp_G = _construct_bisector_line(
        g_span[0], g_span[1], guide_line=True, line_classes=["richmond"], line_id="[ G V5 ]"
    )
    pts_v5 = _add_intersection_points(perp_G, circle_main, guide=True, classes=["vertex"])
    V12, V5 = pts_v5[0], pts_v5[1]
    model[V5].guide = False
    model[V12].guide = False
    _claim_id(model, V5, "V5")
    _claim_id(model, V12, "V12")

    # --- Step 8: Compass stepping around the unit circle to locate all remaining vertices ---
    vertices_map: dict[int, spg.Point] = {
        0: V0,
        3: V3,
        5: V5,
        12: V12,
        14: V14,
    }

    def _compass_step(center_idx: int, radius_idx: int, target_idx: int) -> None:
        p_ctr = vertices_map[center_idx]
        p_rad = vertices_map[radius_idx]
        c_step = model.construct_circle(p_ctr, p_rad, classes=["compass_step"], guide=True)
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

    # Step back 2 arcs from V3 using |V3 V5| to locate V1!
    _compass_step(3, 5, 1)
    # Now |V0 V1| is the exact unit side length of the regular heptadecagon: step around!
    _compass_step(1, 0, 2)
    _compass_step(3, 2, 4)
    _compass_step(5, 4, 6)
    _compass_step(6, 5, 7)
    _compass_step(7, 6, 8)
    _compass_step(8, 7, 9)
    _compass_step(9, 8, 10)
    _compass_step(10, 9, 11)
    _compass_step(12, 11, 13)
    _compass_step(14, 13, 15)
    _compass_step(0, 1, 16)

    vertices = [vertices_map[k] for k in range(17)]

    # --- Step 9: Inscribe the 17 sides of the regular heptadecagon ---
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
    assert len(set(all_ids)) == len(all_ids), "Duplicate element IDs detected in model!"

    milestones = {
        "O": O,
        "V0": V0,
        "A": A,
        "M_OA": M_OA,
        "B": B,
        "S": S,
        "C": C,
        "D": D,
        "E": E,
        "F": F,
        "G": G,
    }
    return model, milestones, vertices
