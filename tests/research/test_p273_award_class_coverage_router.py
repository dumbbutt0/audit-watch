"""P273 — award-class coverage router. Guard + behavior tests (research-only, advisory, default-off)."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/research/award_class_coverage_router.py"
CFG = ROOT / "config/research_award_class_coverage_router.json"
DOCS = ROOT / "documentation/research/assisted_mode/p273_award_class_coverage"
OUTS = DOCS / "outputs"
DOC_FILES = ("SETUP.md", "FAILURE_FORENSICS.md", "COVERAGE_ROUTER_SPEC.md", "IMPLEMENTATION_NOTES.md",
             "BACKTEST_RESULTS.md", "INTEGRATION_PROPOSAL.md", "LIMITATIONS.md", "VERDICT.md")
VERDICTS = ("A — COVERAGE_ROUTER_READY_FOR_FRESH_FULL_PATH_TEST", "B — COVERAGE_ROUTER_PROMISING_NEEDS_REFINEMENT",
            "C — COVERAGE_ROUTER_NOT_USEFUL", "D — ABORTED_CONSTRAINT_VIOLATION")
SELECT = ("COVERAGE_SELECT", "COVERAGE_SELECT_HEAVY")
ALL_LABELS = SELECT + ("COVERAGE_CONTROL", "COVERAGE_DEFER_LOW_SIGNAL", "COVERAGE_DEFER_DUPLICATE_CLASS",
                       "COVERAGE_DEFER_INFEASIBLE", "COVERAGE_UNKNOWN")
PROMO_FALSE = ("reportable", "submission_ready", "concluded", "emits_finding", "production_routing")
FROZEN = {
    "scripts/research/locus_shape_prioritizer.py": "d6b494bc3c0cc746",
    "scripts/research/recall_first_shape_sweep.py": "a48336275cb65a4f",
    "scripts/research/recall_first_harness.py": "be428a1202c45b1a",
    "scripts/research/mechanism_pairwise_selector.py": "b0623b8c88752059",
    "scripts/research/impact_first_poc_triage.py": "63c88d02d2c7eefa",
}
FORBIDDEN = {
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


def _classes(decisions, label_set):
    return {d["award_class"] for d in decisions if d["label"] in label_set}


def test_files_docs_verdict():
    assert SCRIPT.exists() and CFG.exists()
    for d in DOC_FILES:
        assert (DOCS / d).exists(), f"missing {d}"
    assert any(v in (DOCS / "VERDICT.md").read_text() for v in VERDICTS)


def test_config_taxonomy_and_rules():
    c = json.loads(CFG.read_text())
    assert c["is_gate"] is False and c["research_only"] is True and c["emits_findings"] is False
    # 11-class taxonomy present incl. the non-accounting classes
    for cls in ("ACCOUNTING_LIQUIDATION_BAD_DEBT", "ACCESS_CONTROL_AUTHORIZATION", "ORDER_VALIDATION",
                "FRONT_RUNNING_MEV", "DOS_LIVENESS"):
        assert cls in c["class_signals"], f"missing class {cls}"
    # anti-monoculture rule present (guard classes configured)
    assert set(["ACCESS_CONTROL_AUTHORIZATION", "ORDER_VALIDATION", "FRONT_RUNNING_MEV", "DOS_LIVENESS"]).issubset(
        set(c["monoculture_guard_classes"]))


def test_module_unwired_no_answer_key():
    src = SCRIPT.read_text()
    imports = [ln for ln in src.splitlines() if ln.strip().startswith(("import ", "from "))]
    for f in ("run_pipeline", "agent_policy", "dashboard_sync", "confirm_gate", "record_outcome"):
        assert not any(f in ln for ln in imports), f"imports {f}"
    for f in ("ground_truth", "answer_key"):
        assert f not in src


def test_init_fixture_routes_order_or_access_class(tmp_path):
    """The headline: an order/access/front-run candidate is routed alongside accounting (monoculture broken)."""
    cands = [
        {"id": "acct1", "locus": "InitCore liquidate health debt", "signals": ["liquidat", "health", "debt"],
         "recall_delta": True, "impact_supported": True},
        {"id": "acct2", "locus": "collateral credit borrow", "signals": ["collateral", "borrow"],
         "recall_delta": True, "impact_supported": True},
        {"id": "order1", "locus": "MarginTradingHook fillOrder", "signals": ["fill", "order", "limitprice"],
         "recall_delta": True, "impact_supported": True},
        {"id": "fr1", "locus": "coreCallback", "signals": ["callback", "order", "public"],
         "recall_delta": True, "impact_supported": True},
    ]
    r, out = _run(cands, tmp_path)
    assert r.returncode == 0, r.stderr
    sel = _classes(json.loads(out.read_text())["decisions"], SELECT)
    assert sel & {"ORDER_VALIDATION", "FRONT_RUNNING_MEV", "ACCESS_CONTROL_AUTHORIZATION"}, \
        "no order/access/front-run class routed (monoculture not broken)"


def test_wise_fixture_preserves_accounting(tmp_path):
    cands = [
        {"id": "bd", "locus": "FeeManager bad_debt position global", "signals": ["bad_debt", "position", "global"],
         "recall_delta": True, "impact_supported": True},
        {"id": "share", "locus": "share mint precision", "signals": ["share", "mint", "precision"],
         "recall_delta": True, "impact_supported": True},
    ]
    r, out = _run(cands, tmp_path)
    assert "ACCOUNTING_LIQUIDATION_BAD_DEBT" in _classes(json.loads(out.read_text())["decisions"], SELECT)


def test_phi_fixture_routes_dos_liveness(tmp_path):
    cands = [
        {"id": "gasdos", "locus": "distribute enumeration gas dos", "signals": ["distribution", "gas", "enumerable"],
         "recall_delta": True, "impact_supported": True},
        {"id": "skim", "locus": "fee reward", "signals": ["fee", "reward"], "recall_delta": False,
         "impact_supported": True},
    ]
    r, out = _run(cands, tmp_path)
    assert "DOS_LIVENESS" in _classes(json.loads(out.read_text())["decisions"], SELECT)


def test_negative_control_gated_admin_not_routed_on_label(tmp_path):
    cands = [
        {"id": "gated", "locus": "Config setOwner onlyOwner admin", "signals": ["onlyowner", "admin", "set", "owner"],
         "recall_delta": False, "impact_supported": False},  # unsupported -> anti-drama must block
        {"id": "real", "locus": "borrow debt", "signals": ["borrow", "debt"], "recall_delta": True,
         "impact_supported": True},
    ]
    r, out = _run(cands, tmp_path)
    d = {x["id"]: x for x in json.loads(out.read_text())["decisions"]}
    assert d["gated"]["label"] not in SELECT, "routed an unsupported gated-admin on its access-control label"


def test_advisory_only_and_malformed_fails_closed(tmp_path):
    dec = json.loads((OUTS / "p273_sample_output.json").read_text())
    assert dec["emits_findings"] is False
    for d in dec["decisions"]:
        assert d["severity"] is None and d["status"] == "ADVISORY_COVERAGE_DECISION" and d["label"] in ALL_LABELS
        for f in PROMO_FALSE:
            assert d[f] is False
    g = json.loads((OUTS / "coverage_guard_report.json").read_text())
    assert g["result"] == "PASS"
    r, out = _run([{"locus": "x"}], tmp_path)  # missing id
    assert r.returncode == 2 and not out.exists()


def test_frozen_and_forbidden_unchanged():
    for rel, h in FROZEN.items():
        assert _sha16(ROOT / rel) == h, f"{rel} changed"
    for rel, h in FORBIDDEN.items():
        assert _sha16(ROOT / rel).startswith(h), f"forbidden {rel} changed"
