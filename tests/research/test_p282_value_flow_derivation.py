"""P282 — D3 value-flow evidence derivation. Behavior + guard tests (research-only, advisory)."""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DERIVER = ROOT / "scripts/research/completion_evidence_deriver.py"
GATE = ROOT / "scripts/research/poc_readiness_evidence_gate.py"
EXTRACT = ROOT / "scripts/research/source_span_guard_extractor.py"
sys.path.insert(0, str(ROOT / "scripts/research"))
import source_span_guard_extractor as ssx  # noqa: E402

DOCS = ROOT / "documentation/research/assisted_mode/p282_value_flow_evidence_derivation"
OUTS = DOCS / "outputs"
FROZEN = {
    "scripts/research/locus_shape_prioritizer.py": "d6b494bc3c0cc746",
    "scripts/research/recall_first_shape_sweep.py": "a48336275cb65a4f",
    "scripts/research/recall_first_harness.py": "be428a1202c45b1a",
    "scripts/research/mechanism_pairwise_selector.py": "b0623b8c88752059",
    "scripts/research/impact_first_poc_triage.py": "63c88d02d2c7eefa",
    "scripts/research/award_class_coverage_router.py": "6debb753b45f1833",
    "config/research_award_class_coverage_router.json": "91f9deac7867af62",
    "documentation/research/assisted_mode/p271_lending_runtime_scaffold/"
    "LENDING_COMPLETION_CHECKLIST.md": "2929a2154a88104e",
}
FORBIDDEN = {
    "scripts/dashboard_sync.py": "c1af70e1", "prompts/deep_trace.md": "c095c426",
    "scripts/min_confirm_gate.py": "2a15169a", "scripts/confirm_gate.py": "afc481c9",
    "scripts/validate_p208_l3_readiness.py": "ae55eb80",
}
DOC_FILES = ("SETUP.md", "VALUE_FLOW_DERIVER_DESIGN.md", "IMPLEMENTATION_NOTES.md", "VALUE_FLOW_REMAP_RESULTS.md",
             "VALUE_FLOW_EVIDENCE_AUDIT.md", "VALUE_FLOW_REPAIR_BACKLOG.md", "LIMITATIONS.md", "VERDICT.md",
             "ROLLBACK_PLAN.md")
VERDICTS = ("A — VALUE_FLOW_DERIVER_READY_FOR_POC_SWEEP", "B — VALUE_FLOW_DERIVER_PROMISING_NEEDS_REFINEMENT",
            "C — VALUE_FLOW_DERIVER_TOO_NOISY", "D — ABORTED_CONSTRAINT_VIOLATION")
VALUE = "ACCOUNTING_LIQUIDATION_BAD_DEBT"


def _sha16(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


# ---- D3 extractor unit tests ----
def test_d3_detects_state_write():
    d = ssx.detect("function f() external { balances[msg.sender] += amount; }")
    assert d["state_write"] is True


def test_d3_detects_asset_transfer():
    d = ssx.detect("function f() external { token.safeTransfer(to, amt); }")
    assert d["asset_move"] is True


def test_d3_detects_share_math_and_div_before_mul():
    d = ssx.detect("function f() external { y = (a + b) / totalShares * shares; }")
    assert d["value_flow_detected"] is True and d["value_anomaly_div_before_mul"] is True


def test_d3_detects_debt_collateral_terms():
    d = ssx.detect("function f() external { debt[user] = collateral[user] - repay; }")
    assert any(t in d["value_markers"] for t in ("debt", "collateral"))


def test_d3_detects_oracle_terms():
    d = ssx.detect("function f() external { uint p = oracle.latestRoundData(); price = p; }")
    assert any(t in d["value_markers"] for t in ("oracle", "price", "latestrounddata"))


def test_wrapper_delegation_flagged_out_of_span():
    d = ssx.detect("function f() external returns (uint) { return _claimFees(); }")
    assert d["value_flow_out_of_span"] is True and d["value_flow_detected"] is False


def test_d1_gap_either_side_msgsender():
    d = ssx.detect("function f() external { require(actor != msg.sender); x = 1; }")
    assert d["inline_guard_detected"] is True


def test_d1_gap_modifier_auth():
    d = ssx.detect("function f() external onlyManager nonReentrant { x = 1; }")
    assert d["inline_guard_detected"] is True


# ---- gate behavior ----
def _gate_value_class(tmp, body):
    src = Path(tmp) / "C.sol"; src.write_text(body)
    man = {"items": [{"kind": "function", "contract": "C", "name": "f", "signature": "function f()",
                      "visibility": "external", "mutability": "nonpayable", "modifiers": [], "external_calls": False,
                      "has_loop": False, "tags": ["accounting"], "file": str(src),
                      "source_span": {"start_line": 1, "end_line": len(body.splitlines())}}]}
    pkg = {"candidate_id": "c1", "award_class": VALUE, "contract_function": "C.f", "mechanism_hypothesis": "m",
           "root_cause": "rc", "runner_up_mechanism": "ru"}
    mp = Path(tmp) / "m.json"; mp.write_text(json.dumps(man))
    pp = Path(tmp) / "p.json"; pp.write_text(json.dumps({"packages": [pkg]}))
    dp = Path(tmp) / "d.json"
    subprocess.run([sys.executable, str(DERIVER), "--manifest", str(mp), "--packages", str(pp), "--out", str(dp),
                    "--quiet"], capture_output=True, text=True)
    gp = Path(tmp) / "g.json"
    subprocess.run([sys.executable, str(GATE), "--packages", str(dp), "--out", str(gp), "--quiet"],
                   capture_output=True, text=True)
    return json.loads(gp.read_text())["decisions"][0]


def test_generic_transfer_alone_cannot_create_ready():
    with tempfile.TemporaryDirectory() as t:
        d = _gate_value_class(t, "function f() external { token.transfer(to, amt); }")  # value move, no anomaly
        assert d["status"] == "NEEDS_VALUE_FLOW_EVIDENCE"
        assert d["gate_evidence_summary"]["value_flow_subreason"] == "value_flow_present_but_no_anomaly"


def test_inline_guard_still_refutes():
    with tempfile.TemporaryDirectory() as t:
        d = _gate_value_class(t, "function f() external { require(msg.sender == owner); debt[x]=1; }")
        assert d["status"] == "INLINE_GUARD_REFUTED"


def test_missing_source_span_blocks():
    with tempfile.TemporaryDirectory() as t:
        man = {"items": [{"kind": "function", "contract": "C", "name": "f", "visibility": "external",
                          "mutability": "nonpayable", "modifiers": [], "tags": ["accounting"]}]}  # no file/span
        pkg = {"candidate_id": "c1", "award_class": VALUE, "contract_function": "C.f", "mechanism_hypothesis": "m",
               "root_cause": "rc", "runner_up_mechanism": "ru"}
        mp = Path(t) / "m.json"; mp.write_text(json.dumps(man))
        pp = Path(t) / "p.json"; pp.write_text(json.dumps({"packages": [pkg]}))
        dp = Path(t) / "d.json"
        subprocess.run([sys.executable, str(DERIVER), "--manifest", str(mp), "--packages", str(pp), "--out", str(dp),
                        "--quiet"], capture_output=True, text=True)
        # no body -> P279 fallback path (not a D3 NEEDS_SOURCE_SPAN, but never a value-flow READY)
        gp = Path(t) / "g.json"
        subprocess.run([sys.executable, str(GATE), "--packages", str(dp), "--out", str(gp), "--quiet"],
                       capture_output=True, text=True)
        assert json.loads(gp.read_text())["decisions"][0]["status"] != "READY_FOR_POC_INTENT"


# ---- corpus regressions ----
def test_l2governor_remains_ready():
    found = False
    for r in OUTS.glob("*/readiness.json"):
        for d in json.loads(r.read_text())["decisions"]:
            if d["candidate_id"] == "coverage_manifest:L2Governor:execute:20":
                found = True
                assert d["status"] == "READY_FOR_POC_INTENT"
    assert found


def test_transform_and_cancelpodlisting_not_ready():
    seen = {}
    for r in OUTS.glob("*/readiness.json"):
        for d in json.loads(r.read_text())["decisions"]:
            seen[d["candidate_id"]] = d["status"]
    assert seen.get("coverage_manifest:V3Vault:transform:9") == "INLINE_GUARD_REFUTED"
    assert seen.get("coverage_manifest:IBeanstalk:cancelPodListing:0") == "NEEDS_SOURCE_SPAN"


def test_no_severity_reportable_leakage():
    for r in OUTS.glob("*/readiness.json"):
        for d in json.loads(r.read_text())["decisions"]:
            assert d["severity"] is None
            for f in ("reportable", "submission_ready", "concluded", "emits_finding", "production_routing"):
                assert d[f] is False


def test_remap_severe_fp_zero_and_metrics():
    m = json.loads((OUTS / "remap_metrics.json").read_text())
    assert m["severe_concluded_or_reportable_fp"] == 0
    assert m["newly_lifted_to_ready"] == 0
    assert m["after_P282"]["READY_FOR_POC_INTENT"] == 1


def test_frozen_and_forbidden_byte_identical():
    for rel, h in FROZEN.items():
        assert _sha16(ROOT / rel) == h, f"frozen changed: {rel}"
    for rel, h in FORBIDDEN.items():
        assert _sha16(ROOT / rel).startswith(h), f"forbidden changed: {rel}"


def test_docs_and_verdict():
    for d in DOC_FILES:
        assert (DOCS / d).exists(), f"missing {d}"
    assert any(v in (DOCS / "VERDICT.md").read_text() for v in VERDICTS)


