"""P285 — D1 inline-guard granularity (read-vs-guard). Behavior + guard tests (research-only, advisory)."""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DERIVER = ROOT / "scripts/research/completion_evidence_deriver.py"
GATE = ROOT / "scripts/research/poc_readiness_evidence_gate.py"
sys.path.insert(0, str(ROOT / "scripts/research"))
import source_span_guard_extractor as ssx  # noqa: E402

DOCS = ROOT / "documentation/research/assisted_mode/p285_inline_guard_granularity"
OUTS = DOCS / "outputs"
FROZEN = {
    "scripts/research/locus_shape_prioritizer.py": "d6b494bc3c0cc746",
    "scripts/research/recall_first_shape_sweep.py": "a48336275cb65a4f",
    "scripts/research/recall_first_harness.py": "be428a1202c45b1a",
    "scripts/research/mechanism_pairwise_selector.py": "b0623b8c88752059",
    "scripts/research/impact_first_poc_triage.py": "63c88d02d2c7eefa",
    "scripts/research/award_class_coverage_router.py": "6debb753b45f1833",
    "config/research_award_class_coverage_router.json": "91f9deac7867af62",
    "scripts/research/cross_function_value_tracer.py": "f28f0620d3d3548a",
    "scripts/research/invariant_delta_deriver.py": "80bfa9f07d06d38f",
    "config/research_invariant_delta_deriver.json": "4774dfa72974019a",
    "documentation/research/assisted_mode/p271_lending_runtime_scaffold/"
    "LENDING_COMPLETION_CHECKLIST.md": "2929a2154a88104e",
}
# validated detector platform — imported read-only by P284; must stay byte-identical
REUSED = {
    "scripts/sibling_function_parity_taxonomy.py": "e504383db8f33844",
    "scripts/registry_position_lifecycle_taxonomy.py": "da83a7acc217c706",
}
FORBIDDEN = {
    "scripts/dashboard_sync.py": "c1af70e1", "prompts/deep_trace.md": "c095c426",
    "scripts/min_confirm_gate.py": "2a15169a", "scripts/confirm_gate.py": "afc481c9",
    "scripts/validate_p208_l3_readiness.py": "ae55eb80",
}
DOC_FILES = ("SETUP.md", "INLINE_GUARD_GRANULARITY_DESIGN.md", "IMPLEMENTATION_NOTES.md",
             "D1_GRANULARITY_REMAP_RESULTS.md", "INLINE_GUARD_AUDIT.md", "D1_GRANULARITY_REPAIR_BACKLOG.md",
             "LIMITATIONS.md", "VERDICT.md", "ROLLBACK_PLAN.md")
VERDICTS = ("A — D1_GRANULARITY_READY_FOR_POC_SWEEP", "B — D1_GRANULARITY_PROMISING_NEEDS_REFINEMENT",
            "C — D1_GRANULARITY_TOO_PERMISSIVE", "D — ABORTED_CONSTRAINT_VIOLATION")
VALUE = "ACCOUNTING_LIQUIDATION_BAD_DEBT"
ACCESS = "ACCESS_CONTROL_AUTHORIZATION"


def _sha16(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def _ctx(body):
    return {c["token"]: c["context"] for c in ssx.detect(body)["guard_contexts"]}


# ---- execution-gate detection (must stay refuting) ----
def test_require_msgsender_is_execution_guard():
    d = ssx.detect("function f() external { require(msg.sender == owner, \"NO\"); x=1; }")
    assert d["inline_guard_detected"] is True


def test_if_unauthorized_revert_is_execution_guard():
    d = ssx.detect("function f() external { if (msg.sender != owner) revert Unauthorized(); x=1; }")
    assert d["inline_guard_detected"] is True


def test_onlyowner_modifier_is_execution_guard():
    d = ssx.detect("function f() external onlyOwner { x=1; }")
    assert d["inline_guard_detected"] is True


def test_isapprovedorowner_inside_require_is_execution_guard():
    d = ssx.detect("function f() external { require(_isApprovedOrOwner(msg.sender, id)); x=1; }")
    assert d["inline_guard_detected"] is True


def test_isapprovedorowner_inside_assert_is_execution_guard():
    d = ssx.detect("function f() external { assert(_isApprovedOrOwner(msg.sender, id)); x=1; }")
    assert d["inline_guard_detected"] is True


# ---- ownership READ must NOT be a guard ----
def test_ownerof_assigned_to_recipient_is_not_guard():
    d = ssx.detect("function f() external { address recipient = ownerOf(id); token.transfer(recipient, amt); }")
    assert d["inline_guard_detected"] is False
    assert _ctx("function f() external { address recipient = ownerOf(id); x=1; }")["ownerof("] in (
        "RECIPIENT_READ", "VALUE_READ")


def test_ownerof_passed_into_transfer_is_value_read():
    d = ssx.detect("function f() external { rewardToken.transfer(ownerOf(id), amt); }")
    assert d["inline_guard_detected"] is False


def test_ownerof_emitted_is_not_guard():
    d = ssx.detect("function f() external { emit Claimed(ownerOf(id), amt); }")
    assert d["inline_guard_detected"] is False
    assert _ctx("function f() external { emit Claimed(ownerOf(id), amt); }")["ownerof("] == "EVENT_READ"


def test_ownerof_returned_is_not_guard():
    d = ssx.detect("function f() external { x; return ownerOf(id); }")
    assert d["inline_guard_detected"] is False
    assert _ctx("function f() external { x; return ownerOf(id); }")["ownerof("] == "RETURN_READ"


# ---- gate integration ----
def _gate(tmp, body, award_class=ACCESS, extra=None):
    src = Path(tmp) / "C.sol"; src.write_text(body)
    man = {"items": [{"kind": "function", "contract": "C", "name": "f", "signature": "function f()",
                      "visibility": "external", "mutability": "nonpayable", "modifiers": [], "tags": ["x"],
                      "file": str(src), "source_span": {"start_line": 1, "end_line": len(body.splitlines())}}]}
    pkg = {"candidate_id": "c1", "award_class": award_class, "contract_function": "C.f", "mechanism_hypothesis": "m",
           "root_cause": "rc", "runner_up_mechanism": "ru"}
    if extra:
        pkg.update(extra)
    mp = Path(tmp) / "m.json"; mp.write_text(json.dumps(man))
    pp = Path(tmp) / "p.json"; pp.write_text(json.dumps({"packages": [pkg]}))
    dp = Path(tmp) / "d.json"
    subprocess.run([sys.executable, str(DERIVER), "--manifest", str(mp), "--packages", str(pp), "--out", str(dp),
                    "--quiet"], capture_output=True, text=True)
    gp = Path(tmp) / "g.json"
    subprocess.run([sys.executable, str(GATE), "--packages", str(dp), "--out", str(gp), "--quiet"],
                   capture_output=True, text=True)
    return json.loads(gp.read_text())["decisions"][0]


def test_true_guard_still_refutes_in_gate():
    with tempfile.TemporaryDirectory() as t:
        d = _gate(t, "function f() external {\n  require(msg.sender == owner);\n  x = 1;\n}")
        assert d["status"] == "INLINE_GUARD_REFUTED"


def test_ambiguous_auth_read_fails_closed_needs_guard_context():
    # an UNKNOWN_READ auth token (if-condition with NO revert -> not a hard gate) on an ACCESS candidate, no
    # deviation -> held for guard context, never READY
    body = "function f() external {\n  if (msg.sender != owner) { x = 1; }\n  y = 2;\n}"
    with tempfile.TemporaryDirectory() as t:
        assert ssx.detect(body)["inline_guard_ambiguous"] is True
        d = _gate(t, body, ACCESS)
        assert d["status"] == "NEEDS_GUARD_CONTEXT"


# ---- corpus regressions ----
def _corpus_status():
    seen = {}
    for r in OUTS.glob("*/readiness.json"):
        for d in json.loads(r.read_text())["decisions"]:
            seen[d["candidate_id"]] = d["status"]
    return seen


def test_claim_many_no_longer_d1_refuted_and_ready():
    s = _corpus_status()
    assert s.get("coverage_manifest:RewardsDistributor:claim_many:7") == "READY_FOR_POC_INTENT"


def test_true_guards_remain_refuted():
    s = _corpus_status()
    assert s.get("coverage_manifest:V3Vault:transform:9") == "INLINE_GUARD_REFUTED"
    assert s.get("coverage_manifest:VotingEscrow:withdraw:4") == "INLINE_GUARD_REFUTED"  # assert() guard


def test_l2governor_remains_ready():
    s = _corpus_status()
    assert s.get("coverage_manifest:L2Governor:execute:20") == "READY_FOR_POC_INTENT"


def test_ibeanstalk_declaration_only_not_ready():
    s = _corpus_status()
    assert s.get("coverage_manifest:IBeanstalk:cancelPodListing:0") == "NEEDS_SOURCE_SPAN"


def test_no_severity_reportable_leakage():
    for r in OUTS.glob("*/readiness.json"):
        for d in json.loads(r.read_text())["decisions"]:
            assert d["severity"] is None
            for f in ("reportable", "submission_ready", "concluded", "emits_finding", "production_routing"):
                assert d[f] is False


def test_remap_metrics_one_newly_lifted_zero_fp():
    m = json.loads((OUTS / "remap_metrics.json").read_text())
    assert m["severe_concluded_or_reportable_fp"] == 0
    assert m["newly_lifted_to_ready"] == ["coverage_manifest:RewardsDistributor:claim_many:7"]
    assert m["after_P285"]["READY_FOR_POC_INTENT"] == 2
    assert m["inline_guard_refuted_after"] < m["inline_guard_refuted_before"]  # reads reclassified out


# ---- byte-identical guards ----
def test_frozen_reused_forbidden_byte_identical():
    for rel, h in {**FROZEN, **REUSED}.items():
        assert _sha16(ROOT / rel) == h, f"changed: {rel}"
    for rel, h in FORBIDDEN.items():
        assert _sha16(ROOT / rel).startswith(h), f"forbidden changed: {rel}"


def test_docs_and_verdict():
    for d in DOC_FILES:
        assert (DOCS / d).exists(), f"missing {d}"
    assert any(v in (DOCS / "VERDICT.md").read_text() for v in VERDICTS)


