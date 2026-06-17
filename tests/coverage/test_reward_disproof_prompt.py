"""
P3 — Reward-accounting disproof contract (prompt-side conversion). No LLM, no network.

The Hybra eval showed the deep pass kept emitting PROSE reward clears, which scu.classify perpetually re-routes as
incomplete_reward_accounting_clear (route<->prose loop, never a finding). P3 puts a "Reward-accounting disproof
contract" in the deep-pass prompts so the model emits a structured `reward_accounting_checklist` (the validator's
exact 11 fields, answered concretely) instead of prose.

These tests assert:
  - the prompts CONTAIN the disproof contract (header, anti-loop rule, unknown=>not-cleared, "line unavailable",
    bad/good examples);
  - DRIFT GUARD: the prompt enumerates EXACTLY the reward_accounting fields the validator reads (spec_checklist_utils);
  - BEHAVIORAL: a concrete reward_accounting_checklist clears, while prose loops — at the validator unit level AND
    through the real coverage_sweep_write pipeline (no validator/routing/writer change).
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_context  # noqa: E402
scu = importlib.import_module("spec_checklist_utils")
vscc = importlib.import_module("validate_spec_checklist_clears")
sweep_write = importlib.import_module("coverage_sweep_write")

DEEP_PASS = ROOT / "prompts" / "deep_pass_packet.md"
COVERAGE_SWEEP = ROOT / "prompts" / "coverage_sweep.md"
SKILL = ROOT / ".claude" / "skills" / "coverage-sweep" / "SKILL.md"

REWARD_FIELDS = [f for name, _, f in scu.SURFACES if name == "reward_accounting"][0]


def _norm(p: Path) -> str:
    """Whitespace-normalized prompt text (so assertions survive line wrapping)."""
    return " ".join(p.read_text().split())


# ---------------- prompt-content assertions ----------------

def test_deep_pass_packet_has_reward_disproof_contract():
    t = _norm(DEEP_PASS)
    assert "Reward-accounting disproof contract" in t
    assert "reward_accounting_checklist" in t
    # anti-loop rule
    assert "do NOT re-emit the same prose" in t
    assert "incomplete_reward_accounting_clear" in t
    # unknown => not cleared
    assert "if any field is `unknown`" in t
    # anti-fabrication token
    assert '"line unavailable"' in t
    # bad/good examples (good uses the source-verified M-05 fact, not the inverted GaugeV2:512)
    assert "Reviewed reward accounting; rewards are conserved" in t
    assert "GaugeCL.sol:256" in t
    assert "GaugeV2.sol:512" not in t  # the inverted/fabricated example must NOT be taught


def test_coverage_sweep_has_reward_rule():
    t = _norm(COVERAGE_SWEEP)
    assert "Reward-accounting clears" in t
    assert "reward_accounting_checklist" in t
    assert "reward_accounting_spec_review" in t
    assert '"line unavailable"' in t
    # output spec lists the optional field
    assert "[reward_accounting_checklist]" in t


def test_skill_md_has_reward_bullet():
    t = _norm(SKILL)
    assert "reward_accounting_checklist" in t
    assert "reward_accounting_spec_review" in t


# ---------------- drift guard: prompt enumerates exactly the validator's fields ----------------

def test_prompt_lists_exactly_validator_reward_fields():
    """The prompt must name every reward_accounting field the validator reads (and the validator must define 11)."""
    assert len(REWARD_FIELDS) == 11, f"reward_accounting field count changed: {REWARD_FIELDS}"
    t = DEEP_PASS.read_text()
    missing = [f for f in REWARD_FIELDS if f not in t]
    assert not missing, f"deep_pass_packet.md omits reward fields the validator requires: {missing}"
    # coverage_sweep.md must also name them all
    cs = COVERAGE_SWEEP.read_text()
    missing_cs = [f for f in REWARD_FIELDS if f not in cs]
    assert not missing_cs, f"coverage_sweep.md omits reward fields the validator requires: {missing_cs}"


# ---------------- behavioral: concrete checklist clears, prose loops (validator unit level) ----------------

def _concrete_checklist():
    """A concrete reward_accounting_checklist (fn + var + file:line + yes/no + accounting vocab) per the prompt."""
    return {
        "reward_index_update_order": "no missing-ckpt · notifyRewardAmount · rewardRate · GaugeCL.sol:256 · rate set after accrue · safe",
        "totalsupply_sync_before_accrual": "yes · notifyRewardAmount · totalSupply · GaugeCL.sol:244 · synced before accrual",
        "balance_snapshot_timing": "yes · notifyRewardAmount · balanceOf · GaugeCL.sol:280 · checked after transfer",
        "transfer_side_effects": "no · notifyRewardAmount · rewardToken · GaugeCL.sol:277 · standard ERC20, no hook",
        "feeshares_before_after_rewards": "n/a · notifyRewardAmount · feeShares · line unavailable · no feeShares path",
        "fee_recipient_rewards": "no · notifyRewardAmount · DISTRIBUTION · GaugeCL.sol:277 · recipient is distributor",
        "rewards_on_share_transfer": "no · notifyRewardAmount · rewardRate · line unavailable · not a transfer path",
        "rewards_on_mint_burn": "no · notifyRewardAmount · rewardRate · line unavailable · not a mint/burn path",
        "reward_debt_update_order": "yes · notifyRewardAmount · rewardRateByEpoch · GaugeCL.sol:274 · updated before finish",
        "incentives_loop_bounds": "no loop · notifyRewardAmount · rewardRate · GaugeCL.sol:256 · O(1)",
        "totalsupply_includes_pending_feeshares": "yes · notifyRewardAmount · rollover · GaugeCL.sol:251 · rollover tracked",
    }


def _decision(checklist=None, prose=False):
    # NOTE: clear_reason/guard_or_invariant/no_impact_reason must avoid dependency-language (DEP_PHRASES/DEP_TOKENS
    # in dependency_clear_utils, e.g. "bounded by", "guard", "invariant") so this test isolates the spec-checklist
    # path rather than tripping the unrelated dependency-clear gate.
    d = {"manifest_id": "function:GaugeCL:notifyRewardAmount#abcd", "disposition": "cleared",
         "evidence_span": "GaugeCL.sol:239", "reason": "reward path reviewed against the disproof checklist",
         "attacker_reachability": "onlyDistribution caller restriction",
         "guard_or_invariant": "onlyDistribution caller restriction",
         "no_impact_reason": "rate stays within the contract token balance via the require at GaugeCL.sol:281"}
    if checklist:
        d["reward_accounting_checklist"] = checklist
        # notifyRewardAmount (score 4) is also a special-focus surface; a genuine reward clear must satisfy that
        # gate too. These fields are unrelated to the spec-checklist mechanism and do not feed dependency detection.
        d.update({"attacker_entrypoint": "onlyDistribution external call",
                  "cross_function_consumers": "earned()/getReward read rewardRate",
                  "downstream_sinks": "rewardToken transfer to gauge",
                  "state_transition_ordering": "accrue then rate update then periodFinish",
                  "value_source_consistency": "reward funded by DISTRIBUTION transferFrom"})
    if prose:
        d["reason"] = "Reviewed reward accounting; rewards are conserved and no issue found."
    return d


def _item():
    return {"id": "function:GaugeCL:notifyRewardAmount#abcd", "kind": "function", "contract": "GaugeCL",
            "file": "GaugeCL.sol", "name": "notifyRewardAmount",
            "signature": "function notifyRewardAmount(address token, uint256 rewardAmount) external",
            "in_scope": True, "attack_surface_score": 4, "tags": ["reward"],
            "source_span": {"start_line": 239, "end_line": 288}}


CTX = {"has_reward_layer": True, "has_external_markets": True}


def test_validator_unit_concrete_clears_prose_loops():
    item = _item()
    # prose-only clear -> scu.classify routes it incomplete (the loop)
    pcls = scu.classify(_decision(prose=True), item, CTX)
    assert pcls["status"] == "incomplete_reward_accounting_clear"
    # concrete checklist -> field-complete (scu ok) AND not boilerplate (P1 valid) -> CLEAR holds
    d = _decision(checklist=_concrete_checklist())
    assert scu.classify(d, item, CTX)["status"] == "ok"
    assert vscc.validate_clear(d, item, CTX)["status"] == "spec_checklist_valid"


# ---------------- behavioral: through the real coverage_sweep_write pipeline ----------------

@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    return tmp_path


def _write(ws, rel, obj):
    p = ws / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2))
    return p


def _run(mod, argv):
    old = sys.argv
    sys.argv = [mod.__name__] + argv
    try:
        return mod.main()
    finally:
        sys.argv = old


def _setup(ws, decision):
    _write(ws, "output/coverage_manifest.json", {"schema_version": 1, "source": {}, "items": [_item()]})
    _write(ws, "output/coverage_dispositions.json", {"dispositions": [
        {"manifest_id": "function:GaugeCL:notifyRewardAmount#abcd", "status": "unassigned",
         "evidence": [], "finding_refs": [], "clear_reason": None}]})
    _write(ws, "data/coverage_sweep/_decisions.json", {"decisions": [decision]})


def _disp(ws):
    return {d["manifest_id"]: d for d in
            json.loads((ws / "output" / "coverage_dispositions.json").read_text())["dispositions"]}


def test_writer_routes_prose_reward_clear_under_full_audit(ws, monkeypatch):
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")
    _setup(ws, _decision(prose=True))
    assert _run(sweep_write, []) == 0
    item = _disp(ws)["function:GaugeCL:notifyRewardAmount#abcd"]
    assert item["status"] == "assigned"
    assert item["assigned_agent"] == "reward_accounting_spec_review"


def test_writer_clears_concrete_reward_checklist_under_full_audit(ws, monkeypatch):
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")
    _setup(ws, _decision(checklist=_concrete_checklist()))
    assert _run(sweep_write, []) == 0
    assert _disp(ws)["function:GaugeCL:notifyRewardAmount#abcd"]["status"] == "cleared"
