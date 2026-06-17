"""P279 — completion-stage evidence deriver. Behavior + guard tests (research-only, advisory)."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DERIVER = ROOT / "scripts/research/completion_evidence_deriver.py"
GATE = ROOT / "scripts/research/poc_readiness_evidence_gate.py"
DCFG = ROOT / "config/research_completion_evidence_deriver.json"
DOCS = ROOT / "documentation/research/assisted_mode/p279_completion_evidence_auto_derivation"
OUTS = DOCS / "outputs"

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
DOC_FILES = ("SETUP.md", "DERIVER_DESIGN.md", "IMPLEMENTATION_NOTES.md", "CORPUS_DERIVATION_RESULTS.md",
             "EVIDENCE_AUDIT.md", "FP_AND_NOISE_REPORT.md", "LIMITATIONS.md", "VERDICT.md", "ROLLBACK_PLAN.md")
VERDICTS = ("A — EVIDENCE_DERIVER_READY_FOR_POC_SWEEP", "B — EVIDENCE_DERIVER_PROMISING_NEEDS_REFINEMENT",
            "C — EVIDENCE_DERIVER_TOO_NOISY", "D — ABORTED_CONSTRAINT_VIOLATION")
PROMO_FALSE = ("reportable", "submission_ready", "concluded", "emits_finding", "production_routing")


def _sha16(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def _item(contract, name, **kw):
    d = {"kind": "function", "contract": contract, "name": name, "signature": kw.get("signature", f"function {name}()"),
         "visibility": kw.get("visibility", "external"), "mutability": kw.get("mutability", "nonpayable"),
         "modifiers": kw.get("modifiers", []), "external_calls": kw.get("external_calls", False),
         "has_loop": kw.get("has_loop", False), "in_tainted_sink": False, "tags": kw.get("tags", []),
         "source_span": {"start_line": 1, "end_line": 9}}
    return d


def _run(tmp_path, items, packages):
    man = tmp_path / "m.json"; man.write_text(json.dumps({"items": items}))
    pk = tmp_path / "p.json"; pk.write_text(json.dumps({"packages": packages}))
    der = tmp_path / "d.json"
    if der.exists():
        der.unlink()
    r = subprocess.run([sys.executable, str(DERIVER), "--manifest", str(man), "--packages", str(pk),
                        "--out", str(der), "--quiet"], capture_output=True, text=True)
    derived = json.loads(der.read_text()) if der.exists() else None
    gate_out = None
    if derived is not None:
        go = tmp_path / "g.json"
        subprocess.run([sys.executable, str(GATE), "--packages", str(der), "--out", str(go), "--quiet"],
                       capture_output=True, text=True)
        gate_out = json.loads(go.read_text()) if go.exists() else None
    return r, derived, gate_out


def _pkg(cid, cls, cf, **extra):
    base = {"candidate_id": cid, "award_class": cls, "contract_function": cf, "mechanism_hypothesis": "m",
            "root_cause": "rc", "runner_up_mechanism": "ru"}
    base.update(extra)
    return base


def _conf(derived, cid, field):
    p = next(p for p in derived["packages"] if p["candidate_id"] == cid)
    return p["derived_confidence"][field]["confidence"]


def _status(gate, cid):
    return next(d for d in gate["decisions"] if d["candidate_id"] == cid)["status"]


def test_access_no_modifier_config_derives_high_and_ready(tmp_path):
    items = [_item("Cfg", "setFee", visibility="external", modifiers=[], tags=["config"])]
    pk = [_pkg("a", "ACCESS_CONTROL_AUTHORIZATION", "Cfg.setFee")]
    r, d, g = _run(tmp_path, items, pk)
    assert r.returncode == 0
    assert _conf(d, "a", "attacker_path") == "HIGH"
    assert _status(g, "a") == "READY_FOR_POC_INTENT"


def test_auth_guarded_blocks_ready(tmp_path):
    items = [_item("Cfg", "setFee", modifiers=["onlyOwner"], tags=["config"])]
    r, d, g = _run(tmp_path, items, [_pkg("a", "ACCESS_CONTROL_AUTHORIZATION", "Cfg.setFee")])
    assert _conf(d, "a", "attacker_path") == "LOW"
    assert _status(g, "a") != "READY_FOR_POC_INTENT"


def test_dos_has_loop_derives_liveness(tmp_path):
    items = [_item("Q", "distribute", has_loop=True, tags=["distribution"])]
    r, d, g = _run(tmp_path, items, [_pkg("a", "DOS_LIVENESS", "Q.distribute")])
    assert _conf(d, "a", "attacker_path") == "HIGH"
    p = next(p for p in d["packages"] if p["candidate_id"] == "a")
    assert "progress" in p["invariant_expected"].lower() or "revert" in p["invariant_broken"].lower()


def test_math_share_impact_delta_derived_but_attacker_low(tmp_path):
    items = [_item("Pool", "mint", tags=["share", "token"], signature="function mint(uint256 shares)")]
    r, d, g = _run(tmp_path, items, [_pkg("a", "SHARE_ROUNDING_PRECISION", "Pool.mint")])
    # impact_delta derivable, but value-flow anomaly not manifest-visible -> attacker_path LOW -> not READY
    assert _conf(d, "a", "impact_delta") in ("HIGH", "MEDIUM")
    assert _conf(d, "a", "attacker_path") == "LOW"
    assert _status(g, "a") == "NEEDS_MORE_EVIDENCE"


def test_accounting_value_flow_assumption_blocks_ready(tmp_path):
    items = [_item("V", "liquidate", tags=["accounting"])]
    r, d, g = _run(tmp_path, items, [_pkg("a", "ACCOUNTING_LIQUIDATION_BAD_DEBT", "V.liquidate")])
    assert _conf(d, "a", "attacker_path") == "LOW"  # core value-flow assumption unresolved
    assert _status(g, "a") == "NEEDS_MORE_EVIDENCE"


def test_external_calls_high(tmp_path):
    items = [_item("M", "settle", external_calls=True, tags=["token"])]
    r, d, g = _run(tmp_path, items, [_pkg("a", "EXTERNAL_INTEGRATION", "M.settle")])
    assert _conf(d, "a", "attacker_path") == "HIGH"


def test_missing_manifest_item_blocks_high(tmp_path):
    # package references a function with no manifest item -> all LOW, never READY
    r, d, g = _run(tmp_path, [_item("Other", "x")], [_pkg("a", "ACCESS_CONTROL_AUTHORIZATION", "Ghost.fn")])
    assert _conf(d, "a", "attacker_path") == "LOW"
    assert _status(g, "a") != "READY_FOR_POC_INTENT"


def test_forbidden_award_field_fails_closed(tmp_path):
    items = [_item("Cfg", "setFee", tags=["config"])]
    pk = [_pkg("a", "ACCESS_CONTROL_AUTHORIZATION", "Cfg.setFee", award_title="oracle price manipulation")]
    r, d, g = _run(tmp_path, items, pk)
    assert r.returncode == 2 and d is None  # fail-closed; no derived output


def test_advisory_contract_no_leakage(tmp_path):
    items = [_item("Cfg", "setFee", tags=["config"])]
    r, d, g = _run(tmp_path, items, [_pkg("a", "ACCESS_CONTROL_AUTHORIZATION", "Cfg.setFee")])
    p = d["packages"][0]
    assert p["severity"] is None
    for f in PROMO_FALSE:
        assert p[f] is False
    assert d["emits_findings"] is False and g["severe_concluded_or_reportable_fp"] == 0


def test_corpus_outputs_ready_increased_and_no_severe_fp():
    m = json.loads((OUTS / "before_after_metrics.json").read_text())
    assert m["before"]["ready_for_poc_intent"] == 0
    assert m["after"]["ready_for_poc_intent"] > 0
    assert m["after"]["severe_concluded_or_reportable_fp"] == 0
    audit = json.loads((OUTS / "sample_audit.json").read_text())
    ready = [a for a in audit["audited"] if a["status"] == "READY_FOR_POC_INTENT"]
    assert ready and all(a["source_backed"] for a in ready)
    assert not any(a["placeholder_leaked"] for a in audit["audited"])


def test_config_safe():
    c = json.loads(DCFG.read_text())
    assert c["is_gate"] is False and c["research_only"] is True and c["emits_findings"] is False
    assert "forbidden_input_fields" in c and "auth_modifier_patterns" in c


def test_frozen_and_forbidden_byte_identical():
    for rel, h in FROZEN.items():
        assert _sha16(ROOT / rel) == h, f"frozen changed: {rel}"
    for rel, h in FORBIDDEN.items():
        assert _sha16(ROOT / rel).startswith(h), f"forbidden changed: {rel}"


def test_docs_and_verdict():
    for d in DOC_FILES:
        assert (DOCS / d).exists(), f"missing {d}"
    assert any(v in (DOCS / "VERDICT.md").read_text() for v in VERDICTS)


