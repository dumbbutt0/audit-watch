#!/usr/bin/env python3
"""
math_formula_diff_harness.py — adversarial formula-diff harness for math-estimator review.

Given an INTENDED formula (from the whitepaper/model/economic design) and the IMPLEMENTED formula
(read off the code), evaluate BOTH over a parameter sweep built from attacker-favorable / boundary
extremes and report where they DIVERGE: value divergence, uint256 overflow/underflow, integer
precision loss, monotonicity inversion, discontinuities, and attacker-profitable / protocol-loss
ranges. This produces the evidence a `math_estimator_proof` needs (formula_diff /
attacker_favorable_search) so a clear is ADVERSARIAL, not confirmatory (the Swan/Dria getFee M-08 /
QuantAMM H-11 failure). See documentation/math_estimator_proof_policy.md.

Formulas are restricted arithmetic expressions over named integer parameters. Evaluation is done with
a STRICT AST whitelist (no eval, no attribute access, no imports, no calls except min/max/abs) so an
untrusted formula string cannot execute code. If a formula is not expressible in this DSL the harness
declines (exit 2) and the field-based gate in validate_math_estimator_clears.py still governs.

Usage:
  math_formula_diff_harness.py --intended "2*difficulty" --implemented "2<<difficulty" \
      --params "difficulty:0..32" [--uint-bits 256] [--fail-on-divergence] [--out report.json]
  math_formula_diff_harness.py --proof proof.json   # reads intended/implemented/params from a proof
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from fractions import Fraction
from itertools import product

# --- safe arithmetic DSL ------------------------------------------------------------------------
_ALLOWED_NODES = (
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Name, ast.Load, ast.Call,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
    ast.LShift, ast.RShift, ast.BitAnd, ast.BitOr, ast.BitXor, ast.USub, ast.UAdd,
)
_ALLOWED_CALLS = {"min", "max", "abs"}
# Guards against pathological big-int blowups from a swept exponent/shift.
_BLOWUP_SHIFT = 2048


class FormulaError(ValueError):
    """The formula is not expressible in the safe arithmetic DSL."""


class _Overflow(Exception):
    """Intermediate value left the uint range / blew up."""


def parse_formula(expr: str) -> ast.Expression:
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        raise FormulaError(f"cannot parse: {e}") from e
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            raise FormulaError(f"disallowed syntax: {type(node).__name__}")
        if isinstance(node, ast.Call):
            if not (isinstance(node.func, ast.Name) and node.func.id in _ALLOWED_CALLS):
                raise FormulaError("only min/max/abs calls are allowed")
            if node.keywords:
                raise FormulaError("keyword args not allowed")
        if isinstance(node, ast.Constant) and not isinstance(node.value, (int, float)):
            raise FormulaError("only numeric constants allowed")
    return tree


def formula_names(tree: ast.Expression) -> set[str]:
    return {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id not in _ALLOWED_CALLS}


def _eval(node, env, *, exact: bool):
    """Evaluate the whitelisted AST. exact=True uses Fraction (true math); exact=False mirrors EVM
    integer semantics (floor division, integer-only) so precision loss = exact - evm."""
    if isinstance(node, ast.Expression):
        return _eval(node.body, env, exact=exact)
    if isinstance(node, ast.Constant):
        return Fraction(node.value) if exact else node.value
    if isinstance(node, ast.Name):
        v = env[node.id]
        return Fraction(v) if exact else v
    if isinstance(node, ast.UnaryOp):
        v = _eval(node.operand, env, exact=exact)
        return -v if isinstance(node.op, ast.USub) else +v
    if isinstance(node, ast.Call):
        args = [_eval(a, env, exact=exact) for a in node.args]
        return {"min": min, "max": max, "abs": abs}[node.func.id](*args)
    if isinstance(node, ast.BinOp):
        l = _eval(node.left, env, exact=exact)
        r = _eval(node.right, env, exact=exact)
        op = node.op
        if isinstance(op, ast.Add):
            return l + r
        if isinstance(op, ast.Sub):
            return l - r
        if isinstance(op, ast.Mult):
            return l * r
        if isinstance(op, (ast.Div, ast.FloorDiv)):
            if r == 0:
                raise _Overflow("division by zero")
            return Fraction(l, r) if exact else (int(l) // int(r))
        if isinstance(op, ast.Mod):
            if r == 0:
                raise _Overflow("mod by zero")
            return l - (l // r) * r if exact else (int(l) % int(r))
        if isinstance(op, ast.Pow):
            e = int(r)
            if e < 0 or e > _BLOWUP_SHIFT:
                raise _Overflow("exponent out of range")
            return l ** e
        # bitwise / shift only make sense on ints (EVM semantics)
        li, ri = int(l), int(r)
        if isinstance(op, ast.LShift):
            if ri > _BLOWUP_SHIFT:
                raise _Overflow("shift too large")
            return (li << ri) if not exact else Fraction(li << ri)
        if isinstance(op, ast.RShift):
            return (li >> ri) if not exact else Fraction(li >> ri)
        if isinstance(op, ast.BitAnd):
            return li & ri
        if isinstance(op, ast.BitOr):
            return li | ri
        if isinstance(op, ast.BitXor):
            return li ^ ri
    raise FormulaError(f"unhandled node {type(node).__name__}")


def evm_eval(tree, env, uint_max):
    """Integer EVM-style value, or None on overflow/underflow/div-zero."""
    try:
        v = _eval(tree, env, exact=False)
    except _Overflow:
        return None
    v = int(v)
    if v < 0 or v > uint_max:
        return None
    return v


def exact_eval(tree, env):
    try:
        return _eval(tree, env, exact=True)
    except _Overflow:
        return None


# --- parameter sweep ----------------------------------------------------------------------------
def parse_params(specs: list[str]) -> dict[str, tuple[int, int]]:
    out = {}
    for s in specs:
        if ":" not in s or ".." not in s:
            raise FormulaError(f"bad --params spec '{s}', expected name:lo..hi")
        name, rng = s.split(":", 1)
        lo, hi = rng.split("..", 1)
        out[name.strip()] = (int(lo), int(hi))
    return out


def sweep_values(lo: int, hi: int, cap: int = 24) -> list[int]:
    """Boundary + attacker-favorable extremes within [lo, hi]: ends, 0/1/2, 2^k-1/2^k, a coarse sample."""
    vals = {lo, hi, lo + 1, hi - 1}
    for v in (0, 1, 2):
        if lo <= v <= hi:
            vals.add(v)
    k = 1
    while (1 << k) <= hi:
        for v in ((1 << k) - 1, 1 << k):
            if lo <= v <= hi:
                vals.add(v)
        k += 1
    span = hi - lo
    if span > 0:
        step = max(1, span // 8)
        for i in range(lo, hi + 1, step):
            vals.add(i)
    vals = sorted(v for v in vals if lo <= v <= hi)
    if len(vals) > cap:  # keep the extremes, thin the middle
        keep = set(vals[:3] + vals[-3:])
        mid = vals[3:-3]
        stride = max(1, len(mid) // (cap - 6))
        keep.update(mid[::stride])
        vals = sorted(keep)
    return vals


def run(intended: str, implemented: str, params: dict[str, tuple[int, int]],
        uint_bits: int = 256, max_combos: int = 20000) -> dict:
    ti, tm = parse_formula(intended), parse_formula(implemented)
    needed = formula_names(ti) | formula_names(tm)
    missing = sorted(needed - set(params))
    if missing:
        raise FormulaError(f"no range given for parameter(s): {', '.join(missing)}")
    uint_max = (1 << uint_bits) - 1
    grids = {p: sweep_values(*params[p]) for p in params}
    keys = list(grids)
    combos = list(product(*(grids[k] for k in keys)))
    sampled = False
    if len(combos) > max_combos:
        stride = len(combos) // max_combos + 1
        combos = combos[::stride]
        sampled = True

    divergences, overflows, precision, profitable = [], [], [], []
    single = keys[0] if len(keys) == 1 else None
    series = []  # (x, impl, intended) for monotonicity when single-var

    for combo in combos:
        env = dict(zip(keys, combo))
        im = evm_eval(tm, env, uint_max)
        it = evm_eval(ti, env, uint_max)
        ix = exact_eval(tm, env)
        if im is None or it is None:
            overflows.append({"point": env, "implemented_overflow": im is None, "intended_overflow": it is None})
            if single is not None:
                series.append((env[single], im, it))
            continue
        if im != it:
            diff = im - it
            divergences.append({"point": env, "implemented": im, "intended": it, "diff": diff})
            profitable.append({"point": env, "direction": "implemented_lt_intended" if diff < 0 else "implemented_gt_intended", "diff": diff})
        if ix is not None and Fraction(im) != ix:
            loss = abs(ix - Fraction(im))
            precision.append({"point": env, "evm": im, "exact": str(ix), "loss": float(loss)})
        if single is not None:
            series.append((env[single], im, it))

    monotonicity = _monotonicity(series) if single is not None else []

    def _worst(rows, key):
        return max(rows, key=key) if rows else None

    report = {
        "intended_formula": intended,
        "implemented_formula": implemented,
        "params": {k: list(v) for k, v in params.items()},
        "uint_bits": uint_bits,
        "samples": len(combos),
        "sampled": sampled,
        "divergence": {
            "count": len(divergences),
            "max_abs_diff": max((abs(d["diff"]) for d in divergences), default=0),
            "worst": _worst(divergences, lambda d: abs(d["diff"])),
            "examples": divergences[:10],
        },
        "overflow": {"count": len(overflows), "examples": overflows[:10]},
        "precision_loss": {
            "count": len(precision),
            "worst": _worst(precision, lambda d: d["loss"]),
            "examples": precision[:10],
        },
        "monotonicity_inversions": monotonicity[:10],
        "attacker_profitable_ranges": profitable[:10],
        "verdict": "divergence_found" if (divergences or overflows or monotonicity) else "no_divergence",
    }
    return report


def _monotonicity(series: list[tuple]) -> list[dict]:
    """Single-variable: flag points where implemented moves opposite to intended (direction inversion)."""
    pts = sorted((x, im, it) for (x, im, it) in series if im is not None and it is not None)
    inversions = []
    for (x0, im0, it0), (x1, im1, it1) in zip(pts, pts[1:]):
        di, dm = it1 - it0, im1 - im0
        if di != 0 and dm != 0 and (di > 0) != (dm > 0):
            inversions.append({"from": x0, "to": x1, "intended_delta": di, "implemented_delta": dm,
                               "note": "implemented moves opposite to intended"})
    return inversions


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--intended")
    ap.add_argument("--implemented")
    ap.add_argument("--params", nargs="*", default=[])
    ap.add_argument("--proof", help="JSON file/object with intended_formula, implemented_formula, harness_params[]")
    ap.add_argument("--uint-bits", type=int, default=256)
    ap.add_argument("--out")
    ap.add_argument("--fail-on-divergence", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    intended, implemented, param_specs = args.intended, args.implemented, args.params
    if args.proof:
        proof = json.loads(open(args.proof).read())
        intended = intended or proof.get("intended_formula")
        implemented = implemented or proof.get("implemented_formula")
        param_specs = param_specs or proof.get("harness_params", [])
    if not intended or not implemented:
        print("[harness] need --intended and --implemented (or --proof carrying them)", file=sys.stderr)
        return 2
    try:
        params = parse_params(param_specs)
        report = run(intended, implemented, params, uint_bits=args.uint_bits)
    except FormulaError as e:
        print(f"[harness] DECLINED — not expressible in the safe arithmetic DSL: {e}", file=sys.stderr)
        return 2

    if args.out:
        open(args.out, "w").write(json.dumps(report, indent=2))
    if not args.quiet:
        d = report["divergence"]
        print(f"[harness] verdict={report['verdict']} · samples={report['samples']} · "
              f"divergences={d['count']} (max|Δ|={d['max_abs_diff']}) · overflow={report['overflow']['count']} · "
              f"precision_loss={report['precision_loss']['count']} · "
              f"monotonicity_inversions={len(report['monotonicity_inversions'])}")
        if d["worst"]:
            w = d["worst"]
            print(f"   worst divergence at {w['point']}: implemented={w['implemented']} intended={w['intended']} Δ={w['diff']}")
    if not args.out and args.quiet:
        print(json.dumps(report, indent=2))

    if args.fail_on_divergence and report["verdict"] != "no_divergence":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
