"""P283 — bounded cross-function value-flow tracer. Behavior + guard tests (research-only, advisory)."""
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
import cross_function_value_tracer as cfvt  # noqa: E402

DOCS = ROOT / "documentation/research/assisted_mode/p283_cross_function_value_tracing"
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
DOC_FILES = ("SETUP.md", "CROSS_FUNCTION_TRACE_DESIGN.md", "IMPLEMENTATION_NOTES.md", "TRACE_REMAP_RESULTS.md",
             "TRACE_EVIDENCE_AUDIT.md", "TRACE_REPAIR_BACKLOG.md", "LIMITATIONS.md", "VERDICT.md", "ROLLBACK_PLAN.md")
VERDICTS = ("A — CROSS_FUNCTION_TRACE_READY_FOR_POC_SWEEP", "B — CROSS_FUNCTION_TRACE_PROMISING_NEEDS_REFINEMENT",
            "C — CROSS_FUNCTION_TRACE_TOO_NOISY", "D — ABORTED_CONSTRAINT_VIOLATION")
VALUE = "ACCOUNTING_LIQUIDATION_BAD_DEBT"


def _sha16(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def _build(tmp, funcs):
    """funcs: list of (contract, name, body_text). Writes one .sol file, returns (manifest, index)."""
    lines = []
    items = []
    for contract, name, body in funcs:
        start = len(lines) + 1
        body_lines = body.splitlines()
        lines.extend(body_lines)
        end = len(lines)
        items.append({"kind": "function", "contract": contract, "name": name, "file": None,
                      "source_span": {"start_line": start, "end_line": end}})
    src = Path(tmp) / "S.sol"
    src.write_text("\n".join(lines))
    for it in items:
        it["file"] = str(src)
    man = {"items": items}
    return man, cfvt.build_index(man)


# ---- tracer unit tests ----
def test_traces_same_contract_internal():
    with tempfile.TemporaryDirectory() as t:
        man, idx = _build(t, [
            ("C", "f", "function f() external {\n  _g();\n}"),
            ("C", "_g", "function _g() internal {\n  debt[msg.sender] += 1;\n}")])
        item = next(i for i in man["items"] if i["name"] == "f")
        r = cfvt.trace(item, idx, None)
        assert any(e["callee"] == "C._g" for e in r["trace_path"])
        assert r["trace_status"] in ("TRACE_FOUND", "TRACE_PARTIAL")


def test_traces_wrapper_to_internal():
    with tempfile.TemporaryDirectory() as t:
        man, idx = _build(t, [
            ("C", "claim", "function claim() external returns (uint) {\n  return _claimImpl();\n}"),
            ("C", "_claimImpl", "function _claimImpl() internal returns (uint) {\n  reward[msg.sender] = 5;\n}")])
        item = next(i for i in man["items"] if i["name"] == "claim")
        r = cfvt.trace(item, idx, None)
        assert any(e["callee"] == "C._claimImpl" for e in r["trace_path"])


def test_traces_locally_resolved_library_call():
    with tempfile.TemporaryDirectory() as t:
        man, idx = _build(t, [
            ("C", "f", "function f() external {\n  compute();\n}"),
            ("Lib", "compute", "function compute() internal {\n  shares = total / supply * x;\n}")])
        item = next(i for i in man["items"] if i["name"] == "f")
        r = cfvt.trace(item, idx, None)
        edge = next((e for e in r["trace_path"] if e["callee"] == "Lib.compute"), None)
        assert edge is not None and edge["edge"] == "library_or_inherited"


def test_respects_max_depth():
    with tempfile.TemporaryDirectory() as t:
        man, idx = _build(t, [
            ("C", "f", "function f() external {\n  g();\n}"),
            ("C", "g", "function g() internal {\n  h();\n}"),
            ("C", "h", "function h() internal {\n  i();\n}"),
            ("C", "i", "function i() internal {\n  z = 1;\n}")])
        item = next(i for i in man["items"] if i["name"] == "f")
        r = cfvt.trace(item, idx, None)
        # max_depth=2: edges f->g (depth0) and g->h (depth1) visited; h->i (depth2) NOT expanded
        assert not any(e["callee"] == "C.i" for e in r["trace_path"])


def test_fails_closed_on_unknown_external_call():
    with tempfile.TemporaryDirectory() as t:
        man, idx = _build(t, [
            ("C", "f", "function f() external {\n  IGauge(x).claimFees();\n}")])
        item = next(i for i in man["items"] if i["name"] == "f")
        r = cfvt.trace(item, idx, None)
        assert r["too_dynamic_seen"] is True
        assert r["value_flow_path"] is None  # external dispatch is never traced into


def test_unresolved_ambiguous_callee():
    with tempfile.TemporaryDirectory() as t:
        man, idx = _build(t, [
            ("C", "f", "function f() external {\n  helper();\n}"),
            ("A", "helper", "function helper() internal {\n  x = 1;\n}"),
            ("B", "helper", "function helper() internal {\n  y = 2;\n}")])
        item = next(i for i in man["items"] if i["name"] == "f")
        r = cfvt.trace(item, idx, None)
        assert "helper" in r["unresolved_callees"]


def test_comment_only_slashstar_is_not_anomaly():
    # a comment like `// T * (C - L) = G` must NOT register as a div-before-mul anomaly
    d = ssx.detect("function f() internal {\n  // T * (C - L) = G\n  // feeAssets / total * shares\n  x = 1;\n}")
    assert d["value_anomaly_div_before_mul"] is False


def test_exponent_is_not_div_before_mul():
    # `/ 2 ** 64` is fixed-point scaling, the `*` is exponentiation -> NOT div-before-mul (P283 regex fix)
    d = ssx.detect("function f() internal {\n  uint q = (a * b) / 2 ** 64;\n}")
    assert d["value_anomaly_div_before_mul"] is False


def test_real_div_before_mul_still_detected():
    d = ssx.detect("function f() internal {\n  y = total / supply * shares;\n}")
    assert d["value_anomaly_div_before_mul"] is True


def test_declaration_only_blocks_trace():
    with tempfile.TemporaryDirectory() as t:
        man, idx = _build(t, [("I", "f", "function f() external returns (uint);")])
        item = next(i for i in man["items"] if i["name"] == "f")
        r = cfvt.trace(item, idx, None)
        assert r["trace_status"] == "TRACE_UNRESOLVED"  # declaration-only root body -> no trace


# ---- gate integration ----
def _gate_two_func(tmp, caller_body, callee_name, callee_body):
    man, _ = _build(tmp, [("C", "f", caller_body), ("C", callee_name, callee_body)])
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
    return json.loads(gp.read_text())["decisions"][0], json.loads(dp.read_text())["packages"][0]


def test_generic_cross_function_value_move_no_ready():
    # a cross-function value move with NO anomaly must NOT lift to READY (don't infer a bug from movement)
    with tempfile.TemporaryDirectory() as t:
        d, _ = _gate_two_func(t, "function f() external {\n  _move();\n}",
                              "_move", "function _move() internal {\n  token.transfer(to, amt);\n}")
        assert d["status"] == "NEEDS_VALUE_FLOW_EVIDENCE"


def test_cross_function_comment_anomaly_no_ready():
    # callee's only `/ ... *` is a comment -> no anomaly -> no READY
    with tempfile.TemporaryDirectory() as t:
        d, pkg = _gate_two_func(t, "function f() external {\n  _calc();\n}",
                                "_calc", "function _calc() internal {\n  // a / b * c\n  reward[u] = 1;\n}")
        assert d["status"] == "NEEDS_VALUE_FLOW_EVIDENCE"
        te = pkg.get("trace_evidence", {})
        assert (te.get("value_flow_path") or {}).get("anomaly") in (None, False)


def test_inline_guard_still_blocks_with_trace():
    with tempfile.TemporaryDirectory() as t:
        d, _ = _gate_two_func(t, "function f() external {\n  require(msg.sender == owner);\n  _g();\n}",
                              "_g", "function _g() internal {\n  debt[x] = total / supply * shares;\n}")
        assert d["status"] == "INLINE_GUARD_REFUTED"  # D1 precedence over any trace anomaly


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


def test_remap_severe_fp_zero_and_no_false_lift():
    m = json.loads((OUTS / "remap_metrics.json").read_text())
    assert m["severe_concluded_or_reportable_fp"] == 0
    assert m["newly_lifted_to_ready"] == []          # 0 lifts (violations are semantic)
    assert m["after_P283"]["READY_FOR_POC_INTENT"] == 1
    assert m["value_class_v2_anomaly_eligible"] == []  # no value-class lifts on a (false) anomaly


def test_trace_evidence_has_found_records():
    te = json.loads((OUTS / "trace_evidence.json").read_text())
    assert te["trace_status_counts"].get("TRACE_FOUND", 0) >= 10  # tracing genuinely resolves callees


def test_frozen_and_forbidden_byte_identical():
    for rel, h in FROZEN.items():
        assert _sha16(ROOT / rel) == h, f"frozen changed: {rel}"
    for rel, h in FORBIDDEN.items():
        assert _sha16(ROOT / rel).startswith(h), f"forbidden changed: {rel}"


def test_docs_and_verdict():
    for d in DOC_FILES:
        assert (DOCS / d).exists(), f"missing {d}"
    assert any(v in (DOCS / "VERDICT.md").read_text() for v in VERDICTS)


