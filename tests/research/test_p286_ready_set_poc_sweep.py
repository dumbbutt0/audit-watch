"""P286 — READY-set PoC sweep. Verifies the claim_many PoC + L2Governor regression results (research-only, advisory)."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "documentation/research/assisted_mode/p286_ready_set_poc_sweep"
OUTS = DOCS / "outputs"
P285_OUTS = ROOT / "documentation/research/assisted_mode/p285_inline_guard_granularity/outputs"
FROZEN = {
    "scripts/research/locus_shape_prioritizer.py": "d6b494bc3c0cc746",
    "scripts/research/recall_first_shape_sweep.py": "a48336275cb65a4f",
    "scripts/research/recall_first_harness.py": "be428a1202c45b1a",
    "scripts/research/mechanism_pairwise_selector.py": "b0623b8c88752059",
    "scripts/research/impact_first_poc_triage.py": "63c88d02d2c7eefa",
    "scripts/research/award_class_coverage_router.py": "6debb753b45f1833",
    "config/research_award_class_coverage_router.json": "91f9deac7867af62",
    "scripts/research/cross_function_value_tracer.py": "f28f0620d3d3548a",
    "scripts/research/invariant_delta_deriver.py": "80bfa9f07d06d38f",
    "config/research_invariant_delta_deriver.json": "4774dfa72974019a",
    "documentation/research/assisted_mode/p271_lending_runtime_scaffold/"
    "LENDING_COMPLETION_CHECKLIST.md": "2929a2154a88104e",
}
REUSED = {
    "scripts/sibling_function_parity_taxonomy.py": "e504383db8f33844",
    "scripts/registry_position_lifecycle_taxonomy.py": "da83a7acc217c706",
}
FORBIDDEN = {
    "scripts/dashboard_sync.py": "c1af70e1", "prompts/deep_trace.md": "c095c426",
    "scripts/min_confirm_gate.py": "2a15169a", "scripts/confirm_gate.py": "afc481c9",
    "scripts/validate_p208_l3_readiness.py": "ae55eb80",
}
DOC_FILES = ("SETUP.md", "POC_RESULTS.md", "POC_EVIDENCE_AUDIT.md", "LIMITATIONS.md", "VERDICT.md", "ROLLBACK_PLAN.md")
VERDICTS = ("A — READY_SET_POC_SUPPORTED", "B — POC_PARTIAL", "C — POC_REFUTED", "D — ABORTED_CONSTRAINT_VIOLATION")


def _sha16(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def test_poc_results_claim_many_all_layers_pass():
    r = json.loads((OUTS / "poc_results.json").read_text())
    cm = next(p for p in r["pocs"] if p["candidate"] == "RewardsDistributor.claim_many")
    assert cm["tier"] == "C" and cm["mechanism"] == "recipient_divergence" and cm["all_pass"] is True
    for layer in ("L1_entry", "L2_state_flip", "L3_outcome"):
        assert cm["layers"][layer]["pass"] is True
    assert all(v == "pass" for v in cm["tests"].values())


def test_p286_run_output_three_passed():
    t = (OUTS / "p286_run_output.txt").read_text()
    assert "3 passed" in t and "0 failed" in t


def test_l2governor_regression_two_passed():
    t = (OUTS / "l2governor_regression_log.txt").read_text()
    assert "2 passed" in t and "0 failed" in t


def test_claim_many_is_ready_in_p285_corpus():
    found = False
    for j in P285_OUTS.glob("*/readiness.json"):
        for d in json.loads(j.read_text())["decisions"]:
            if d["candidate_id"] == "coverage_manifest:RewardsDistributor:claim_many:7":
                found = True
                assert d["status"] == "READY_FOR_POC_INTENT"
    assert found


def test_no_severity_reportable_leakage():
    r = json.loads((OUTS / "poc_results.json").read_text())
    assert r["severity"] is None
    for f in ("reportable", "submission_ready", "concluded", "production_routing", "emits_findings"):
        assert r[f] is False
    assert r["fabricated_pass"] == 0 and r["severe_concluded_or_reportable_fp"] == 0


def test_poc_file_exists():
    assert (ROOT / "pocs/p286/test/P286_ClaimManyRecipient.t.sol").exists()


def test_frozen_reused_forbidden_byte_identical():
    for rel, h in {**FROZEN, **REUSED}.items():
        assert _sha16(ROOT / rel) == h, f"changed: {rel}"
    for rel, h in FORBIDDEN.items():
        assert _sha16(ROOT / rel).startswith(h), f"forbidden changed: {rel}"


def test_docs_and_verdict():
    for d in DOC_FILES:
        assert (DOCS / d).exists(), f"missing {d}"
    assert any(v in (DOCS / "VERDICT.md").read_text() for v in VERDICTS)


