"""
Tests for the P84 handoff bundle generator (scripts/handoff_generator.py).

Covers: all 3 seed finding types generate a complete bundle; reject-first (fresh bundle is un-promotable,
PoC scaffold is a non-passing stub, gate verdict is DO_NOT_SUBMIT, no finding-specific item is PASS); refuses
frozen-dir writes + no-overwrite; unknown type / missing field rejected; and a GOLDEN structural match of the
shared-accounting/fee-routing template against the proven P83 H-01 package.
"""
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import handoff_generator as hg  # noqa: E402
import funnel  # noqa: E402

SEED_TYPES = ["shared_position_fee_routing", "access_control_privileged", "oracle_price_manipulation",
              "reward_accrual_state_lifecycle", "validation_liveness_counter_scope",
              "access_control_index_integrity", "signature_replay_authorization"]
H01_DIR = ROOT / "documentation/research/_p83_h01_submission"


def _descriptor(ftype="shared_position_fee_routing", **over):
    d = {
        "finding_type": ftype,
        "subject": "DemoProto",
        "finding_id": "D-01",
        "contract": "Vault",
        "function": "claim",
        "commit": "abc1234",
    }
    d.update(over)
    return d


def _headings(text):
    return [h.strip() for h in re.findall(r"^##\s+(.+)$", text, flags=re.M)]


def _stems(headings):
    # stable heading stem = text before any parenthetical (which is finding-specific)
    return {re.split(r"\s*\(", h, 1)[0].strip() for h in headings}


# ------------------------------------------------------- generation, all types
@pytest.mark.parametrize("ftype", SEED_TYPES)
def test_all_seed_types_generate_complete_bundle(ftype, tmp_path):
    out = tmp_path / ftype
    man = hg.generate_bundle(_descriptor(ftype), out, force=True)
    names = {p.name for p in out.glob("*")}
    assert {"submission_draft.md", "evidence_bundle.md", "pre_submission_gate.md",
            "reviewer_notes.md", "run_plan.md", "funnel_record.json"} <= names
    assert any(n.endswith(".t.sol") for n in names)
    assert man["reject_first_ok"] is True


@pytest.mark.parametrize("ftype", SEED_TYPES)
def test_no_unfilled_placeholders(ftype, tmp_path):
    out = tmp_path / ftype
    hg.generate_bundle(_descriptor(ftype), out, force=True)
    for p in out.glob("*"):
        assert "{{" not in p.read_text(), f"unfilled placeholder in {p.name}"


# --------------------------------------------------------------- reject-first
@pytest.mark.parametrize("ftype", SEED_TYPES)
def test_fresh_bundle_is_unpromotable(ftype, tmp_path):
    out = tmp_path / ftype
    hg.generate_bundle(_descriptor(ftype), out, force=True)
    rec = funnel._read_json(out / "funnel_record.json")
    assert funnel.can_promote_to_poc_reproduced(rec)[0] is False
    assert funnel.can_promote_to_submission_ready(rec)[0] is False
    assert funnel.compute_pipeline_status(rec) not in {
        "POC_REPRODUCED", "PARTIAL_REPRO", "SUBMISSION_READY_HUMAN_REVIEW"}


def test_p86_reward_accrual_state_lifecycle_generates_reject_first_bundle(tmp_path):
    # P86 new finding type (H-05 class) must generate the same reject-first, un-promotable bundle.
    out = tmp_path / "ral"
    man = hg.generate_bundle(_descriptor("reward_accrual_state_lifecycle", finding_id="RA-01",
                                         contract="Staking", function="transferToValidSlot"), out, force=True)
    assert man["reject_first_ok"] is True
    rec = funnel._read_json(out / "funnel_record.json")
    assert funnel.can_promote_to_poc_reproduced(rec)[0] is False
    assert funnel.can_promote_to_submission_ready(rec)[0] is False
    gate = (out / "pre_submission_gate.md").read_text()
    assert re.search(r"VERDICT_TOKEN:\s*DO_NOT_SUBMIT", gate)
    assert any(p.name.endswith(".t.sol") and "assertTrue(false" in p.read_text() for p in out.glob("*.t.sol"))


def test_p88_validation_liveness_counter_scope_generates_reject_first_bundle(tmp_path):
    # P88 new finding type (TraitForge H-01 class) must generate the same reject-first, un-promotable bundle.
    out = tmp_path / "vlcs"
    man = hg.generate_bundle(_descriptor("validation_liveness_counter_scope", finding_id="VL-01",
                                         contract="NFT", function="mintWithBudget"), out, force=True)
    assert man["reject_first_ok"] is True
    rec = funnel._read_json(out / "funnel_record.json")
    assert funnel.can_promote_to_poc_reproduced(rec)[0] is False
    assert funnel.can_promote_to_submission_ready(rec)[0] is False
    gate = (out / "pre_submission_gate.md").read_text()
    assert re.search(r"VERDICT_TOKEN:\s*DO_NOT_SUBMIT", gate)
    assert any(p.name.endswith(".t.sol") and "assertTrue(false" in p.read_text() for p in out.glob("*.t.sol"))


def test_poc_scaffold_has_non_passing_guard(tmp_path):
    out = tmp_path / "x"
    hg.generate_bundle(_descriptor(), out, force=True)
    poc = next(p for p in out.glob("*.t.sol"))
    assert "assertTrue(false" in poc.read_text()


def test_gate_verdict_is_do_not_submit_and_items_not_pass(tmp_path):
    out = tmp_path / "x"
    hg.generate_bundle(_descriptor(), out, force=True)
    gate = (out / "pre_submission_gate.md").read_text()
    assert re.search(r"VERDICT_TOKEN:\s*DO_NOT_SUBMIT", gate)
    for n in range(4, 10):
        row = re.search(rf"\|\s*{n}\s*\|[^\n]*", gate).group(0)
        assert "✅ PASS" not in row, f"item {n} must not be PASS in a fresh bundle"


def test_validate_bundle_flags_tampered_gate(tmp_path):
    out = tmp_path / "x"
    hg.generate_bundle(_descriptor(), out, force=True)
    # tamper: flip the verdict token to a ready state -> validation must fail
    g = out / "pre_submission_gate.md"
    g.write_text(g.read_text().replace("VERDICT_TOKEN: DO_NOT_SUBMIT", "VERDICT_TOKEN: READY_FOR_HUMAN_REVIEW"))
    report = hg.validate_bundle(out)
    assert report["ok"] is False
    assert any("verdict token" in v for v in report["violations"])


# ----------------------------------------------------------- safety / refusals
def test_refuses_frozen_dir(tmp_path):
    frozen = ROOT / "documentation/research/_p82_h01_claim_poc/_scratch"
    with pytest.raises(hg.HandoffGeneratorError):
        hg.generate_bundle(_descriptor(), frozen)


def test_refuses_overwrite_without_force(tmp_path):
    out = tmp_path / "x"
    hg.generate_bundle(_descriptor(), out)  # first time ok (empty)
    with pytest.raises(hg.HandoffGeneratorError):
        hg.generate_bundle(_descriptor(), out)  # second time blocked


def test_unknown_finding_type_rejected(tmp_path):
    with pytest.raises(hg.HandoffGeneratorError):
        hg.generate_bundle(_descriptor(ftype="not_a_type"), tmp_path / "x", force=True)


def test_missing_required_field_rejected(tmp_path):
    d = _descriptor()
    del d["contract"]
    with pytest.raises(hg.HandoffGeneratorError):
        hg.generate_bundle(d, tmp_path / "x", force=True)


def test_render_bundle_does_not_write(tmp_path):
    # render_bundle is in-memory only
    rendered = hg.render_bundle(_descriptor())
    assert "submission_draft.md" in rendered and "{{" not in rendered["submission_draft.md"]


def test_commit_pins_gate_item_1_only_with_real_hash(tmp_path):
    out1 = tmp_path / "pinned"
    hg.generate_bundle(_descriptor(commit="befb1b1170"), out1, force=True)
    g1 = (out1 / "pre_submission_gate.md").read_text()
    assert re.search(r"\|\s*1\s*\|[^\n]*✅ PASS", g1)  # real hash -> item 1 PASS (a fact, not a claim)

    out2 = tmp_path / "nopin"
    d = _descriptor()
    del d["commit"]
    hg.generate_bundle(d, out2, force=True)
    g2 = (out2 / "pre_submission_gate.md").read_text()
    assert re.search(r"\|\s*1\s*\|[^\n]*TODO", g2)  # no commit -> item 1 TODO


# ---------------------------------------------- golden: generalizes H-01 package
def test_feerouting_template_matches_h01_package_structure():
    """The shared-accounting/fee-routing templates must reproduce the section structure of the proven
    P83 H-01 package (the canonical worked example)."""
    rendered = hg.render_bundle(_descriptor("shared_position_fee_routing"))

    h01_draft = _stems(_headings((H01_DIR / "submission_draft.md").read_text()))
    gen_draft = _stems(_headings(rendered["submission_draft.md"]))
    assert h01_draft <= gen_draft, f"missing draft sections: {h01_draft - gen_draft}"

    h01_notes = _headings((H01_DIR / "reviewer_notes.md").read_text())
    gen_notes = _headings(rendered["reviewer_notes.md"])
    # core reviewer-notes sections must be present (titles are parametrized, so compare on count + key stems)
    assert len(gen_notes) >= 5
    assert any("dust" in n.lower() for n in gen_notes)
    assert any("triager" in n.lower() for n in gen_notes)

    # both gates carry a 9-row checklist
    gen_gate = rendered["pre_submission_gate.md"]
    assert all(re.search(rf"\|\s*{n}\s*\|", gen_gate) for n in range(1, 10))
