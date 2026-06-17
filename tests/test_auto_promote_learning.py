"""
Tests for scripts/auto_promote_learning.py — recall-safe AUTO promotion of learning candidates.

Validation bar (user-locked): confirmed provenance + recall-safe + dedup. Anything failing the gate
stays staged for the human promote_learning.py path. Auto-promoted rules land in SEPARATE files; the
integrity-pinned curated baseline (rejection_rules.jsonl) is never mutated by automation.
"""
import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import auto_promote_learning as apl  # noqa: E402
import fp_pattern_check  # noqa: E402

CONFIRMED_REJECTION = {
    "rule_id": "FP-PROP-test1",
    "pattern_type": "requires_compromised_key",
    "trigger_conditions": ["attack requires a trusted operator key to be compromised"],
    "rejection_reason": "needs trusted operator hot key compromise to do anything",
    "vuln_type": "access-control",
    "agent": "access_control",
    "confidence_threshold": 0.85,
    "trust_level": 5,
    "_proposed": True,
    "_evidence_class": "human_confirmed",
}

# A known-VALID finding the recall-safety oracle protects (about oracle price manipulation).
VALID_FINDING = {
    "vuln_type": "oracle",
    "description": "oracle price manipulation via spot reserves enables draining the lending pool reserves",
    "impact": "",
    "_source_agent": "oracle",
}


@pytest.fixture
def env(tmp_path, monkeypatch):
    """Isolate every path the engine touches into tmp_path; default config; controlled TP corpus."""
    proj = tmp_path / "proj"
    staging = proj / "audit" / "data" / "learning" / "_proposed"
    staging.mkdir(parents=True)

    def fake_audit_path(*parts):
        p = proj / "audit"
        for part in parts:
            p = p / part
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    monkeypatch.setattr(apl, "PROJECT_ROOT", proj)
    monkeypatch.setattr(apl, "SHARED_REJECTION", proj / "data" / "fp_autopsies" / "rejection_rules.jsonl")
    monkeypatch.setattr(apl, "AUTO_REJECTION", proj / "data" / "fp_autopsies" / "auto_promoted_rules.jsonl")
    monkeypatch.setattr(apl, "AUTO_DUPES", proj / "data" / "auto_promoted_duplicate_registry.jsonl")
    monkeypatch.setattr(apl, "CONFIG_FILE", proj / "config" / "agent_policy.json")  # absent → DEFAULT_CONFIG
    monkeypatch.setattr(apl, "audit_path", fake_audit_path)
    monkeypatch.setattr(apl, "tp_corpus", lambda: [dict(VALID_FINDING)])

    apl.SHARED_REJECTION.parent.mkdir(parents=True, exist_ok=True)
    apl.SHARED_REJECTION.write_text("")  # empty curated baseline
    return {"proj": proj, "staging": staging, "audit_path": fake_audit_path}


def _stage(env, rows, fname="rejection_rules.jsonl"):
    (env["staging"] / fname).write_text("\n".join(json.dumps(r) for r in rows) + "\n")


def test_confirmed_recall_safe_candidate_is_promoted(env):
    _stage(env, [CONFIRMED_REJECTION])
    s = apl.run(kinds=["rejection"])
    assert s["promoted"] == 1 and s["left_staged"] == 0
    promoted = apl.load_jsonl(apl.AUTO_REJECTION)
    assert len(promoted) == 1
    assert promoted[0]["rule_id"] == "FP-PROP-test1"
    assert promoted[0]["promoted_by"] == "auto:recall_safe_v1"
    assert "_evidence_class" not in promoted[0]  # internal keys stripped
    # staging file consumed (no candidates left for human)
    assert not (env["staging"] / "rejection_rules.jsonl").exists()


def test_recall_regression_candidate_is_blocked(env):
    # rule whose reason/vuln_type/agent match the known-valid oracle finding → would reject it
    bad = dict(CONFIRMED_REJECTION)
    bad["rule_id"] = "FP-PROP-bad"
    bad["vuln_type"] = "oracle"
    bad["agent"] = "oracle"
    bad["rejection_reason"] = "oracle price manipulation via spot reserves draining the lending pool"
    bad["trigger_conditions"] = ["oracle price manipulation draining pool"]
    _stage(env, [bad])
    s = apl.run(kinds=["rejection"])
    assert s["promoted"] == 0 and s["left_staged"] == 1
    assert "recall_regression" in s["reasons"]
    assert not apl.AUTO_REJECTION.exists()  # nothing promoted
    # candidate remains staged for human review
    assert apl.load_jsonl(env["staging"] / "rejection_rules.jsonl")[0]["rule_id"] == "FP-PROP-bad"


def test_duplicate_candidate_is_blocked(env):
    # seed the curated baseline with the same structural signature
    apl.SHARED_REJECTION.write_text(json.dumps(apl._strip_internal(CONFIRMED_REJECTION)) + "\n")
    dup = dict(CONFIRMED_REJECTION)
    dup["rule_id"] = "FP-PROP-different-id"  # different id, same signature
    _stage(env, [dup])
    s = apl.run(kinds=["rejection"])
    assert s["promoted"] == 0 and s["reasons"].get("duplicate") == 1


def test_unconfirmed_provenance_is_blocked(env):
    weak = dict(CONFIRMED_REJECTION)
    weak["_evidence_class"] = "ai_inferred"
    _stage(env, [weak])
    s = apl.run(kinds=["rejection"])
    assert s["promoted"] == 0 and s["reasons"].get("unconfirmed_provenance") == 1


def test_human_only_marker_is_skipped(env):
    ho = dict(CONFIRMED_REJECTION)
    ho["status"] = "PROPOSED_HUMAN_PROMOTE_REQUIRED"
    _stage(env, [ho])
    s = apl.run(kinds=["rejection"])
    assert s["promoted"] == 0 and s["reasons"].get("human_only_marked") == 1
    assert apl.load_jsonl(env["staging"] / "rejection_rules.jsonl")  # left staged


def test_curated_baseline_is_byte_identical(env):
    apl.SHARED_REJECTION.write_text(json.dumps({"rule_id": "BASE-1", "pattern_type": "x"}) + "\n")
    before = hashlib.sha256(apl.SHARED_REJECTION.read_bytes()).hexdigest()
    _stage(env, [CONFIRMED_REJECTION])
    apl.run(kinds=["rejection"])
    after = hashlib.sha256(apl.SHARED_REJECTION.read_bytes()).hexdigest()
    assert before == after, "automation must never mutate the curated rejection_rules.jsonl"


def test_disabled_via_eval_mode(env, monkeypatch):
    _stage(env, [CONFIRMED_REJECTION])
    s = apl.run(kinds=["rejection"], eval_mode=True)
    assert s.get("skipped") == "eval_mode" and not apl.AUTO_REJECTION.exists()


def test_fp_pattern_check_loads_auto_file(tmp_path, monkeypatch):
    fp_dir = tmp_path / "fp"
    fp_dir.mkdir()
    (fp_dir / "auto_promoted_rules.jsonl").write_text(
        json.dumps({"rule_id": "AUTO-1", "pattern_type": "p", "rejection_reason": "r"}) + "\n"
    )
    monkeypatch.setattr(fp_pattern_check, "PROJECT_FP_DIR", fp_dir)
    monkeypatch.setattr(fp_pattern_check, "FP_DIR", fp_dir)
    rules = fp_pattern_check.load_rejection_rules()
    assert any(r["rule_id"] == "AUTO-1" for r in rules)
