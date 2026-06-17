"""P295 — corpus-wide recall-of-confirmed harness. Funnel from read-only answer keys + executed-PoC overlay.

Runs `forge` (confirmation is by real execution). FP=0 is by construction (only awarded loci with a passing
exploit PoC are confirmed).
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/research"))
import recall_of_confirmed_corpus as rcc  # noqa: E402

D = ROOT / "documentation/research/assisted_mode/p295_recall_of_confirmed_corpus"
O = D / "outputs"
FORGE = shutil.which("forge")
needs_forge = pytest.mark.skipif(FORGE is None, reason="forge not installed")

BYTE_IDENTICAL = {"scripts/research/executed_poc_verifier.py": "1a005811fbb9e0d0"}
FORBIDDEN = {
    "scripts/dashboard_sync.py": "c1af70e1", "prompts/deep_trace.md": "c095c426",
    "scripts/min_confirm_gate.py": "2a15169a", "scripts/confirm_gate.py": "afc481c9",
    "scripts/validate_p208_l3_readiness.py": "ae55eb80",
}
DOC_FILES = ("SETUP.md", "DESIGN.md", "IMPLEMENTATION_NOTES.md", "FUNNEL_RESULTS.md", "EVIDENCE_AUDIT.md",
             "LIMITATIONS.md", "VERDICT.md", "ROLLBACK_PLAN.md")
VERDICTS = ("A — ", "B — ", "C — ", "D — ")


def _funnel():
    return json.loads((O / "recall_funnel.json").read_text())


# ---- the harness produces a coherent funnel ----
def test_funnel_built_with_recall_fractions():
    f = _funnel()
    agg = f["aggregate_full_local"]
    assert agg["awarded"] > 0 and 0.0 <= agg["recall_of_surfaced"] <= 1.0
    assert 0.0 <= agg["recall_of_confirmed"] <= 1.0
    assert agg["confirmed"] <= agg["surfaced"] <= agg["awarded"]  # funnel monotonicity


def test_recall_of_confirmed_climbed_this_phase():
    f = _funnel()
    # P294 confirmed 2 loci; P295 wires 4 + adds the net-new ecg climb -> >= 4 full-local, >=5 total.
    assert f["aggregate_full_local"]["confirmed"] >= 4
    assert f["total_loci_confirmed_by_execution"] >= 5


def test_surfacing_ceiling_high():
    # open recall surfaces most awarded loci; the gap to 100% is confirmation, not surfacing.
    assert _funnel()["aggregate_full_local"]["recall_of_surfaced"] >= 0.6


# ---- FP oracle: confirmed-FP must be 0; the false hypothesis is refused ----
def test_confirmed_false_positive_zero():
    assert _funnel()["confirmed_false_positive_count"] == 0


def test_refutation_control_not_confirmed():
    f = _funnel()
    for fid, r in f["refutation_controls"].items():
        assert r["attacker_verified"] is False


@needs_forge
def test_every_confirmed_backed_by_real_log():
    recs = json.loads((O / "verification_records.json").read_text())["records"]
    confirmed = [r for r in recs if r.get("attacker_verified")]
    assert len(confirmed) >= 5
    for r in confirmed:
        assert any(x.get("passed") and x.get("log_ref") for x in r.get("runs", []))  # a real passing exploit run


@needs_forge
def test_surfaced_string_helper():
    assert rcc._surfaced(True) and rcc._surfaced("EXACT function") and rcc._surfaced("contract only (queued)")
    assert not rcc._surfaced(False) and not rcc._surfaced("MISSED") and not rcc._surfaced("not surfaced")


# ---- backlog = the climb worklist ----
def test_backlog_nonempty_and_ranked():
    b = json.loads((O / "backlog.json").read_text())
    assert len(b["surfaced_unconfirmed_poc_worklist"]) > 0   # PoC worklist toward 100%
    assert "missed_surfacing_worklist" in b


# ---- integrity / authority ----
def test_unwired_from_confirm_gates():
    for rel in ("scripts/confirm_gate.py", "scripts/min_confirm_gate.py"):
        txt = (ROOT / rel).read_text()
        assert "recall_of_confirmed_corpus" not in txt and "executed_poc_verifier" not in txt


def test_no_leakage_advisory_stamps():
    for name in ("recall_funnel.json", "backlog.json", "guard_report.json", "verification_records.json"):
        r = json.loads((O / name).read_text())
        for fld in ("reportable", "submission_ready", "concluded", "production_routing", "auto_submitted"):
            if fld in r:
                assert r[fld] is False
        if "severity" in r:
            assert r["severity"] is None


def test_verifier_and_forbidden_byte_identical():
    for rel, h in BYTE_IDENTICAL.items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:16] == h, f"changed: {rel}"
    for rel, h in FORBIDDEN.items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:8].startswith(h), f"forbidden changed: {rel}"


def test_docs_and_verdict():
    for d in DOC_FILES:
        assert (D / d).exists(), f"missing {d}"
    assert any(v in (D / "VERDICT.md").read_text() for v in VERDICTS)


