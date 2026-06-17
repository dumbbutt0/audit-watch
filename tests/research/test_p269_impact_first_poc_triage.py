"""P269 — impact-first PoC triage. Guard + behavior tests (research-only, advisory, default-off)."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/research/impact_first_poc_triage.py"
CFG = ROOT / "config/research_impact_first_poc_triage.json"
DOCS = ROOT / "documentation/research/assisted_mode/p269_impact_first_triage"
OUTS = DOCS / "outputs"
DOC_FILES = ("SETUP.md", "FAILURE_FORENSICS.md", "TRIAGE_POLICY_SPEC.md", "IMPLEMENTATION_NOTES.md",
             "BACKTEST_RESULTS.md", "INTEGRATION_PROPOSAL.md", "LIMITATIONS.md", "VERDICT.md")
VERDICTS = ("A — TRIAGE_POLICY_READY_FOR_FRESH_FULL_PATH_TEST", "B — TRIAGE_POLICY_PROMISING_NEEDS_REFINEMENT",
            "C — TRIAGE_POLICY_NOT_USEFUL", "D — ABORTED_CONSTRAINT_VIOLATION")
SELECT = ("SELECT_FOR_FULL_POC", "SELECT_FOR_PARTIAL_RUNTIME", "SELECT_FOR_MANUAL_HARNESS_DESIGN")
ALL_OUT = SELECT + ("KEEP_AS_CONTROL", "DEFER_LOW_IMPACT", "DEFER_INFEASIBLE")
FORBIDDEN_FIELDS = ("reportable", "submission_ready", "concluded", "emits_finding", "production_routing")
FROZEN = {
    "scripts/research/locus_shape_prioritizer.py": "d6b494bc3c0cc746",
    "scripts/research/recall_first_shape_sweep.py": "a48336275cb65a4f",
    "scripts/research/recall_first_harness.py": "be428a1202c45b1a",
    "scripts/research/mechanism_pairwise_selector.py": "b0623b8c88752059",
}
FORBIDDEN_FILES = {
    "scripts/dashboard_sync.py": "c1af70e1", "prompts/deep_trace.md": "c095c426",
    "scripts/min_confirm_gate.py": "2a15169a", "scripts/confirm_gate.py": "afc481c9",
    "scripts/validate_p208_l3_readiness.py": "ae55eb80",
}


def _sha16(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def _run(cands, tmp_path):
    inp = tmp_path / "c.json"; inp.write_text(json.dumps({"candidates": cands}))
    out = tmp_path / "o.json"
    r = subprocess.run([sys.executable, str(SCRIPT), "--candidates", str(inp), "--out", str(out), "--quiet"],
                       capture_output=True, text=True)
    return r, out


def test_files_docs_verdict():
    assert SCRIPT.exists() and CFG.exists()
    for d in DOC_FILES:
        assert (DOCS / d).exists(), f"missing {d}"
    assert any(v in (DOCS / "VERDICT.md").read_text() for v in VERDICTS)


def test_config_anti_easy_poc_and_heavy_routing():
    c = json.loads(CFG.read_text())
    assert c["is_gate"] is False and c["research_only"] is True and c["emits_findings"] is False
    # award-class impact dominates; feasibility is NOT an impact weight
    assert c["impact_class_weight"]["slashing"] >= 5 and c["impact_class_weight"]["one_off_skim"] <= 2
    # harness-weight blockers are routable (heavy), not infeasible
    assert "needs_beacon_fixtures" in c["harness_weight_blockers"]
    assert "needs_beacon_fixtures" not in c["infeasible_blockers"]
    assert "no_exploit_path" in c["infeasible_blockers"]


def test_module_unwired_no_answer_key():
    src = SCRIPT.read_text()
    imports = [ln for ln in src.splitlines() if ln.strip().startswith(("import ", "from "))]
    for f in ("run_pipeline", "agent_policy", "dashboard_sync", "confirm_gate", "record_outcome"):
        assert not any(f in ln for ln in imports), f"imports {f}"
    for f in ("ground_truth", "answer_key"):
        assert f not in src


def test_karak_award_subsystem_routed_heavy(tmp_path):
    """The headline: a slashing/snapshot candidate needing beacon fixtures is ROUTED (heavy), not de-scoped."""
    cands = [
        {"id": "k_slash", "subsystem": "native_vault_slashing_snapshot", "impact_class": "slashing",
         "recall_delta": True, "terminality": "permanent", "value_at_risk": "systemic",
         "poc_feasibility": "heavy", "feasibility_blockers": ["needs_beacon_fixtures"], "impact_supported": True},
        {"id": "k_easy", "subsystem": "erc20_vault", "impact_class": "griefing_minor", "recall_delta": False,
         "terminality": "one_off", "value_at_risk": "single_op", "poc_feasibility": "easy", "impact_supported": True},
    ]
    r, out = _run(cands, tmp_path)
    assert r.returncode == 0, r.stderr
    d = {x["id"]: x for x in json.loads(out.read_text())["decisions"]}
    assert d["k_slash"]["outcome"] in SELECT, "award subsystem de-scoped (P268 bug not fixed)"
    assert d["k_slash"]["heavy_poc"] is True
    assert d["k_slash"]["outcome"] != "DEFER_INFEASIBLE"
    assert d["k_easy"]["outcome"] not in SELECT or d["k_slash"]["impact_fit"] > d["k_easy"]["impact_fit"]


def test_phi_does_not_route_only_skim(tmp_path):
    cands = [
        {"id": "h03", "subsystem": "curator_rewards", "impact_class": "systemic_liveness_failure",
         "recall_delta": True, "terminality": "permanent", "value_at_risk": "systemic", "poc_feasibility": "moderate",
         "selector_outcome": "KEEP_BOTH", "impact_supported": True},
        {"id": "skim", "subsystem": "curator_rewards", "impact_class": "one_off_skim", "recall_delta": False,
         "terminality": "one_off", "value_at_risk": "single_op", "poc_feasibility": "easy", "impact_supported": True},
    ]
    r, out = _run(cands, tmp_path)
    d = {x["id"]: x for x in json.loads(out.read_text())["decisions"]}
    assert d["h03"]["outcome"] in SELECT, "H-03 high-impact not routed"
    assert d["skim"]["outcome"] not in SELECT or d["h03"]["impact_fit"] > d["skim"]["impact_fit"]


def test_negative_control_unsupported_drama_not_routed(tmp_path):
    cands = [
        {"id": "drama", "subsystem": "nc", "impact_class": "insolvency", "recall_delta": False,
         "terminality": "permanent", "value_at_risk": "systemic", "poc_feasibility": "easy",
         "impact_supported": False},  # unsupported drama
        {"id": "infeasible", "subsystem": "nc", "impact_class": "insolvency", "recall_delta": True,
         "terminality": "permanent", "value_at_risk": "systemic", "poc_feasibility": "heavy",
         "feasibility_blockers": ["no_exploit_path"], "impact_supported": True},
    ]
    r, out = _run(cands, tmp_path)
    d = {x["id"]: x for x in json.loads(out.read_text())["decisions"]}
    assert d["drama"]["outcome"] not in SELECT, "routed an unsupported high-drama candidate"
    assert d["infeasible"]["outcome"] == "DEFER_INFEASIBLE"


def test_backtest_outputs_advisory_only():
    dec = json.loads((OUTS / "p269_sample_output.json").read_text())
    assert dec["emits_findings"] is False
    for d in dec["decisions"]:
        assert d["severity"] is None and d["status"] == "ADVISORY_TRIAGE_DECISION"
        assert d["outcome"] in ALL_OUT
        for f in FORBIDDEN_FIELDS:
            assert d[f] is False
    g = json.loads((OUTS / "triage_guard_report.json").read_text())
    assert g["result"] == "PASS" and g["guard_violations"] == 0


def test_malformed_input_fails_closed(tmp_path):
    r, out = _run([{"locus": "x"}], tmp_path)  # missing id
    assert r.returncode == 2 and not out.exists()


def test_frozen_infrastructure_unchanged():
    for rel, h in FROZEN.items():
        assert _sha16(ROOT / rel) == h, f"{rel} changed (P260/P262/P264/P267 must be unchanged)"


def test_forbidden_files_byte_identical():
    for rel, h in FORBIDDEN_FILES.items():
        assert _sha16(ROOT / rel).startswith(h), f"forbidden file {rel} changed"
