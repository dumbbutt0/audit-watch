#!/usr/bin/env python3
"""validate_p188.py — READ-ONLY validation for the P188 adjudication-support detectors.

Replays the 5 frozen P186 deep-trace outputs through the updated (advisory) check_output() and records, per
finding, the new flags BEFORE (none — the detectors did not exist) vs AFTER. Emits before_after_matrix.json +
metrics.json under the P188 deliverable dir. Never writes the frozen inputs; never blocks.

Usage: python scripts/validate_p188.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "scripts").is_dir())
sys.path.insert(0, str(ROOT / "scripts"))
import validate_deep_pass_mechanisms as v  # noqa: E402

P186_RAW = ROOT / "documentation/research/assisted_mode/p186_fresh_model_blind_selection/raw_outputs"
OUT = ROOT / "documentation/research/assisted_mode/p188_adjudication_support"

# function file -> the awarded finding(s) on that surface (for labeling only; not used by the detectors).
CASES = [
    ("onAfterRemoveLiquidity.json", "onAfterRemoveLiquidity", "M-02 (non-responsive)", False),
    ("UpdateWeightRunner__getData.json", "UpdateWeightRunner._getData", "M-06 (severity-floor)", False),
    ("afterUpdate.json", "afterUpdate", "M-03/M-10/L-01 (stable)", True),
    ("onAfterSwap.json", "onAfterSwap", "H-03 (stable)", True),
    ("MultiHopOracle__getData.json", "MultiHopOracle._getData", "L-02 (stable)", True),
]
NEW_FLAGS = ("non_responsive_rejection", "severity_floor_misrejection")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rows, false_positives = [], 0
    for fname, fn, label, is_stable in CASES:
        d = json.loads((P186_RAW / fname).read_text())   # read-only
        res = v.check_output(dict(d))                     # operate on a copy
        after = [f for f in res["flags"] if f in NEW_FLAGS]
        if is_stable and after:
            false_positives += len(after)
        rows.append({"function": fn, "awarded_label": label, "is_stable_selection": is_stable,
                     "flags_before": [], "flags_after": after,
                     "flag_details": res.get("flag_details", []),
                     "needs_harness_count": res.get("needs_harness_count", 0)})

    m02 = next(r for r in rows if r["function"] == "onAfterRemoveLiquidity")
    m06 = next(r for r in rows if r["function"] == "UpdateWeightRunner._getData")
    matrix = {"phase": "P188", "advisory": True, "corpus": "quantamm-2024-12-eval (frozen P186 outputs)",
              "read_only": True, "new_flags": list(NEW_FLAGS), "rows": rows}
    (OUT / "before_after_matrix.json").write_text(json.dumps(matrix, indent=2) + "\n")

    metrics = {
        "phase": "P188",
        "m02_non_responsive_flagged": "non_responsive_rejection" in m02["flags_after"],
        "m02_claimed_locus": next((fd.get("claimed_locus") for fd in m02["flag_details"]
                                   if fd["flag"] == "non_responsive_rejection"), None),
        "m06_severity_floor_flagged": "severity_floor_misrejection" in m06["flags_after"],
        "stable_selection_false_positives": false_positives,
        "checker_advisory": True,
        "acceptance_pass": ("non_responsive_rejection" in m02["flags_after"]
                            and "severity_floor_misrejection" in m06["flags_after"]
                            and false_positives == 0),
    }
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    print(json.dumps(metrics, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
