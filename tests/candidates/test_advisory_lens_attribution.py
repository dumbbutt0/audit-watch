"""Advisory-lens attribution (review J5 measurement hook). Joins lens hits -> findings -> canonical state so
lens LIVE value is measurable. Hermetic tmp audit. Asserts: a lens hit whose manifest/loc became a finding is
counted (with its canonical state); a hit that became nothing is counted as hit-but-not-finding; and the step
is pure measurement (no disposition mutation)."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_context as ac  # noqa: E402
import advisory_lens_attribution as ala  # noqa: E402


@pytest.fixture
def patched(tmp_path, monkeypatch):
    (tmp_path / "output" / "candidates").mkdir(parents=True)
    monkeypatch.setattr(ac, "get_audit_root", lambda: tmp_path)
    monkeypatch.setattr(ac, "get_active_audit", lambda: {"audit_id": "t"})
    return tmp_path


def _write(tmp, gate, merged, records):
    out = tmp / "output"
    (out / "advisory_escalation_gate.json").write_text(json.dumps(gate))
    (out / "merged_findings.json").write_text(json.dumps({"findings": merged}))
    for r in records:
        (out / "candidates" / f"{r['id']}.json").write_text(json.dumps(r))


def test_hit_that_became_a_ready_finding_is_attributed(patched):
    # recipient_custody flagged manifest m1; F-1 carries m1 in manifest_refs and is canonical 'ready'.
    _write(
        patched,
        gate={"escalations": [{"lens": "recipient_custody", "manifest_id": "m1",
                               "file": "A.sol", "name": "withdraw", "routed_to": "needs_deep_pass"}]},
        merged=[{"id": "F-1", "manifest_refs": ["m1"], "location": {"file": "A.sol", "function": "withdraw"}}],
        records=[{"id": "F-1", "state": "ready", "evidence": {}}],
    )
    doc = ala.attribute(patched)
    L = doc["lenses"]["recipient_custody"]
    assert L["hits"] == 1 and L["routed_to_deep_pass"] == 1
    assert L["became_finding"] == 1 and L["became_ready"] == 1
    assert L["finding_ids"] == ["F-1"]


def test_hit_that_became_nothing_is_counted_but_not_a_finding(patched):
    # cross_function_invariant flagged m9; no finding references m9 or its loc -> hit, became_finding 0.
    _write(
        patched,
        gate={"escalations": [{"lens": "cross_function_invariant", "manifest_id": "m9",
                               "file": "B.sol", "name": "poke", "routed_to": "advisory_only"}]},
        merged=[{"id": "F-1", "manifest_refs": ["m1"], "location": {"file": "A.sol", "function": "withdraw"}}],
        records=[{"id": "F-1", "state": "ready"}],
    )
    doc = ala.attribute(patched)
    L = doc["lenses"]["cross_function_invariant"]
    assert L["hits"] == 1 and L["became_finding"] == 0 and L["finding_ids"] == []


def test_loc_match_when_no_manifest_ref(patched):
    # promoted advisory hit (manifest_id None) matched by (file, function) to a human_pending finding.
    _write(
        patched,
        gate={"promoted_advisory_lens_hits": [{"lens": "nonstandard_permit", "manifest_id": None,
                                               "file": "C.sol", "name": "permit"}]},
        merged=[{"id": "F-2", "location": {"file": "C.sol", "function": "permit"}}],
        records=[{"id": "F-2", "state": "human_pending"}],
    )
    doc = ala.attribute(patched)
    L = doc["lenses"]["nonstandard_permit"]
    assert L["became_finding"] == 1 and L["by_state"] == {"human_pending": 1} and L["became_ready"] == 0


def test_measurement_only_writes_attribution_not_dispositions(patched):
    _write(patched, gate={"escalations": []}, merged=[], records=[])
    ala.attribute(patched)
    assert (patched / "output" / "advisory_lens_attribution.json").exists()
    # never creates/mutates a dispositions file
    assert not (patched / "data" / "coverage").exists()
