"""P278 — expanded discovery & validation queue + PoC-readiness gate. Guard + behavior tests (research-only, advisory)."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VQ = ROOT / "scripts/research/expanded_validation_queue.py"
GATE = ROOT / "scripts/research/poc_readiness_evidence_gate.py"
RCFG = ROOT / "config/research_award_class_coverage_router.json"
VCFG = ROOT / "config/research_expanded_validation_queue.json"
DOCS = ROOT / "documentation/research/assisted_mode/p278_expanded_discovery_validation"
OUTS = DOCS / "outputs"

# router CODE + the other modules stay byte-identical (P278 edits only the router CONFIG)
FROZEN = {
    "scripts/research/locus_shape_prioritizer.py": "d6b494bc3c0cc746",
    "scripts/research/recall_first_shape_sweep.py": "a48336275cb65a4f",
    "scripts/research/recall_first_harness.py": "be428a1202c45b1a",
    "scripts/research/mechanism_pairwise_selector.py": "b0623b8c88752059",
    "scripts/research/impact_first_poc_triage.py": "63c88d02d2c7eefa",
    "scripts/research/award_class_coverage_router.py": "6debb753b45f1833",
    "documentation/research/assisted_mode/p271_lending_runtime_scaffold/"
    "LENDING_COMPLETION_CHECKLIST.md": "2929a2154a88104e",
}
FORBIDDEN = {
    "scripts/dashboard_sync.py": "c1af70e1", "prompts/deep_trace.md": "c095c426",
    "scripts/min_confirm_gate.py": "2a15169a", "scripts/confirm_gate.py": "afc481c9",
    "scripts/validate_p208_l3_readiness.py": "ae55eb80",
}
DOC_FILES = ("SETUP.md", "BUDGET_AND_QUEUE_POLICY.md", "EXPANDED_REPLAY_RESULTS.md", "EVIDENCE_PACKAGES.md",
             "POC_READINESS_GATE.md", "FP_AND_NOISE_REPORT.md", "REPAIR_BACKLOG.md", "LIMITATIONS.md",
             "VERDICT.md", "ROLLBACK_PLAN.md")
VERDICTS = ("A — EXPANDED_VALIDATION_READY_FOR_POC_SWEEP", "B — EXPANDED_VALIDATION_PROMISING_NEEDS_REFINEMENT",
            "C — EXPANDED_VALIDATION_TOO_NOISY", "D — ABORTED_CONSTRAINT_VIOLATION")
PROMO_FALSE = ("reportable", "submission_ready", "concluded", "emits_finding", "production_routing")


def _sha16(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def _gate(packages, tmp_path):
    inp = tmp_path / "p.json"; inp.write_text(json.dumps({"packages": packages}))
    out = tmp_path / "r.json"
    if out.exists():
        out.unlink()
    r = subprocess.run([sys.executable, str(GATE), "--packages", str(inp), "--out", str(out), "--quiet"],
                       capture_output=True, text=True)
    return r, (json.loads(out.read_text()) if out.exists() else None)


def _full_pkg(**over):
    base = {f: "x" for f in json.loads(VCFG.read_text())["readiness_required_dimensions"]}
    base.update({"candidate_id": "c1", "award_class": "ACCESS_CONTROL_AUTHORIZATION"})
    base.update(over)
    return base


# ---- config / budgets ----
def test_router_config_budget_raised():
    caps = json.loads(RCFG.read_text())["caps"]
    assert caps["poc_budget"] == 10 and caps["max_classes"] == 8
    assert caps["poc_budget"] <= caps["hard_max_poc_budget"] and caps["max_classes"] <= caps["hard_max_classes"]


def test_validation_config_budgets_distinct():
    c = json.loads(VCFG.read_text())
    assert c["validation_queue_budget"] == 10
    assert c["poc_execution_budget"] == 5  # separate from validation budget
    assert c["anti_monoculture_max_class_fraction"] == 0.40
    assert c["is_gate"] is False and c["research_only"] is True and c["emits_findings"] is False


# ---- readiness gate behavior ----
def test_complete_evidence_is_ready(tmp_path):
    r, out = _gate([_full_pkg(candidate_id="ok")], tmp_path)
    assert r.returncode == 0
    assert out["decisions"][0]["status"] == "READY_FOR_POC_INTENT"


def test_operator_to_derive_counts_as_missing(tmp_path):
    r, out = _gate([_full_pkg(candidate_id="stub", attacker_model="operator-to-derive")], tmp_path)
    d = out["decisions"][0]
    assert d["status"] != "READY_FOR_POC_INTENT"
    assert "attacker_model" in d["missing_dimensions"]


def test_missing_field_cannot_become_ready(tmp_path):
    r, out = _gate([_full_pkg(candidate_id="m", victim_gainer="")], tmp_path)
    assert out["decisions"][0]["status"] in ("NEEDS_MORE_EVIDENCE", "NEEDS_MORE_RUNTIME")


def test_runtime_only_missing_routes_needs_more_runtime(tmp_path):
    # only refutation_result + poc_assertion missing -> NEEDS_MORE_RUNTIME (not _EVIDENCE)
    r, out = _gate([_full_pkg(candidate_id="rt", refutation_result="operator-to-derive", poc_assertion="")], tmp_path)
    assert out["decisions"][0]["status"] == "NEEDS_MORE_RUNTIME"


def test_poc_budget_separate_demotes_extra_ready(tmp_path):
    pkgs = [_full_pkg(candidate_id=f"r{i}") for i in range(7)]  # 7 complete -> 5 READY, 2 DEFER_POC_BUDGET
    r, out = _gate(pkgs, tmp_path)
    from collections import Counter
    t = Counter(d["status"] for d in out["decisions"])
    assert t["READY_FOR_POC_INTENT"] == 5 and t["DEFER_POC_BUDGET"] == 2


def test_advisory_contract_and_no_leakage(tmp_path):
    r, out = _gate([_full_pkg(candidate_id="a")], tmp_path)
    assert out["emits_findings"] is False and out["severe_concluded_or_reportable_fp"] == 0
    for d in out["decisions"]:
        assert d["severity"] is None
        for f in PROMO_FALSE:
            assert d[f] is False


def test_fail_closed_on_malformed(tmp_path):
    inp = tmp_path / "bad.json"; inp.write_text(json.dumps({"packages": "notalist"}))
    out = tmp_path / "o.json"
    r = subprocess.run([sys.executable, str(GATE), "--packages", str(inp), "--out", str(out), "--quiet"],
                       capture_output=True, text=True)
    assert r.returncode == 2 and not out.exists()


# ---- corpus outputs: queue budget + anti-monoculture + READY breadth ----
def test_validation_queue_budget_enforced():
    for f in OUTS.glob("*/validation_queue.json"):
        d = json.loads(f.read_text())
        assert d["queue_size"] <= d["validation_queue_budget"] == 10
        # anti-monoculture satisfied OR small-queue exception (<5) — never silently violated on full queues
        assert d["anti_monoculture_ok"] or d["queue_size"] < 5


def test_corpus_readiness_no_severe_fp_and_hand_sample_ready():
    severe = 0
    for f in OUTS.glob("*/poc_readiness_report.json"):
        severe += json.loads(f.read_text())["severe_concluded_or_reportable_fp"]
    severe += json.loads((OUTS / "_handsample/poc_readiness_report.json").read_text())["severe_concluded_or_reportable_fp"]
    assert severe == 0
    hand = json.loads((OUTS / "_handsample/poc_readiness_report.json").read_text())
    assert len(hand["ready_for_poc_intent"]) >= 2  # standard is reachable


def test_glue_unwired():
    for s in (VQ, GATE):
        src = s.read_text()
        for bad in ("run_pipeline", "dashboard_sync", "confirm_gate", "record_outcome"):
            assert bad not in src
        assert "SUPERVISED_EVAL" in src


# ---- integrity ----
def test_frozen_and_forbidden_byte_identical():
    for rel, h in FROZEN.items():
        assert _sha16(ROOT / rel) == h, f"frozen changed: {rel}"
    for rel, h in FORBIDDEN.items():
        assert _sha16(ROOT / rel).startswith(h), f"forbidden changed: {rel}"


def test_docs_and_verdict():
    for d in DOC_FILES:
        assert (DOCS / d).exists(), f"missing {d}"
    assert any(v in (DOCS / "VERDICT.md").read_text() for v in VERDICTS)


