"""P227 Part A — bounded griefing/DoS cap in decide().

A proven, permissionless, material griefing/DoS whose impact is explicitly bounded (fee-loss / self-scoped /
selective / no principal theft) must stay MEDIUM, not auto-promote to High. The cap is narrow (structured
`bounded_griefing_dos` flag primary; a tight notes fallback), flag-independent, and DISJOINT from the P214
core-path DoS carve-out. Real Highs (theft / permanent_loss / privileged_control) and unflagged core-path DoS
must NOT be downgraded.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_p208_l3_readiness as v3  # noqa: E402

L3 = ROOT / "output_research" / "l3_readiness"


def _base(**over):
    """A record that, absent the cap, would decide High (permissionless + PASS + material + control)."""
    r = {
        "candidate_id": "T", "threat_ceiling": "HIGH_THREAD", "l3_status": "PASS",
        "poc_tier": "L3_REAL_CONTRACT_POC", "poc_path": "x", "poc_command": "x", "poc_result": "PASS",
        "actual_delta": "delta", "expected_delta_or_control": "control", "affected_asset_or_state": "asset",
        "attacker_model": "permissionless", "victim_or_protocol_loss": "loss", "magnitude_basis": "mag",
        "dependency_mocks": "external_only", "production_source_modified": False,
        "impact_class": "theft", "research_only": True, "routes_in_production": False,
    }
    r.update(over)
    return r


def _d(rec):
    os.environ.pop("AUDITWATCH_L3_READINESS", None)  # flag-OFF: cap is flag-independent
    return v3.decide(rec)


# ---- cap fires for bounded griefing / DoS ----
def test_griefing_bounded_flag_capped_medium():
    d = _d(_base(impact_class="griefing", bounded_griefing_dos=True))
    assert d["calibrated_severity"] == "medium"
    assert d["high_promotion_allowed"] is False
    assert "bounded griefing/DoS cap" in d["high_promotion_blocker"]


def test_dos_bounded_flag_capped_medium():
    d = _d(_base(impact_class="dos", bounded_griefing_dos=True))
    assert d["calibrated_severity"] == "medium" and d["high_promotion_allowed"] is False


def test_dos_notes_fallback_self_scoped_capped():
    d = _d(_base(impact_class="dos", victim_or_protocol_loss="self-scoped DoS, no principal loss; alternatives exist"))
    assert d["calibrated_severity"] == "medium" and d["high_promotion_allowed"] is False


# ---- cap does NOT fire: real Highs + unflagged core-path DoS stay High ----
def test_theft_high_not_downgraded():
    d = _d(_base(impact_class="theft"))
    assert d["calibrated_severity"] == "high" and d["high_promotion_allowed"] is True


def test_permanent_loss_high_not_downgraded():
    d = _d(_base(impact_class="permanent_loss"))
    assert d["high_promotion_allowed"] is True


def test_unflagged_core_path_dos_stays_high():
    # a DoS with NO bounded flag and NO bounded phrase -> cap must NOT fire (base High preserved)
    d = _d(_base(impact_class="dos", victim_or_protocol_loss="all depositors blocked",
                 magnitude_basis="core path unavailable", source_validity_notes="no workaround, protocol-wide"))
    assert d["calibrated_severity"] == "high" and d["high_promotion_allowed"] is True


def test_explicit_false_flag_not_capped():
    # author explicitly marks NOT bounded -> never capped even if a stray phrase exists
    d = _d(_base(impact_class="dos", bounded_griefing_dos=False,
                 source_validity_notes="bounded? no — core path"))
    assert d["high_promotion_allowed"] is True


def test_principal_phrase_overrides_bounded_notes():
    # notes contain both a bounded phrase AND a principal-loss phrase -> principal wins, not capped
    d = _d(_base(impact_class="dos", victim_or_protocol_loss="self-scoped but causes principal theft of user funds"))
    assert d["high_promotion_allowed"] is True


# ---- cap only applies to dos/griefing, not other classes ----
def test_cap_only_dos_griefing():
    d = _d(_base(impact_class="insolvency", bounded_griefing_dos=True))  # flag present but wrong class
    assert d["high_promotion_allowed"] is True


# ---- real records: SC-03 (permissionless, capped) and SC-04 (unknown) both Medium ----
# ---- P214 disjointness: a core-path DoS carve-out still upgrades flag-ON and the cap never touches it ----
def test_p214_carveout_still_upgrades_flag_on():
    soph03 = L3 / "SOPH-03.json"
    if not soph03.exists():
        return
    rec = json.loads(soph03.read_text())
    os.environ["AUDITWATCH_L3_READINESS"] = "1"
    try:
        d = v3.decide(rec)
        # SOPH-03 is l3_status=FAIL -> base medium -> P214 carve-out upgrades it; the P227 cap (allowed-only) never fires
        assert d["calibrated_severity"] == "high" and d["high_promotion_allowed"] is True
    finally:
        os.environ.pop("AUDITWATCH_L3_READINESS", None)
