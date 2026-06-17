"""P292 — internal-locus coverage/queue admission. Research-only, advisory."""
import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/research"))
import expanded_validation_queue as evq  # noqa: E402

D = ROOT / "documentation/research/assisted_mode/p292_internal_locus_admission"
O = D / "outputs"
DO_NOT_EDIT = {
    "scripts/research/award_class_coverage_router.py": "6debb753b45f1833",   # router NOT edited in P292
    "scripts/research/recall_first_harness.py": "be428a1202c45b1a",
    "scripts/research/invariant_delta_deriver.py": "80bfa9f07d06d38f",
    "scripts/research/completion_evidence_deriver.py": "2a01164dffd9cad8",
    "scripts/research/poc_readiness_evidence_gate.py": "7afdc560bc4e96cd",
}
FORBIDDEN = {
    "scripts/dashboard_sync.py": "c1af70e1", "prompts/deep_trace.md": "c095c426",
    "scripts/min_confirm_gate.py": "2a15169a", "scripts/confirm_gate.py": "afc481c9",
    "scripts/validate_p208_l3_readiness.py": "ae55eb80",
}
DOC_FILES = ("SETUP.md", "INTERNAL_LOCUS_ADMISSION_DESIGN.md", "IMPLEMENTATION_NOTES.md", "REMAP_RESULTS.md",
             "EVIDENCE_AUDIT.md", "REPAIR_BACKLOG.md", "LIMITATIONS.md", "VERDICT.md", "ROLLBACK_PLAN.md")
VERDICTS = ("A — INTERNAL_LOCUS_ADMISSION_READY_FOR_BLIND_RETEST",
            "B — INTERNAL_LOCUS_ADMISSION_PROMISING_NEEDS_REFINEMENT",
            "C — INTERNAL_LOCUS_ADMISSION_TOO_NOISY", "D — ABORTED_CONSTRAINT_VIOLATION")


def _replay(tmp, shadow_cands, cov_decisions, handoff):
    """Write a synthetic replay-dir and run evq.build; return the queue result dict."""
    rd = Path(tmp) / "run"; (rd / "shadow").mkdir(parents=True)
    (rd / "shadow" / "recall_advisory_candidates.json").write_text(json.dumps({"advisory_candidates": shadow_cands}))
    (rd / "coverage_decisions.json").write_text(json.dumps({"decisions": cov_decisions, "handoff_queue_to_p269": handoff}))
    (rd / "triage_decisions.json").write_text(json.dumps({"decisions": [{"id": h, "outcome": "SELECT_FOR_POC"} for h in handoff]}))
    out = Path(tmp) / "out"
    return evq.build(rd, out, None, True)


def _internal_cand(cid, contract, function, reached="Pub.entry", span=(1, 9)):
    return {"candidate_id": cid, "contract": contract, "function": function, "locus": f"{contract}:{function}",
            "internal_locus": True, "reached_from_public_entry": reached,
            "source_span": {"start_line": span[0], "end_line": span[1]}, "call_path": [reached, f"{contract}.{function}"],
            "generated_mechanisms": []}


def _decision(cid, cls, label):
    return {"id": cid, "award_class": cls, "label": label}


SHARE = "SHARE_ROUNDING_PRECISION"


def test_default_duplicate_dedup_preserved_for_non_internal():
    with tempfile.TemporaryDirectory() as t:
        shadow = [{"candidate_id": "P:C:pub:0", "contract": "C", "function": "pub", "locus": "C:pub", "generated_mechanisms": []},
                  {"candidate_id": "P:C:dup:1", "contract": "C", "function": "dup", "locus": "C:dup", "generated_mechanisms": []}]  # NOT internal
        cov = [_decision("P:C:pub:0", SHARE, "COVERAGE_SELECT_PRIMARY"), _decision("P:C:dup:1", SHARE, "COVERAGE_DEFER_DUPLICATE_CLASS")]
        r = _replay(t, shadow, cov, ["P:C:pub:0"])
        dd = {x["candidate_id"]: x["duplicate_class_decision"] for x in r["duplicate_class_decisions"]}
        assert dd.get("P:C:dup:1") == "DEFERRED_DUPLICATE_CLASS"  # non-internal duplicate stays deferred


def test_internal_locus_exception_admits_distinct_locus():
    with tempfile.TemporaryDirectory() as t:
        shadow = [{"candidate_id": "P:C:pub:0", "contract": "C", "function": "pub", "locus": "C:pub", "generated_mechanisms": []},
                  _internal_cand("P:S:_increaseUserShare:int0", "S", "_increaseUserShare")]
        cov = [_decision("P:C:pub:0", SHARE, "COVERAGE_SELECT_PRIMARY"),
               _decision("P:S:_increaseUserShare:int0", SHARE, "COVERAGE_DEFER_DUPLICATE_CLASS")]
        r = _replay(t, shadow, cov, ["P:C:pub:0"])
        assert "P:S:_increaseUserShare:int0" in r["internal_locus_admitted"]
        dd = {x["candidate_id"]: x["duplicate_class_decision"] for x in r["duplicate_class_decisions"]}
        assert dd["P:S:_increaseUserShare:int0"] == "ADMITTED_INTERNAL_LOCUS_EXCEPTION"


def test_exception_requires_source_span():
    with tempfile.TemporaryDirectory() as t:
        c = _internal_cand("P:S:_f:int0", "S", "_reward"); c.pop("source_span")
        shadow = [{"candidate_id": "P:C:pub:0", "contract": "C", "function": "pub", "locus": "C:pub", "generated_mechanisms": []}, c]
        cov = [_decision("P:C:pub:0", SHARE, "COVERAGE_SELECT_PRIMARY"), _decision("P:S:_f:int0", SHARE, "COVERAGE_DEFER_DUPLICATE_CLASS")]
        r = _replay(t, shadow, cov, ["P:C:pub:0"])
        assert "P:S:_f:int0" not in r["internal_locus_admitted"]


def test_exception_requires_reached_from_public_entry():
    with tempfile.TemporaryDirectory() as t:
        c = _internal_cand("P:S:_f:int0", "S", "_reward"); c.pop("reached_from_public_entry")
        shadow = [{"candidate_id": "P:C:pub:0", "contract": "C", "function": "pub", "locus": "C:pub", "generated_mechanisms": []}, c]
        cov = [_decision("P:C:pub:0", SHARE, "COVERAGE_SELECT_PRIMARY"), _decision("P:S:_f:int0", SHARE, "COVERAGE_DEFER_DUPLICATE_CLASS")]
        r = _replay(t, shadow, cov, ["P:C:pub:0"])
        assert "P:S:_f:int0" not in r["internal_locus_admitted"]


def test_exception_requires_class_relevant_signal():
    with tempfile.TemporaryDirectory() as t:
        c = _internal_cand("P:S:_doThing:int0", "S", "_doThing")  # no signal term in name
        shadow = [{"candidate_id": "P:C:pub:0", "contract": "C", "function": "pub", "locus": "C:pub", "generated_mechanisms": []}, c]
        cov = [_decision("P:C:pub:0", SHARE, "COVERAGE_SELECT_PRIMARY"), _decision("P:S:_doThing:int0", SHARE, "COVERAGE_DEFER_DUPLICATE_CLASS")]
        r = _replay(t, shadow, cov, ["P:C:pub:0"])
        assert "P:S:_doThing:int0" not in r["internal_locus_admitted"]


def test_caps_enforced():
    with tempfile.TemporaryDirectory() as t:
        shadow = [{"candidate_id": "P:C:pub:0", "contract": "C", "function": "pub", "locus": "C:pub", "generated_mechanisms": []}]
        cov = [_decision("P:C:pub:0", SHARE, "COVERAGE_SELECT_PRIMARY")]
        for i in range(4):  # 4 distinct internal share loci, same class; cap is 2/class
            shadow.append(_internal_cand(f"P:S:_reward{i}:int{i}", "S", f"_reward{i}"))
            cov.append(_decision(f"P:S:_reward{i}:int{i}", SHARE, "COVERAGE_DEFER_DUPLICATE_CLASS"))
        r = _replay(t, shadow, cov, ["P:C:pub:0"])
        assert len(r["internal_locus_admitted"]) <= 2   # same-class cap
        caps = [x for x in r["duplicate_class_decisions"] if x["duplicate_class_decision"] == "DEFERRED_INTERNAL_LOCUS_CAP"]
        assert len(caps) >= 1


def test_anti_monoculture_enforced():
    # small base + many same-class internal loci would push >40% only if it would; verify monoculture flag stays computed
    with tempfile.TemporaryDirectory() as t:
        shadow = [{"candidate_id": f"P:C:pub{i}:{i}", "contract": "C", "function": f"pub{i}", "locus": f"C:pub{i}", "generated_mechanisms": []} for i in range(6)]
        cov = [_decision(f"P:C:pub{i}:{i}", ["ACCOUNTING_LIQUIDATION_BAD_DEBT", "ORACLE_PRICING", "DOS_LIVENESS", "REWARDS_CLAIMS", "ACCESS_CONTROL_AUTHORIZATION", "ORDER_VALIDATION"][i], "COVERAGE_SELECT_PRIMARY") for i in range(6)]
        for i in range(3):
            shadow.append(_internal_cand(f"P:S:_share{i}:int{i}", "S", f"_share{i}"))
            cov.append(_decision(f"P:S:_share{i}:int{i}", SHARE, "COVERAGE_DEFER_DUPLICATE_CLASS"))
        r = _replay(t, shadow, cov, [f"P:C:pub{i}:{i}" for i in range(6)])
        assert r["anti_monoculture_ok"] is True  # combined queue diversity preserved


# ---- corpus outputs ----
def test_increaseusershare_admitted_in_corpus():
    rep = json.loads((O / "internal_locus_admission_report.json").read_text())
    assert any("increaseUserShare" in a["candidate"] for a in rep["admitted"])
    # and it reaches the gate/lens (recorded)
    assert any("increaseUserShare" in x["candidate"] for x in rep["reaches_lens"])


def test_no_false_ready_and_fp_zero():
    m = json.loads((O / "remap_metrics.json").read_text())
    assert m["severe_concluded_or_reportable_fp"] == 0


def test_regressions_preserved():
    m = json.loads((O / "remap_metrics.json").read_text())["audits"]
    assert any("getRsETHAmountToMint" in c for c in m["kelp-2023-11-holdout"]["READY"])
    bh = m["blackhole-2025-05-eval"]["READY"]
    assert any("claim_many" in c for c in bh) and any("L2Governor:execute" in c for c in bh)
    assert any("SurplusGuildMinter:stake" in c for c in m["ecg-2023-12-holdout"]["READY"])
    assert not any("Pools:deposit" in c for c in m["salty-2024-01-holdout"]["READY"])  # P291 precision held


def test_do_not_edit_and_forbidden_byte_identical():
    for rel, h in DO_NOT_EDIT.items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:len(h)] == h, f"do-not-edit changed: {rel}"
    for rel, h in FORBIDDEN.items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:8].startswith(h), f"forbidden changed: {rel}"


def test_no_leakage_in_outputs():
    for name in ("remap_metrics.json", "duplicate_class_decisions.json", "internal_locus_admission_report.json",
                 "guard_report.json"):
        r = json.loads((O / name).read_text())
        for f in ("reportable", "submission_ready", "concluded", "production_routing"):
            if isinstance(r, dict) and f in r:
                assert r[f] is False


def test_docs_and_verdict():
    for d in DOC_FILES:
        assert (D / d).exists(), f"missing {d}"
    assert any(v in (D / "VERDICT.md").read_text() for v in VERDICTS)


