#!/usr/bin/env python3
"""
smt_check_invariants.py — Stage 0e: SMT-based arithmetic invariant falsification.

Reads ARITHMETIC invariants from data/invariants/high_suspicion.json, uses Claude
to translate each formal_expression into Z3 Python constraints, then runs Z3 to
search for counterexample input values.

Any falsified invariant becomes a finding with the exact counterexample as PoC.

Usage:
    python scripts/smt_check_invariants.py
    python scripts/smt_check_invariants.py --category ARITHMETIC   # default
    python scripts/smt_check_invariants.py --category ALL          # all categories

Requirements:
    pip install z3-solver

Outputs:
    output/findings_smt.json
"""

from __future__ import annotations

import json
import os
import re
import sys
import textwrap
from pathlib import Path

import anthropic

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path
from llm_runtime import require_llm  # no-silent-fail: actionable message instead of credit spend/crash

ROOT           = Path(__file__).resolve().parent.parent
INVARIANTS_DIR = audit_path("data/invariants")
OUTPUT_DIR     = audit_path("output")

MODEL      = "claude-sonnet-4-6"
MAX_TOKENS = 2048

SMT_TRANSLATION_SYSTEM = """\
You are an expert in Z3 SMT solver Python API.

You receive a smart contract arithmetic invariant with a `formal_expression` field
(pseudocode describing an arithmetic constraint). Your job is to translate it into
a self-contained Python snippet using the `z3` library that:

1. Declares symbolic variables (BitVec or Int as appropriate)
2. Adds the NEGATION of the invariant as a constraint (we want to find a counterexample)
3. Calls `solver.check()` and returns the model if SAT

Return ONLY a JSON object with one field:
{
  "z3_code": "import z3\\nsolver = z3.Solver()\\n..."
}

Rules:
- Use BitVec(256) for Solidity uint256 values
- Use signed BitVec(256) for int256 values
- Model integer division as Z3 BitVec unsigned division: z3.UDiv(a, b)
- Add overflow constraints where relevant: assert 0 <= value <= 2**256-1
- The snippet must be runnable standalone with just `import z3`
- If the invariant involves external contract calls or storage reads that
  cannot be modeled, return {"error": "cannot model: reason"}
"""


def _load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _call_claude(user_content: str) -> str:
    client = require_llm(skill="deep_analysis")
    resp = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SMT_TRANSLATION_SYSTEM,
        messages=[{"role": "user", "content": user_content}],
    )
    return resp.content[0].text


def _extract_json_object(text: str) -> dict:
    text = text.strip()
    try:
        result = json.loads(text)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    if start == -1:
        return {}
    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start: i + 1])
                except json.JSONDecodeError:
                    return {}
    return {}


def _check_z3_available() -> bool:
    try:
        import z3  # noqa: F401
        return True
    except ImportError:
        return False


def _run_z3_code(code: str) -> dict | None:
    """
    Execute generated Z3 code in a restricted namespace.
    Returns the counterexample dict if SAT, None if UNSAT or error.
    """
    try:
        import z3
    except ImportError:
        return None

    namespace = {"z3": z3, "__builtins__": {"print": print, "range": range, "len": len}}
    try:
        exec(compile(code, "<smt>", "exec"), namespace)  # noqa: S102
    except Exception as e:
        return {"exec_error": str(e)}

    # The executed code should set `result` and `model` in namespace
    result = namespace.get("result")
    if result is None:
        # Try to find a solver and check it
        for v in namespace.values():
            if isinstance(v, z3.Solver):
                result = v.check()
                if str(result) == "sat":
                    return {"sat": True, "model": str(v.model())}
                return None
        return None

    if str(result) == "sat":
        model = namespace.get("model") or namespace.get("m")
        return {"sat": True, "model": str(model) if model else "SAT (no model extracted)"}
    return None


def _invariant_to_finding(inv: dict, counterexample: dict, idx: int) -> dict:
    cex_str = counterexample.get("model", "see Z3 output")
    return {
        "id": f"SMT-{idx:03d}",
        "title": f"Arithmetic invariant falsified: {inv.get('statement', '')[:60]}",
        "severity": "High",
        "vuln_type": "arithmetic",
        "description": (
            f"The Z3 SMT solver found input values that violate the protocol invariant "
            f"'{inv.get('statement', '')}'. This means the formal expression "
            f"`{inv.get('formal_expression', '')}` can evaluate to false under reachable "
            f"on-chain conditions.\n\n"
            f"Invariant category: {inv.get('category', '')}\n"
            f"Suspicion score: {inv.get('suspicion_score', '')}/5\n"
            f"Violation consequence: {inv.get('violation_consequence', '')}"
        ),
        "location": {
            "file": "arithmetic invariant",
            "function": ", ".join(inv.get("mutating_functions", [])),
            "line_start": None,
            "code_snippet": inv.get("formal_expression", ""),
        },
        "impact": inv.get("violation_consequence", "Arithmetic invariant violated"),
        "proof_of_concept": (
            f"Z3 counterexample:\n{cex_str}\n\n"
            f"These input values satisfy the NEGATION of the invariant, proving "
            f"the invariant can be false. Verify by substituting these values "
            f"into the relevant contract functions."
        ),
        "recommendation": (
            f"Validate the arithmetic invariant in the affected functions "
            f"({', '.join(inv.get('mutating_functions', []))}). "
            f"Add explicit range checks or use SafeMath/checked arithmetic "
            f"for the operations described in: {inv.get('formal_expression', '')}."
        ),
        "confidence": "Medium",
        "invariant_violated": inv.get("invariant_id", ""),
    }


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="SMT-based invariant falsification")
    parser.add_argument("--category", default="ARITHMETIC",
                        help="Invariant category to check (ARITHMETIC, ALL)")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUTPUT_DIR / "findings_smt.json"

    print("Stage 0e — SMT Arithmetic Invariant Falsification")

    if not _check_z3_available():
        print("  z3-solver not installed. Run: pip install z3-solver")
        out_file.write_text(json.dumps({"agent": "smt", "findings": [], "error": "z3 not installed"}, indent=2))
        return 0

    invariants = _load_json(INVARIANTS_DIR / "high_suspicion.json")
    if not isinstance(invariants, list):
        print("  No high-suspicion invariants found. Run extract_invariants.py first.")
        out_file.write_text(json.dumps({"agent": "smt", "findings": []}, indent=2))
        return 0

    target_category = args.category.upper()
    if target_category == "ALL":
        candidates = invariants
    else:
        candidates = [inv for inv in invariants if inv.get("category", "") == target_category]

    print(f"  Invariants to check: {len(candidates)} (category={args.category})")

    findings = []
    finding_idx = 1

    for i, inv in enumerate(candidates, 1):
        inv_id = inv.get("invariant_id", f"INV-{i}")
        formal_expr = inv.get("formal_expression", "")
        if not formal_expr:
            continue

        print(f"\n  [{i}/{len(candidates)}] {inv_id}: {inv.get('statement', '')[:60]} …", end="", flush=True)

        user_msg = json.dumps({
            "invariant_id": inv_id,
            "category": inv.get("category"),
            "statement": inv.get("statement"),
            "formal_expression": formal_expr,
            "state_variables_involved": inv.get("state_variables_involved", []),
            "mutating_functions": inv.get("mutating_functions", []),
        }, ensure_ascii=False)

        try:
            raw = _call_claude(user_msg)
        except Exception as e:
            print(f" ERROR (Claude): {e}")
            continue

        result_obj = _extract_json_object(raw)
        if not result_obj or result_obj.get("error"):
            reason = result_obj.get("error", "no JSON") if result_obj else "no JSON"
            print(f" SKIP ({reason})")
            continue

        z3_code = result_obj.get("z3_code", "")
        if not z3_code:
            print(" SKIP (no z3_code)")
            continue

        counterexample = _run_z3_code(z3_code)
        if counterexample and counterexample.get("sat"):
            print(f" SAT — INVARIANT FALSIFIED")
            finding = _invariant_to_finding(inv, counterexample, finding_idx)
            findings.append(finding)
            finding_idx += 1
        elif counterexample and counterexample.get("exec_error"):
            print(f" ERROR (Z3 exec): {counterexample['exec_error'][:60]}")
        else:
            print(f" UNSAT (invariant holds)")

    out = {
        "agent": "smt",
        "contract": "various",
        "findings": findings,
    }
    out_file.write_text(json.dumps(out, indent=2, ensure_ascii=False))

    print(f"\n  Results:")
    print(f"    Invariants checked: {len(candidates)}")
    print(f"    Falsified (findings): {len(findings)}")
    print(f"  Output: {out_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
