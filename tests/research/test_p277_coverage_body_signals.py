"""P277 — R1 coverage-class body-signal repair. Behavior + guard tests (research-only, advisory).

Verifies body-derived class signals route a class the LOCUS NAME misses, while: never overriding a confident locus
class, holding anti-drama (impact_supported), preserving pre-P277 behavior when no body is present, and never reading
award-text fields. Plus the advisory contract + fail-closed + frozen/forbidden integrity.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/research/award_class_coverage_router.py"
CFG = ROOT / "config/research_award_class_coverage_router.json"
DOCS = ROOT / "documentation/research/assisted_mode/p277_coverage_body_signal_repair"
OUTS = DOCS / "outputs"
SELECT = ("COVERAGE_SELECT", "COVERAGE_SELECT_HEAVY")
PROMO_FALSE = ("reportable", "submission_ready", "concluded", "emits_finding", "production_routing")
# these stay byte-identical (P277 only edits the coverage router + its config)
FROZEN = {
    "scripts/research/locus_shape_prioritizer.py": "d6b494bc3c0cc746",
    "scripts/research/recall_first_shape_sweep.py": "a48336275cb65a4f",
    "scripts/research/recall_first_harness.py": "be428a1202c45b1a",
    "scripts/research/mechanism_pairwise_selector.py": "b0623b8c88752059",
    "scripts/research/impact_first_poc_triage.py": "63c88d02d2c7eefa",
    "scripts/research/p276_corpus_replay.py": None,  # presence only (its hash is not pinned; must be unchanged-ish)
    "documentation/research/assisted_mode/p271_lending_runtime_scaffold/"
    "LENDING_COMPLETION_CHECKLIST.md": "2929a2154a88104e",
}
FORBIDDEN = {
    "scripts/dashboard_sync.py": "c1af70e1", "prompts/deep_trace.md": "c095c426",
    "scripts/min_confirm_gate.py": "2a15169a", "scripts/confirm_gate.py": "afc481c9",
    "scripts/validate_p208_l3_readiness.py": "ae55eb80",
}
DOC_FILES = ("SETUP.md", "BODY_SIGNAL_DESIGN.md", "IMPLEMENTATION_NOTES.md", "REPAIR_METRICS.md", "FP_REPORT.md",
             "LIMITATIONS.md", "VERDICT.md", "ROLLBACK_PLAN.md")
VERDICTS = ("A — BODY_SIGNAL_REPAIR_READY_FOR_SUPERVISED_SWEEP", "B — BODY_SIGNAL_REPAIR_PROMISING_NEEDS_REFINEMENT",
            "C — BODY_SIGNAL_REPAIR_NOT_USEFUL", "D — ABORTED_CONSTRAINT_VIOLATION")


def _sha16(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


_RC = [0]


def _route(cands, tmp_path):
    _RC[0] += 1
    inp = tmp_path / f"c{_RC[0]}.json"; inp.write_text(json.dumps({"candidates": cands}))
    out = tmp_path / f"o{_RC[0]}.json"
    if out.exists():
        out.unlink()
    r = subprocess.run([sys.executable, str(SCRIPT), "--candidates", str(inp), "--out", str(out), "--quiet"],
                       capture_output=True, text=True)
    return r, (json.loads(out.read_text()) if out.exists() else None)


def _dec(out, cid):
    return next(d for d in out["decisions"] if d["id"] == cid)


def test_oracle_signal_only_in_body_routes_oracle(tmp_path):
    # locus name carries NO class keyword; oracle signal lives only in the mechanism body
    cands = [{"id": "x", "locus": "Vault:refresh", "contract": "Vault", "function": "refresh",
              "signals": [], "impact_supported": True,
              "mechanisms": [{"mechanism_summary": "a stale price from the oracle feed lets exchange rate diverge"}]}]
    r, out = _route(cands, tmp_path)
    assert r.returncode == 0, r.stderr
    d = _dec(out, "x")
    assert d["award_class"] == "ORACLE_PRICING", d
    assert d["label"] in SELECT and d["body_changed_decision"] is True


def test_external_signal_only_in_body_routes_external(tmp_path):
    cands = [{"id": "x", "locus": "Manager:settle", "contract": "Manager", "function": "settle",
              "signals": [], "impact_supported": True,
              "mechanisms": [{"attacker_action": "the external adapter callback to a third-party bridge is trusted"}]}]
    r, out = _route(cands, tmp_path)
    assert _dec(out, "x")["award_class"] == "EXTERNAL_INTEGRATION"


def test_order_or_frontrun_signal_only_in_body_routes(tmp_path):
    cands = [{"id": "x", "locus": "Book:process", "contract": "Book", "function": "process",
              "signals": [], "impact_supported": True,
              "mechanisms": [{"mechanism_summary": "a maker order can be filled before cancel via slippage bypass"}]}]
    r, out = _route(cands, tmp_path)
    assert _dec(out, "x")["award_class"] in ("ORDER_VALIDATION", "FRONT_RUNNING_MEV")


def test_high_drama_body_without_impact_support_deferred(tmp_path):
    cands = [{"id": "drama", "locus": "X:f", "contract": "X", "function": "f", "signals": [],
              "impact_supported": False,
              "mechanisms": [{"mechanism_summary": "oracle price manipulation drains all funds"}]},
             {"id": "real", "locus": "Pool:liquidate", "contract": "Pool", "function": "liquidate",
              "signals": ["liquidat", "debt"], "impact_supported": True}]
    r, out = _route(cands, tmp_path)
    assert _dec(out, "drama")["label"] not in SELECT  # anti-drama held


def test_locus_only_accounting_still_routes_backcompat(tmp_path):
    # no mechanism body at all -> pre-P277 behavior
    cands = [{"id": "a", "locus": "Pool:liquidate", "contract": "Pool", "function": "liquidate",
              "signals": ["liquidat", "collateral", "debt"], "impact_supported": True}]
    r, out = _route(cands, tmp_path)
    d = _dec(out, "a")
    assert d["award_class"] == "ACCOUNTING_LIQUIDATION_BAD_DEBT" and d["label"] in SELECT
    assert d["body_changed_decision"] is False


def test_missing_body_does_not_crash_and_preserves_class(tmp_path):
    cands = [{"id": "a", "locus": "Order:fill", "contract": "Order", "function": "fill", "signals": ["order", "fill"],
              "impact_supported": True}]  # no 'mechanisms' key
    r, out = _route(cands, tmp_path)
    assert r.returncode == 0
    assert _dec(out, "a")["award_class"] == "ORDER_VALIDATION"


def test_body_does_not_override_confident_locus(tmp_path):
    # locus clearly ACCESS; body mentions oracle -> must KEEP ACCESS (body never overrides a confident locus class)
    cands = [{"id": "a", "locus": "Config:setOwner", "contract": "Config", "function": "setOwner",
              "signals": ["onlyowner", "admin", "owner"], "impact_supported": True,
              "mechanisms": [{"mechanism_summary": "incidentally mentions oracle price feed staleness"}]}]
    r, out = _route(cands, tmp_path)
    d = _dec(out, "a")
    assert d["award_class"] == "ACCESS_CONTROL_AUTHORIZATION" and d["body_changed_decision"] is False


def test_award_text_field_not_used_as_signal(tmp_path):
    # an award-text-ish field with oracle words must NOT route ORACLE (not in allowlist; on denylist)
    cands = [{"id": "a", "locus": "Vault:deposit", "contract": "Vault", "function": "deposit",
              "signals": [], "impact_supported": True,
              "award_title": "oracle price feed manipulation stale price",
              "title": "oracle staleness", "root_cause": "oracle price feed stale"}]
    r, out = _route(cands, tmp_path)
    assert _dec(out, "a")["award_class"] != "ORACLE_PRICING"


def test_advisory_contract_and_fail_closed(tmp_path):
    cands = [{"id": "a", "locus": "Pool:liquidate", "contract": "Pool", "function": "liquidate",
              "signals": ["liquidat"], "impact_supported": True}]
    r, out = _route(cands, tmp_path)
    assert out["guard_violations"] == 0 and out["emits_findings"] is False
    for d in out["decisions"]:
        assert d["severity"] is None and d["status"] == "ADVISORY_COVERAGE_DECISION"
        for f in PROMO_FALSE:
            assert d[f] is False
    # malformed (missing id) fails closed, no output
    r2, out2 = _route([{"locus": "x"}], tmp_path)
    assert r2.returncode == 2 and out2 is None


def test_config_has_body_signal_keys():
    c = json.loads(CFG.read_text())
    assert "body_signal_fields" in c and "body_signal_weight" in c and "body_field_denylist" in c
    assert c["is_gate"] is False and c["research_only"] is True and c["emits_findings"] is False


def test_frozen_and_forbidden_byte_identical():
    for rel, h in FROZEN.items():
        p = ROOT / rel
        assert p.exists(), f"missing {rel}"
        if h:
            assert _sha16(p) == h, f"frozen changed: {rel}"
    for rel, h in FORBIDDEN.items():
        assert _sha16(ROOT / rel).startswith(h), f"forbidden changed: {rel}"


def test_repair_metrics_and_verdict_present():
    for d in DOC_FILES:
        assert (DOCS / d).exists(), f"missing {d}"
    assert any(v in (DOCS / "VERDICT.md").read_text() for v in VERDICTS)
    before = json.loads((OUTS / "metrics_BEFORE.json").read_text())["corpus"]
    after = json.loads((OUTS / "metrics_AFTER.json").read_text())["corpus"]
    # class_routed improved and severe FP stayed 0
    assert after["class_routed_pct"] >= before["class_routed_pct"]
    assert json.loads((OUTS / "metrics_AFTER.json").read_text())[
        "false_positive_report"]["severe_concluded_or_reportable_fp"] == 0
