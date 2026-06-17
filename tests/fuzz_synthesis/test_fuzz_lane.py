"""P141 fuzz lane regression — the fuzz-informed attacker-mindset synthesis must raise recall without weakening
the FP structure. Locks: (1) the cause-confirmation derivation (only reproduced + artifact-ruled-out signals are
'confirmed'); (2) only 'confirmed' records are promoted; (3) config gating is present and precision-safe;
(4) the agent is registered + forbidden from setting final severity/triage; (5) schemas are valid.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import fuzz_evidence_gate as feg  # noqa: E402


def _rec(**kw):
    base = dict(harness_kind="property", falsified=True, reproduced=True)
    base.update(kw)
    return base


# ---- (1) cause-confirmation derivation (the fuzz-lane FP guard) -------------------------------------------
def test_property_confirmed_requires_reproduced_and_negative_control():
    assert feg._derive_status(_rec(negative_control={"passed": True})) == "confirmed"


def test_held_when_invariant_not_falsified():
    assert feg._derive_status(_rec(falsified=False, negative_control={"passed": True})) == "held"


def test_harness_artifact_when_negative_control_failed():
    # an ill-formed property (control fails) is a harness artifact, never a finding
    assert feg._derive_status(_rec(negative_control={"passed": False})) == "harness_artifact"


def test_unreproduced_when_not_reproduced():
    assert feg._derive_status(_rec(reproduced=False, negative_control={"passed": True})) == "unreproduced"


def test_unreproduced_when_no_negative_control():
    # falsified + reproduced but cause not ruled out (no control) -> NOT promoted
    assert feg._derive_status(_rec()) == "unreproduced"


def test_differential_confirmed_only_when_oracle_sides_with_reference():
    assert feg._derive_status(_rec(harness_kind="differential", tie_break={"agrees_with": "reference"})) == "confirmed"
    assert feg._derive_status(_rec(harness_kind="differential", tie_break={"agrees_with": "sut"})) == "harness_artifact"
    assert feg._derive_status(_rec(harness_kind="differential", tie_break={"agrees_with": "neither"})) == "harness_artifact"
    assert feg._derive_status(_rec(harness_kind="differential", tie_break={})) == "unreproduced"


# ---- (2) only confirmed records are promoted to the synthesis specialist ----------------------------------
def test_only_confirmed_promoted(tmp_path):
    (tmp_path / "data" / "fuzz_results").mkdir(parents=True)
    recs = [
        {"evidence_id": "FZ-001", "status": "confirmed"},
        {"evidence_id": "FZ-002", "status": "held"},
        {"evidence_id": "FZ-003", "status": "harness_artifact"},
        {"evidence_id": "FZ-004", "status": "unreproduced"},
    ]
    (tmp_path / "data" / "fuzz_results" / "divergences.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in recs))
    got = feg.confirmed_evidence(tmp_path)
    assert [r["evidence_id"] for r in got] == ["FZ-001"]


# ---- (3) config gating present + precision-safe -----------------------------------------------------------
def test_config_gating_present_and_safe():
    c = json.loads((ROOT / "config" / "agent_policy.json").read_text())["fuzz_synthesis"]
    assert c["enabled"] is True
    assert c["require_cause_confirmation"] is True
    assert c["never_set_severity"] is True
    assert "move" in c["languages"]


# ---- (4) agent registered + forbidden from final severity/triage authority --------------------------------
def test_findings_schema_includes_fuzz_agent():
    s = json.loads((ROOT / "schema" / "findings_schema.json").read_text())
    assert "fuzz_attacker_synthesis" in s["properties"]["agent"]["enum"]


def test_agent_forbids_severity_and_triage_authority():
    t = (ROOT / "agents" / "fuzz_attacker_synthesis.md").read_text().lower()
    assert "never set final severity" in t
    assert "triage" in t
    assert "confirmed-only" in t or "status == \"confirmed\"" in t or 'status == "confirmed"' in t


# ---- (5) schemas valid ------------------------------------------------------------------------------------
def test_fuzz_evidence_schema_valid():
    s = json.loads((ROOT / "schemas" / "fuzz_evidence.schema.json").read_text())
    assert s["title"] == "FuzzEvidenceRecord"
    assert "confirmed" in s["properties"]["status"]["enum"]
