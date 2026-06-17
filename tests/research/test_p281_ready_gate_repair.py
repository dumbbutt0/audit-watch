"""P281 — READY gate repair (inline guards / state machines / value-flow / source spans). Guard + behavior tests."""
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
GCFG = ROOT / "config/research_poc_readiness_gate.json"
DOCS = ROOT / "documentation/research/assisted_mode/p281_ready_gate_repair"
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
DOC_FILES = ("SETUP.md", "READY_GATE_REPAIR_DESIGN.md", "IMPLEMENTATION_NOTES.md", "P280_REGRESSION.md",
             "CORPUS_REMAP.md", "POC_REVALIDATION.md", "READY_NOISE_REPORT.md", "LIMITATIONS.md", "VERDICT.md",
             "ROLLBACK_PLAN.md")
VERDICTS = ("A — READY_GATE_REPAIRED_FOR_POC_SWEEP", "B — READY_GATE_PROMISING_NEEDS_MORE_REFINEMENT",
            "C — READY_GATE_TOO_STRICT_BLOCKS_USEFUL_CANDIDATES", "D — READY_GATE_STILL_TOO_NOISY",
            "E — ABORTED_CONSTRAINT_VIOLATION")


def _sha16(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def _write(tmp, name, text):
    p = Path(tmp) / name
    p.write_text(text)
    return p


def _gate_one(tmp, award_class, body=None, is_decl=False, item_file=None, span=None, extra=None):
    """Build a manifest+package for one synthetic candidate (with a real on-disk body) and run deriver->gate."""
    if body is not None and not is_decl:
        src = _write(tmp, "C.sol", body)
        item_file = str(src)
        span = span or [1, len(body.splitlines())]
    man = {"items": [{"kind": "function", "contract": "C", "name": "f", "signature": "function f()",
                      "visibility": "external", "mutability": "nonpayable", "modifiers": [], "external_calls": False,
                      "has_loop": False, "tags": [], "file": item_file or "", "source_span":
                      {"start_line": (span or [1, 1])[0], "end_line": (span or [1, 1])[1]} if (item_file) else {}}]}
    pkg = {"candidate_id": "c1", "award_class": award_class, "contract_function": "C.f",
           "mechanism_hypothesis": "m", "root_cause": "rc", "runner_up_mechanism": "ru"}
    if extra:
        pkg.update(extra)
    mp = _write(tmp, "m.json", json.dumps(man))
    pp = _write(tmp, "p.json", json.dumps({"packages": [pkg]}))
    dp = Path(tmp) / "d.json"
    subprocess.run([sys.executable, str(DERIVER), "--manifest", str(mp), "--packages", str(pp),
                    "--out", str(dp), "--quiet"], capture_output=True, text=True)
    gp = Path(tmp) / "g.json"
    subprocess.run([sys.executable, str(GATE), "--packages", str(dp), "--out", str(gp), "--quiet"],
                   capture_output=True, text=True)
    return json.loads(dp.read_text())["packages"][0], json.loads(gp.read_text())["decisions"][0]


ACCESS = "ACCESS_CONTROL_AUTHORIZATION"
STATE = "STATE_MACHINE_LIFECYCLE"
VALUE = "ACCOUNTING_LIQUIDATION_BAD_DEBT"
GUARD_BODY = "function f() external {\n  require(msg.sender == owner, \"NO\");\n  x = 1;\n}"


def test_inline_require_msgsender_blocks_ready():
    with tempfile.TemporaryDirectory() as t:
        _, d = _gate_one(t, ACCESS, body=GUARD_BODY)
        assert d["status"] == "INLINE_GUARD_REFUTED"


def test_if_msgsender_revert_blocks_ready():
    body = "function f() external {\n  if (msg.sender != owner) revert Unauthorized();\n  x = 1;\n}"
    with tempfile.TemporaryDirectory() as t:
        _, d = _gate_one(t, ACCESS, body=body)
        assert d["status"] == "INLINE_GUARD_REFUTED"


def test_ownership_mapping_check_blocks_ready():
    body = "function f() external {\n  require(s.accts[lister].fields[id].plots[index] > 0, \"NO\");\n  x=1;\n}"
    with tempfile.TemporaryDirectory() as t:
        _, d = _gate_one(t, "ORDER_VALIDATION", body=body)
        assert d["status"] == "INLINE_GUARD_REFUTED"


def test_approval_check_blocks_ready():
    body = "function f() external {\n  require(isApprovedForAll[owner][msg.sender], \"NO\");\n  x=1;\n}"
    with tempfile.TemporaryDirectory() as t:
        _, d = _gate_one(t, ACCESS, body=body)
        assert d["status"] == "INLINE_GUARD_REFUTED"


def test_declaration_only_blocks_ready_needs_source_span():
    # interface-style: file with a declaration line only (ends ';', no body)
    with tempfile.TemporaryDirectory() as t:
        src = _write(t, "I.sol", "function f(uint256 a) external;")
        _, d = _gate_one(t, ACCESS, item_file=str(src), span=[1, 1])
        assert d["status"] == "NEEDS_SOURCE_SPAN"


def test_state_class_without_state_gate_needs_state_evidence():
    body = "function f() external {\n  x = 1;\n  emit E();\n}"  # no status/state gate
    with tempfile.TemporaryDirectory() as t:
        _, d = _gate_one(t, STATE, body=body)
        assert d["status"] == "NEEDS_STATE_MACHINE_EVIDENCE"


def test_value_class_without_value_flow_needs_value_flow():
    body = "function f() external {\n  emit E();\n}"  # no value-flow signal
    with tempfile.TemporaryDirectory() as t:
        _, d = _gate_one(t, VALUE, body=body)
        assert d["status"] == "NEEDS_VALUE_FLOW_EVIDENCE"


def test_state_machine_or_gate_can_be_ready():
    # a state-machine function with an OR-state gate (forbidden-state acceptance) is NOT blocked by D1-D4
    body = ("function f() external {\n  require(status == Succeeded || status == Defeated || status == Expired, \"x\");"
            "\n  executed = true;\n}")
    with tempfile.TemporaryDirectory() as t:
        pkg, d = _gate_one(t, STATE, body=body)
        assert d["gate_evidence_summary"]["state_machine_detected"] is True
        assert d["gate_evidence_summary"]["or_state_gate"] is True
        assert d["status"] not in ("NEEDS_STATE_MACHINE_EVIDENCE",)  # passes D2; reaches the P279 readiness path


def test_no_severity_reportable_leakage_in_corpus_outputs():
    for j in OUTS.glob("*/readiness.json"):
        for d in json.loads(j.read_text())["decisions"]:
            assert d["severity"] is None
            for f in ("reportable", "submission_ready", "concluded", "emits_finding", "production_routing"):
                assert d[f] is False


def test_p280_three_cases_no_longer_plain_ready():
    reg = {c["candidate"]: c for c in json.loads((OUTS / "p280_regression.json").read_text())["cases"]}
    assert reg["V3Vault.transform"]["P281"] == "INLINE_GUARD_REFUTED"
    assert reg["IBeanstalk.cancelPodListing"]["P281"] == "NEEDS_SOURCE_SPAN"
    assert "state-machine" in reg["L2Governor.execute"]["P281"].lower()


def test_ready_precision_improved_and_supported():
    ba = json.loads((OUTS / "before_after_ready_queue.json").read_text())
    assert ba["before_P279_P280"]["ready_for_poc_intent"] == 3
    assert ba["after_P281"]["ready_for_poc_intent"] <= 3
    assert ba["after_P281"]["poc_supported"] >= 1
    assert ba["after_P281"]["severe_concluded_or_reportable_fp"] == 0


def test_extractor_does_not_infer_bypass_from_source():
    src = EXTRACT.read_text()
    # bypass must NOT be derived from body keyword scan
    assert "bypass_evidence_present" not in src


def test_frozen_and_forbidden_byte_identical():
    for rel, h in FROZEN.items():
        assert _sha16(ROOT / rel) == h, f"frozen changed: {rel}"
    for rel, h in FORBIDDEN.items():
        assert _sha16(ROOT / rel).startswith(h), f"forbidden changed: {rel}"


def test_docs_and_verdict():
    for d in DOC_FILES:
        assert (DOCS / d).exists(), f"missing {d}"
    assert any(v in (DOCS / "VERDICT.md").read_text() for v in VERDICTS)


