"""P242 — final recall sprint (2 families). Docs guard + research-only flag checks."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "documentation/research/assisted_mode/p242_recall_sprint"
VAL = BASE / "VALIDATION_REPORT.md"
OUT = BASE / "outputs"

VERDICTS = (
    "A — BOTH_READY_FOR_ADVISORY_USE",
    "B — ONLY_CREATE_TIME_READY",
    "C — ONLY_4626_READY",
    "D — KEEP_BOTH_RESEARCH_ONLY",
    "E — DISCARD",
)


def test_reports_exist_with_verdict():
    for f in ("FAMILY_A_create_time_reentrancy.md", "FAMILY_B_erc4626_share_accounting.md",
              "VALIDATION_REPORT.md", "COUNTERFACTUAL.md"):
        assert (BASE / f).exists(), f"missing {f}"
    assert any(v in VAL.read_text() for v in VERDICTS), "no recognized P242 verdict token"


def test_both_detectors_emit_research_flags():
    for f in OUT.glob("*_ctr.json"):
        r = json.loads(f.read_text())
        assert r.get("research_only") is True and r.get("routed_manifest_ids") == [] and r.get("is_gate") is False
    for f in OUT.glob("*_e46.json"):
        r = json.loads(f.read_text())
        assert r.get("research_only") is True and r.get("routed_manifest_ids") == [] and r.get("is_gate") is False


def test_anchors_recovered_negative_controls_clean():
    # Family A recovers nextgen; negative controls (quantamm/dittoeth/kelp/fenix) emit 0 for both families.
    a = json.loads((OUT / "nextgen-2023-10-fresh_ctr.json").read_text())
    assert any(c["function"] == "mint" and c["contract"] == "NextGenCore" for c in a["candidates"])
    b = json.loads((OUT / "pooltogether-2024-03-holdout_e46.json").read_text())
    assert any(c["function"] == "_maxYieldVaultWithdraw" for c in b["candidates"])
    for ctrl in ("quantamm-2024-12-eval", "dittoeth-2024-03-holdout", "kelp-2023-11-holdout", "fenix-2024-09-fresh"):
        assert json.loads((OUT / f"{ctrl}_ctr.json").read_text())["candidates"] == []
        assert json.loads((OUT / f"{ctrl}_e46.json").read_text())["candidates"] == []
