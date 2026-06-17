"""P293 — cross-function, naming-flexible reward-index lens (Lens 3). Behavior + refutation + corpus regressions.

Research-only, advisory. The lens lifts ONLY on a source-backed reward-debt/first-depositor deviation with a
connectable pending formula, across the candidate body + resolved P283 trace callees + same-contract siblings.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/research"))
import invariant_delta_deriver as idd  # noqa: E402

D = ROOT / "documentation/research/assisted_mode/p293_cross_function_reward_index_lens"
O = D / "outputs"
# P293 edits ONLY the deriver + its config + (fill-if-missing) the completion deriver. The tracer and the gate stay
# byte-identical — assert that here (the do-not-edit anchors for this phase).
BYTE_IDENTICAL = {
    "scripts/research/cross_function_value_tracer.py": "f28f0620d3d3548a",   # tracer NOT edited
    "scripts/research/poc_readiness_evidence_gate.py": "7afdc560bc4e96cd",   # gate NOT edited
    "scripts/research/award_class_coverage_router.py": "6debb753b45f1833",   # P273 router NOT edited
    "scripts/sibling_function_parity_taxonomy.py": "e504383db8f33844",       # reused detector (read-only)
    "scripts/registry_position_lifecycle_taxonomy.py": "da83a7acc217c706",
}
FORBIDDEN = {
    "scripts/dashboard_sync.py": "c1af70e1", "prompts/deep_trace.md": "c095c426",
    "scripts/min_confirm_gate.py": "2a15169a", "scripts/confirm_gate.py": "afc481c9",
    "scripts/validate_p208_l3_readiness.py": "ae55eb80",
}
DOC_FILES = ("SETUP.md", "REWARD_INDEX_LENS_DESIGN.md", "IMPLEMENTATION_NOTES.md", "REMAP_RESULTS.md",
             "EVIDENCE_AUDIT.md", "REPAIR_BACKLOG.md", "LIMITATIONS.md", "VERDICT.md", "ROLLBACK_PLAN.md")
VERDICTS = ("A — REWARD_INDEX_LENS_READY_FOR_BLIND_RETEST", "B — REWARD_INDEX_LENS_PROMISING_NEEDS_REFINEMENT",
            "C — REWARD_INDEX_LENS_TOO_NOISY", "D — ABORTED_CONSTRAINT_VIOLATION")


def _it(name, c="C"):
    return {"name": name, "contract": c, "signature": f"function {name}()"}


def _mani(items):
    return {"items": [dict(kind="function", **it) for it in items]}


def _cross(item, body, manifest=None, trace=None):
    return idd._lens_reward_index_cross(item, body, manifest or _mani([]), "aud", trace)


# ---- the five patterns lift to LENS3_READY ----
def test_pattern_a_missing_user_index_init():
    body = ("function stake(uint a) external { _shares[msg.sender] += a; uint g = rewardPerToken; "
            "uint owed = rewardPerToken * _shares[msg.sender] / totalShares; }")
    r = _cross(_it("stake"), body)
    assert r["lens3_status"] == "LENS3_READY" and r["lens3_pattern"] == "MISSING_USER_INDEX_INIT"
    assert r["invariant_delta_status"] == "REWARD_INDEX_INIT_FOUND"


def test_pattern_b_share_increase_before_checkpoint():
    body = ("function stake(uint a) external { _balances[msg.sender] += a; updateReward(msg.sender); "
            "uint i = rewardPerToken; uint owed = rewardPerToken*_balances[msg.sender]/totalSupply "
            "- rewardDebt[msg.sender]; }")
    r = _cross(_it("stake"), body)
    assert r["lens3_status"] == "LENS3_READY" and r["lens3_pattern"] == "SHARE_INCREASE_BEFORE_CHECKPOINT"


def test_pattern_c_global_index_not_paired():
    body = ("function deposit(uint a) external { rewardPerToken += newRewards; _shares[msg.sender] += a; "
            "uint owed = rewardPerToken*_shares[msg.sender]/totalShares - userRewardPerTokenPaid[msg.sender]; }")
    r = _cross(_it("deposit"), body)
    assert r["lens3_status"] == "LENS3_READY" and r["lens3_pattern"] == "GLOBAL_INDEX_NOT_PAIRED"


def test_pattern_d_first_depositor_zero_supply():
    body = ("function increase(uint a) external { if (totalShares != 0) { user.virtualRewards += "
            "totalRewards*a/totalShares; } user.userShare += a; totalShares += a; }")
    r = _cross(_it("increase"), body)
    assert r["lens3_status"] == "LENS3_READY" and r["lens3_pattern"] == "FIRST_DEPOSITOR_ZERO_SUPPLY"


def test_pattern_e_loss_reward_index_contagion():
    body = "function join(uint a) external { uint l = totalLoss; _stakes[msg.sender] += a; }"
    r = _cross(_it("join"), body)
    assert r["lens3_status"] == "LENS3_READY" and r["lens3_pattern"] == "LOSS_REWARD_INDEX_CONTAGION"


# ---- FP controls: refute / hold / silent ----
def test_generic_staking_balance_update_does_not_lift():
    # share write only, no global index / reward / loss -> silent (None), so derive() is unchanged elsewhere
    assert _cross(_it("stake"), "function stake(uint a) external { _balances[msg.sender] += a; }") is None


def test_updatereward_before_share_refutes():
    body = ("function stake(uint a) external { updateReward(msg.sender); _balances[msg.sender] += a; "
            "uint i = rewardPerToken; uint owed = rewardPerToken*_balances[msg.sender]/totalSupply "
            "- rewardDebt[msg.sender]; }")
    r = _cross(_it("stake"), body)
    assert r["lens3_status"] == "LENS3_REFUTED_NORMAL_CHECKPOINT" and r["invariant_delta_status"] == "NO_REFERENCE"


def test_atomic_init_refutes():
    body = ("function deposit(uint a) external { userRewardPerTokenPaid[msg.sender] = rewardPerToken; "
            "_balances[msg.sender] += a; uint owed = rewardPerToken*_balances[msg.sender]/totalSupply "
            "- userRewardPerTokenPaid[msg.sender]; }")
    assert _cross(_it("deposit"), body)["lens3_status"] == "LENS3_REFUTED_NORMAL_CHECKPOINT"


def test_unresolved_trace_blocks():
    body = "function stake(uint a) external { rewardDebt[msg.sender] = 0; _shares[msg.sender] += a; _accrue(); }"
    te = {"trace_status": "TRACE_UNRESOLVED", "unresolved_callees": ["_accrue"], "trace_path": []}
    assert _cross(_it("stake"), body, trace=te)["lens3_status"] == "LENS3_TRACE_UNRESOLVED"


def test_no_award_text_consumed():
    body = ("function increase(uint a) external { if (totalShares != 0) { user.virtualRewards += "
            "totalRewards*a/totalShares; } user.userShare += a; }")
    it = dict(_it("increase"), award_title="SECRET AWARD TITLE", award_body="answer key text")
    blob = json.dumps(_cross(it, body)).lower()
    assert "secret award title" not in blob and "answer key text" not in blob


# ---- cross-function resolution (sibling pending formula + trace callee) ----
def test_increaseusershare_style_reaches_lens_via_sibling(monkeypatch):
    bodies = {"userRewardForPool": "function userRewardForPool() public view returns(uint){ "
              "uint r = totalRewards*user.userShare/totalShares; return r - user.virtualRewards; }"}
    monkeypatch.setattr(idd, "_body", lambda item, aud: bodies.get(item.get("name")))
    man = _mani([_it("increase"), {"name": "userRewardForPool", "contract": "C", "signature": "f"}])
    # faithful to salty: the snapshot uses ceilDiv(global*amount, total) (comma, no in-span '/'), so the pending
    # formula is NOT in-span — it must be resolved from the same-contract sibling userRewardForPool.
    body = ("function increase(uint a) external { if (totalShares != 0) { user.virtualRewards += "
            "ceilDiv(totalRewards*a, totalShares); } user.userShare += a; totalShares += a; }")
    r = idd._lens_reward_index_cross(_it("increase"), body, man, "aud", None)
    assert r["lens3_status"] == "LENS3_READY" and "userRewardForPool" in (r["pending_reward_formula_basis"] or "")


def test_cross_function_via_trace_callee(monkeypatch):
    bodies = {"_credit": "function _credit() internal { rewardPerToken += x; uint owed = "
              "rewardPerToken*_shares[msg.sender]/totalShares - userRewardPerTokenPaid[msg.sender]; }"}
    monkeypatch.setattr(idd, "_body", lambda item, aud: bodies.get(item.get("name")))
    man = _mani([{"name": "_credit", "contract": "C", "signature": "f"}])
    te = {"trace_status": "TRACE_FOUND", "trace_path": [{"callee": "C._credit"}], "unresolved_callees": []}
    r = idd._lens_reward_index_cross(_it("deposit"), "function deposit(uint a) external { _shares[msg.sender] += a; "
                                     "_credit(); }", man, "aud", te)
    assert r["lens3_status"] == "LENS3_READY" and r["trace_path_used"] == ["C._credit"]


# ---- P289 span-local behavior preserved (the direct lens is untouched) ----
def test_p289_span_local_reward_index_still_matches():
    body = ("function stake(uint a) external { _balances[msg.sender] += a; uint r = rewardPerToken; "
            "uint p = userRewardPerTokenPaid[msg.sender]; claim(); }")
    r = idd._lens_reward_index_init(_it("stake"), body)
    assert r and r["invariant_delta_status"] == "REWARD_INDEX_INIT_FOUND" and r["lens_status"] == "LENS_MATCH"


# ---- corpus remap outputs ----
def test_increaseusershare_ready_in_corpus():
    m = json.loads((O / "remap_metrics.json").read_text())
    assert m["increaseUserShare"]["status"] == "READY_FOR_POC_INTENT"
    assert m["increaseUserShare"]["lens3_status"] == "LENS3_READY"
    assert len(m["lens3_lifts_to_ready"]) == 1 and "_increaseUserShare" in m["lens3_lifts_to_ready"][0]["candidate"]


def test_no_false_ready_and_fp_zero():
    m = json.loads((O / "remap_metrics.json").read_text())
    assert m["severe_concluded_or_reportable_fp"] == 0
    # exactly one genuinely-new READY locus across the corpus vs the P292 baseline = _increaseUserShare
    p292 = json.loads((ROOT / "documentation/research/assisted_mode/p292_internal_locus_admission/outputs/"
                       "remap_metrics.json").read_text())["audits"]
    new = 0
    for t, a in m["audits"].items():
        nb = {x.replace("coverage_manifest:", "") for x in a["READY"]}
        ob = {x.replace("coverage_manifest:", "") for x in p292.get(t, {}).get("READY", [])}
        new += len(nb - ob)
    assert new == 1


def test_regressions_preserved():
    r = json.loads((O / "remap_metrics.json").read_text())["regressions"]
    assert r["kelp_getRsETHAmountToMint"] == "READY"
    assert r["blackhole_claim_many"] == "READY"
    assert r["L2Governor_execute"] == "READY"
    assert r["ecg_stake"] == "READY"
    assert r["salty_Pools_deposit"] == "NEEDS_INTEGRATION_DEVIATION_EVIDENCE"  # P291 precision held


def test_control_target_no_lift():
    m = json.loads((O / "remap_metrics.json").read_text())
    ctrl = m["control_target"]
    assert m["audits"][ctrl]["READY"] == [] and m["audits"][ctrl]["lens3_fired"] == []


# ---- integrity ----
def test_tracer_and_gate_byte_identical():
    for rel, h in BYTE_IDENTICAL.items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:16] == h, f"must stay byte-identical: {rel}"
    for rel, h in FORBIDDEN.items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:8].startswith(h), f"forbidden changed: {rel}"


def test_no_severity_reportable_submission_confirmed_leakage():
    for name in ("remap_metrics.json", "lens3_evidence.json", "guard_report.json"):
        r = json.loads((O / name).read_text())
        if "severity" in r:
            assert r["severity"] is None
        for f in ("reportable", "submission_ready", "concluded", "production_routing", "emits_findings",
                  "routes_in_production"):
            if isinstance(r, dict) and f in r:
                assert r[f] is False


def test_docs_and_verdict():
    for d in DOC_FILES:
        assert (D / d).exists(), f"missing {d}"
    assert any(v in (D / "VERDICT.md").read_text() for v in VERDICTS)


