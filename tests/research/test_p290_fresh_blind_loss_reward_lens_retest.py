"""P290 — third fresh blind retest (loss/reward lens generalization). Blind protocol + integrity (verdict D)."""
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "documentation/research/assisted_mode/p290_fresh_blind_loss_reward_lens_retest"
O = D / "outputs"
FORBIDDEN = {
    "scripts/dashboard_sync.py": "c1af70e1", "prompts/deep_trace.md": "c095c426",
    "scripts/min_confirm_gate.py": "2a15169a", "scripts/confirm_gate.py": "afc481c9",
    "scripts/validate_p208_l3_readiness.py": "ae55eb80",
}
DOC_FILES = ("TARGET_SCREEN.md", "BASELINE_FREEZE.md", "DISCOVERY_AND_ROUTING.md", "EVIDENCE_AND_READY_GATE.md",
             "POC_INTENT_FREEZE.md", "POC_RESULTS.md", "PRE_REVEAL_GATE.md", "REVEAL_AND_SCORE.md",
             "P290_DIAGNOSIS.md", "VERDICT.md", "ROLLBACK_PLAN.md")
VERDICTS = ("A — FULL_PATH_GENERALIZED_WITH_AWARDED_RECOVERY", "B — LENS_GENERALIZED_WITH_AWARDED_RECOVERY",
            "C — FULL_PATH_GENERALIZED_WITH_NONAWARDED_TP", "D — READY_GENERATED_BUT_NOT_SUPPORTED",
            "E — NO_READY_BUT_FAILURE_LOCALIZED", "F — TARGET_NOT_DIAGNOSTIC", "G — ABORTED_SAFETY_OR_CONTAMINATION")
BOTTLENECKS = ("EVIDENCE_DERIVATION_GAP", "TARGET_FIT_GAP", "RECALL_GAP", "COVERAGE_GAP", "SELECTOR_GAP", "TRIAGE_GAP",
               "READY_GATE_TOO_STRICT", "POC_HARNESS_GAP", "FULL_PATH_GENERALIZED_REPLICATED", "LENS_GENERALIZED",
               "OBJECTIVE_MISMATCH", "INCONCLUSIVE")


def _sha(p, n=16):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:n]


def test_target_hm_count_ge2_recorded_before_commitment():
    hm = json.loads((O / "hash_manifest.json").read_text())
    assert hm["target"] == "salty-2024-01-holdout"
    assert hm["target_hm_count"]["total"] >= 2


def test_frozen_stack_unchanged_since_baseline():
    # P291 authorized-edited these (EXTERNAL_INTEGRATION precision + internal-locus recall); baseline preserved,
    # excluded from the live re-check (the rest of the frozen stack must still match).
    p291_edited = {"scripts/research/completion_evidence_deriver.py", "scripts/research/poc_readiness_evidence_gate.py",
                   "scripts/research/recall_first_harness.py",
                   # P292 authorized edit (internal-locus queue admission):
                   "scripts/research/expanded_validation_queue.py", "config/research_expanded_validation_queue.json",
                   # P293 authorized edit (cross-function reward-index lens — deriver + its config):
                   "scripts/research/invariant_delta_deriver.py", "config/research_invariant_delta_deriver.json"}
    hm = json.loads((O / "hash_manifest.json").read_text())
    for rel, h in hm["frozen_stack"].items():
        if rel in p291_edited:
            continue
        assert h != "MISSING" and _sha(ROOT / rel) == h, f"frozen stack changed during run: {rel}"


def test_forbidden_byte_identical():
    for rel, h in FORBIDDEN.items():
        assert _sha(ROOT / rel, 8).startswith(h), f"forbidden changed: {rel}"


def test_reveal_blocked_before_pre_reveal_freeze():
    pre = json.loads((O / "pre_reveal_freeze.json").read_text())["pre_reveal_artifacts"]
    keys = " ".join(pre.keys()).lower()
    assert "reveal_score" not in keys and "reveal_and_score" not in keys
    assert (O / "reveal_score.json").exists()


def test_only_ready_candidates_got_poc():
    rd = json.loads((O / "readiness.json").read_text())
    ready = [d["candidate_id"] for d in rd["decisions"] if d["status"] == "READY_FOR_POC_INTENT"]
    pr = json.loads((O / "poc_results.json").read_text())
    # exactly the READY candidate(s) were PoC'd; the PoC'd candidate must be among READY
    for poc in pr["pocs"]:
        fn = poc["candidate"].split(".")[-1]
        assert any(fn in r for r in ready), f"PoC for non-READY {poc['candidate']}"


def test_p289_lens_firings_recorded_zero():
    le = json.loads((O / "lens_evidence.json").read_text())
    assert le["p289_lens_firings"] == 0
    assert json.loads((O / "reveal_score.json").read_text())["p289_lens_firings"] == 0


def test_no_severity_reportable_leakage():
    for name in ("poc_results.json", "reveal_score.json", "readiness.json"):
        r = json.loads((O / name).read_text())
        if "severity" in r:
            assert r["severity"] is None
        for f in ("reportable", "submission_ready", "concluded", "production_routing", "emits_findings"):
            if f in r:
                assert r[f] is False


def test_reveal_score_zero_recovery_zero_severe_fp_one_refuted_ready():
    t = json.loads((O / "reveal_score.json").read_text())["totals"]
    assert t["strong_or_exact_awarded_recoveries"] == 0
    assert t["severe_concluded_or_reportable_fp"] == 0
    assert t["ready"] == 1 and t["poc_supported"] == 0  # the one READY was refuted (verdict D)


def test_docs_verdict_and_bottleneck():
    for d in DOC_FILES:
        assert (D / d).exists(), f"missing {d}"
    v = (D / "VERDICT.md").read_text()
    assert any(x in v for x in VERDICTS)
    assert any(b in v for b in BOTTLENECKS)


