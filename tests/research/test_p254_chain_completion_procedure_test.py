"""P254 — held-out exploit-chain completion procedure test. Docs guard (no pipeline behavior)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "documentation/research/assisted_mode/p254_chain_completion_procedure_test"
DOCS = ("SETUP.md", "BASE_HUNT_FREEZE.md", "SELECTED_LOCI.md", "PROCEDURE_OUTPUTS.md",
        "REVEAL_AND_SCORE.md", "OPERATION_CONTRIBUTION.md", "VERDICT.md")
VERDICTS = ("A — SCAFFOLD_BUILD_JUSTIFIED", "B — PROCEDURE_PROMISING_BUT_NEEDS_MORE_HELDOUT",
            "C — PROCEDURE_NOT_USEFUL", "D — OPERATION_SET_WRONG")
OPS = ("STATE_TRANSITION_SIMULATION", "ADVERSARIAL_ACTOR_SUBSTITUTION", "TERMINAL_STATE_EVALUATION",
       "INVARIANT_DELTA_COMPUTATION", "CROSS_CALL_IDENTITY_TRACKING")
CHAIN_STATUS = ("COMPLETED_CHAIN", "PARTIAL_CHAIN", "NO_CHAIN", "REFUTED")


def test_all_docs_exist():
    for d in DOCS:
        assert (BASE / d).exists(), f"missing P254 doc: {d}"


def test_verdict_recognized():
    assert any(v in (BASE / "VERDICT.md").read_text() for v in VERDICTS)


def test_freeze_before_reveal_hashes_present():
    rev = (BASE / "REVEAL_AND_SCORE.md").read_text()
    assert "AFTER the three pre-reveal freezes" in rev
    # the three frozen-doc hash prefixes are echoed in the reveal doc
    for h in ("2983bee06430d536", "bad10f234dd0b192", "d36be8ca11db4826"):
        assert h in rev, f"freeze hash {h} not echoed in REVEAL_AND_SCORE.md"


def test_procedure_doc_has_five_ops_and_chain_status_labels():
    proc = (BASE / "PROCEDURE_OUTPUTS.md").read_text()
    setup = (BASE / "SETUP.md").read_text()
    for op in OPS:
        assert op in setup, f"operation {op} not named in SETUP.md"
    # all four chain-status labels appear in the procedure outputs
    for cs in CHAIN_STATUS:
        assert cs in proc, f"chain-status label {cs} missing in PROCEDURE_OUTPUTS.md"


def test_no_hindsight_lock_fields_in_selected_loci():
    sel = (BASE / "SELECTED_LOCI.md").read_text().lower()
    for token in ("why selected", "signal that selected", "already completed", "remained incomplete"):
        assert token in sel, f"no-hindsight-lock field missing: {token}"


def test_checkpoint_outputs_are_reasoning_records_zero_conclusions():
    outs = list((BASE / "outputs").glob("loopfi_*checkpoint.json"))
    assert len(outs) >= 2, "expected both isolated checkpoint outputs"
    for f in outs:
        d = json.loads(f.read_text())
        assert d["emits_findings"] is False and d["concludes_vulnerability"] is False
        assert all(r.get("severity") is None and r.get("concluded") is False for r in d["records"])
