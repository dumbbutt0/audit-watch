#!/usr/bin/env python3
"""
P180 validation (READ-ONLY) — re-run the P179 precision measurement with the patched extractor and compare to
the P179 (pre-patch) record. Confirms the loadLive/boilerplate artifact is removed: zaros structured blocks
83 → ~0, loadLive concentration gone, generic prose still advisory. Writes ONLY before_after.json here (the
P179 record is NOT overwritten). Reuses the P179 harness helpers.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
P179 = ROOT / "documentation/research/assisted_mode/p179_structured_dependency_precision"

# import the P179 harness module by path (reuse build_awarded_index / derive_blocks / measure)
spec = importlib.util.spec_from_file_location("p179_harness", P179 / "precision_harness.py")
ph = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ph)

import dependency_clear_utils as dcu  # noqa: E402


def main():
    aid = ph.AID
    disp = ph.load(f"audits/{aid}/output/coverage_dispositions.json")["dispositions"]
    man = ph.load(f"audits/{aid}/output/coverage_manifest.json")["items"]
    mi = {i["id"]: i for i in man}; ni = dcu.build_manifest_name_index(man)
    di = {d["manifest_id"]: d for d in disp}
    awarded = ph.build_awarded_index(mi, ni)

    after = ph.measure(disp, mi, ni, di, awarded, structured=True)   # patched extractor
    names_after = Counter(r["dependency_name"] for r in after["rows"])

    before = json.loads((P179 / "metrics.json").read_text())["p178_structured_blocks"]

    out = {
        "phase": "P180", "corpus": aid, "read_only": True,
        "before_p179": {"n_blocks": before["n_blocks"], "buckets": before["buckets"],
                        "exact_precision_pct": before["exact_precision_pct"],
                        "dependency_name": "loadlive x83 (boilerplate artifact)"},
        "after_p180": {"n_blocks": after["n_blocks"], "buckets": after["buckets"],
                       "exact_precision_pct": after["exact_precision_pct"],
                       "dependency_name_concentration": dict(names_after)},
        "artifact_removed": after["n_blocks"] == 0 or "loadlive" not in names_after,
    }
    (HERE / "before_after.json").write_text(json.dumps(out, indent=2))

    print("=== P180 validation (patched extractor, zaros) ===")
    print(f"structured blocks: BEFORE(P179) {before['n_blocks']}  ->  AFTER(P180) {after['n_blocks']}")
    print(f"dependency_name concentration AFTER: {dict(names_after) or '{}'}")
    print(f"buckets AFTER: {after['buckets']}")

    # assertions (the P180 success criteria)
    assert after["n_blocks"] < before["n_blocks"], "structured blocks did not drop"
    assert after["n_blocks"] <= 2, f"expected ~0 structured blocks, got {after['n_blocks']}"
    assert "loadlive" not in names_after, "loadLive concentration still present"

    # regression: real explicit deps still resolve via the patched extractor
    import dependency_metadata as dmeta
    g = {"manifest_id": "function:Pool:pack#x", "status": "cleared", "evidence": ["P.sol:1"],
         "clear_reason": "clamped by _guardQuantAMMWeights"}
    gi = {"function:Guard:_guardQuantAMMWeights#y": {"manifest_id": "function:Guard:_guardQuantAMMWeights#y",
                                                     "status": "assigned"}}
    gmi = {"function:Guard:_guardQuantAMMWeights#y": {"id": "function:Guard:_guardQuantAMMWeights#y",
            "contract": "Guard", "name": "_guardQuantAMMWeights", "file": "Guard.sol", "in_scope": True,
            "source_span": {"start_line": 1, "end_line": 2}}}
    gni = dcu.build_manifest_name_index(list(gmi.values()))
    assert dmeta.extract_dependency_metadata(g, gmi, gni, gi)["dependency_name"] == "_guardquantammweights", \
        "regression: real guard no longer resolves"
    print("regression OK: _guardQuantAMMWeights still resolves")
    print("\n[OK] read-only; artifact removed; wrote before_after.json only")
    return 0


if __name__ == "__main__":
    sys.exit(main())
