"""Exact cyclotomic number-field arithmetic and Gaussian radical canonicalization for p = 17.

Every vertex coordinate (x_k, y_k) = (cos(2*pi*k/17), sin(2*pi*k/17)) and every axial
milestone in H. W. Richmond's 1893 construction lives inside the 16-dimensional cyclotomic
subfield K_16 = K_8(sin(2*pi/17)) of Q(zeta_17), built as a 4-step quadratic radical tower:

    Q  ⊂  Q(sqrt(17))  ⊂  Q(sqrt(34 - 2*sqrt(17)))  ⊂  K_8 = Q(R_1)  ⊂  K_16

Auxiliary compass-and-straightedge scaffolding (equilateral bisector poles and Step 4/5
intermediate circles) lives in biquadratic extensions K_8[sqrt(3), sqrt(U)] with U in K_8.
This module evaluates SymPy expressions in exact polynomial arithmetic over
QQ[t] / (M_8(t)) (where t = R_1 satisfies t^8 - 68*t^6 + 1088*t^4 - 5440*t^2 + 4352 = 0)
and projects results onto Gauss's 8-element radical basis {1, sqrt(17), A_-, A_+, R_1..R_4}.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction

import mpmath as mp
import sympy as sp
from sympy.polys.polytools import Poly, gcdex, rem

# --- The 4-Level Gaussian Radical Tower for p = 17 ---
SQRT17 = sp.sqrt(17)
A_MINUS = sp.sqrt(34 - 2 * SQRT17)
A_PLUS = sp.sqrt(34 + 2 * SQRT17)

R1 = sp.sqrt(17 + 3 * SQRT17 - A_MINUS - 2 * A_PLUS)
R2 = sp.sqrt(17 + 3 * SQRT17 + A_MINUS + 2 * A_PLUS)
R3 = sp.sqrt(17 - 3 * SQRT17 + 2 * A_MINUS - A_PLUS)
R4 = sp.sqrt(17 - 3 * SQRT17 - 2 * A_MINUS + A_PLUS)

B8_NAMES = ("1", "√17", "A₋", "A₊", "R₁", "R₂", "R₃", "R₄")
B8_EXPRS = (sp.Integer(1), SQRT17, A_MINUS, A_PLUS, R1, R2, R3, R4)

_t = sp.Symbol("t")
# Minimal polynomial of R1 over Q (Eisenstein at 17: all non-leading coefficients divisible by 17)
M8 = Poly(_t**8 - 68 * _t**6 + 1088 * _t**4 - 5440 * _t**2 + 4352, _t, domain="QQ")
ZERO_P = Poly(0, _t, domain="QQ")
ONE_P = Poly(1, _t, domain="QQ")
THREE_P = Poly(3, _t, domain="QQ")
THIRD_P = Poly(sp.Rational(1, 3), _t, domain="QQ")

LUVal = tuple[Poly, Poly, Poly, Poly]  # a0 + a1*sqrt(3) + a2*sqrt(U) + a3*sqrt(3*U)
ZERO_LU: LUVal = (ZERO_P, ZERO_P, ZERO_P, ZERO_P)
ONE_LU: LUVal = (ONE_P, ZERO_P, ZERO_P, ZERO_P)


@dataclass
class _EvalCtx:
    """Tracks the active quadratic radicand U in K_8 during biquadratic evaluation."""

    u_poly: Poly | None = None
    u_inv: Poly | None = None

    def clone(self) -> _EvalCtx:
        return _EvalCtx(self.u_poly, self.u_inv)

    def adopt(self, other: _EvalCtx) -> None:
        if self.u_poly is None and other.u_poly is not None:
            self.u_poly = other.u_poly
            self.u_inv = other.u_inv


class _Cyclotomic17Engine:
    """Lazy-initialized exact arithmetic engine in K_8[sqrt(3), sqrt(U)]."""

    def __init__(self) -> None:
        cols = []
        self.b8_polys: list[Poly] = []
        for expr in B8_EXPRS:
            nf = sp.to_number_field(expr, R1)
            coeffs = nf.coeffs()  # descending powers of R1
            p = Poly(coeffs, _t, domain="QQ")
            self.b8_polys.append(p)
            cols.append([sp.Integer(0)] * (8 - len(coeffs)) + list(coeffs))

        m_mat = sp.Matrix(cols).T
        self.m_inv: sp.Matrix = m_mat.inv()

        with mp.workdps(85):
            self.roots_mp = [
                mp.mpf(str(r.evalf(85))) for r in sp.nroots(M8.as_expr(), n=85)
            ]
            v_mp = mp.matrix(
                [[r ** (7 - j) for j in range(8)] for r in self.roots_mp]
            )
            self.v_inv_mp = v_mp ** (-1)

        self.r1_float = float(R1.evalf())
        self.sqrt_cache: dict[tuple, Poly | None] = {}

        # Pre-seed square roots of the radical basis elements
        for b_poly in self.b8_polys[1:]:
            sq = self.k8_mul(b_poly, b_poly)
            self.sqrt_cache[tuple(sq.all_coeffs())] = b_poly

        # Canonical normalized W2 = 16 * sin^2(2*pi/17) in K_8
        p_x1 = (
            -self.b8_polys[0]
            + self.b8_polys[1]
            + self.b8_polys[2]
            + Poly(2, _t, domain="QQ") * self.b8_polys[4]
        ) * Poly(sp.Rational(1, 16), _t, domain="QQ")
        raw_w2 = ONE_P - self.k8_mul(p_x1, p_x1)
        self.p_w2, _ = self.normalize_radicand(raw_w2)
        self.p_w2_inv = self.k8_inv(self.p_w2)

    @staticmethod
    def k8_mul(p1: Poly, p2: Poly) -> Poly:
        if p1.is_zero or p2.is_zero:
            return ZERO_P
        return rem(p1 * p2, M8, domain="QQ")

    @staticmethod
    def k8_inv(p: Poly) -> Poly:
        s, _, g = gcdex(p, M8, domain="QQ")
        if not g.is_ground or g.LC() == 0:
            raise ValueError("Non-invertible element in K_8")
        return Poly(s / g.LC(), _t, domain="QQ")

    def k8s3_mul(self, x: tuple[Poly, Poly], y: tuple[Poly, Poly]) -> tuple[Poly, Poly]:
        return (
            self.k8_mul(x[0], y[0]) + THREE_P * self.k8_mul(x[1], y[1]),
            self.k8_mul(x[0], y[1]) + self.k8_mul(x[1], y[0]),
        )

    def k8s3_inv(self, x: tuple[Poly, Poly]) -> tuple[Poly, Poly]:
        norm = self.k8_mul(x[0], x[0]) - THREE_P * self.k8_mul(x[1], x[1])
        inv_n = self.k8_inv(norm)
        return (self.k8_mul(x[0], inv_n), -self.k8_mul(x[1], inv_n))

    def lu_mul(self, a: LUVal, b: LUVal, u_poly: Poly | None) -> LUVal:
        x1, y1 = (a[0], a[1]), (a[2], a[3])
        x2, y2 = (b[0], b[1]), (b[2], b[3])
        xx = self.k8s3_mul(x1, x2)
        if (y1[0].is_zero and y1[1].is_zero) and (y2[0].is_zero and y2[1].is_zero):
            return (xx[0], xx[1], ZERO_P, ZERO_P)
        xy = self.k8s3_mul(x1, y2)
        yx = self.k8s3_mul(y1, x2)
        z_hi = (xy[0] + yx[0], xy[1] + yx[1])
        if (y1[0].is_zero and y1[1].is_zero) or (y2[0].is_zero and y2[1].is_zero):
            return (xx[0], xx[1], z_hi[0], z_hi[1])
        assert u_poly is not None
        yy = self.k8s3_mul(y1, y2)
        z_lo = (
            xx[0] + self.k8_mul(u_poly, yy[0]),
            xx[1] + self.k8_mul(u_poly, yy[1]),
        )
        return (z_lo[0], z_lo[1], z_hi[0], z_hi[1])

    def lu_inv(self, a: LUVal, u_poly: Poly | None) -> LUVal:
        x, y = (a[0], a[1]), (a[2], a[3])
        if y[0].is_zero and y[1].is_zero:
            xi = self.k8s3_inv(x)
            return (xi[0], xi[1], ZERO_P, ZERO_P)
        assert u_poly is not None
        x2 = self.k8s3_mul(x, x)
        y2 = self.k8s3_mul(y, y)
        denom = (
            x2[0] - self.k8_mul(u_poly, y2[0]),
            x2[1] - self.k8_mul(u_poly, y2[1]),
        )
        inv_d = self.k8s3_inv(denom)
        nx = self.k8s3_mul(x, inv_d)
        ny = self.k8s3_mul((-y[0], -y[1]), inv_d)
        return (nx[0], nx[1], ny[0], ny[1])

    def poly_eval_at_r1(self, p: Poly) -> float:
        if p.is_zero:
            return 0.0
        c = p.all_coeffs()
        c_desc = [sp.Integer(0)] * (8 - len(c)) + list(c)
        return sum(float(c_desc[j]) * (self.r1_float ** (7 - j)) for j in range(8))

    def poly_to_b8_coords(self, p: Poly) -> list[sp.Rational]:
        if p.is_zero:
            return [sp.Rational(0)] * 8
        c = p.all_coeffs()
        vec = sp.Matrix([sp.Integer(0)] * (8 - len(c)) + list(c))
        return list(self.m_inv * vec)

    def poly_to_b8_expr(self, p: Poly) -> sp.Expr:
        coords = self.poly_to_b8_coords(p)
        return sum(coords[i] * B8_EXPRS[i] for i in range(8))

    def normalize_radicand(self, p: Poly) -> tuple[Poly, sp.Rational]:
        """Factor p = scale^2 * u_norm where u_norm has square-free integer B8 coordinates."""
        coords = self.poly_to_b8_coords(p)
        den_lcm = 1
        for q in coords:
            den_lcm = math.lcm(den_lcm, int(q.q))
        factors_d = sp.factorint(den_lcm)
        mult_d = 1
        for prime, exp in factors_d.items():
            if exp % 2 == 1:
                mult_d *= prime
        sq_den = den_lcm * mult_d
        root_den = math.isqrt(sq_den)

        int_nums = [int(q * sq_den) for q in coords]
        num_gcd = 0
        for n in int_nums:
            num_gcd = math.gcd(num_gcd, abs(n))
        root_num = 1
        if num_gcd > 1:
            for prime, exp in sp.factorint(num_gcd).items():
                if exp >= 2:
                    root_num *= prime ** (exp // 2)

        scale = sp.Rational(root_num, root_den)
        inv_scale_sq = Poly(sp.Rational(sq_den, root_num * root_num), _t, domain="QQ")
        u_norm = self.k8_mul(p, inv_scale_sq)
        return u_norm, scale

    def k8_sqrt(self, p: Poly) -> Poly | None:
        """Return exact q in K_8 (with q(R1) >= 0) such that q^2 == p mod M8, or None."""
        if p.is_zero:
            return ZERO_P
        key = tuple(p.all_coeffs())
        if key in self.sqrt_cache:
            return self.sqrt_cache[key]

        c_desc = [sp.Integer(0)] * (8 - len(p.all_coeffs())) + list(p.all_coeffs())
        scale = 10**50
        with mp.workdps(85):
            c_mp = [mp.mpf(int(c.p)) / mp.mpf(int(c.q)) for c in c_desc]
            vals = []
            for r in self.roots_mp:
                v = sum(c_mp[j] * (r ** (7 - j)) for j in range(8))
                if v < mp.mpf("-1e-55"):
                    self.sqrt_cache[key] = None
                    return None
                vals.append(mp.sqrt(max(v, mp.mpf(0))))

            for mask in range(128):
                signed = [vals[0]] + [
                    (-vals[i + 1] if (mask >> i) & 1 else vals[i + 1])
                    for i in range(7)
                ]
                cand_vec = self.v_inv_mp * mp.matrix(signed)
                rats = []
                ok = True
                for i in range(8):
                    num = int(mp.nint(cand_vec[i] * scale))
                    frac = Fraction(num, scale).limit_denominator(10**20)
                    err = abs(
                        cand_vec[i]
                        - mp.mpf(frac.numerator) / mp.mpf(frac.denominator)
                    )
                    if err > mp.mpf("1e-30"):
                        ok = False
                        break
                    rats.append(sp.Rational(frac.numerator, frac.denominator))
                if not ok:
                    continue
                q = Poly(rats, _t, domain="QQ")
                if self.k8_mul(q, q) == p:
                    res = q if self.poly_eval_at_r1(q) >= 0 else -q
                    self.sqrt_cache[key] = res
                    return res

        self.sqrt_cache[key] = None
        return None

    def lu_sqrt_k8(self, p: Poly, ctx: _EvalCtx) -> LUVal | None:
        """Take exact positive square root of p in K_8 inside K_8[sqrt(3), sqrt(U)]."""
        if p.is_zero:
            return ZERO_LU
        if self.poly_eval_at_r1(p) < -1e-14:
            return None

        # 1. Square in K_8?
        q = self.k8_sqrt(p)
        if q is not None:
            return (q, ZERO_P, ZERO_P, ZERO_P)

        # 2. 3 * square in K_8?
        q3 = self.k8_sqrt(THIRD_P * p)
        if q3 is not None:
            return (ZERO_P, q3, ZERO_P, ZERO_P)

        # 3. Active U already chosen?
        if ctx.u_poly is not None:
            assert ctx.u_inv is not None
            qu = self.k8_sqrt(self.k8_mul(p, ctx.u_inv))
            if qu is not None:
                return (ZERO_P, ZERO_P, qu, ZERO_P)
            q3u = self.k8_sqrt(THIRD_P * self.k8_mul(p, ctx.u_inv))
            if q3u is not None:
                return (ZERO_P, ZERO_P, ZERO_P, q3u)
            return None

        # 4. Check canonical W2 = 16*sin^2(2*pi/17) first for maximum cache reuse
        qw = self.k8_sqrt(self.k8_mul(p, self.p_w2_inv))
        if qw is not None:
            ctx.u_poly = self.p_w2
            ctx.u_inv = self.p_w2_inv
            return (ZERO_P, ZERO_P, qw, ZERO_P)
        q3w = self.k8_sqrt(THIRD_P * self.k8_mul(p, self.p_w2_inv))
        if q3w is not None:
            ctx.u_poly = self.p_w2
            ctx.u_inv = self.p_w2_inv
            return (ZERO_P, ZERO_P, ZERO_P, q3w)

        # 5. Adjoin normalized U from p
        u_norm, scale = self.normalize_radicand(p)
        # Also strip factor of 3 if integer coordinates are all divisible by 3
        ctx.u_poly = u_norm
        ctx.u_inv = self.k8_inv(u_norm)
        scale_p = Poly(scale, _t, domain="QQ")
        return (ZERO_P, ZERO_P, scale_p, ZERO_P)

    def format_clean_sqrt_k8(self, p: Poly) -> sp.Expr:
        """Format sqrt(p) for p >= 0 in K_8 with a square-free integer inner radicand."""
        u_norm, scale = self.normalize_radicand(p)
        inner = self.poly_to_b8_expr(u_norm)
        return scale * sp.sqrt(inner)

    def eval_lu(self, expr: sp.Expr, ctx: _EvalCtx, _expanded: bool = False) -> LUVal | None:
        """Evaluate expr into K_8[sqrt(3), sqrt(U)]."""
        expr = sp.sympify(expr)
        if expr.is_Integer:
            return (Poly(int(expr), _t, domain="QQ"), ZERO_P, ZERO_P, ZERO_P)
        if expr.is_Rational:
            return (Poly(sp.Rational(expr), _t, domain="QQ"), ZERO_P, ZERO_P, ZERO_P)

        if expr.is_Add:
            acc = ZERO_LU
            work_ctx = ctx.clone()
            for arg in expr.args:
                child_ctx = work_ctx.clone()
                sub = self.eval_lu(arg, child_ctx)
                if sub is None:
                    return None
                if not sub[2].is_zero or not sub[3].is_zero:
                    work_ctx.adopt(child_ctx)
                acc = (
                    acc[0] + sub[0],
                    acc[1] + sub[1],
                    acc[2] + sub[2],
                    acc[3] + sub[3],
                )
            if not acc[2].is_zero or not acc[3].is_zero:
                ctx.adopt(work_ctx)
            return acc

        if expr.is_Mul:
            half_rads: list[sp.Expr] = []
            other_factors: list[sp.Expr] = []
            has_add = False
            for f in expr.args:
                if f.is_Add:
                    has_add = True
                if f.is_Pow and f.args[1].is_Rational and f.args[1].q == 2:
                    base, exp = f.args
                    k = (int(exp.p) - 1) // 2
                    if k != 0:
                        other_factors.append(base**k)
                    half_rads.append(base)
                else:
                    other_factors.append(f)

            mul_ctx = ctx.clone()
            acc = ONE_LU
            ok = True
            for f in other_factors:
                child_ctx = mul_ctx.clone()
                sub = self.eval_lu(f, child_ctx)
                if sub is None:
                    ok = False
                    break
                if not sub[2].is_zero or not sub[3].is_zero:
                    mul_ctx.adopt(child_ctx)
                acc = self.lu_mul(acc, sub, mul_ctx.u_poly)

            if ok and half_rads:
                rad_expr = sp.Mul(*half_rads) if len(half_rads) > 1 else half_rads[0]
                rad_ctx = mul_ctx.clone()
                rad_val = self.eval_lu(rad_expr, rad_ctx)
                if rad_val is None and len(half_rads) > 1:
                    rad_val = self.eval_lu(sp.expand_mul(rad_expr), rad_ctx)
                if (
                    rad_val is not None
                    and rad_val[1].is_zero
                    and rad_val[2].is_zero
                    and rad_val[3].is_zero
                ):
                    sq_val = self.lu_sqrt_k8(rad_val[0], mul_ctx)
                    if sq_val is not None:
                        acc = self.lu_mul(acc, sq_val, mul_ctx.u_poly)
                    else:
                        ok = False
                else:
                    ok = False

            if ok:
                if not acc[2].is_zero or not acc[3].is_zero:
                    ctx.adopt(mul_ctx)
                return acc

            if has_add and not _expanded:
                return self.eval_lu(sp.expand_mul(expr), ctx, _expanded=True)
            return None

        if expr.is_Pow:
            base, exp = expr.args
            if exp.is_Integer:
                n = int(exp)
                if n == 0:
                    return ONE_LU
                pow_ctx = ctx.clone()
                sub = self.eval_lu(base, pow_ctx)
                if sub is None:
                    return None
                if n < 0:
                    sub = self.lu_inv(sub, pow_ctx.u_poly)
                    n = -n
                res = ONE_LU
                b_cur = sub
                while n > 0:
                    if n & 1:
                        res = self.lu_mul(res, b_cur, pow_ctx.u_poly)
                    n >>= 1
                    if n > 0:
                        b_cur = self.lu_mul(b_cur, b_cur, pow_ctx.u_poly)
                if not res[2].is_zero or not res[3].is_zero:
                    ctx.adopt(pow_ctx)
                return res

            if exp.is_Rational and exp.q == 2:
                k = (int(exp.p) - 1) // 2
                pow_ctx = ctx.clone()
                sub = self.eval_lu(base, pow_ctx)
                if sub is None:
                    return None
                if not (sub[1].is_zero and sub[2].is_zero and sub[3].is_zero):
                    return None
                sq = self.lu_sqrt_k8(sub[0], pow_ctx)
                if sq is None:
                    return None
                if k != 0:
                    int_part = self.eval_lu(base**k, pow_ctx)
                    if int_part is None:
                        return None
                    sq = self.lu_mul(int_part, sq, pow_ctx.u_poly)
                if not sq[2].is_zero or not sq[3].is_zero:
                    ctx.adopt(pow_ctx)
                return sq

        return None

    def lu_to_expr(self, val: LUVal, u_poly: Poly | None) -> sp.Expr:
        a0, a1, a2, a3 = val
        out = sp.Integer(0)
        if not a0.is_zero:
            out += self.poly_to_b8_expr(a0)
        if not a1.is_zero:
            out += self.poly_to_b8_expr(a1) * sp.sqrt(3)
        if not a2.is_zero:
            assert u_poly is not None
            sgn = 1 if self.poly_eval_at_r1(a2) >= 0 else -1
            sq2 = self.k8_mul(self.k8_mul(a2, a2), u_poly)
            out += sgn * self.format_clean_sqrt_k8(sq2)
        if not a3.is_zero:
            assert u_poly is not None
            sgn = 1 if self.poly_eval_at_r1(a3) >= 0 else -1
            sq3 = self.k8_mul(self.k8_mul(a3, a3), u_poly)
            out += sgn * sp.sqrt(3) * self.format_clean_sqrt_k8(sq3)
        return out


_ENGINE: _Cyclotomic17Engine | None = None


def _get_engine() -> _Cyclotomic17Engine:
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = _Cyclotomic17Engine()
    return _ENGINE


def decompose_k8(expr: sp.Expr) -> dict[str, sp.Rational] | None:
    """Decompose an element of K_8 into rational coefficients over {1, √17, A₋, A₊, R₁..R₄}."""
    eng = _get_engine()
    ctx = _EvalCtx()
    lu = eng.eval_lu(expr, ctx)
    if lu is None or not (lu[1].is_zero and lu[2].is_zero and lu[3].is_zero):
        return None
    coords = eng.poly_to_b8_coords(lu[0])
    return dict(zip(B8_NAMES, coords))


def canonicalize_17(expr: sp.Expr) -> sp.Expr:
    """Canonicalize an exact geometric coordinate into Gauss's nested √17 radical tower."""
    expr = sp.sympify(expr)
    if expr.is_Rational:
        return expr

    eng = _get_engine()
    ctx = _EvalCtx()
    lu = eng.eval_lu(expr, ctx)
    if lu is not None:
        return eng.lu_to_expr(lu, ctx.u_poly)

    return sp.sqrtdenest(sp.simplify(expr))
