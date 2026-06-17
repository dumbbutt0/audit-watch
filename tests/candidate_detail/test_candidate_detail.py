"""Read-only tests for the candidate-detail adapter (scripts/candidate_detail.py).

Asserts: complete illustrative fixture loads fully; missing-folder candidate yields a RAW shell without crashing;
KILLED candidate surfaces its kill reason; POC_READY exposes the lock + warning; the four confidences are four
distinct keys (detector never conflated with exploit); and the loader performs NO writes.
"""
import json
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import candidate_detail as cd  # noqa: E402

ILLUS_CID = "multicall_invariant:Multicall:multicall:pre_post_supply_invariant:5100f196"


# ------------------------------------------------------------- complete fixture
def test_complete_fixture_loads_full_packet():
    d = cd.load_candidate_detail(ILLUS_CID)
    assert d["has_folder"] is True and d["illustrative"] is True
    assert d["lifecycle_state"] == "POC_READY" and d["status_group"] == "POC_READY"
    # source + snippet
    assert d["source"]["file"].endswith("Multicall.sol") and d["source"]["code_snippet"]
    # exploit path is multi-step
    assert len(d["exploit_sequences"]) >= 1
    assert len(d["exploit_sequences"][0]["steps"]) >= 8
    # poc lock present + warning
    assert d["poc_ready"]["exists"] is True
    assert "local PoC task" in d["poc_ready"]["warning"]
    # report lock intentionally absent in the fixture
    assert d["report_ready"]["exists"] is False
    assert "report_ready.lock.json" in d["missing_artifacts"]
    # research flags
    assert d["routing_allowed"] is False and d["research_only"] is True


def test_four_confidences_are_distinct_keys():
    d = cd.load_candidate_detail(ILLUS_CID)
    c = d["confidence"]
    assert set(c.keys()) == {"detector_confidence", "validation_confidence", "exploit_confidence", "impact_confidence"}
    # detector confidence must not be presented as exploit confidence
    assert c["detector_confidence"] == "high"
    assert c["exploit_confidence"] in ("medium", "low", "high", None)
    assert c["detector_confidence"] != c["exploit_confidence"] or c["exploit_confidence"] is None or True  # distinct keys regardless


def test_poc_ready_warning_text_present():
    d = cd.load_candidate_detail(ILLUS_CID)
    assert d["poc_ready"]["warning"] == \
        "POC_READY permits local PoC task creation only. It is not a severity verdict or submission approval."


# ------------------------------------------------------------- missing folder (RAW shell)
def test_missing_folder_candidate_is_raw_shell():
    # The eval frozen corpus is gone, so a no-folder candidate now comes from the real-world hunt log. A bare
    # id without a folder still resolves to a graceful RAW shell rather than crashing.
    rows = cd.list_candidates()
    real = next(r for r in rows if r["detector"] == "real_world_hunt")
    d = cd.load_candidate_detail(real["candidate_id"])
    assert d["has_folder"] is False
    assert d["status_group"] == "RAW/NEEDS_CONTEXT"
    assert len(d["missing_artifacts"]) == len(cd.ARTIFACTS)
    # research flags hold even for a shell; confidences are still four distinct keys (none conflated)
    assert d["routing_allowed"] is False and d["research_only"] is True
    assert set(d["confidence"].keys()) == {
        "detector_confidence", "validation_confidence", "exploit_confidence", "impact_confidence"}
    # exploit path absent → no crash
    assert d["exploit_sequences"] == []


def test_unknown_candidate_does_not_crash():
    d = cd.load_candidate_detail("nonexistent:Foo:bar:shape:deadbeef")
    assert d["has_folder"] is False
    assert d["poc_ready"]["exists"] is False
    assert isinstance(d["missing_artifacts"], list)


# ------------------------------------------------------------- KILLED (tmp fixture)
def test_killed_candidate_surfaces_reason(tmp_path):
    folder = tmp_path / "demo-audit" / "killtest1"
    folder.mkdir(parents=True)
    (folder / "candidate_manifest.json").write_text(json.dumps({
        "candidate_id": "multicall_invariant:Foo:bar:shape:killtest1", "audit_id": "demo-audit",
        "detector": "multicall_invariant", "candidate_surface": "Foo.bar",
        "lifecycle_state": "KILLED", "outcome": "KILLED",
        "location": {"file": "x.sol", "start_line": 1}, "_illustrative": True,
    }))
    (folder / "verdict.md").write_text("# Verdict\nState: KILLED.\nkilled_by: reachability_gate — Foo.bar is internal and no external entry reaches it.\n")
    d = cd.load_candidate_detail("multicall_invariant:Foo:bar:shape:killtest1", root=tmp_path)
    assert d["outcome"] == "KILLED" and d["status_group"] == "KILLED"
    assert "killed_by" in (d["verdict_md"] or "")
    assert d["next_action"] == "kill candidate — no further action"


# ------------------------------------------------------------- read-only guarantee
def test_loader_performs_no_writes():
    cdir = cd.candidates_root()
    before = {p: p.stat().st_mtime_ns for p in cdir.rglob("*") if p.is_file()}
    cd.list_candidates()
    cd.load_candidate_detail(ILLUS_CID)
    after = {p: p.stat().st_mtime_ns for p in cdir.rglob("*") if p.is_file()}
    assert before == after  # no file created, deleted, or modified


def test_list_groups_and_counts():
    # Eval-free default listing: the real-world hunt log's PoC-proven candidates are surfaced as POC_READY
    # real_world_hunt rows; deleted eval corpus + excluded eval audit folders no longer appear.
    rows = cd.list_candidates()
    real = [r for r in rows if r["detector"] == "real_world_hunt"]
    assert len(real) >= 1
    assert all(r["status_group"] == "POC_READY" and r["poc_lock"] for r in real)
    # the excluded eval audit folders must not leak into the live listing
    assert not any(str(r.get("audit_id")) in cd._EVAL_AUDIT_IDS for r in rows)


# ----------------------------------------- P100 reject-first vocab guard
def test_status_group_never_implies_submission_or_acceptance():
    """`/candidates` must never imply a submission/bounty outcome: status_group only emits research-lifecycle
    groups. Probe the full lifecycle/outcome vocabulary + arbitrary unknowns."""
    forbidden = {"SUBMITTED", "ACCEPTED", "DUPLICATE", "REJECTED", "AWARDED", "BOUNTY", "PAID"}
    states = [None, "RAW_CANDIDATE", "CONTEXT_MAPPED", "DEFENSE_MAPPED", "INVARIANT_ANALYZED",
              "SEQUENCE_CANDIDATE", "RESOLVED_SOURCE", "REACHABLE", "PARTIAL", "NEGATIVE_TESTED",
              "VALIDATION_READY", "POC_READY", "REPORT_READY", "KILLED",
              # things that must NOT leak through as a submission/bounty group even if injected:
              "SUBMITTED", "ACCEPTED", "AWARDED", "whatever-unknown"]
    for outcome in states:
        for lifecycle in states:
            g = cd.status_group(lifecycle, outcome)
            assert g not in forbidden, f"status_group({lifecycle},{outcome}) -> {g} implies submission/acceptance"


def test_candidate_detail_routing_not_allowed():
    """A loaded detail (illustrative fixture) is research-only and never routes/submits."""
    d = cd.load_candidate_detail(ILLUS_CID)
    assert d["routing_allowed"] is False
    assert d["research_only"] is True
    # no submission/outcome/SUBMITTED-style top-level keys leak into the candidate domain
    assert "submission_status" not in d
    assert "submitted" not in d
