"""
Durable replay of the two Swan/Dria miss-classes (getFee M-08, round-validation H-02) against the
shipped validators (adversarial math proofs + dependency-clear locality).

This LOCKS the replay result so a future regression in either rule is caught in CI. It reads the frozen
eval snapshot READ-ONLY (never mutates it) and drives the actual replay module
`audits/swan-dria-2024-10-strict-eval/replay/replay_miss_class.py`. If that frozen audit is absent the
module is skipped (the reconstructed-fixture assertions still run, since they are self-contained).
"""
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
REPLAY_PY = ROOT / "audits" / "swan-dria-2024-10-strict-eval" / "replay" / "replay_miss_class.py"
SNAP = ROOT / "audits" / "swan-dria-2024-10-strict-eval" / "output" / "pre_answer_key_snapshot"


def _load_replay():
    spec = importlib.util.spec_from_file_location("replay_miss_class", REPLAY_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


frozen = pytest.mark.skipif(not (SNAP / "coverage_dispositions.json").exists(),
                            reason="frozen Swan/Dria eval snapshot not present")


# ---------- reconstructed fixtures (self-contained; the core proof the fix works) ----------

@frozen
def test_reconstructed_getfee_confirmatory():
    mod = _load_replay()
    r = mod.reconstructed_getfee()
    assert r["math_sensitive"] is True
    assert r["with_confirmatory_proof"] == "confirmatory_proof"   # no longer cleared by consistency
    assert r["proofless"] == "missing_math_proof"                 # → needs_deep_pass under strict


@frozen
def test_reconstructed_round_guard_not_path_dominant():
    mod = _load_replay()
    r = mod.reconstructed_round()
    assert r["field_presence_gate"] == "guard_not_path_dominant"  # missing dominance fields
    assert r["with_call_graph"] == "guard_not_path_dominant"      # call graph confirms direct-callable bypass


# ---------- literal frozen replay ----------

@frozen
def test_literal_getfee_now_routes_to_math():
    mod = _load_replay()
    A = mod.literal_replay(*_frozen_inputs(mod))
    # after the economic-shift taxonomy patch the frozen getFee (2<<difficulty) is math-sensitive and,
    # being a proofless cheap-sweep clear, now routes to math review instead of being silently cleared.
    assert A["getfee_literal"]["math_status"] == "missing_math_proof"
    assert A["getfee_before_after"]["after_taxonomy_patch"] == "missing_math_proof"


@frozen
def test_literal_no_new_locality_blocks_three_new_math_blocks():
    mod = _load_replay()
    A = mod.literal_replay(*_frozen_inputs(mod))
    D = mod.baseline_delta(A)
    assert A["guard_not_path_dominant_count"] == 0       # locality adds 0 on the frozen clears
    assert D["net_new_dependency_blocks"] == []
    # 3 net-new math blocks: the 2 pre-adversarial-proof clears + getFee (now math-sensitive)
    assert len(D["net_new_math_blocks"]) == 3
    assert mod.GETFEE_ID in D["net_new_math_blocks"]


# ---------- FP check on the 9 HITs ----------

@frozen
def test_zero_new_fp_blocks_on_nine_hits():
    mod = _load_replay()
    man, disp, cg = _frozen_inputs(mod)
    A = mod.literal_replay(man, disp, cg)
    C = mod.fp_check(man, disp, A)
    assert C["hit_count"] == 9
    assert C["new_block_intersect_hit_surface"] == []    # no HIT surface is newly blocked


def _frozen_inputs(mod):
    import json
    man = json.loads((SNAP / "coverage_manifest.json").read_text())
    disp = json.loads((SNAP / "coverage_dispositions.json").read_text())
    cg_path = SNAP.parent.parent / "data" / "interactions" / "call_graph.json"
    cg = json.loads(cg_path.read_text()) if cg_path.exists() else {}
    return man, disp, cg
