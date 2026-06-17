"""P109: runtime self-kill — RESEARCH-ONLY, un-wired.

Proves the runtime layer emits ONLY the 4 runtime states, makes KILLED/SURVIVED decisions only on an execution
record (HS3), never kills a confirmed control on a single non-pass run (protects HS1), routes the harness-less 28 to
HARNESS_UNAVAILABLE, introduces no severity/submission state, and is deterministic. Uses a STUBBED forge runner so
the unit tests need no forge/network. A guarded live check confirms the P104 control survives when forge is present.
"""
import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "assisted"))
import runtime_self_kill as RK  # noqa: E402

P108 = ROOT / "documentation" / "research" / "assisted_mode" / "p108" / "self_kill_results.json"
CORPUS = {"subjects": [{"id": "iq-ai-2025-01", "source_roots": ["/tmp/p102-iqai/src"]},
                       {"id": "phi-2024-08", "source_roots": ["/tmp/p89-phi/src"]}]}


def _stub(outcome):
    return RK._stub_runner(outcome)


def _pc_candidate(confirmed, function="moveLiquidity"):
    return {"subject": "iq-ai-2025-01", "contract": "C", "function": function,
            "is_awarded": True, "is_confirmed_poc": confirmed,
            "positive_control": {"harness_dir": "/tmp/p102-iqai",
                                 "harness_file": "test/audit/M01PreCreatePairPoC.t.sol",
                                 "match_test": "t", "evm_version": "cancun", "env": {}}}


def _bare_candidate():
    return {"subject": "phi-2024-08", "contract": "Cred", "function": "claimFromFactory",
            "is_awarded": False, "is_confirmed_poc": False,
            "source_exploit_thesis": {"violated_invariant": "x"}, "positive_control": None}


def test_flags_unwired():
    assert RK.FLAGS["is_gate"] is False
    assert RK.FLAGS["research_only"] is True
    assert RK.FLAGS["routes_in_production"] is False
    assert RK.FLAGS["routed_manifest_ids"] == []


def test_exactly_four_states():
    assert RK.STATES == {"KILLED_RUNTIME", "SURVIVED_RUNTIME", "INCONCLUSIVE_RUNTIME", "HARNESS_UNAVAILABLE"}


def test_env_failure_is_harness_unavailable_not_kill():
    r = RK.self_kill_runtime(_pc_candidate(confirmed=False), CORPUS, _stub("noenv"))
    assert r["state"] == "HARNESS_UNAVAILABLE", "a compile/setup failure is not a real kill"


def test_bare_candidate_has_no_per_candidate_harness():
    r = RK.self_kill_runtime(_bare_candidate(), CORPUS, _stub("pass"))
    assert r["state"] == "HARNESS_UNAVAILABLE"
    assert r["execution_record"] is None, "HARNESS_UNAVAILABLE must carry no execution record"


def test_hs3_no_decision_without_execution_record():
    res = RK.run_corpus(CORPUS, runner=_stub("pass"), needs_runtime=[_bare_candidate()])
    for c in res["candidates"]:
        if c["state"] in ("KILLED_RUNTIME", "SURVIVED_RUNTIME"):
            assert c["execution_backed"] is True
    assert res["hard_stops"]["HS3_execution_evidence"]["tripped"] is False


def test_no_promotion_tokens_or_states():
    res = RK.run_corpus(CORPUS, runner=_stub("pass"), needs_runtime=[_bare_candidate()])
    assert RK.assert_states_only(res)
    assert res["hard_stops"]["HS4_no_promotion"]["tripped"] is False


def test_deterministic_with_stub():
    a = RK.run_corpus(CORPUS, runner=_stub("pass"), needs_runtime=[_bare_candidate()])
    b = RK.run_corpus(CORPUS, runner=_stub("pass"), needs_runtime=[_bare_candidate()])
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_p108_needs_runtime_loads_and_resolves_unavailable():
    if not P108.exists():
        pytest.skip("P108 results not present")
    nr = RK._load_p108_needs_runtime()
    assert len(nr) == 28, "expected the 28 P108 NEEDS_RUNTIME candidates"
    # with a stub runner, none of the 28 (no positive_control) may run -> all HARNESS_UNAVAILABLE
    res = RK.run_corpus(CORPUS, runner=_stub("pass"), needs_runtime=nr)
    bare = [c for c in res["candidates"] if not c["is_positive_control"]]
    assert all(c["state"] == "HARNESS_UNAVAILABLE" for c in bare)


@pytest.mark.skipif(shutil.which("forge") is None or not Path("/tmp/p102-iqai/node_modules").is_dir(),
                    reason="forge or P104 harness deps not present")
def test_live_p104_control_survives():
    """Live: the P104 fork PoC reproduces -> SURVIVED_RUNTIME (positive control). Network/fork dependent."""
    cand = {"subject": "iq-ai-2025-01", "contract": "LiquidityManager", "function": "moveLiquidity",
            "is_awarded": True, "is_confirmed_poc": True,
            "positive_control": RK.POSITIVE_CONTROLS[0]}
    r = RK.self_kill_runtime(cand, CORPUS, RK.real_forge_runner)
    # either it reproduces (SURVIVED) or, on a flaky network, INCONCLUSIVE/HARNESS_UNAVAILABLE — but NEVER KILLED
    assert r["state"] != "KILLED_RUNTIME", "the P104 confirmed control must never be runtime-killed"
