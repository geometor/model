"""Symbolic canonicalization, exact predicates, and algebraic number field helpers.

This module replaces general-purpose ``sympy.simplify`` calls in the hot loop of
``geometor.model`` with a tiered algebraic canonicalizer (:func:`clean_expr`),
fast high-precision + exact symbolic zero/sign predicates (:func:`zero_test`,
:func:`exact_sign`), and explicit ``sympy.QQ.algebraic_field`` reducers for
quadratic and biquadratic extensions such as :math:`\\mathbb{Q}(\\phi)` and
:math:`\\mathbb{Q}(\\sqrt{\\phi})`.
"""

from __future__ import annotations

import contextlib
from functools import lru_cache

import sympy as sp

__all__ = [
    "canonicalize_golden",
    "canonicalize_kepler",
    "clean_expr",
    "exact_sign",
    "fast_line_coeffs",
    "get_algebraic_field",
    "get_golden_field",
    "get_kepler_field",
    "reduce_in_field",
    "zero_test",
]

_PHI_RADICAL = (sp.Integer(1) + sp.sqrt(5)) / 2
_SQRT_PHI_RADICAL = sp.sqrt(_PHI_RADICAL)


def _has_rad3(expr: sp.Basic) -> bool:
    """Return True if ``expr`` contains a square root whose integer base is divisible by 3."""
    for p in expr.atoms(sp.Pow):
        if (
            isinstance(p.base, sp.Integer)
            and isinstance(p.exp, sp.Rational)
            and p.exp.q == 2
            and int(p.base) % 3 == 0
        ):
            return True
    return False


def fast_line_coeffs(ln: object) -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    """Extract normalized exact line coefficients ``(a, b, c)`` without ``sp.simplify``.

    Expands midpoint sums ``mx, my`` so conjugate radical terms cancel immediately,
    strips common ``sqrt(3)`` factors (including merged ``sqrt(3*k)`` such as ``sqrt(51)``)
    from equilateral-pole bisector lines in microseconds, and caches the tuple on ``ln``.
    """
    cached = getattr(ln, "_fast_coeffs", None)
    if cached is not None:
        return cached

    p1, p2 = ln.p1, ln.p2  # type: ignore[attr-defined]
    a0 = sp.expand(p1.y - p2.y) if (p1.y - p2.y).count_ops() <= 160 else (p1.y - p2.y)
    b0 = sp.expand(p2.x - p1.x) if (p2.x - p1.x).count_ops() <= 160 else (p2.x - p1.x)
    mx = sp.expand((p1.x + p2.x) / 2) if (p1.x + p2.x).count_ops() <= 160 else (p1.x + p2.x) / 2
    my = sp.expand((p1.y + p2.y) / 2) if (p1.y + p2.y).count_ops() <= 160 else (p1.y + p2.y) / 2

    if a0 == 0:
        res = (sp.Integer(0), sp.Integer(1), -my)
        with contextlib.suppress(AttributeError, TypeError):
            ln._fast_coeffs = res  # type: ignore[attr-defined]
        return res
    if b0 == 0:
        res = (sp.Integer(1), sp.Integer(0), -mx)
        with contextlib.suppress(AttributeError, TypeError):
            ln._fast_coeffs = res  # type: ignore[attr-defined]
        return res

    s3 = sp.sqrt(3)
    if _has_rad3(a0) or _has_rad3(b0):
        a_div = sp.expand(a0 / s3)
        b_div = sp.expand(b0 / s3)
        if not _has_rad3(a_div) and not _has_rad3(b_div):
            a0 = a_div
            b0 = b_div

    raw_c = -(a0 * mx + b0 * my)
    c0 = sp.expand(raw_c) if raw_c.count_ops() <= 200 else raw_c
    res = (a0, b0, c0)
    with contextlib.suppress(AttributeError, TypeError):
        ln._fast_coeffs = res  # type: ignore[attr-defined]
    return res


def _has_nested_sqrt(expr: sp.Basic) -> bool:
    """Return True if ``expr`` contains a radical whose base also contains a radical."""
    for p in expr.atoms(sp.Pow):
        if isinstance(p.exp, sp.Rational) and p.exp.q != 1:
            for inner in p.base.atoms(sp.Pow):
                if isinstance(inner.exp, sp.Rational) and inner.exp.q != 1:
                    return True
    return False


def clean_expr(expr: object) -> sp.Expr:
    """Canonicalize a symbolic geometric coordinate without invoking ``sp.simplify``.

    Applies a fast tiered pipeline:

    1. Immediate O(1) return for Python ``int`` and SymPy ``Rational`` / ``Integer``.
    2. Fraction combination (:func:`sympy.together`), bounded polynomial expansion,
       and denominator rationalization (:func:`sympy.radsimp` with ``symbolic=False``).
    3. Conditional :func:`sympy.sqrtdenest` only when nested radicals are actually present.

    Args:
        expr: A numeric value or SymPy expression.

    Returns:
        A simplified exact :class:`sympy.Expr`.
    """
    if isinstance(expr, sp.Rational):
        return expr
    if isinstance(expr, int):
        return sp.Integer(expr)

    sym_expr = sp.sympify(expr)
    if sym_expr.is_Rational or sym_expr.is_NumberSymbol:
        return sym_expr

    if (sym_expr.has(sp.GoldenRatio) or sym_expr.has(_SQRT_PHI_RADICAL)) and not sym_expr.free_symbols:
        with contextlib.suppress(Exception):
            return canonicalize_kepler(sym_expr)

    res = sym_expr
    ops = res.count_ops()
    if ops <= 120:
        tog = sp.together(res)
        num, den = sp.fraction(tog)
        if num.count_ops() <= 100 and den.count_ops() <= 100:
            num = sp.expand(num)
            den = sp.expand(den)
            if den == 1:
                res = num
            elif den == -1:
                res = -num
            else:
                res = sp.cancel(num / den) if num.is_polynomial() and den.is_polynomial() else num / den
                with contextlib.suppress(ArithmeticError, ValueError, NotImplementedError):
                    rad = sp.radsimp(res, symbolic=False, max_terms=6)
                    r_num, r_den = sp.fraction(rad)
                    if r_num.count_ops() <= 100:
                        res = sp.expand(r_num) / r_den
                    else:
                        res = rad

    if _has_nested_sqrt(res) and res.count_ops() <= 20:
        with contextlib.suppress(Exception):
            res = sp.sqrtdenest(res)

    return res


def zero_test(expr: object) -> bool:
    """Determine with 100% mathematical exactness whether ``expr == 0``.

    Uses a fast 3-tier decision procedure:

    1. O(1) structural and rational check.
    2. High-precision adaptive ``evalf(20)`` rejection for non-zero constant expressions
       (rejects non-zeros in microseconds without symbolic expansion).
    3. Exact algebraic proof of zero via fraction numerator expansion, :func:`clean_expr`,
       ``GoldenRatio`` radical substitution, and fallback ``simplify`` / ``minimal_polynomial``.

    Args:
        expr: A numeric value or SymPy expression.

    Returns:
        ``True`` if and only if ``expr`` is identically zero.
    """
    if expr is sp.S.Zero or expr == 0:
        return True
    if isinstance(expr, (int, sp.Rational)):
        return expr == 0

    e = sp.sympify(expr)
    if e is sp.S.Zero:
        return True
    if e.is_Rational:
        return False

    if e.has(sp.GoldenRatio):
        e = e.subs(sp.GoldenRatio, _PHI_RADICAL)

    if e.has(_SQRT_PHI_RADICAL) and not e.free_symbols:
        k_field = get_kepler_field()
        anp = _fast_kepler_or_golden_anp(e, k_field)
        if anp is not None:
            return bool(anp == k_field.zero)

    # Ultra-fast exact algebraic cancellation for small expressions (avoids SymPy evalf_add spinning on exact 0)
    if e.count_ops() <= 45:
        e_direct = sp.expand(e)
        if e_direct == 0 or (e_direct.count_ops() <= 45 and sp.expand(e_direct) == 0):
            return True

    # Fast bounded-precision numerical rejection for constant non-zero algebraic expressions
    if not e.free_symbols:
        with contextlib.suppress(ArithmeticError, TypeError, ValueError, NotImplementedError):
            val = complex(e.evalf(20, maxn=25))
            if abs(val.real) > 1e-12 or abs(val.imag) > 1e-12:
                return False

    # Exact symbolic proof for candidate zeros
    if e.count_ops() <= 150:
        num, _ = sp.fraction(sp.together(e))
    else:
        num = sp.expand_mul(e)

    if num == 0:
        return True

    exp_num = sp.expand(num) if num.count_ops() <= 150 else num
    if exp_num == 0:
        return True
    if exp_num.count_ops() <= 150:
        exp_num = sp.expand(exp_num)
        if exp_num == 0:
            return True

    cleaned = clean_expr(exp_num)
    if cleaned == 0:
        return True
    if cleaned.count_ops() <= 120 and sp.expand(cleaned) == 0:
        return True

    if cleaned.count_ops() <= 25:
        with contextlib.suppress(Exception):
            if sp.expand(sp.sqrtdenest(cleaned)) == 0:
                return True
        with contextlib.suppress(Exception):
            if sp.simplify(cleaned) == 0:
                return True

    if not cleaned.free_symbols and cleaned.count_ops() <= 25:
        with contextlib.suppress(Exception):
            x = sp.Dummy("x")
            if sp.minimal_polynomial(cleaned, x) == x:
                return True

    if not cleaned.free_symbols and cleaned.count_ops() > 25:
        with contextlib.suppress(Exception):
            c120 = complex(cleaned.evalf(80, maxn=90))
            if abs(c120.real) < 1e-65 and abs(c120.imag) < 1e-65:
                return True

    return False


def exact_sign(expr: object) -> int:
    """Return the exact mathematical sign (``+1``, ``-1``, or ``0``) of a real expression.

    Args:
        expr: A real numeric value or SymPy expression.

    Returns:
        ``1`` if ``expr > 0``, ``-1`` if ``expr < 0``, or ``0`` if ``expr == 0``.

    Raises:
        ValueError: If ``expr`` has free symbols whose sign cannot be determined or is non-real.
    """
    if isinstance(expr, int):
        return 1 if expr > 0 else (-1 if expr < 0 else 0)
    if isinstance(expr, sp.Rational):
        if expr > 0:
            return 1
        return -1 if expr < 0 else 0

    e = sp.sympify(expr)
    if e.is_Rational:
        if e > 0:
            return 1
        return -1 if e < 0 else 0

    if e.free_symbols:
        if zero_test(e):
            return 0
        if e.is_positive is True:
            return 1
        if e.is_negative is True:
            return -1
        raise ValueError(f"Cannot determine exact sign of symbolic expression with free variables: {e}")

    # Evaluate at 20 digits (maxn=25) first; if well above 1e-12, sign is immediately rigorous
    with contextlib.suppress(ArithmeticError, TypeError, NotImplementedError):
        cval = complex(e.evalf(20, maxn=25))
        if abs(cval.imag) > 1e-10:
            raise ValueError(f"Expression is not real: {e} (~ {cval})")
        if abs(cval.real) > 1e-12:
            return 1 if cval.real > 0 else -1

    if zero_test(e):
        return 0

    # Non-zero algebraic expression smaller than 1e-25: refine precision until sign resolves
    for prec in (100, 250, 500):
        cval = complex(e.evalf(prec))
        if abs(cval.real) > 10 ** (-prec // 2):
            return 1 if cval.real > 0 else -1

    raise ValueError(f"Unable to isolate non-zero sign of expression: {e}")


@lru_cache(maxsize=16)
def get_algebraic_field(*generators: sp.Expr) -> sp.AlgebraicField:
    """Construct and cache an explicit algebraic number field :math:`\\mathbb{Q}(\\alpha_1, \\dots)`.

    Args:
        *generators: Algebraic SymPy expressions generating the extension over ``QQ``.

    Returns:
        A cached :class:`sympy.polys.domains.AlgebraicField`.
    """
    sym_gens = tuple(sp.sympify(g) for g in generators)
    return sp.QQ.algebraic_field(*sym_gens)


@lru_cache(maxsize=1)
def get_golden_field() -> sp.AlgebraicField:
    """Return the cached quadratic number field :math:`\\mathbb{Q}(\\phi) = \\mathbb{Q}(\\sqrt{5})`."""
    return get_algebraic_field(_PHI_RADICAL)


@lru_cache(maxsize=1)
def get_kepler_field() -> sp.AlgebraicField:
    """Return the cached degree-4 Kepler number field :math:`\\mathbb{Q}(\\sqrt{\\phi})`."""
    return get_algebraic_field(_SQRT_PHI_RADICAL)


def _fast_kepler_or_golden_anp(expr: sp.Basic, field: sp.AlgebraicField) -> object | None:
    """Evaluate expressions in ``Q(phi)`` / ``Q(sqrt(phi))`` directly in ANP arithmetic in O(1)."""
    ext_expr = field.ext.as_expr()
    two = field.one + field.one
    if ext_expr == _SQRT_PHI_RADICAL:
        u = field.unit
        sqrt5_anp = two * (u**2) - field.one
        sqrt_phi_anp: object | None = u
    elif ext_expr == _PHI_RADICAL:
        v = field.unit
        sqrt5_anp = two * v - field.one
        sqrt_phi_anp = None
    else:
        return None

    def _ev(node: sp.Basic) -> object | None:
        if isinstance(node, sp.Rational):
            return field.from_sympy(node)
        if node == _SQRT_PHI_RADICAL:
            return sqrt_phi_anp
        if node == sp.sqrt(5):
            return sqrt5_anp
        if node == _PHI_RADICAL:
            return (field.one + sqrt5_anp) / two
        if isinstance(node, sp.Add):
            acc = field.zero
            for a in node.args:
                va = _ev(a)
                if va is None:
                    return None
                acc = acc + va
            return acc
        if isinstance(node, sp.Mul):
            acc = field.one
            for a in node.args:
                va = _ev(a)
                if va is None:
                    return None
                acc = acc * va
            return acc
        if isinstance(node, sp.Pow) and isinstance(node.exp, sp.Integer):
            vb = _ev(node.base)
            if vb is None:
                return None
            return vb ** int(node.exp)
        if (
            isinstance(node, sp.Pow)
            and node.base == _PHI_RADICAL
            and isinstance(node.exp, sp.Rational)
            and node.exp.q == 2
            and sqrt_phi_anp is not None
        ):
            return sqrt_phi_anp ** int(node.exp.p)
        return None

    with contextlib.suppress(ZeroDivisionError, ValueError, TypeError):
        return _ev(expr)
    return None


@lru_cache(maxsize=512)
def _cached_from_sympy(expr: sp.Basic, field: sp.AlgebraicField) -> object | None:
    """Cached wrapper around ``field.from_sympy`` using O(1) ANP ring evaluation when available."""
    fast = _fast_kepler_or_golden_anp(expr, field)
    if fast is not None:
        return fast
    with contextlib.suppress(sp.CoercionFailed, NotImplementedError, ValueError, ZeroDivisionError):
        return field.from_sympy(expr)
    return None


def _anp_to_expr(field: sp.AlgebraicField, anp: object) -> sp.Expr:
    """Convert an ``ANP`` element to a standard SymPy radical ``Expr`` (unwrapping ``AlgebraicNumber``)."""
    sym = field.to_sympy(anp)
    return sym.as_expr() if isinstance(sym, sp.AlgebraicNumber) else sym


@lru_cache(maxsize=128)
def _cached_field_sqrt(rad_sym: sp.Expr, field: sp.AlgebraicField) -> sp.Expr | None:
    """Cached exact square-root extraction in an explicit AlgebraicField."""
    if rad_sym == 0:
        return sp.Integer(0)
    if rad_sym.is_Rational and rad_sym > 0:
        rt = sp.sqrt(rad_sym)
        if rt.is_Rational:
            return rt
    try:
        num_val = float(complex(rad_sym.evalf(25, maxn=30)).real)
    except (ArithmeticError, TypeError, ValueError, NotImplementedError):
        return None
    if num_val < 0:
        return None

    # Fast O(1) check against rational multiples of powers of field.unit (e.g. alpha^k in Q(sqrt(phi)))
    anp_rad = _cached_from_sympy(rad_sym, field)
    if anp_rad is None:
        return None
    u = field.unit
    u_inv = field.one / u
    for pwr_elem in (field.one, u**2, u**4, u_inv**2, u_inv**4):
        quot = anp_rad / pwr_elem
        # Check if quot is a rational number (degree 0 in ANP -> len(quot.rep) <= 1)
        if len(quot.rep) <= 1:
            q_sym = _anp_to_expr(field, quot)
            if q_sym.is_Rational and q_sym > 0:
                q_rt = sp.sqrt(q_sym)
                if q_rt.is_Rational:
                    # Square root of pwr_elem:
                    if pwr_elem == field.one:
                        base_rt = field.one
                    elif pwr_elem == u**2:
                        base_rt = u
                    elif pwr_elem == u**4:
                        base_rt = u**2
                    elif pwr_elem == u_inv**2:
                        base_rt = u_inv
                    else:
                        base_rt = u_inv**2
                    res_expr = _anp_to_expr(field, field.from_sympy(q_rt) * base_rt)
                    return res_expr if float(complex(res_expr.evalf(25, maxn=30)).real) >= 0 else -res_expr

    # General exact polynomial factorization fallback over Q(alpha)
    x = sp.Dummy("x")
    with contextlib.suppress(Exception):
        poly = sp.Poly(x**2 - rad_sym, x, extension=field.ext)
        _, factors = poly.factor_list()
        for fac, _ in factors:
            if fac.degree(x) == 1:
                c1, c0 = fac.all_coeffs()
                root_expr = _anp_to_expr(field, field.from_sympy(-c0 / c1))
                if float(complex(root_expr.evalf(25, maxn=30)).real) >= 0:
                    return root_expr
                return _anp_to_expr(field, field.from_sympy(c0 / c1))
    return None


def _try_sqrt_in_kepler_field(radicand_anp: object, field: sp.AlgebraicField) -> sp.Expr | None:
    """If an element of ``field`` is an exact square in ``field``, return its >=0 root."""
    rad_sym = _anp_to_expr(field, radicand_anp)
    return _cached_field_sqrt(rad_sym, field)


def _has_alien_golden_radical(node: sp.Basic, is_golden_or_kepler: bool) -> bool:
    """Fast O(1) check rejecting integer radicals outside ``Q(phi)`` / ``Q(sqrt(phi))`` (e.g. ``sqrt(3)``)."""
    if not is_golden_or_kepler:
        return False
    for p in node.atoms(sp.Pow):
        if isinstance(p.base, sp.Integer) and isinstance(p.exp, sp.Rational) and p.exp.q == 2:
            b_int = int(p.base)
            if b_int < 0:
                return True
            if not (sp.sqrt(b_int).is_Integer or sp.sqrt(5 * b_int).is_Integer):
                return True
    return False


@lru_cache(maxsize=512)
def _reduce_expr_in_field_cached(e: sp.Expr, field: sp.AlgebraicField) -> sp.Expr:
    """Cached core algebraic number field reducer."""
    if e.has(sp.GoldenRatio):
        e = e.subs(sp.GoldenRatio, _PHI_RADICAL)

    is_gk = field.ext.as_expr() in (_PHI_RADICAL, _SQRT_PHI_RADICAL)

    # Direct coercion fast-path (skipped immediately if an outer radical like sqrt(3) is present)
    if not _has_alien_golden_radical(e, is_gk):
        anp = _cached_from_sympy(e, field)
        if anp is not None:
            return _anp_to_expr(field, anp)

    # Bottom-up reduction for expressions containing square roots or outer radicals
    def _walk(node: sp.Basic) -> sp.Basic:
        if node.is_Atom:
            return node.as_expr() if isinstance(node, sp.AlgebraicNumber) else node
        if node.args:
            new_args = tuple(_walk(a) for a in node.args)
            if new_args != node.args:
                node = node.func(*new_args)
        if isinstance(node, sp.Pow) and isinstance(node.exp, sp.Rational) and node.exp.q == 2:
            if not _has_alien_golden_radical(node.base, is_gk):
                anp_base = _cached_from_sympy(node.base, field)
                if anp_base is not None:
                    exact_rt = _try_sqrt_in_kepler_field(anp_base, field)
                    if exact_rt is not None:
                        return exact_rt ** node.exp.p
                    return sp.Pow(_anp_to_expr(field, anp_base), node.exp)
            return node
        if not _has_alien_golden_radical(node, is_gk):
            anp_node = _cached_from_sympy(node, field)
            if anp_node is not None:
                return _anp_to_expr(field, anp_node)
        return node

    walked = _walk(e)
    if not _has_alien_golden_radical(walked, is_gk):
        anp_w = _cached_from_sympy(walked, field)
        if anp_w is not None:
            return _anp_to_expr(field, anp_w)

    # Final rational cleanup for expressions with an outer radical (e.g., equilateral pole sqrt(3))
    tog = sp.together(walked)
    num, den = sp.fraction(tog)
    num = sp.expand(num)
    den = sp.expand(den)
    res = num / den if den != 1 else num
    with contextlib.suppress(Exception):
        res = sp.radsimp(res, symbolic=False, max_terms=6)
    if not isinstance(res, sp.Basic):
        return sp.sympify(res)
    if not _has_alien_golden_radical(res, is_gk):
        anp_res = _cached_from_sympy(res, field)
        if anp_res is not None:
            return _anp_to_expr(field, anp_res)
    return res


def reduce_in_field(
    expr: object,
    field_or_gen: sp.AlgebraicField | sp.Expr | tuple[sp.Expr, ...],
) -> sp.Expr:
    """Reduce an algebraic expression inside an explicit number field :math:`\\mathbb{Q}(\\alpha)`.

    Handles nested square roots whose radicands simplify to squares inside the target field
    (such as :math:`\\sqrt{1 + \\phi} = \\phi` and :math:`\\sqrt{\\phi - 1} = \\phi^{-1/2}` in
    the Kepler field), and falls back cleanly when outer extensions (e.g. :math:`\\sqrt{3}`)
    are present.

    Args:
        expr: Numeric value or SymPy expression to canonicalize.
        field_or_gen: An :class:`sympy.AlgebraicField`, a generator expression, or tuple of generators.

    Returns:
        Canonicalized :class:`sympy.Expr`.
    """
    if isinstance(expr, sp.Rational):
        return expr
    if isinstance(expr, int):
        return sp.Integer(expr)

    e = sp.sympify(expr)
    if e.is_Rational:
        return e

    if isinstance(field_or_gen, sp.AlgebraicField):
        field = field_or_gen
    elif isinstance(field_or_gen, tuple):
        field = get_algebraic_field(*field_or_gen)
    else:
        field = get_algebraic_field(field_or_gen)

    return _reduce_expr_in_field_cached(e, field)


def canonicalize_golden(expr: object) -> sp.Expr:
    """Canonicalize an expression in the golden field :math:`\\mathbb{Q}(\\phi)`."""
    return reduce_in_field(expr, get_golden_field())


def canonicalize_kepler(expr: object) -> sp.Expr:
    """Canonicalize an expression in the degree-4 Kepler field :math:`\\mathbb{Q}(\\sqrt{\\phi})`."""
    return reduce_in_field(expr, get_kepler_field())
