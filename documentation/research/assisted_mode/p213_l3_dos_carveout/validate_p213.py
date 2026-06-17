#!/usr/bin/env python3
"""validate_p213.py — RESEARCH-ONLY, UN-WIRED validator for the L3 deterministic core-path DoS carve-out (P213).

Reads regression_cases.json ONLY. For each case it computes:
  - old_label  = the current P208 mapping  (imports validate_p208_l3_readiness.decide READ-ONLY)
  - repaired_label = old_label, except raised to "high" when ALL 10 carve-out criteria hold (and never upgrading an
    invalid/source-refuted case). See L3_DOS_CARVEOUT_RULE.md.
Emits a scorecard + metrics.json. NEVER mutates artifacts; NEVER imported by production; NEVER submits/routes.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_p208_l3_readiness import decide  # pure, read-only

RESEARCH_ONLY = True
ROUTES_IN_PRODUCTION = False
_ATT_OK = {"permissionless", "unavoidable", "normal_user_behavior"}
CRITERIA = ["deterministic_l3_proof", "core_path", "supported_asset", "not_optional_griefing",
            "source_valid_token_behavior", "attacker_model", "no_workaround",
            "affects_class_or_protocol", "control_case_present", "no_admin_prereq"]


def carveout_eval(cv: dict):
    """Return (all_satisfied, missing[]). attacker_model is an enum membership; the rest are booleans."""
    missing = []
    for k in CRITERIA:
        v = cv.get(k)
        ok = (v in _ATT_OK) if k == "attacker_model" else (v is True)
        if not ok:
            missing.append(k)
    return (len(missing) == 0, missing)


def repaired_label(old: str, cv: dict):
    sat, missing = carveout_eval(cv)
    if old == "invalid":               # never upgrade a source-refuted/invalid case
        return "invalid", sat, missing
    if sat:
        return "high", sat, missing
    return old, sat, missing


def main():
    data = json.loads((HERE / "regression_cases.json").read_text())
    rows, n, passed = [], 0, 0
    new_false_highs, soph03_fixed, dos_upgraded, dos_retained = 0, False, 0, 0
    for c in data["cases"]:
        old = decide(c["base"]).get("calibrated_severity")
        rep, sat, missing = repaired_label(old, c["carveout"])
        exp = c["expected"]
        ok = (rep == exp)
        n += 1; passed += 1 if ok else 0
        if rep == "high" and exp != "high":
            new_false_highs += 1
        if c["id"] == "SOPH-03" and rep == "high":
            soph03_fixed = True
        if c["base"].get("impact_class") in ("dos", "griefing"):
            dos_upgraded += 1 if rep == "high" else 0
            dos_retained += 1 if rep != "high" else 0
        rows.append({"id": c["id"], "old": old, "repaired": rep, "expected": exp,
                     "carveout_satisfied": sat, "missing": missing, "pass": ok, "desc": c["desc"]})
    for r in rows:
        st = "OK " if r["pass"] else "XX "
        print(f"{st}{r['id']:24} old={r['old']:26} repaired={r['repaired']:26} exp={r['expected']:26} "
              f"carveout={'ALL' if r['carveout_satisfied'] else 'miss:'+','.join(r['missing'])}")
    metrics = {
        "phase": "P213", "cases_tested": n, "expected_matches": passed, "regression_failures": n - passed,
        "soph03_fixed": soph03_fixed, "new_false_highs": new_false_highs,
        "old_false_demotions_fixed": 1 if soph03_fixed else 0,
        "dos_cases_upgraded_to_high": dos_upgraded, "dos_cases_retained_below_high": dos_retained,
        "all_pass": (passed == n) and new_false_highs == 0 and soph03_fixed,
        "research_only": RESEARCH_ONLY, "routes_in_production": ROUTES_IN_PRODUCTION,
    }
    print("\nMETRICS " + json.dumps(metrics))
    (HERE / "metrics.json").write_text(json.dumps({"scorecard": rows, **metrics}, indent=2) + "\n")
    return 0 if metrics["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
