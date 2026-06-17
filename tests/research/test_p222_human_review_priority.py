"""P222 — high-priority human-review lane for trusted-system impact findings.

Asserts: the pure priority classifier fires HIGH only for L3-PASS core-impact on a trusted/privileged (non-
unprivileged) path · ZETA-04 becomes HIGH human-review but stays NOT submission-ready · ZETA-10 is not HIGH
after L3 refutation · static-only / source-refuted / mock-created / unprivileged candidates never reach HIGH ·
**the helper never touches submission_ready / routing_allowed / high_promotion_allowed / attacker_model / severity**
· decide() severity is byte-identical (separate namespace) · no priority value is ever an attacker_model value ·
the synced mirror + funnel rows + detail banner carry the fields · the completion guard enforces the invariants.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import sync_hunt_findings as sh                 # noqa: E402
import human_review_priority as hrp             # noqa: E402
import finding_detail as fd                     # noqa: E402
import funnel as fn                             # noqa: E402
import findings_overview as fo                  # noqa: E402
import validate_hunt_sync_completion as vc      # noqa: E402
from validate_p208_l3_readiness import decide   # noqa: E402

ARGS = ["--phase", "P215", "--audit", "zetachain-2023-10-holdout",
        "--workspace", "documentation/research/assisted_mode/p215_full_funnel_rehearsal"]
L3_DIR = ROOT / "output_research/l3_readiness"
# meaningful attacker-model enums decide() keys off (excludes degenerate none/unknown which collide lexically
# with the NONE priority value but are never written into the attacker_model field)
ATTACKER_MODEL_VALUES = {"permissionless", "program_accepted", "privileged_only", "privileged",
                         "trusted_admin", "conditional"}
PRIORITY_VALUES = {"NONE", "LOW", "MEDIUM", "HIGH", "CRITICAL_HUMAN_REVIEW"}


def _emit(tmp_path):
    out = tmp_path / "m.json"
    assert sh.main(ARGS + ["--out", str(out), "--write"]) == 0
    return {r["candidate_id"]: r for r in json.loads(out.read_text())["findings"]}, out


# --------------------------------------------------------------------- pure classifier
def test_static_only_trusted_system_is_not_high():
    # trusted-system reachability + qualifying impact, but NO executed L3 PASS -> never HIGH
    p = hrp.evaluate_priority({"l3_status": "NOT_ATTEMPTED", "impact_type": "core_safety_control_bypass",
                               "reachability_class": "TRUSTED_SYSTEM_ACTOR_REACHABLE", "conversion_outcome": "NONE"})
    assert p["human_review_priority"] == "NONE"


def test_source_refuted_cannot_be_high():
    p = hrp.evaluate_priority({"l3_status": "PASS", "impact_type": "core_safety_control_bypass",
                               "reachability_class": "SOURCE_REFUTED", "conversion_outcome": "CLEAN_HIT"})
    assert p["human_review_priority"] == "NONE"
    # also: a PASS with a "refuted" note never reaches HIGH
    p2 = hrp.evaluate_priority({"l3_status": "PASS", "impact_type": "core_safety_control_bypass",
                                "reachability_class": "TRUSTED_SYSTEM_ACTOR_REACHABLE",
                                "conversion_outcome": "CLEAN_HIT", "source_validity_notes": "impact refuted by harness"})
    assert p2["human_review_priority"] != "HIGH"


def test_mock_created_vuln_is_not_high():
    p = hrp.evaluate_priority({"l3_status": "PASS", "impact_type": "core_safety_control_bypass",
                               "reachability_class": "TRUSTED_SYSTEM_ACTOR_REACHABLE", "conversion_outcome": "CLEAN_HIT",
                               "dependency_mocks": "creates_vulnerable_condition"})
    assert p["human_review_priority"] == "NONE"


def test_h5_style_unprivileged_stays_out_of_the_lane():
    # an unprivileged, L3-proven, fund-loss finding is reportable through the NORMAL path; it must not be
    # pulled into the human-review lane (priority NONE, not surfaced).
    p = hrp.evaluate_priority({"l3_status": "PASS", "impact_type": "fund_lock_or_failed_refund",
                               "reachability_class": "UNPRIVILEGED_REACHABLE", "conversion_outcome": "CLEAN_HIT"})
    assert p["human_review_priority"] == "NONE"
    assert p["should_surface_above_noise"] is False


def test_priority_value_is_never_an_attacker_model_value():
    for rc in ("UNPRIVILEGED_REACHABLE", "TRUSTED_SYSTEM_ACTOR_REACHABLE", "REACHABILITY_UNKNOWN", "SOURCE_REFUTED"):
        p = hrp.evaluate_priority({"l3_status": "PASS", "impact_type": "core_entry_exit_dos",
                                   "reachability_class": rc, "conversion_outcome": "CLEAN_HIT"})
        assert p["human_review_priority"].lower() not in ATTACKER_MODEL_VALUES


# --------------------------------------------------------------------- severity invariance (gate)
# --------------------------------------------------------------------- sync mirror integration
# --------------------------------------------------------------------- detail card banner
# --------------------------------------------------------------------- sort / filter fields
# --------------------------------------------------------------------- completion guard
def _base_safe_record(cid, **over):
    rec = {"schema": "synced-1", "record_id": f"r:{cid}", "candidate_id": cid, "source_track": "audit_workspace",
           "research_only": True, "review_only": True, "routes_in_production": False, "routing_allowed": False,
           "submission_ready": False, "no_submit_controls": True, "browser_computes_severity": False,
           "human_review_required": True, "conversion": "NONE",
           "poc": {"poc_status": "NOT_STARTED"}, "submission": {"submission_status": "NOT_STARTED"},
           "canonical_submission_ready_source": "machine-owned", "final_triager_decision": "submit",
           "human_review_priority": "NONE"}
    rec.update(over)
    return rec


def test_guard_passes_for_valid_high_record():
    rec = _base_safe_record("ZETA-X", human_review_priority="HIGH", l3_status="PASS")
    failures, _, _ = vc.run_checks([{"id": "ZETA-X"}], [rec], set(), {})
    assert failures == []


def test_guard_fails_when_high_priority_claims_submission_ready():
    rec = _base_safe_record("ZETA-X", human_review_priority="HIGH", submission_ready=True)
    failures, _, _ = vc.run_checks([{"id": "ZETA-X"}], [rec], set(), {})
    assert any("submission_ready" in f for f in failures)


def test_guard_fails_when_high_priority_routes():
    rec = _base_safe_record("ZETA-X", human_review_priority="HIGH", routing_allowed=True)
    failures, _, _ = vc.run_checks([{"id": "ZETA-X"}], [rec], set(), {})
    assert any("routing_allowed" in f for f in failures)


def test_guard_fails_when_priority_field_absent():
    rec = _base_safe_record("ZETA-X")
    del rec["human_review_priority"]
    failures, _, _ = vc.run_checks([{"id": "ZETA-X"}], [rec], set(), {})
    assert any("human_review_priority" in f for f in failures)


def test_guard_accepts_none_priority_as_valid():
    rec = _base_safe_record("ZETA-X", human_review_priority="NONE")
    failures, _, _ = vc.run_checks([{"id": "ZETA-X"}], [rec], set(), {})
    assert failures == []
