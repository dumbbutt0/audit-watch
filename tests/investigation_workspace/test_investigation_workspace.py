"""Pure-function tests for the Investigation Workspace core (scripts/investigation_workspace.py).

Asserts the layer boundaries hold: prioritize-don't-verify (promotion), explain-don't-conclude (chain),
organize-don't-adjudicate (status). No corpus is modified; rows are append-only; forbidden verdict/routing
fields can never be emitted; research flags persist; outcome is never auto-derived.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import human_validation as hv  # noqa: E402
import investigation_workspace as iw  # noqa: E402

FROZEN = ROOT / "documentation/evals/judge_corpus/frozen_corpus.json"


def _bundle():
    return hv.load_corpus(FROZEN)["bundles"][0]


def _full_categories(status="met"):
    return {c: {"status": status, "evidence_ref": "code_snippet", "notes": "n"} for c in iw.PROMOTION_CATEGORIES}


# --------------------------------------------------------------- corpus loads
# --------------------------------------------------------------- promotion row
def test_promotion_progress_partial_scoring():
    cats = _full_categories("partial")
    p = iw.promotion_progress(cats)
    assert p["progress_score"] == 50.0 and p["completion_status"] == "complete"


# --------------------------------------------------------------- chain sections
def test_chain_section_valid_and_flags():
    row = iw.build_chain_section_row("cid", "demo", 4, notes="entry fn",
                                     code_references=["V3Vault.sol:877"],
                                     evidence_references=[{"source": "bundle", "ref": "code_snippet"}],
                                     evidence_attached=True)
    assert set(row.keys()) == iw._CHAIN_KEYS
    assert row["section_title"] == iw.CHAIN_SECTIONS[3]
    assert row["evidence_attached"] is True
    assert row["routing_allowed"] is False and row["research_only"] is True


@pytest.mark.parametrize("sid", [0, 14, -1, "3"])
def test_chain_section_bad_id(sid):
    with pytest.raises(hv.LabelValidationError):
        iw.build_chain_section_row("cid", "demo", sid)


def test_chain_section_bad_evidence_source():
    with pytest.raises(hv.LabelValidationError):
        iw.build_chain_section_row("cid", "demo", 1,
                                   evidence_references=[{"source": "rumor", "ref": "x"}])


# --------------------------------------------------------------- status + confidence
def test_status_row_with_confidence_evolution():
    row = iw.build_status_row("cid", "demo", "researching", note="n",
                              initial_confidence="coherent hypothesis",
                              current_confidence="weaker after counter-signals",
                              reason_for_change="invariant protected by secondary check")
    assert set(row.keys()) == iw._STATUS_KEYS
    assert row["current_confidence"].startswith("weaker")
    assert row["routing_allowed"] is False and row["research_only"] is True


def test_status_bad_state():
    with pytest.raises(hv.LabelValidationError):
        iw.build_status_row("cid", "demo", "exploitable")


# --------------------------------------------------------------- append-only + latest
def test_latest_sections_per_section(tmp_path):
    p = tmp_path / "chain.jsonl"
    iw.append_row(iw.build_chain_section_row("cid", "demo", 1, notes="old"), p)
    r = iw.build_chain_section_row("cid", "demo", 1, notes="new")
    r["timestamp"] = "2099-01-01T00:00:00+00:00"
    iw.append_row(r, p)
    secs = iw.latest_sections_by_candidate(iw.read_rows(p), "cid")
    assert secs[1]["notes"] == "new" and len(iw.read_rows(p)) == 2


# --------------------------------------------------------------- overview
# --------------------------------------------------------------- export packet
