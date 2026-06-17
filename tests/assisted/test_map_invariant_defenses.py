"""P101: defense mapping — RESEARCH-ONLY, un-wired. Proves coverage classification (COVERS / PARTIAL / NONE /
UNKNOWN) so a covered invariant can be rejected and a partial/uncovered one proceeds to trace."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "assisted"))
import map_invariant_defenses as M  # noqa: E402


def test_self_test_passes():
    assert M._self_test() == 0


def test_covers_when_guard_present():
    r = M.map_defenses({"invariant_type": "role_access"}, 'require(msg.sender != listing.seller, "x")')
    assert r["coverage"] == M.COVERS


def test_partial_or_none_when_guard_absent():
    r = M.map_defenses({"invariant_type": "role_access"}, "require(msg.sender != _referral)")
    assert r["coverage"] in (M.PARTIALLY_COVERS, M.DOES_NOT_COVER)


def test_unknown_when_no_source():
    assert M.map_defenses({"invariant_type": "ordering_race"}, "")["coverage"] == M.UNKNOWN_NEEDS_TRACE


def test_cross_contract_needs_trace():
    assert M.map_defenses({"invariant_type": "cross_contract_consistency"}, "pool.staticcall(x)")["coverage"] == M.UNKNOWN_NEEDS_TRACE


def test_partial_coverage_detected():
    # per_user_accounting with a state update but no invariant assert -> partial/none, not COVERS
    r = M.map_defenses({"invariant_type": "per_user_accounting"}, "bought += amount;")
    assert r["coverage"] != M.COVERS
