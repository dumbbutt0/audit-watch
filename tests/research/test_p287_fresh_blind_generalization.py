"""P287 — fresh blind generalization test. Verifies the blind protocol + frozen-stack integrity (research/blind-eval)."""
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "documentation/research/assisted_mode/p287_fresh_blind_generalization"
O = D / "outputs"
FORBIDDEN = {
    "scripts/dashboard_sync.py": "c1af70e1", "prompts/deep_trace.md": "c095c426",
    "scripts/min_confirm_gate.py": "2a15169a", "scripts/confirm_gate.py": "afc481c9",
    "scripts/validate_p208_l3_readiness.py": "ae55eb80",
}
DOC_FILES = ("TARGET_SCREEN.md", "BASELINE_FREEZE.md", "DISCOVERY_AND_ROUTING.md", "EVIDENCE_AND_READY_GATE.md",
             "POC_INTENT_FREEZE.md", "POC_RESULTS.md", "PRE_REVEAL_GATE.md", "REVEAL_AND_SCORE.md",
             "P287_DIAGNOSIS.md", "VERDICT.md", "ROLLBACK_PLAN.md")
VERDICTS = ("A — FULL_PATH_GENERALIZED_WITH_AWARDED_RECOVERY", "B — FULL_PATH_GENERALIZED_WITH_NONAWARDED_TP",
            "C — READY_GENERATED_BUT_NOT_SUPPORTED", "D — NO_READY_BUT_FAILURE_LOCALIZED", "E — TARGET_NOT_DIAGNOSTIC",
            "F — ABORTED_SAFETY_OR_CONTAMINATION")
BOTTLENECKS = ("FULL_PATH_GENERALIZED", "TARGET_FIT_GAP", "RECALL_GAP", "COVERAGE_GAP", "SELECTOR_GAP", "TRIAGE_GAP",
               "EVIDENCE_DERIVATION_GAP", "READY_GATE_TOO_STRICT", "POC_HARNESS_GAP", "OBJECTIVE_MISMATCH",
               "INCONCLUSIVE")


def _sha(p, n=16):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:n]


def test_target_hm_count_recorded_ge1_before_commitment():
    hm = json.loads((O / "hash_manifest.json").read_text())
    assert hm["target"] == "kelp-2023-11-holdout"
    assert hm["target_hm_count"]["total"] >= 1


def test_frozen_stack_unchanged_since_baseline():
    # every frozen-stack file's current hash must match the baseline hash_manifest (no tuning/repair during the run).
    # NOTE: the invariant_delta_deriver + its config were AUTHORIZED-edited by the later P289 lens repair; the P287
    # baseline record below is preserved truthfully, and those two files are excluded from the live re-check.
    p289_edited = {"scripts/research/invariant_delta_deriver.py", "config/research_invariant_delta_deriver.json",
                   # P291 authorized edits (EXTERNAL_INTEGRATION precision + internal-locus recall):
                   "scripts/research/completion_evidence_deriver.py", "scripts/research/poc_readiness_evidence_gate.py",
                   "scripts/research/recall_first_harness.py",
                   # P292 authorized edit (internal-locus queue admission):
                   "scripts/research/expanded_validation_queue.py", "config/research_expanded_validation_queue.json"}
    hm = json.loads((O / "hash_manifest.json").read_text())
    for rel, h in hm["frozen_stack"].items():
        assert h != "MISSING"
        if rel in p289_edited:
            continue
        assert _sha(ROOT / rel) == h, f"frozen stack changed during run: {rel}"


def test_forbidden_byte_identical():
    for rel, h in FORBIDDEN.items():
        assert _sha(ROOT / rel, 8).startswith(h), f"forbidden changed: {rel}"


def test_reveal_blocked_before_pre_reveal_freeze():
    # the pre-reveal freeze must NOT include the reveal artifacts (reveal happened after the freeze)
    pre = json.loads((O / "pre_reveal_freeze.json").read_text())["pre_reveal_artifacts"]
    keys = " ".join(pre.keys()).lower()
    assert "reveal_score" not in keys and "reveal_and_score" not in keys
    assert (O / "reveal_score.json").exists()  # reveal produced, but only after the freeze


def test_no_issue_body_access_attested():
    ts = (D / "TARGET_SCREEN.md").read_text().lower()
    assert "no issue titles/bodies" in ts or "no finding titles/bodies" in ts.replace("issue", "finding")


def test_only_ready_candidates_got_poc():
    rd = json.loads((O / "readiness.json").read_text())
    ready = {d["candidate_id"].split(":")[-2] if ":" in d["candidate_id"] else d["candidate_id"]
             for d in rd["decisions"] if d["status"] == "READY_FOR_POC_INTENT"}
    pr = json.loads((O / "poc_results.json").read_text())
    for poc in pr["pocs"]:
        fn = poc["candidate"].split(".")[-1]
        assert any(fn in r for r in [d["candidate_id"] for d in rd["decisions"]
                                     if d["status"] == "READY_FOR_POC_INTENT"]), f"PoC for non-READY {poc['candidate']}"


def test_no_severity_reportable_leakage():
    for name in ("poc_results.json", "reveal_score.json", "readiness.json"):
        r = json.loads((O / name).read_text())
        if "severity" in r:
            assert r["severity"] is None
        for f in ("reportable", "submission_ready", "concluded", "production_routing", "emits_findings"):
            if f in r:
                assert r[f] is False


def test_reveal_score_has_one_strong_recovery_zero_fp():
    s = json.loads((O / "reveal_score.json").read_text())
    t = s["totals"]
    assert t["strong_or_exact_awarded_recoveries"] >= 1
    assert t["severe_concluded_or_reportable_fp"] == 0


def test_docs_verdict_and_bottleneck():
    for d in DOC_FILES:
        assert (D / d).exists(), f"missing {d}"
    v = (D / "VERDICT.md").read_text()
    assert any(x in v for x in VERDICTS)
    assert any(b in v for b in BOTTLENECKS)


