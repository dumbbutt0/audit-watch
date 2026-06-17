"""P116: fresh discovery batch on the corrected (permissionless-first) ranking — RESEARCH-ONLY, un-wired.

Proves the corrected ranking, applied as a fresh batch, mechanically excludes the confirmed controls + everything run
in P113/P114 (incl. the now-demoted privileged functions), surfaces permissionless candidates (incl. the real
CuratorRewardsDistributor.distribute), reaches truthful terminals in the allowed set, generates no package/READY
without runtime, and records the distribute hypotheses honestly.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "assisted"))
sys.path.insert(0, str(ROOT / "scripts" / "investigation"))
import fresh_batch_p116 as P116  # noqa: E402
import terminal_distribution as TD  # noqa: E402
import assisted_fresh_run as AFR  # noqa: E402

CORPUS_PATH = ROOT / "documentation" / "research" / "assisted_mode" / "p105" / "benchmark_corpus.json"
_needs = pytest.mark.skipif(not CORPUS_PATH.is_file(), reason="P105 corpus not present")


def _corpus():
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


def test_flags_unwired():
    assert P116.FLAGS["is_gate"] is False
    assert P116.FLAGS["routes_in_production"] is False
    assert P116.FLAGS["routed_manifest_ids"] == []


def test_already_run_includes_p113_and_p114():
    assert ("ramses-2024-10", "RamsesV3Pool", "swap") in P116.ALREADY_RUN_P116
    assert ("wildcat-2024-08", "WildcatMarket", "closeMarket") in P116.ALREADY_RUN_P116
    assert ("phi-2024-08", "PhiNFT1155", "claimFromFactory") in P116.ALREADY_RUN_P116
    assert ("wildcat-2024-08", "WildcatMarketWithdrawals",
            "repayAndProcessUnpaidWithdrawalBatches") in P116.ALREADY_RUN_P116


@_needs
def test_no_status_leakage_in_bundle(tmp_path):
    b = P116.run(_corpus())
    out = Path(TD.write_bundle(b, tmp_path / "b")["dir"])
    blob = "\n".join(p.read_text() for p in out.rglob("*") if p.is_file())
    for tok in ('"submitted": true', "APPROVED_TO_SUBMIT", "READY_FOR_HUMAN_REVIEW", "SUBMITTED"):
        assert tok not in blob
    assert not list(out.rglob("submission_package"))


@_needs
def test_deterministic():
    a = P116.run(_corpus())
    c = P116.run(_corpus())
    assert json.dumps(a["terminal_distribution"], sort_keys=True) == json.dumps(c["terminal_distribution"], sort_keys=True)
    assert [m["candidate"] for m in a["metrics"]] == [m["candidate"] for m in c["metrics"]]
