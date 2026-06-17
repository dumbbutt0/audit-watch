"""P110: harness scaffold generation — RESEARCH-ONLY, un-wired.

Proves scaffolds are INERT skeletons (banner + actor/handle decls + setUp TODOs + vm.skip test stub), that the
inertness guard accepts skeletons and REJECTS planted exploit logic / promotion tokens, that no
severity/submission/report state is produced, and that generation is deterministic.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "assisted"))
import generate_harness_scaffold as G  # noqa: E402

_ASSESS = {
    "subject": "fx", "contract": "Vault", "function": "withdraw", "classification": "HARNESS_MODERATE",
    "rationale": "multi-contract", "dependency_map": {"in_scope_imports": ["./Token.sol"],
                                                      "in_scope_deployable": ["Token", "Vault"],
                                                      "external_integrations": [], "tokens": ["ERC20"],
                                                      "interfaces_referenced": ["IERC20"]},
    "environment": {"fork_required": False, "fork_reasons": [], "deployment_sequence": ["Token", "Vault"],
                    "config_required": True, "funding_required": True, "setup_steps": 4},
    "actor_model": [{"role": "attacker", "evidence": "EOA"}, {"role": "admin", "evidence": "owner"}],
}

_FORK_ASSESS = {**_ASSESS, "classification": "HARNESS_COMPLEX",
                "environment": {**_ASSESS["environment"], "fork_required": True,
                                "fork_reasons": ["hardcoded mainnet address"]}}


def test_flags_unwired():
    assert G.FLAGS["is_gate"] is False
    assert G.FLAGS["routes_in_production"] is False
    assert G.FLAGS["routed_manifest_ids"] == []


def test_self_test_passes():
    assert G._self_test() == 0


def test_scaffold_structure():
    s = G.generate_scaffold(_ASSESS)
    assert "SCAFFOLD ONLY" in s
    assert "vm.skip(true)" in s
    assert "TODO" in s
    assert 'makeAddr("attacker")' in s and 'makeAddr("admin")' in s
    assert "Vault vault;" in s and "Token token;" in s
    assert "TODO[deploy]" in s and "TODO[config]" in s and "TODO[fund]" in s


def test_fork_scaffold_has_fork_todo():
    s = G.generate_scaffold(_FORK_ASSESS)
    assert "TODO[fork]" in s


def test_generated_scaffold_is_inert():
    assert G.assert_scaffold_is_inert(G.generate_scaffold(_ASSESS)) is True
    assert G.assert_scaffold_is_inert(G.generate_scaffold(_FORK_ASSESS)) is True


def test_planted_exploit_is_rejected():
    s = G.generate_scaffold(_ASSESS)
    bad = s.replace("vm.skip(true); // inert: scaffold is not an executable adversarial sequence",
                    "IERC20(t).transfer(attacker, 1e18); assertGt(t.balanceOf(attacker), 1e18);")
    assert G.assert_scaffold_is_inert(bad) is False


def test_promotion_token_in_code_is_rejected():
    assert G.assert_scaffold_is_inert("// SCAFFOLD ONLY\nvm.skip(true) // TODO\nseverity = high;") is False
    assert G.assert_scaffold_is_inert("// SCAFFOLD ONLY\nvm.skip(true) // TODO\nsubmission_ready = true;") is False


def test_missing_skeleton_pieces_rejected():
    assert G.assert_scaffold_is_inert("contract X {}") is False  # no banner/skip/todo


def test_no_forbidden_tokens_in_generated_code():
    s = G.generate_scaffold(_FORK_ASSESS)
    code = G._code_only(s).lower()
    for tok in (".call(", "assertgt(", "asserteq(", "severity", "submission", "validated", "exploit", "profit"):
        assert tok not in code


def test_run_all_inert_and_deterministic():
    feas = {"invariant": "x", "assessments": [_ASSESS, _FORK_ASSESS], "controls": [],
            "metrics": {"total_candidates": 2}}
    a = G.run(feas)
    b = G.run(feas)
    assert a["all_scaffolds_inert"] is True
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
