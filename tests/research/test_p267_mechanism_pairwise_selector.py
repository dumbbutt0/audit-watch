"""P267 — pairwise mechanism selector. Guard + behavior tests (research-only, advisory, default-off)."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/research/mechanism_pairwise_selector.py"
CFG = ROOT / "config/research_mechanism_pairwise_selector.json"
DOCS = ROOT / "documentation/research/assisted_mode/p267_mechanism_selection_repair"
OUTS = DOCS / "outputs"
DOC_FILES = ("SETUP.md", "FAILURE_FORENSICS.md", "SELECTOR_SPEC.md", "IMPLEMENTATION_NOTES.md",
             "BACKTEST_RESULTS.md", "INTEGRATION_PROPOSAL.md", "LIMITATIONS.md", "VERDICT.md")
VERDICTS = ("A — SELECTOR_READY_FOR_FRESH_PRODUCTION_PATH_TEST", "B — SELECTOR_PROMISING_NEEDS_REFINEMENT",
            "C — SELECTOR_NOT_USEFUL", "D — ABORTED_CONSTRAINT_VIOLATION")
FORBIDDEN_FIELDS = ("reportable", "submission_ready", "concluded", "emits_finding", "production_routing")
OUTCOMES = ("SELECT_M1", "SELECT_M2", "KEEP_BOTH", "REFUTE_M1_FIRST", "REFUTE_M2_FIRST", "INSUFFICIENT_EVIDENCE")
# infrastructure that must NOT change
FROZEN = {
    "scripts/research/locus_shape_prioritizer.py": "d6b494bc3c0cc746",
    "scripts/research/recall_first_shape_sweep.py": "a48336275cb65a4f",
    "scripts/research/recall_first_harness.py": "be428a1202c45b1a",
    "config/research_locus_shape_prioritizer.json": "c61da091ad3ed21e",
    "config/research_recall_first_shape_sweep.json": "62e860199e7c51cd",
    "config/research_recall_first_harness.json": "0ea77ea476450520",
}
FORBIDDEN_FILES = {
    "scripts/dashboard_sync.py": "c1af70e1",
    "prompts/deep_trace.md": "c095c426",
    "scripts/min_confirm_gate.py": "2a15169a",
    "scripts/confirm_gate.py": "afc481c9",
    "scripts/validate_p208_l3_readiness.py": "ae55eb80",
}


def _sha16(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def _run(pairs, tmp_path):
    inp = tmp_path / "pairs.json"
    inp.write_text(json.dumps(pairs))
    out = tmp_path / "dec.json"
    r = subprocess.run([sys.executable, str(SCRIPT), "--pairs", str(inp), "--out", str(out), "--quiet"],
                       capture_output=True, text=True)
    return r, out


def test_files_and_docs_and_verdict():
    assert SCRIPT.exists() and CFG.exists()
    for d in DOC_FILES:
        assert (DOCS / d).exists(), f"missing {d}"
    assert any(v in (DOCS / "VERDICT.md").read_text() for v in VERDICTS)


def test_config_advisory_and_dimensions():
    c = json.loads(CFG.read_text())
    assert c["is_gate"] is False and c["research_only"] is True and c["routes_in_production"] is False
    assert c["emits_findings"] is False
    # terminal-impact-dominance dimension exists (award-like impact classes weighted high)
    assert c["impact_class_weight"]["permanent_dos"] >= 5 and c["impact_class_weight"]["one_off_skim"] <= 2
    # anti-easy-PoC-bias dimension exists (a feasibility rank the selector uses to flag, never to promote)
    assert "poc_feasibility_rank" in c


def test_module_unwired_and_no_answer_key():
    src = SCRIPT.read_text()
    # no IMPORTS of production wiring (docstring may mention these to declare it is un-wired)
    import_lines = [ln for ln in src.splitlines() if ln.strip().startswith(("import ", "from "))]
    for forbidden in ("run_pipeline", "agent_policy", "dashboard_sync", "confirm_gate", "record_outcome"):
        assert not any(forbidden in ln for ln in import_lines), f"module imports {forbidden}"
    # no answer-key dependency anywhere
    for forbidden in ("ground_truth", "answer_key"):
        assert forbidden not in src, f"module references {forbidden}"


def test_backtest_outputs_advisory_only_and_bounded():
    dec = json.loads((OUTS / "p267_backtest_decisions.json").read_text())
    assert dec["emits_findings"] is False and dec["concludes_vulnerability"] is False
    assert dec["decision_count"] <= 50
    for d in dec["decisions"]:
        assert d["severity"] is None
        assert d["status"] == "ADVISORY_SELECTOR_DECISION"
        assert d["outcome"] in OUTCOMES
        for f in FORBIDDEN_FIELDS:
            assert d[f] is False, f"{f} set"
    guard = json.loads((OUTS / "selector_guard_report.json").read_text())
    assert guard["result"] == "PASS" and guard["guard_violations"] == 0


def test_p266_h03_fixture_keeps_high_impact(tmp_path):
    """The headline: the P266 H-03 pair must SELECT or KEEP the high-impact gas-DoS, never drop it for the skim."""
    pairs = {"pairs": [{
        "case": "h03",
        "M1": {"id": "skim", "impact_class": "one_off_skim", "value_at_risk": "single_op",
               "victim_gainer_clarity": "clear", "intent_violation": "none", "attacker_control": "permissionless",
               "persistence": "one_off", "refutation_resistance": "conditional", "poc_feasibility": "easy"},
        "M2": {"id": "dos", "impact_class": "permanent_dos", "value_at_risk": "systemic",
               "victim_gainer_clarity": "clear", "intent_violation": "invariant_or_comparand",
               "attacker_control": "permissionless", "persistence": "permanent",
               "refutation_resistance": "survives", "poc_feasibility": "hard"}}]}
    r, out = _run(pairs, tmp_path)
    assert r.returncode == 0, r.stderr
    d = json.loads(out.read_text())["decisions"][0]
    assert d["outcome"] in ("SELECT_M2", "KEEP_BOTH"), f"H-03 high-impact dropped: {d['outcome']}"
    assert d["anti_easy_poc_flag"] is True  # easier low-impact rival -> flag must fire
    assert d["outcome"] != "SELECT_M1"


def test_negative_control_not_blindly_messy(tmp_path):
    """A dramatic-but-refuted mechanism must NOT be selected."""
    pairs = {"pairs": [{
        "case": "nc",
        "M1": {"id": "drama", "impact_class": "insolvency", "value_at_risk": "systemic",
               "victim_gainer_clarity": "partial", "intent_violation": "documented_intent",
               "attacker_control": "privileged", "persistence": "permanent",
               "refutation_resistance": "refuted", "poc_feasibility": "hard"},
        "M2": {"id": "clean", "impact_class": "stranded_funds", "value_at_risk": "multi_user",
               "victim_gainer_clarity": "clear", "intent_violation": "invariant_or_comparand",
               "attacker_control": "permissionless", "persistence": "permanent",
               "refutation_resistance": "survives", "poc_feasibility": "moderate"}}]}
    r, out = _run(pairs, tmp_path)
    assert r.returncode == 0, r.stderr
    d = json.loads(out.read_text())["decisions"][0]
    assert d["outcome"] != "SELECT_M1", "selected a dramatic but refuted mechanism"


def test_keep_both_supported(tmp_path):
    dec = json.loads((OUTS / "p267_backtest_decisions.json").read_text())
    assert any(d["outcome"] == "KEEP_BOTH" for d in dec["decisions"]), "KEEP_BOTH never produced"


def test_malformed_input_fails_closed(tmp_path):
    r, out = _run({"pairs": [{"case": "bad", "M1": {"id": "x"}}]}, tmp_path)  # missing M2
    assert r.returncode == 2 and not out.exists()


def test_frozen_infrastructure_unchanged():
    for rel, h in FROZEN.items():
        assert _sha16(ROOT / rel) == h, f"{rel} changed (P260/P262/P264 must be unchanged)"


def test_forbidden_files_byte_identical():
    for rel, h in FORBIDDEN_FILES.items():
        assert _sha16(ROOT / rel).startswith(h), f"forbidden file {rel} changed"
