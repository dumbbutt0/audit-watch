"""P289 — loss/reward mechanism lenses. Lens behavior + refutation + corpus regressions (research-only, advisory)."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/research"))
import invariant_delta_deriver as idd  # noqa: E402

D = ROOT / "documentation/research/assisted_mode/p289_loss_reward_mechanism_lenses"
O = D / "outputs"
FORBIDDEN = {
    "scripts/dashboard_sync.py": "c1af70e1", "prompts/deep_trace.md": "c095c426",
    "scripts/min_confirm_gate.py": "2a15169a", "scripts/confirm_gate.py": "afc481c9",
    "scripts/validate_p208_l3_readiness.py": "ae55eb80",
}
# frozen-OTHERS (P289 may edit only the invariant_delta_deriver + its config)
FROZEN_OTHERS = {
    "scripts/research/award_class_coverage_router.py": "6debb753b45f1833",
    "scripts/research/cross_function_value_tracer.py": "f28f0620d3d3548a",
    "scripts/sibling_function_parity_taxonomy.py": "e504383db8f33844",
    "scripts/registry_position_lifecycle_taxonomy.py": "da83a7acc217c706",
}
DOC_FILES = ("SETUP.md", "LOSS_REWARD_LENS_DESIGN.md", "IMPLEMENTATION_NOTES.md", "LOSS_REWARD_REMAP_RESULTS.md",
             "LOSS_REWARD_EVIDENCE_AUDIT.md", "LOSS_REWARD_REPAIR_BACKLOG.md", "LIMITATIONS.md", "VERDICT.md",
             "ROLLBACK_PLAN.md")
VERDICTS = ("A — LOSS_REWARD_LENSES_READY_FOR_BLIND_RETEST", "B — LOSS_REWARD_LENSES_PROMISING_NEEDS_REFINEMENT",
            "C — LOSS_REWARD_LENSES_TOO_NOISY", "D — ABORTED_CONSTRAINT_VIOLATION")


def _it(name):
    return {"name": name, "contract": "C"}


# ---- lens MATCH fixtures ----
def test_lens1_loss_on_stake_match():
    body = ("function stake(address t, uint a) external { uint loss = gaugeLoss[t]; "
            "require(loss != block.timestamp); _stakes[msg.sender][t] = a; }")
    r = idd._lens_loss_on_stake(_it("stake"), body)
    assert r and r["invariant_delta_status"] == "LOSS_ON_STAKE_FOUND" and r["lens_status"] == "LENS_MATCH"


def test_lens2_bad_debt_contagion_match():
    body = "function onBid(uint id) external { uint loss = badDebt[id]; totalBadDebt += loss; }"
    r = idd._lens_bad_debt_contagion(_it("onBid"), body)
    assert r and r["invariant_delta_status"] == "BAD_DEBT_CONTAGION_FOUND" and r["lens_status"] == "LENS_MATCH"


def test_lens3_reward_index_init_match():
    body = ("function stake(uint a) external { _balances[msg.sender] += a; uint r = rewardPerToken; "
            "uint p = userRewardPerTokenPaid[msg.sender]; claim(); }")
    r = idd._lens_reward_index_init(_it("stake"), body)
    assert r and r["invariant_delta_status"] == "REWARD_INDEX_INIT_FOUND" and r["lens_status"] == "LENS_MATCH"


def test_lens4_share_transfer_theft_match():
    body = "function transfer(address to, uint a) external { balances[msg.sender] -= a; balances[to] += a; uint i = rewardIndex; }"
    r = idd._lens_share_transfer_theft(_it("transfer"), body)
    assert r and r["invariant_delta_status"] == "SHARE_TRANSFER_THEFT_FOUND" and r["lens_status"] == "LENS_MATCH"


# ---- refutation fixtures ----
def test_lens1_refutes_when_index_initialized():
    body = ("function deposit(uint a) external { userIndex[msg.sender] = rewardIndex(); "
            "_balances[msg.sender] = a; uint d = deficit; }")
    r = idd._lens_loss_on_stake(_it("deposit"), body)
    assert r and r["lens_status"] == "LENS_REFUTED"


def test_lens2_refutes_when_loss_per_term_isolated():
    body = "function onBid(uint id) external { uint loss = badDebt[id]; perTerm[term] -= loss; }"
    r = idd._lens_bad_debt_contagion(_it("onBid"), body)
    assert r and r["lens_status"] == "LENS_REFUTED"


def test_lens4_refutes_when_both_checkpoints_updated():
    body = ("function transfer(address to, uint a) external { _updateCheckpoint(msg.sender); _updateCheckpoint(to); "
            "uint i = rewardIndex; balances[msg.sender] -= a; }")
    r = idd._lens_share_transfer_theft(_it("transfer"), body)
    assert r and r["lens_status"] == "LENS_REFUTED"


# ---- FP-safety: generic / naming-only must NOT match ----
def test_generic_stake_no_match():
    assert idd._lens_loss_on_stake(_it("stake"), "function stake() external { return; }") is None


def test_generic_transfer_no_reward_no_match():
    assert idd._lens_share_transfer_theft(_it("transfer"), "function transfer(address to,uint a) external { balances[to]+=a; }") is None


def test_naming_only_loss_no_state_no_match():
    # 'loss' in a name/comment-free body but no stake write -> None
    assert idd._lens_loss_on_stake(_it("getLoss"), "function getLoss() external view returns (uint) { return loss; }") is None


# ---- ECG-specific names are NOT required (renamed function still matches) ----
def test_lens1_matches_renamed_function():
    body = ("function joinPool(address t, uint a) external { uint slash = deficit[t]; "
            "require(slash != block.timestamp); _balances[msg.sender] = a; }")
    r = idd._lens_loss_on_stake(_it("joinPool"), body)  # not 'stake'
    assert r and r["lens_status"] == "LENS_MATCH"


# ---- no award-text consumed (award fields ignored by the lens) ----
def test_no_award_text_consumed():
    body = "function stake(uint a) external { uint loss = gaugeLoss; require(loss != block.timestamp); _stakes[msg.sender]=a; }"
    it = dict(_it("stake"), award_title="THIS IS AWARD TEXT", award_body="ignore me")
    r = idd._lens_loss_on_stake(it, body)
    blob = json.dumps(r).lower()
    assert "award text" not in blob and "ignore me" not in blob


# ---- corpus regressions (from the P289 remap outputs) ----
def test_ecg_stake_newly_ready():
    m = json.loads((O / "remap_metrics.json").read_text())
    ecg = m["audits"]["ecg-2023-12-holdout"]
    assert any("stake" in c for c in ecg["READY"])


def test_regressions_stable():
    m = json.loads((O / "remap_metrics.json").read_text())
    assert m["regressions"]["kelp_getRsETHAmountToMint"] == "READY"
    assert m["regressions"]["blackhole_claim_many"] == "READY"
    assert m["regressions"]["L2Governor_execute"] == "READY"


def test_no_false_ready_zero_fp():
    m = json.loads((O / "remap_metrics.json").read_text())
    assert m["severe_concluded_or_reportable_fp"] == 0
    # exactly one lens lift to READY, and it is the awarded ECG locus
    lifts = m["lens_lifts_to_ready"]
    assert len(lifts) == 1 and "stake" in lifts[0]["candidate"]


def test_no_severity_reportable_leakage():
    for name in ("lens_evidence.json", "remap_metrics.json", "guard_report.json"):
        r = json.loads((O / name).read_text())
        if "severity" in r:
            assert r["severity"] is None


def test_frozen_others_and_forbidden_byte_identical():
    for rel, h in FROZEN_OTHERS.items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:16] == h, f"frozen-other changed: {rel}"
    for rel, h in FORBIDDEN.items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:8].startswith(h), f"forbidden changed: {rel}"


def test_docs_and_verdict():
    for d in DOC_FILES:
        assert (D / d).exists(), f"missing {d}"
    assert any(v in (D / "VERDICT.md").read_text() for v in VERDICTS)


