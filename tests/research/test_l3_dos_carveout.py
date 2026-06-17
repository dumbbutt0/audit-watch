"""P214 — tests for the flag-gated deterministic core-path DoS carve-out in validate_p208_l3_readiness.decide().

Flag-off: decide() is byte-equivalent to pre-P214 (no carve-out keys, no upgrade).
Flag-on: a declared medium-DoS carve-out candidate upgrades to high ONLY when all 10 criteria + guards pass.
"""
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_p208_l3_readiness as v208  # noqa: E402

CRITERIA = v208._DOS_CARVEOUT_CRITERIA


def _rec(**over):
    """A base medium-DoS carve-out candidate with all 10 criteria true; override to mutate."""
    r = {
        "candidate_id": "T", "threat_ceiling": "HIGH_THREAD", "l3_status": "FAIL", "impact_class": "dos",
        "poc_tier": "L3_REAL_CONTRACT_POC", "source_validity_notes": "deterministic deposit DoS",
        "actual_delta": "depositX reverts", "victim_or_protocol_loss": "class of depositors blocked",
        "magnitude_basis": "core path DoS", "affected_asset_or_state": "deposit path",
        "expected_delta_or_control": "control: honest token succeeds", "attacker_model": "permissionless",
        "dependency_mocks": "external_only", "production_source_modified": False,
        "dos_carveout_candidate": True, "dos_carveout_human_judgment_required": True,
        "dos_carveout_notes": "supported asset; no workaround; class-wide; not self-inflicted",
    }
    for k in CRITERIA:
        r[k] = True
    r.update(over)
    return r


@pytest.fixture(autouse=True)
def _clean_flag():
    saved = os.environ.pop("AUDITWATCH_L3_READINESS", None)
    yield
    os.environ.pop("AUDITWATCH_L3_READINESS", None)
    if saved is not None:
        os.environ["AUDITWATCH_L3_READINESS"] = saved


def _on():
    os.environ["AUDITWATCH_L3_READINESS"] = "1"


# ----- flag OFF: output-equivalent to pre-P214 -----
def test_flag_off_no_carveout_keys_no_upgrade():
    d = v208.decide(_rec())
    assert d["calibrated_severity"] == "medium"
    assert d["high_promotion_allowed"] is False
    assert "dos_carveout_evaluated" not in d and "dos_carveout_applied" not in d


# ----- flag ON: the positive case -----
def test_flag_on_full_carveout_upgrades_to_high():
    _on()
    d = v208.decide(_rec())
    assert d["calibrated_severity"] == "high"
    assert d["high_promotion_allowed"] is True
    assert d["dos_carveout_applied"] is True
    assert d["submission_state"] == "ready_for_submission_package"


@pytest.mark.parametrize("missing", v208._DOS_CARVEOUT_CRITERIA)
def test_flag_on_missing_one_criterion_blocks(missing):
    _on()
    d = v208.decide(_rec(**{missing: False}))
    assert d["calibrated_severity"] == "medium"
    assert d["high_promotion_allowed"] is False
    assert d["dos_carveout_applied"] is False
    assert missing in d["dos_carveout_missing_criteria"]


def test_flag_on_not_candidate_no_upgrade():
    _on()
    d = v208.decide(_rec(dos_carveout_candidate=False))
    assert d["calibrated_severity"] == "medium"
    assert d["dos_carveout_applied"] is False


def test_flag_on_needs_harness_not_upgraded():
    _on()
    d = v208.decide(_rec(l3_status="NEEDS_HARNESS"))
    assert d["calibrated_severity"] != "high"
    assert d["dos_carveout_applied"] is False


def test_flag_on_source_refuted_stays_invalid():
    _on()
    d = v208.decide(_rec(source_validity_notes="source REFUTES the mechanism: guard present"))
    assert d["calibrated_severity"] == "invalid"
    assert d["dos_carveout_applied"] is False


def test_flag_on_production_source_modified_not_upgraded():
    _on()
    d = v208.decide(_rec(production_source_modified=True))
    assert d["calibrated_severity"] != "high"
    assert d["dos_carveout_applied"] is False


def test_flag_on_human_judgment_required_without_notes_not_upgraded():
    _on()
    d = v208.decide(_rec(dos_carveout_notes=""))
    assert d["calibrated_severity"] != "high"
    assert "human_judgment_required" in d["dos_carveout_blocker"]


def test_flag_on_malformed_empty_record_fail_closed():
    _on()
    d = v208.decide({})
    assert d["high_promotion_allowed"] is False
    assert d["calibrated_severity"] != "high"


def test_flag_on_non_dos_high_path_unaffected():
    # a real theft High (allowed via base conditions) must remain high and not be touched by the carve-out
    _on()
    rec = _rec(impact_class="theft", l3_status="PASS")
    d = v208.decide(rec)
    assert d["calibrated_severity"] == "high"  # base already high; carve-out is a no-op (cal!=medium guard)


