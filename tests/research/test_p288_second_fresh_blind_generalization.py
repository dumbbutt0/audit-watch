"""P288 — second fresh blind generalization (replication). Verifies blind protocol + frozen-stack integrity (NO_READY/D)."""
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "documentation/research/assisted_mode/p288_second_fresh_blind_generalization"
O = D / "outputs"
FORBIDDEN = {
    "scripts/dashboard_sync.py": "c1af70e1", "prompts/deep_trace.md": "c095c426",
    "scripts/min_confirm_gate.py": "2a15169a", "scripts/confirm_gate.py": "afc481c9",
    "scripts/validate_p208_l3_readiness.py": "ae55eb80",
}
DOC_FILES = ("TARGET_SCREEN.md", "BASELINE_FREEZE.md", "DISCOVERY_AND_ROUTING.md", "EVIDENCE_AND_READY_GATE.md",
             "NO_READY_DIAGNOSIS.md", "PRE_REVEAL_GATE.md", "REVEAL_AND_SCORE.md", "P288_DIAGNOSIS.md", "VERDICT.md",
             "ROLLBACK_PLAN.md")
VERDICTS = ("A — FULL_PATH_GENERALIZED_REPLICATED_WITH_AWARDED_RECOVERY", "B — FULL_PATH_GENERALIZED_WITH_NONAWARDED_TP",
            "C — READY_GENERATED_BUT_NOT_SUPPORTED", "D — NO_READY_BUT_FAILURE_LOCALIZED", "E — TARGET_NOT_DIAGNOSTIC",
            "F — ABORTED_SAFETY_OR_CONTAMINATION")
BOTTLENECKS = ("EVIDENCE_DERIVATION_GAP", "TARGET_FIT_GAP", "RECALL_GAP", "COVERAGE_GAP", "SELECTOR_GAP", "TRIAGE_GAP",
               "READY_GATE_TOO_STRICT", "POC_HARNESS_GAP", "FULL_PATH_GENERALIZED_REPLICATED", "OBJECTIVE_MISMATCH",
               "INCONCLUSIVE")


def _sha(p, n=16):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:n]


def test_target_hm_count_ge2_recorded_before_commitment():
    hm = json.loads((O / "hash_manifest.json").read_text())
    assert hm["target"] == "ecg-2023-12-holdout"
    assert hm["target_hm_count"]["total"] >= 2  # P288 stricter bar


def test_frozen_stack_unchanged_and_matches_p287_baseline():
    # invariant_delta_deriver + config were AUTHORIZED-edited by the later P289 lens repair; baseline preserved,
    # those two excluded from the live re-check (the other 21 frozen files must still match).
    p289_edited = {"scripts/research/invariant_delta_deriver.py", "config/research_invariant_delta_deriver.json",
                   # P291 authorized edits:
                   "scripts/research/completion_evidence_deriver.py", "scripts/research/poc_readiness_evidence_gate.py",
                   "scripts/research/recall_first_harness.py",
                   # P292 authorized edit (internal-locus queue admission):
                   "scripts/research/expanded_validation_queue.py", "config/research_expanded_validation_queue.json"}
    hm = json.loads((O / "hash_manifest.json").read_text())
    assert hm.get("frozen_vs_p287_mismatches") == []
    for rel, h in hm["frozen_stack"].items():
        if rel in p289_edited:
            continue
        assert h != "MISSING" and _sha(ROOT / rel) == h, f"frozen stack changed: {rel}"


def test_forbidden_byte_identical():
    for rel, h in FORBIDDEN.items():
        assert _sha(ROOT / rel, 8).startswith(h), f"forbidden changed: {rel}"


def test_reveal_blocked_before_pre_reveal_freeze():
    pre = json.loads((O / "pre_reveal_freeze.json").read_text())["pre_reveal_artifacts"]
    keys = " ".join(pre.keys()).lower()
    assert "reveal_score" not in keys and "reveal_and_score" not in keys
    assert (O / "reveal_score.json").exists()


def test_zero_ready_and_no_poc_attempts():
    r = json.loads((O / "readiness.json").read_text())
    ready = [d for d in r["decisions"] if d["status"] == "READY_FOR_POC_INTENT"]
    assert ready == []  # NO_READY outcome
    # only READY candidates may get PoCs -> with 0 READY there must be no poc_results / no p288 PoC project
    assert not (O / "poc_results.json").exists()
    assert not (ROOT / "pocs/p288").exists()


def test_no_severity_reportable_leakage():
    for name in ("reveal_score.json", "readiness.json", "pre_reveal_freeze.json"):
        r = json.loads((O / name).read_text())
        if "severity" in r:
            assert r["severity"] is None
        for f in ("reportable", "submission_ready", "concluded", "production_routing", "emits_findings"):
            if f in r:
                assert r[f] is False


def test_reveal_score_zero_recovery_zero_fp_localized():
    t = json.loads((O / "reveal_score.json").read_text())["totals"]
    assert t["strong_or_exact_awarded_recoveries"] == 0
    assert t["ready"] == 0
    assert t["severe_concluded_or_reportable_fp"] == 0
    assert t["false_positive"] == 0


def test_docs_verdict_and_bottleneck():
    for d in DOC_FILES:
        assert (D / d).exists(), f"missing {d}"
    v = (D / "VERDICT.md").read_text()
    assert any(x in v for x in VERDICTS)
    assert any(b in v for b in BOTTLENECKS)


