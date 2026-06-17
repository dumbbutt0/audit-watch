"""P291 — EXTERNAL_INTEGRATION precision (Part A) + internal-locus recall (Part B). Research-only, advisory."""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DERIVER = ROOT / "scripts/research/completion_evidence_deriver.py"
GATE = ROOT / "scripts/research/poc_readiness_evidence_gate.py"
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/research"))
import completion_evidence_deriver as ced  # noqa: E402
import recall_first_harness as rfh  # noqa: E402

D = ROOT / "documentation/research/assisted_mode/p291_ext_integration_precision_internal_locus_recall"
O = D / "outputs"
# do-not-edit modules (P291 must NOT change these)
DO_NOT_EDIT = {
    "scripts/research/award_class_coverage_router.py": "6debb753b45f1833",
    "scripts/research/cross_function_value_tracer.py": "f28f0620d3d3548a",
    "scripts/research/invariant_delta_deriver.py": "80bfa9f07d06d38f",
    "scripts/research/source_span_guard_extractor.py": "cd472bd82963",  # 12-char prefix
    "scripts/sibling_function_parity_taxonomy.py": "e504383db8f33844",
    "scripts/registry_position_lifecycle_taxonomy.py": "da83a7acc217c706",
}
FORBIDDEN = {
    "scripts/dashboard_sync.py": "c1af70e1", "prompts/deep_trace.md": "c095c426",
    "scripts/min_confirm_gate.py": "2a15169a", "scripts/confirm_gate.py": "afc481c9",
    "scripts/validate_p208_l3_readiness.py": "ae55eb80",
}
DOC_FILES = ("SETUP.md", "REPAIR_DESIGN.md", "IMPLEMENTATION_NOTES.md", "REMAP_RESULTS.md", "EVIDENCE_AUDIT.md",
             "REPAIR_BACKLOG.md", "LIMITATIONS.md", "VERDICT.md", "ROLLBACK_PLAN.md")
VERDICTS = ("A — EXT_PRECISION_INTERNAL_RECALL_READY_FOR_BLIND_RETEST",
            "B — EXT_PRECISION_INTERNAL_RECALL_PROMISING_NEEDS_REFINEMENT",
            "C — REPAIR_TOO_NOISY_OR_TOO_STRICT", "D — ABORTED_CONSTRAINT_VIOLATION")
EXT = "EXTERNAL_INTEGRATION"


def _sha(p, n=16):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:n]


# ---- Part A: deviation detector ----
def test_nonreentrant_safetransferfrom_no_deviation():
    r = ced._integration_deviation_evidence({"name": "deposit"},
        "function deposit() external nonReentrant { _d[msg.sender]+=a; token.safeTransferFrom(msg.sender,address(this),a); }", {})
    assert r["deviation_present"] is False


def test_safetransferfrom_alone_no_deviation():
    r = ced._integration_deviation_evidence({"name": "f"}, "function f() external { token.safeTransferFrom(a,b,c); }", {})
    assert r["deviation_present"] is False


def test_lowlevel_call_is_deviation():
    r = ced._integration_deviation_evidence({"name": "f"}, "function f() external { (bool ok,)=t.call{value:a}(d); s=1; }", {})
    assert r["deviation_present"] is True


def test_callback_interface_is_deviation():
    r = ced._integration_deviation_evidence({"name": "onFlashLoan"}, "function onFlashLoan() external { state=1; }", {})
    assert r["deviation_present"] is True


def test_explicit_fee_on_transfer_is_deviation():
    r = ced._integration_deviation_evidence({"name": "deposit"},
        "function deposit() external { _d[msg.sender]+=a; token.transferFrom(a,b,c); }",
        {"integration_deviation_evidence": {"deviation_present": True, "basis": "fee_on_transfer"}})
    assert r["deviation_present"] is True


# ---- Part A: gate integration ----
def _gate_ext(tmp, body, external_calls=False, extra=None):
    src = Path(tmp) / "C.sol"; src.write_text(body)
    man = {"items": [{"kind": "function", "contract": "C", "name": "f", "signature": "function f()",
                      "visibility": "external", "mutability": "nonpayable", "modifiers": [],
                      "external_calls": external_calls, "tags": ["integration"], "file": str(src),
                      "source_span": {"start_line": 1, "end_line": len(body.splitlines())}}]}
    pkg = {"candidate_id": "c1", "award_class": EXT, "contract_function": "C.f", "mechanism_hypothesis": "m",
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


def test_generic_external_integration_not_ready():
    with tempfile.TemporaryDirectory() as t:
        d = _gate_ext(t, "function f() external nonReentrant {\n  _d[msg.sender]+=a;\n  token.safeTransferFrom(a,b,c);\n}")
        assert d["status"] == "NEEDS_INTEGRATION_DEVIATION_EVIDENCE"


def test_callback_deviation_can_be_ready():
    with tempfile.TemporaryDirectory() as t:
        d = _gate_ext(t, "function f() external {\n  (bool ok,) = target.call{value: a}(data);\n  state = 1;\n}",
                      external_calls=True)
        assert d["status"] == "READY_FOR_POC_INTENT"


# ---- Part B: internal-locus expansion ----
def _man(funcs):
    lines, items = [], []
    for c, n, vis, body in funcs:
        start = len(lines) + 1
        lines.extend(body.splitlines())
        items.append({"kind": "function", "contract": c, "name": n, "visibility": vis, "file": None,
                      "source_span": {"start_line": start, "end_line": len(lines)}})
    return lines, items


def test_internal_reward_function_surfaced_and_getter_not():
    with tempfile.TemporaryDirectory() as t:
        lines, items = _man([
            ("S", "stake", "external", "function stake(uint a) external { _increaseUserShare(msg.sender, a); }"),
            ("S", "_increaseUserShare", "internal", "function _increaseUserShare(address u, uint a) internal { userShare[u] += a; rewardIndex[u] = globalIndex; }"),
            ("S", "getShare", "internal", "function getShare(address u) internal view returns (uint) { return userShare[u]; }")])
        src = Path(t) / "S.sol"; src.write_text("\n".join(lines))
        for it in items:
            it["file"] = str(src)
        man = {"items": items}
        cands = [{"contract": "S", "function": "stake", "candidate_id": "x:S:stake:0", "prioritizer_score": 5}]
        cfg = json.loads((ROOT / "config/research_recall_first_harness.json").read_text())
        out = rfh._expand_internal_loci(man, cands, "x", cfg)
        fns = {c["function"] for c in out}
        assert "_increaseUserShare" in fns                      # reward/share internal surfaced
        assert "getShare" not in fns                            # trivial getter NOT surfaced
        for c in out:
            assert c["internal_locus"] is True and c["advisory_only"] is True
            assert c["severity"] is None and c["reportable"] is False


def test_internal_expansion_caps_enforced():
    cfg = json.loads((ROOT / "config/research_recall_first_harness.json").read_text())
    assert cfg["internal_locus_recall"]["max_expansions_per_public_entry"] <= 5
    assert cfg["internal_locus_recall"]["max_internal_candidates_per_contest"] <= 30


# ---- corpus outputs ----
def test_pools_deposit_not_ready():
    rep = json.loads((O / "integration_precision_report.json").read_text())
    pd = rep.get("pools_deposit")
    assert pd and pd["status"] == "NEEDS_INTEGRATION_DEVIATION_EVIDENCE"


def test_increaseusershare_surfaced_in_corpus():
    il = json.loads((O / "internal_locus_candidates.json").read_text())
    assert any("increaseUserShare" in r["function"] for r in il["records"])


def test_regressions_preserved():
    m = json.loads((O / "remap_metrics.json").read_text())["regressions"]
    assert m["SurplusGuildMinter:stake"] == "READY_FOR_POC_INTENT"
    assert m["getRsETHAmountToMint"] == "READY_FOR_POC_INTENT"
    assert m["claim_many"] == "READY_FOR_POC_INTENT"
    assert m["L2Governor.execute"] == "READY_FOR_POC_INTENT"


def test_severe_fp_zero():
    assert json.loads((O / "remap_metrics.json").read_text())["severe_concluded_or_reportable_fp"] == 0


def test_do_not_edit_and_forbidden_byte_identical():
    for rel, h in DO_NOT_EDIT.items():
        assert _sha(ROOT / rel, len(h)) == h, f"do-not-edit changed: {rel}"
    for rel, h in FORBIDDEN.items():
        assert _sha(ROOT / rel, 8).startswith(h), f"forbidden changed: {rel}"


def test_no_leakage_in_outputs():
    for name in ("remap_metrics.json", "integration_precision_report.json", "internal_locus_candidates.json",
                 "guard_report.json"):
        r = json.loads((O / name).read_text())
        for f in ("reportable", "submission_ready", "concluded", "production_routing"):
            if isinstance(r, dict) and f in r:
                assert r[f] is False


def test_docs_and_verdict():
    for d in DOC_FILES:
        assert (D / d).exists(), f"missing {d}"
    assert any(v in (D / "VERDICT.md").read_text() for v in VERDICTS)


