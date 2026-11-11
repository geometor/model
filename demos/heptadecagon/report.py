"""Rich symbolic comparison report and SVG generators for all three regular heptadecagon models."""

from __future__ import annotations

import math
import time
from pathlib import Path

import rich
import sympy as sp
import sympy.geometry as spg
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from geometor.model import Model, load_model

from .algebra import (
    A_MINUS,
    A_PLUS,
    B8_EXPRS,
    B8_NAMES,
    R1,
    R2,
    R3,
    R4,
    SQRT17,
    canonicalize_17,
    decompose_k8,
)
from .carlyle import construct_carlyle_heptadecagon
from .mascheroni import construct_mascheroni_heptadecagon
from .richmond import construct_richmond_heptadecagon

# Quadratic residues mod 17 among {1..16}: 1^2=1, 2^2=4, 3^2=9, 4^2=16, 5^2=8, 6^2=2, 7^2=15, 8^2=13
QUAD_RESIDUES_17 = {1, 2, 4, 8, 9, 13, 15, 16}


def format_shorthand_k8(expr: sp.Expr) -> str:
    """Format an element of K_8 cleanly in terms of {1, √17, A₋, A₊, R₁..R₄}."""
    dec = decompose_k8(expr)
    if dec is None:
        return str(expr)
    coords = [dec[name] for name in B8_NAMES]
    if all(c == 0 for c in coords):
        return "0"
    den_lcm = sp.Integer(1)
    for c in coords:
        den_lcm = sp.ilcm(den_lcm, c.q)
    nums = [int(c * den_lcm) for c in coords]
    terms: list[str] = []
    for num, name in zip(nums, B8_NAMES):
        if num == 0:
            continue
        sign = "+" if num > 0 else "-"
        abs_n = abs(num)
        if name == "1":
            body = f"{abs_n}"
        elif abs_n == 1:
            body = name
        else:
            body = f"{abs_n}·{name}"
        if not terms:
            terms.append(f"-{body}" if sign == "-" else body)
        else:
            terms.append(f"{sign} {body}")
    numer_str = " ".join(terms)
    if den_lcm == 1:
        return numer_str
    return f"({numer_str}) / {den_lcm}"


def format_shorthand_sqrt_y(expr: sp.Expr) -> str:
    """Format ±sqrt(p)/d where p ∈ K_8 using shorthand tower symbols."""
    if expr == 0:
        return "0"
    if expr.is_Rational:
        return str(expr)
    val = float(expr.evalf())
    sign_prefix = "-" if val < 0 else "+"
    sq = canonicalize_17(expr**2)
    if sq.is_Integer:
        return f"{sign_prefix}√{sq}"
    dec = decompose_k8(sq)
    if dec is None:
        return str(expr)
    coords = [dec[name] for name in B8_NAMES]
    den_lcm = sp.Integer(1)
    for c in coords:
        den_lcm = sp.ilcm(den_lcm, c.q)
    factors = sp.factorint(int(den_lcm))
    mult = 1
    for p, e in factors.items():
        if e % 2 == 1:
            mult *= p
    sq_den = int(den_lcm) * mult
    root_den = math.isqrt(sq_den)
    inner_str = format_shorthand_k8(
        sum((coords[i] * sq_den) * B8_EXPRS[i] for i in range(8))
    )
    if root_den == 1:
        return f"{sign_prefix}√({inner_str})"
    return f"{sign_prefix}√({inner_str}) / {root_den}"


def _clip_line_to_box(
    el: spg.Line, xmin: float, xmax: float, ymin: float, ymax: float
) -> tuple[tuple[float, float], tuple[float, float]] | None:
    """Clip a SymPy Line to an axis-aligned rectangle."""
    a, b, c = [float(v.evalf()) for v in el.coefficients]
    clipped: list[tuple[float, float]] = []
    if abs(b) > 1e-9:
        for xv in (xmin, xmax):
            yv = (-a * xv - c) / b
            if ymin - 1e-7 <= yv <= ymax + 1e-7:
                clipped.append((xv, yv))
    if abs(a) > 1e-9:
        for yv in (ymin, ymax):
            xv = (-b * yv - c) / a
            if xmin - 1e-7 <= xv <= xmax + 1e-7 and all(
                abs(xv - ox) + abs(yv - oy) > 1e-5 for ox, oy in clipped
            ):
                clipped.append((xv, yv))
    if len(clipped) >= 2:
        return clipped[0], clipped[1]
    return None


def render_heptadecagon_svg(
    model: Model,
    milestones: dict[str, spg.Point],
    vertices: list[spg.Point],
    out_path: Path,
) -> None:
    """Render a high-contrast GEOMETOR dark-theme SVG of Richmond's (1893) 17-gon construction."""
    size = 1000
    scale = 360.0
    cx, cy = 500.0, 500.0

    def tx(x: float) -> float:
        return cx + x * scale

    def ty(y: float) -> float:
        return cy - y * scale

    lines_svg: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">',
        '<rect width="100%" height="100%" fill="#0e1015"/>',
        "<style>",
        "  .guide-circle { stroke: #334155; stroke-width: 0.9; stroke-dasharray: 4 4; fill: none; opacity: 0.55; }",
        "  .richmond-circle { stroke: #38bdf8; stroke-width: 1.4; stroke-dasharray: 6 3; fill: none; opacity: 0.85; }",
        "  .richmond-line { stroke: #38bdf8; stroke-width: 1.2; stroke-dasharray: 4 3; opacity: 0.8; }",
        "  .axis { stroke: #64748b; stroke-width: 1.3; }",
        "  .main-circle { stroke: #94a3b8; stroke-width: 1.8; fill: none; }",
        "  .poly-fill { fill: #f59e0b; fill-opacity: 0.07; stroke: #f59e0b; stroke-width: 2.4; stroke-linejoin: round; }",
        "  .chord-star { stroke: #f59e0b; stroke-width: 0.6; opacity: 0.22; }",
        "  .pt-vertex { fill: #fbbf24; stroke: #0e1015; stroke-width: 1.5; }",
        "  .pt-milestone { fill: #38bdf8; stroke: #0e1015; stroke-width: 1.4; }",
        "  .pt-given { fill: #f8fafc; stroke: #f59e0b; stroke-width: 2.0; }",
        "  .lbl-v { fill: #fde68a; font-family: monospace; font-size: 13px; font-weight: bold; }",
        "  .lbl-m { fill: #7dd3fc; font-family: monospace; font-size: 12px; font-weight: bold; }",
        "  .title { fill: #f8fafc; font-family: monospace; font-size: 18px; font-weight: bold; letter-spacing: 3px; }",
        "  .subtitle { fill: #94a3b8; font-family: monospace; font-size: 12px; }",
        "</style>",
        '<text x="36" y="44" class="title">GEOMETOR • REGULAR HEPTADECAGON (17-GON)</text>',
        '<text x="36" y="66" class="subtitle">Method 1: H. W. Richmond (1893) Angle-Quartering • Lands on Non-Residues V3 &amp; V5</text>',
    ]

    for el, data in model.items():
        if isinstance(el, spg.Circle):
            hx, ky, r = (
                float(el.center.x.evalf()),
                float(el.center.y.evalf()),
                float(el.radius.evalf()),
            )
            if data.ID == "( O V0 )":
                continue
            if "richmond" in data.classes:
                lines_svg.append(
                    f'<circle cx="{tx(hx):.2f}" cy="{ty(ky):.2f}" r="{r * scale:.2f}" class="richmond-circle"/>'
                )
            elif "compass_step" not in data.classes and r < 1.6:
                lines_svg.append(
                    f'<circle cx="{tx(hx):.2f}" cy="{ty(ky):.2f}" r="{r * scale:.2f}" class="guide-circle"/>'
                )
        elif isinstance(el, spg.Line) and "richmond" in data.classes:
            seg = _clip_line_to_box(el, -1.12, 1.12, -1.12, 1.12)
            if seg is not None:
                (x1, y1), (x2, y2) = seg
                lines_svg.append(
                    f'<line x1="{tx(x1):.2f}" y1="{ty(y1):.2f}" x2="{tx(x2):.2f}" y2="{ty(y2):.2f}" class="richmond-line"/>'
                )

    lines_svg.append(
        f'<line x1="{tx(-1.2):.2f}" y1="{ty(0):.2f}" x2="{tx(1.2):.2f}" y2="{ty(0):.2f}" class="axis"/>'
    )
    lines_svg.append(
        f'<line x1="{tx(0):.2f}" y1="{ty(-1.2):.2f}" x2="{tx(0):.2f}" y2="{ty(1.2):.2f}" class="axis"/>'
    )
    lines_svg.append(
        f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{scale:.2f}" class="main-circle"/>'
    )

    for k in range(17):
        p1, p2 = vertices[k], vertices[(k + 3) % 17]
        x1, y1 = float(p1.x.evalf()), float(p1.y.evalf())
        x2, y2 = float(p2.x.evalf()), float(p2.y.evalf())
        lines_svg.append(
            f'<line x1="{tx(x1):.2f}" y1="{ty(y1):.2f}" x2="{tx(x2):.2f}" y2="{ty(y2):.2f}" class="chord-star"/>'
        )

    pts_attr = " ".join(
        f"{tx(float(v.x.evalf())):.2f},{ty(float(v.y.evalf())):.2f}" for v in vertices
    )
    lines_svg.append(f'<polygon points="{pts_attr}" class="poly-fill"/>')

    milestone_offsets = {
        "O": (-16, 16),
        "A": (8, -10),
        "B": (-22, 4),
        "S": (2, 18),
        "C": (-6, -10),
        "D": (-14, 18),
        "E": (-20, -4),
        "F": (4, 18),
        "G": (-14, 18),
    }
    for name, pt in milestones.items():
        if name in ("V0", "M_OA"):
            continue
        px, py = float(pt.x.evalf()), float(pt.y.evalf())
        cls = "pt-given" if name == "O" else "pt-milestone"
        lines_svg.append(
            f'<circle cx="{tx(px):.2f}" cy="{ty(py):.2f}" r="4.2" class="{cls}"/>'
        )
        ox, oy = milestone_offsets.get(name, (6, -6))
        lines_svg.append(
            f'<text x="{tx(px) + ox:.2f}" y="{ty(py) + oy:.2f}" class="lbl-m">{name}</text>'
        )

    for k, v in enumerate(vertices):
        vx, vy = float(v.x.evalf()), float(v.y.evalf())
        cls = "pt-given" if k == 0 else "pt-vertex"
        r_dot = 5.2 if k in (0, 3, 5) else 4.2
        lines_svg.append(
            f'<circle cx="{tx(vx):.2f}" cy="{ty(vy):.2f}" r="{r_dot}" class="{cls}"/>'
        )
        lx = tx(vx * 1.085) - 10
        ly = ty(vy * 1.085) + 4
        lines_svg.append(f'<text x="{lx:.2f}" y="{ly:.2f}" class="lbl-v">V{k}</text>')

    lines_svg.append("</svg>")
    out_path.write_text("\n".join(lines_svg), encoding="utf-8")


def render_carlyle_svg(
    model: Model,
    milestones: dict[str, spg.Point],
    vertices: list[spg.Point],
    out_path: Path,
) -> None:
    """Render a dark-theme SVG of DeTemple's (1991) 4-Carlyle-circle construction."""
    size = 1000
    scale = 175.0
    cx, cy = 565.0, 520.0

    def tx(x: float) -> float:
        return cx + x * scale

    def ty(y: float) -> float:
        return cy - y * scale

    carlyle_palette = {
        "( M1 A )": ("#34d399", "C1 (8-periods)"),
        "( H1 A )": ("#38bdf8", "C2 (QR 4-periods)"),
        "( H2 A )": ("#c084fc", "C3 (NR 4-periods)"),
        "( M4 A )": ("#fb7185", "C4 (2-periods)"),
    }

    lines_svg: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">',
        '<rect width="100%" height="100%" fill="#0e1015"/>',
        "<style>",
        "  .guide-circle { stroke: #334155; stroke-width: 0.9; stroke-dasharray: 3 4; fill: none; opacity: 0.5; }",
        "  .carlyle-line { stroke: #fb7185; stroke-width: 1.25; stroke-dasharray: 5 3; opacity: 0.82; }",
        "  .axis { stroke: #64748b; stroke-width: 1.3; }",
        "  .main-circle { stroke: #cbd5e1; stroke-width: 1.9; fill: none; }",
        "  .poly-fill { fill: #f59e0b; fill-opacity: 0.09; stroke: #f59e0b; stroke-width: 2.2; stroke-linejoin: round; }",
        "  .pt-vertex { fill: #fbbf24; stroke: #0e1015; stroke-width: 1.4; }",
        "  .pt-milestone { fill: #34d399; stroke: #0e1015; stroke-width: 1.4; }",
        "  .pt-given { fill: #f8fafc; stroke: #f59e0b; stroke-width: 2.0; }",
        "  .lbl-v { fill: #fde68a; font-family: monospace; font-size: 11px; font-weight: bold; }",
        "  .lbl-m { fill: #6ee7b7; font-family: monospace; font-size: 11.5px; font-weight: bold; }",
        "  .title { fill: #f8fafc; font-family: monospace; font-size: 18px; font-weight: bold; letter-spacing: 3px; }",
        "  .subtitle { fill: #94a3b8; font-family: monospace; font-size: 12px; }",
        "  .legend { font-family: monospace; font-size: 11.5px; font-weight: bold; }",
        "</style>",
        '<text x="36" y="44" class="title">GEOMETOR • REGULAR HEPTADECAGON (17-GON)</text>',
        '<text x="36" y="66" class="subtitle">Method 2: Duane W. DeTemple (1991) 4-Carlyle-Circle Gauss Period Construction • Lands on V1 &amp; V4</text>',
    ]

    # Legend for the 4 Carlyle circles
    lx_leg = 36
    for col, desc in carlyle_palette.values():
        lines_svg.append(
            f'<text x="{lx_leg}" y="92" fill="{col}" class="legend">● {desc}</text>'
        )
        lx_leg += 225

    # Axes across full Carlyle domain [-3.05, 2.22] x [-1.8, 1.9]
    lines_svg.append(
        f'<line x1="{tx(-3.05):.2f}" y1="{ty(0):.2f}" x2="{tx(2.22):.2f}" y2="{ty(0):.2f}" class="axis"/>'
    )
    lines_svg.append(
        f'<line x1="{tx(0):.2f}" y1="{ty(-1.80):.2f}" x2="{tx(0):.2f}" y2="{ty(1.90):.2f}" class="axis"/>'
    )

    for el, data in model.items():
        if isinstance(el, spg.Circle):
            if data.ID == "( O V0 )":
                continue
            hx, ky, r = (
                float(el.center.x.evalf()),
                float(el.center.y.evalf()),
                float(el.radius.evalf()),
            )
            if data.ID in carlyle_palette:
                col, _ = carlyle_palette[data.ID]
                lines_svg.append(
                    f'<circle cx="{tx(hx):.2f}" cy="{ty(ky):.2f}" r="{r * scale:.2f}" '
                    f'stroke="{col}" stroke-width="1.65" stroke-dasharray="7 4" fill="none" opacity="0.9"/>'
                )
            elif data.ID == "( O W3 )":
                lines_svg.append(
                    f'<circle cx="{tx(hx):.2f}" cy="{ty(ky):.2f}" r="{r * scale:.2f}" class="guide-circle"/>'
                )
        elif isinstance(el, spg.Line) and "carlyle_line" in data.classes:
            seg = _clip_line_to_box(el, -1.5, 2.15, -1.25, 1.45)
            if seg is not None:
                (x1, y1), (x2, y2) = seg
                lines_svg.append(
                    f'<line x1="{tx(x1):.2f}" y1="{ty(y1):.2f}" x2="{tx(x2):.2f}" y2="{ty(y2):.2f}" class="carlyle-line"/>'
                )

    lines_svg.append(
        f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{scale:.2f}" class="main-circle"/>'
    )

    pts_attr = " ".join(
        f"{tx(float(v.x.evalf())):.2f},{ty(float(v.y.evalf())):.2f}" for v in vertices
    )
    lines_svg.append(f'<polygon points="{pts_attr}" class="poly-fill"/>')

    mile_offsets = {
        "O": (-14, 15),
        "A": (-18, -10),
        "M1": (-10, -10),
        "H1": (-6, 17),
        "H2": (-10, -10),
        "W1": (4, 17),
        "W2": (-18, 17),
        "W3": (3, -9),
        "W4": (-12, 17),
        "Y3": (-24, 4),
        "M4": (7, -6),
        "Z1": (5, -9),
        "Z4": (3, 17),
    }
    for name, pt in milestones.items():
        if name == "V0":
            continue
        px, py = float(pt.x.evalf()), float(pt.y.evalf())
        cls = "pt-given" if name in ("O", "A") else "pt-milestone"
        lines_svg.append(
            f'<circle cx="{tx(px):.2f}" cy="{ty(py):.2f}" r="4.0" class="{cls}"/>'
        )
        ox, oy = mile_offsets.get(name, (5, -6))
        lines_svg.append(
            f'<text x="{tx(px) + ox:.2f}" y="{ty(py) + oy:.2f}" class="lbl-m">{name}</text>'
        )

    for k, v in enumerate(vertices):
        vx, vy = float(v.x.evalf()), float(v.y.evalf())
        cls = "pt-given" if k == 0 else "pt-vertex"
        r_dot = 4.8 if k in (0, 1, 4, 13, 16) else 3.6
        lines_svg.append(
            f'<circle cx="{tx(vx):.2f}" cy="{ty(vy):.2f}" r="{r_dot}" class="{cls}"/>'
        )
        lx = tx(vx * 1.13) - 9
        ly = ty(vy * 1.13) + 4
        lines_svg.append(f'<text x="{lx:.2f}" y="{ly:.2f}" class="lbl-v">V{k}</text>')

    lines_svg.append("</svg>")
    out_path.write_text("\n".join(lines_svg), encoding="utf-8")


def render_mascheroni_svg(
    model: Model,
    milestones: dict[str, spg.Point],
    vertices: list[spg.Point],
    out_path: Path,
) -> None:
    """Render a two-viewport pure-circle SVG of the Mohr-Mascheroni compass-only construction."""
    size = 1000
    lines_svg: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">',
        '<rect width="100%" height="100%" fill="#0e1015"/>',
        "<defs>",
        '  <clipPath id="clip-macro"><rect x="36" y="88" width="928" height="352" rx="8"/></clipPath>',
        '  <clipPath id="clip-micro"><rect x="36" y="468" width="928" height="496" rx="8"/></clipPath>',
        "</defs>",
        "<style>",
        "  .panel-bg { fill: #121620; stroke: #334155; stroke-width: 1.2; }",
        "  .panel-hdr { fill: #cbd5e1; font-family: monospace; font-size: 12px; font-weight: bold; }",
        "  .c-guide { stroke: #334155; stroke-width: 0.75; fill: none; opacity: 0.42; }",
        "  .c-pair { stroke: #38bdf8; stroke-width: 1.25; stroke-dasharray: 5 3; fill: none; opacity: 0.78; }",
        "  .c-inv { stroke: #34d399; stroke-width: 1.6; stroke-dasharray: 6 3; fill: none; opacity: 0.92; }",
        "  .c-nap { stroke: #c084fc; stroke-width: 1.2; stroke-dasharray: 4 3; fill: none; opacity: 0.8; }",
        "  .c-step { stroke: #f59e0b; stroke-width: 0.9; stroke-dasharray: 3 3; fill: none; opacity: 0.45; }",
        "  .c-main { stroke: #f8fafc; stroke-width: 1.9; fill: none; }",
        "  .pt-vertex { fill: #fbbf24; stroke: #0e1015; stroke-width: 1.4; }",
        "  .pt-mile { fill: #38bdf8; stroke: #0e1015; stroke-width: 1.3; }",
        "  .pt-given { fill: #f8fafc; stroke: #f59e0b; stroke-width: 2.0; }",
        "  .lbl-v { fill: #fde68a; font-family: monospace; font-size: 12px; font-weight: bold; }",
        "  .lbl-m { fill: #7dd3fc; font-family: monospace; font-size: 11px; font-weight: bold; }",
        "  .title { fill: #f8fafc; font-family: monospace; font-size: 18px; font-weight: bold; letter-spacing: 3px; }",
        "  .subtitle { fill: #94a3b8; font-family: monospace; font-size: 12px; }",
        "</style>",
        '<text x="36" y="44" class="title">GEOMETOR • REGULAR HEPTADECAGON (17-GON)</text>',
        '<text x="36" y="66" class="subtitle">Method 3: Mohr–Mascheroni Pure-Compass Construction • 83 Circles, Strictly 0 Straightedge Lines</text>',
    ]

    # --- Panel 1 (Macro): Full Symmetric Carlyle-Pair & Inversion Field ---
    lines_svg.append('<rect x="36" y="88" width="928" height="352" rx="8" class="panel-bg"/>')
    lines_svg.append(
        '<text x="52" y="110" class="panel-hdr">A. MACRO FIELD — SYMMETRIC CARLYLE CIRCLE PAIRS (k = 3) &amp; INVERSION IN C_root3 (R = √3)</text>'
    )
    mcx, mcy, mscale = 545.0, 272.0, 52.0

    def mtx(x: float) -> float:
        return mcx + x * mscale

    def mty(y: float) -> float:
        return mcy - y * mscale

    lines_svg.append('<g clip-path="url(#clip-macro)">')
    for el, data in model.items():
        if not isinstance(el, spg.Circle):
            continue
        hx, ky, r = (
            float(el.center.x.evalf()),
            float(el.center.y.evalf()),
            float(el.radius.evalf()),
        )
        if data.ID == "( O V0 )":
            cls = "c-main"
        elif "inversion_circle" in data.classes or "inversion" in data.classes:
            cls = "c-inv"
        elif "carlyle_pair" in data.classes:
            cls = "c-pair"
        elif "compass_step" in data.classes:
            continue
        else:
            cls = "c-guide"
        lines_svg.append(
            f'<circle cx="{mtx(hx):.2f}" cy="{mty(ky):.2f}" r="{r * mscale:.2f}" class="{cls}"/>'
        )

    macro_labels = [
        ("W4_hat", (-18, 15)),
        ("H2_hat", (-18, -8)),
        ("W2_hat", (-18, 15)),
        ("H0", (-10, -9)),
        ("O", (4, 14)),
        ("W3_hat", (5, -10)),
        ("H1_hat", (-8, 15)),
        ("Z4_hat", (-18, 16)),
        ("Z1_hat", (4, 15)),
        ("W1_hat", (5, -8)),
        ("M4_up", (6, -6)),
    ]
    for name, (ox, oy) in macro_labels:
        pt = milestones[name]
        px, py = float(pt.x.evalf()), float(pt.y.evalf())
        pcls = "pt-given" if name == "O" else "pt-mile"
        lines_svg.append(
            f'<circle cx="{mtx(px):.2f}" cy="{mty(py):.2f}" r="3.4" class="{pcls}"/>'
        )
        lines_svg.append(
            f'<text x="{mtx(px) + ox:.2f}" y="{mty(py) + oy:.2f}" class="lbl-m">{name}</text>'
        )
    lines_svg.append("</g>")

    # --- Panel 2 (Micro): Unit-Circle Compass Rosette, Napoleon Seed & (P1, O) Projection ---
    lines_svg.append('<rect x="36" y="468" width="928" height="496" rx="8" class="panel-bg"/>')
    lines_svg.append(
        '<text x="52" y="492" class="panel-hdr">B. UNIT-CIRCLE DETAIL — NAPOLEON √2 SEED, C_root3, (P1, O) PROJECTION → V1, V16 &amp; 14 COMPASS STEPS</text>'
    )
    ucx, ucy, uscale = 500.0, 726.0, 122.0

    def utx(x: float) -> float:
        return ucx + x * uscale

    def uty(y: float) -> float:
        return ucy - y * uscale

    lines_svg.append('<g clip-path="url(#clip-micro)">')
    for el, data in model.items():
        if not isinstance(el, spg.Circle):
            continue
        hx, ky, r = (
            float(el.center.x.evalf()),
            float(el.center.y.evalf()),
            float(el.radius.evalf()),
        )
        if data.ID == "( O V0 )":
            continue
        if "inversion_circle" in data.classes:
            cls = "c-inv"
        elif data.ID == "( P1 O )":
            cls = "c-pair"
        elif "napoleon" in data.classes or "mascheroni_seed" in data.classes:
            cls = "c-nap"
        elif "compass_step" in data.classes:
            cls = "c-step"
        elif r <= 2.2 and abs(hx) <= 1.5 and abs(ky) <= 1.5:
            cls = "c-guide"
        else:
            continue
        lines_svg.append(
            f'<circle cx="{utx(hx):.2f}" cy="{uty(ky):.2f}" r="{r * uscale:.2f}" class="{cls}"/>'
        )

    lines_svg.append(
        f'<circle cx="{ucx:.2f}" cy="{ucy:.2f}" r="{uscale:.2f}" class="c-main"/>'
    )

    micro_labels = [
        ("O", (-15, 14)),
        ("A", (-16, -8)),
        ("N_up", (7, -4)),
        ("R_up", (7, -4)),
        ("P1", (4, 15)),
        ("H0", (-18, 15)),
    ]
    for name, (ox, oy) in micro_labels:
        pt = milestones[name]
        px, py = float(pt.x.evalf()), float(pt.y.evalf())
        pcls = "pt-given" if name == "O" else "pt-mile"
        lines_svg.append(
            f'<circle cx="{utx(px):.2f}" cy="{uty(py):.2f}" r="3.8" class="{pcls}"/>'
        )
        lines_svg.append(
            f'<text x="{utx(px) + ox:.2f}" y="{uty(py) + oy:.2f}" class="lbl-m">{name}</text>'
        )

    for k, v in enumerate(vertices):
        vx, vy = float(v.x.evalf()), float(v.y.evalf())
        cls = "pt-given" if k == 0 else "pt-vertex"
        r_dot = 5.0 if k in (0, 1, 16) else 3.9
        lines_svg.append(
            f'<circle cx="{utx(vx):.2f}" cy="{uty(vy):.2f}" r="{r_dot}" class="{cls}"/>'
        )
        lx = utx(vx * 1.15) - 9
        ly = uty(vy * 1.15) + 4
        lines_svg.append(f'<text x="{lx:.2f}" y="{ly:.2f}" class="lbl-v">V{k}</text>')

    lines_svg.append("</g>")
    lines_svg.append("</svg>")
    out_path.write_text("\n".join(lines_svg), encoding="utf-8")


def run_report(save_dir: Path | None = None) -> dict[str, Model]:
    """Build all three symbolic heptadecagon models, verify exact equivalence, print tables, and save SVGs/JSONs."""
    console = Console(width=122)
    if save_dir is None:
        save_dir = Path(__file__).resolve().parent

    t0 = time.perf_counter()
    m_rich, mile_rich, v_rich = construct_richmond_heptadecagon(quiet=True, add_sides=True)
    dt_rich = time.perf_counter() - t0

    t1 = time.perf_counter()
    m_carl, mile_carl, v_carl = construct_carlyle_heptadecagon(quiet=True, add_sides=True)
    dt_carl = time.perf_counter() - t1

    t2 = time.perf_counter()
    m_masch, mile_masch, v_masch = construct_mascheroni_heptadecagon(
        quiet=True, add_sides=False
    )
    dt_masch = time.perf_counter() - t2

    # --- Exact Cross-Method & Algebraic Verification ---
    assert v_rich == v_carl == v_masch, (
        "Symbolic vertex mismatch across Richmond, Carlyle, and Mascheroni models!"
    )
    assert len(m_masch.lines) == 0, "Mascheroni model must have strictly 0 lines!"

    vertices = v_rich
    for k, v in enumerate(vertices):
        norm_sq = canonicalize_17(v.x**2 + v.y**2)
        assert norm_sq == 1, f"Vertex V{k} failed exact unit circle identity: {norm_sq}"

    side_sq_ref = canonicalize_17(2 - 2 * vertices[1].x)
    for k in range(17):
        v_a, v_b = vertices[k], vertices[(k + 1) % 17]
        d_sq = canonicalize_17((v_a.x - v_b.x) ** 2 + (v_a.y - v_b.y) ** 2)
        assert d_sq == side_sq_ref, f"Side / V{k} V{(k+1)%17} / squared length mismatch!"

    chord_sqs = [canonicalize_17(2 - 2 * vertices[m].x) for m in range(1, 9)]
    assert canonicalize_17(sum(chord_sqs)) == 17
    prod_chord_sqs = sp.Integer(1)
    for csq in chord_sqs:
        prod_chord_sqs = canonicalize_17(prod_chord_sqs * csq)
    assert prod_chord_sqs == 17

    # --- Save JSONs and SVGs ---
    outputs = [
        ("richmond", m_rich, "heptadecagon.json", "heptadecagon.svg"),
        ("carlyle", m_carl, "heptadecagon_carlyle.json", "heptadecagon_carlyle.svg"),
        (
            "mascheroni",
            m_masch,
            "heptadecagon_mascheroni.json",
            "heptadecagon_mascheroni.svg",
        ),
    ]
    for _, mdl, jname, _ in outputs:
        jpath = save_dir / jname
        mdl.save(str(jpath))
        reloaded = load_model(str(jpath))
        assert len(reloaded) == len(mdl), f"Reloaded element count mismatch for {jname}"

    render_heptadecagon_svg(m_rich, mile_rich, v_rich, save_dir / "heptadecagon.svg")
    render_carlyle_svg(
        m_carl, mile_carl, v_carl, save_dir / "heptadecagon_carlyle.svg"
    )
    render_mascheroni_svg(
        m_masch, mile_masch, v_masch, save_dir / "heptadecagon_mascheroni.svg"
    )

    # --- Header Panel ---
    console.print(
        Panel.fit(
            f"[bold gold1]GEOMETOR • REGULAR HEPTADECAGON (17-GON) — THREE CONSTRUCTIVE PATHWAYS[/bold gold1]\n"
            f"1. [cyan]H. W. Richmond (1893)[/cyan]      • Angle-quartering (compass + straightedge) -> [bold]{len(m_rich)}[/bold] elements ({dt_rich:.1f}s)\n"
            f"2. [green]Duane W. DeTemple (1991)[/green]  • 4 Carlyle circles solving Gauss periods   -> [bold]{len(m_carl)}[/bold] elements ({dt_carl:.1f}s)\n"
            f"3. [magenta]Mohr–Mascheroni (Pure)[/magenta]    • Collapsible circles only (0 lines!)       -> [bold]{len(m_masch)}[/bold] elements ({dt_masch:.1f}s)\n"
            f"Exact Equivalence: v_richmond == v_carlyle == v_mascheroni ✓  •  ∑ dₘ² = 17 ✓  •  ∏ dₘ = √17 ✓",
            border_style="gold1",
        )
    )

    # --- Table 0: Side-by-Side Comparison of the 3 Constructions ---
    t_cmp = Table(
        title="0. Side-by-Side Comparison of the Three Symbolic Constructions",
        border_style="gold1",
    )
    t_cmp.add_column("Method", style="bold white")
    t_cmp.add_column("Tools Allowed", justify="center")
    t_cmp.add_column("Lines", justify="right", style="cyan")
    t_cmp.add_column("Circles", justify="right", style="green")
    t_cmp.add_column("Points", justify="right", style="yellow")
    t_cmp.add_column("Entry Vertices", justify="center")
    t_cmp.add_column("Core Geometric Mechanism")

    for label, tools, mdl, entry_v, mech in [
        (
            "Richmond (1893)",
            "Compass + Straightedge",
            m_rich,
            "V3, V14 & V5, V12 (NR)",
            "Quarters ∠OBV0 = arctan(4); circle (C, E) splits cos(6π/17), cos(10π/17)",
        ),
        (
            "DeTemple Carlyle (1991)",
            "Compass + Straightedge",
            m_carl,
            "V1, V16 & V4, V13 (QR)",
            "4 Carlyle circles through A(0,1) solve Gauss's 8-, 4-, and 2-period quadratics",
        ),
        (
            "Mohr–Mascheroni",
            "Compass ONLY (0 lines)",
            m_masch,
            "V1, V16 (QR)",
            "Napoleon √2 + C_root3 inversion + symmetric Carlyle pairs + (P1, O) ∩ C0",
        ),
    ]:
        n_pts = len(mdl.points)
        n_vis = sum(1 for p in mdl.points if not mdl[p].guide)
        t_cmp.add_row(
            label,
            tools,
            str(len(mdl.lines)),
            str(len(mdl.circles)),
            f"{n_pts} ({n_vis})",
            entry_v,
            mech,
        )
    console.print(t_cmp)

    # --- Table 1: Radical Tower Basis ---
    t_basis = Table(
        title="1. The 4-Level √17 Gaussian Radical Tower (Basis of K₈)",
        border_style="cyan",
    )
    t_basis.add_column("Symbol", style="bold yellow", justify="center")
    t_basis.add_column("Depth", justify="center")
    t_basis.add_column("Exact Radical Definition (Pure √17)", style="cyan")
    t_basis.add_column("Numeric", justify="right")
    for sym, depth, formula, val in [
        ("√17", "1", "√17", float(SQRT17.evalf())),
        ("A₋", "2", "√(34 - 2·√17)", float(A_MINUS.evalf())),
        ("A₊", "2", "√(34 + 2·√17)   [= (1 + √17)·A₋ / 4]", float(A_PLUS.evalf())),
        ("R₁", "3", "√(17 + 3·√17 - A₋ - 2·A₊)", float(R1.evalf())),
        ("R₂", "3", "√(17 + 3·√17 + A₋ + 2·A₊)", float(R2.evalf())),
        ("R₃", "3", "√(17 - 3·√17 + 2·A₋ - A₊)", float(R3.evalf())),
        ("R₄", "3", "√(17 - 3·√17 - 2·A₋ + A₊)", float(R4.evalf())),
    ]:
        t_basis.add_row(sym, depth, formula, f"{val:+.10f}")
    console.print(t_basis)

    # --- Table 2A: Richmond Milestones ---
    t_rich = Table(
        title="2A. Pathway 1 — H. W. Richmond (1893) Angle-Quartering Milestones",
        border_style="bright_blue",
    )
    t_rich.add_column("ID", style="bold bright_cyan", justify="center")
    t_rich.add_column("Geometric Role", style="white")
    t_rich.add_column("Exact Coordinates (x, y)", style="cyan")
    t_rich.add_column("(x, y) Float", justify="right")
    for mid, role in [
        ("B", "Quarter-radius mark (OB = 1/4 OA)"),
        ("S", "1st bisection (∠OBS = 1/2 ∠OBV0) • QR centroid"),
        ("C", "2nd bisection (∠OBC = 1/4 ∠OBV0) • Midpoint(V3.x, V5.x)"),
        ("D", "45° ray intersection (∠DBC = 45°)"),
        ("E", "Circle on diameter DV0 ∩ OA (y_E = √(-x_D))"),
        ("F", "Circle (C, E) ∩ OV0 right -> cos(6π/17) = V3.x"),
        ("G", "Circle (C, E) ∩ OV0 left  -> cos(10π/17) = V5.x"),
    ]:
        pt = mile_rich[mid]
        sx = format_shorthand_k8(pt.x)
        sy = format_shorthand_sqrt_y(pt.y)
        t_rich.add_row(
            mid,
            role,
            f"({sx},  {sy})",
            f"({float(pt.x.evalf()):+.6f}, {float(pt.y.evalf()):+.6f})",
        )
    console.print(t_rich)

    # --- Table 2B: DeTemple Carlyle Milestones ---
    t_carl = Table(
        title="2B. Pathway 2 — Duane W. DeTemple (1991) Carlyle-Circle Period Milestones",
        border_style="green",
    )
    t_carl.add_column("ID", style="bold green", justify="center")
    t_carl.add_column("Quadratic Solved / Role", style="white")
    t_carl.add_column("Exact Coordinates (x, y)", style="cyan")
    t_carl.add_column("(x, y) Float", justify="right")
    for mid, role in [
        ("M1", "Center of C1 (-1/4, 0) for u² + (1/2)u - 1 = 0"),
        ("H1", "C1 ∩ x-axis -> η₁/2 (half QR 8-period)"),
        ("H2", "C1 ∩ x-axis -> η₂/2 (half NR 8-period)"),
        ("W1", "C2=(H1, A) ∩ x-axis -> w₁ (QR 4-period: V1,V4,V13,V16)"),
        ("W2", "C2=(H1, A) ∩ x-axis -> w₂ (QR 4-period: V2,V8,V9,V15)"),
        ("W3", "C3=(H2, A) ∩ x-axis -> w₃ (NR 4-period: V3,V5,V12,V14)"),
        ("W4", "C3=(H2, A) ∩ x-axis -> w₄ (NR 4-period: V6,V7,V10,V11)"),
        ("M4", "Center (w₁/2, (1+w₃)/2) of C4 for z² - w₁z + w₃ = 0"),
        ("Z1", "C4=(M4, A) ∩ x-axis -> 2·cos(2π/17) = 2·V1.x"),
        ("Z4", "C4=(M4, A) ∩ x-axis -> 2·cos(8π/17) = 2·V4.x"),
    ]:
        pt = mile_carl[mid]
        sx = format_shorthand_k8(pt.x)
        sy = format_shorthand_k8(pt.y)
        t_carl.add_row(
            mid,
            role,
            f"({sx},  {sy})",
            f"({float(pt.x.evalf()):+.6f}, {float(pt.y.evalf()):+.6f})",
        )
    console.print(t_carl)

    # --- Table 2C: Mohr-Mascheroni Milestones ---
    t_masch = Table(
        title="2C. Pathway 3 — Mohr–Mascheroni Pure-Compass Milestones (0 Lines)",
        border_style="magenta",
    )
    t_masch.add_column("ID", style="bold magenta", justify="center")
    t_masch.add_column("Compass-Only Step", style="white")
    t_masch.add_column("Exact Coordinates (x, y)", style="cyan")
    t_masch.add_column("(x, y) Float", justify="right")
    for mid, role in [
        ("R_up", "(T1, O) ∩ (T2, O) -> defines inversion circle C_root3 (R² = 3)"),
        ("N_up", "Napoleon circles (V0, T2) ∩ (W, T1) -> orthogonal √2 seed"),
        ("H0", "Inverse of X_m4(-4, 0) in C_root3 -> 3-scaled seed (-3/4, 0)"),
        ("H1_hat", "Symmetric Carlyle pair at H0 -> 3·u₁"),
        ("W1_hat", "Symmetric Carlyle pair at H1_hat -> 3·w₁"),
        ("W3_hat", "Symmetric Carlyle pair at H2_hat -> 3·w₃"),
        ("M4_up", "7-circle Mascheroni midpoint (3·w₁/2, (3 + 3·w₃)/2)"),
        ("Z1_hat", "(M4_up, A_3) ∩ (M4_dn, A_3s) -> 6·cos(2π/17)"),
        ("P1", "Inverse of Z1_hat in C_root3 -> 1/(2·cos(2π/17)) [mixes QR & NR!]"),
    ]:
        pt = mile_masch[mid]
        sx = format_shorthand_k8(pt.x)
        sy = (
            format_shorthand_k8(pt.y)
            if decompose_k8(pt.y) is not None
            else format_shorthand_sqrt_y(pt.y)
        )
        t_masch.add_row(
            mid,
            role,
            f"({sx},  {sy})",
            f"({float(pt.x.evalf()):+.6f}, {float(pt.y.evalf()):+.6f})",
        )
    console.print(t_masch)

    # --- Table 3: All 17 Vertices ---
    t_verts = Table(
        title="3. Complete Symbolic Coordinates of All 17 Vertices (Identical Across All 3 Constructions)",
        border_style="gold1",
    )
    t_verts.add_column("ID", style="bold gold1", justify="center")
    t_verts.add_column("Mod 17", justify="center")
    t_verts.add_column("Exact xₖ = cos(2πk/17)", style="cyan")
    t_verts.add_column("Exact yₖ = sin(2πk/17)", style="green")
    t_verts.add_column("(xₖ, yₖ)", justify="right")

    for k, v in enumerate(vertices):
        if k == 0:
            res_tag = "0"
        elif k in QUAD_RESIDUES_17:
            res_tag = "[bold green]QR (+√17)[/bold green]"
        else:
            res_tag = "[bold magenta]NR (-√17)[/bold magenta]"
        sx = format_shorthand_k8(v.x)
        sy = "0" if k == 0 else format_shorthand_sqrt_y(v.y)
        fx, fy = float(v.x.evalf()), float(v.y.evalf())
        t_verts.add_row(f"V{k}", res_tag, sx, sy, f"({fx:+.5f}, {fy:+.5f})")
    console.print(t_verts)

    for _, _, jname, sname in outputs:
        rich.print(f"[dim]Saved {save_dir / jname}  &  {save_dir / sname}[/dim]")

    return {"richmond": m_rich, "carlyle": m_carl, "mascheroni": m_masch}
