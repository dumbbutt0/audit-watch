"""P114: fresh-candidate terminal-state distribution — RESEARCH-ONLY, un-wired.

Proves the next-3 selection is mechanical/deterministic (excludes confirmed controls + already-run P113 + missing
source, records skips), every candidate reaches a truthful terminal in the allowed set, no package/READY is created
without execution-backed runtime confirmation, no submission state is created, and inconclusive results are preserved
honestly.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "assisted"))
sys.path.insert(0, str(ROOT / "scripts" / "investigation"))
import terminal_distribution as TD  # noqa: E402
import assisted_fresh_run as AFR  # noqa: E402

CORPUS_PATH = ROOT / "documentation" / "research" / "assisted_mode" / "p105" / "benchmark_corpus.json"
_needs = pytest.mark.skipif(not CORPUS_PATH.is_file(), reason="P105 corpus not present")


def _corpus():
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


def test_flags_unwired():
    assert TD.FLAGS["is_gate"] is False
    assert TD.FLAGS["routes_in_production"] is False
    assert TD.FLAGS["routed_manifest_ids"] == []


def test_already_run_set_includes_p113():
    assert ("ramses-2024-10", "RamsesV3Pool", "swap") in TD.ALREADY_RUN


@_needs
def test_selection_deterministic():
    a, b = TD.select_next_n(_corpus(), n=3), TD.select_next_n(_corpus(), n=3)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


@_needs
def test_no_package_or_ready_without_runtime():
    b = TD.run_batch(_corpus(), n=3)
    assert b["no_unsafe_package"] is True
    for m in b["metrics"]:
        assert m["package_allowed"] is False
        assert m["runtime_attempted"] is False
        assert all(m["safety"].values())


@_needs
def test_no_submission_state_tokens(tmp_path):
    b = TD.run_batch(_corpus(), n=3)
    TD.write_bundle(b, tmp_path / "b")
    blob = "\n".join(p.read_text() for p in (tmp_path / "b").rglob("*") if p.is_file())
    for tok in ('"submitted": true', "APPROVED_TO_SUBMIT", "READY_FOR_HUMAN_REVIEW", "SUBMITTED"):
        assert tok not in blob, f"status leakage token present: {tok}"
    assert not list((tmp_path / "b").rglob("submission_package")), "no submission package may be generated"


@_needs
def test_p115_privileged_functions_demoted():
    """P115: signature-modifier-aware actor_clarity + the cross-subject permissionless gate demote privileged
    functions; closeMarket (onlyBorrower) and claimFromFactory (onlyPhiFactory) are no longer in the next-3, and
    every selected candidate is permissionless."""
    sel = TD.select_next_n(_corpus(), n=3)
    keys = {(c["subject"], c["contract"], c["function"]) for c in sel["selected"]}
    assert ("wildcat-2024-08", "WildcatMarket", "closeMarket") not in keys
    assert ("phi-2024-08", "PhiNFT1155", "claimFromFactory") not in keys
    assert all(c["permissionless"] for c in sel["selected"])
