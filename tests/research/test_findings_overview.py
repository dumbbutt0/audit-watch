"""Isolated read-only tests for the unified findings-overview aggregator (research-only dashboard view)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import findings_overview as fo  # noqa: E402


def test_overview_is_research_only_and_not_routing():
    o = fo.load_overview()
    assert o["research_only"] is True
    assert o["routing_allowed"] is False
    assert o["routes_in_production"] is False
    # display-only board never marks anything submittable
    assert o["summary"]["submission_ready"] == 0
    assert all(r.get("routing_allowed") is False for r in o["rows"])
    assert all(r.get("submission_ready") is False for r in o["rows"])


def test_funnel_track_present():
    # The eval-era runtime/detector tracks were removed with the eval data; the funnel track (now sourced from
    # the real-world hunt log) is the live track and must be present.
    o = fo.load_overview()
    tracks = {r["track"] for r in o["rows"]}
    assert "funnel" in tracks


def test_real_world_poc_candidate_visible_not_submitted():
    # The PoC-proven real-world candidates surface as REPRODUCED funnel rows and are NEVER marked submittable.
    o = fo.load_overview()
    repro = [r for r in o["rows"] if r["track"] == "funnel" and r["state"] == "REPRODUCED"]
    assert repro, "PoC-proven real-world candidates must be visible"
    assert all(r["submission_ready"] is False for r in repro)


def test_strongest_signals_sort_first():
    o = fo.load_overview()
    ranks = [r.get("glance_rank", 99) for r in o["rows"]]
    assert ranks == sorted(ranks), "rows must be sorted strongest-first by glance_rank"
    # the very first row should be the reportable candidate when one exists
    if o["summary"]["reportable_candidates"]:
        assert o["rows"][0]["state"] == "REPORTABLE_CANDIDATE"
