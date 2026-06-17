"""P255 — multi-heldout chain-completion replication. Docs guard (no pipeline behavior)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "documentation/research/assisted_mode/p255_multiheldout_replication"
CONTESTS = ("basin", "bakerfi")
PER_CONTEST = ("_BASE_FREEZE.md", "_SELECTED_LOCI.md", "_PROCEDURE_OUTPUTS.md", "_REVEAL_AND_SCORE.md")
TOP_DOCS = ("SETUP.md", "REPLICATION_METRICS.md", "VERDICT.md")
VERDICTS = ("A — REPLICATES_STRONGLY", "B — PARTIAL_REPLICATION",
            "C — DOES_NOT_REPLICATE", "D — OPERATION_SET_FAILS")
OPS = ("STATE_TRANSITION_SIMULATION", "ADVERSARIAL_ACTOR_SUBSTITUTION", "TERMINAL_STATE_EVALUATION",
       "INVARIANT_DELTA_COMPUTATION", "CROSS_CALL_IDENTITY_TRACKING")
CHAIN_STATUS = ("COMPLETED_CHAIN", "PARTIAL_CHAIN", "NO_CHAIN", "REFUTED")
MECH_LABELS = ("awarded-mechanism-selected", "awarded-mechanism-visible-but-not-selected",
               "awarded-mechanism-enumerated-then-refuted-incorrectly", "awarded-mechanism-not-enumerated")


def test_all_docs_exist():
    for d in TOP_DOCS:
        assert (BASE / d).exists(), f"missing top doc {d}"
    for c in CONTESTS:
        for suf in PER_CONTEST:
            assert (BASE / f"{c}{suf}").exists(), f"missing {c}{suf}"


def test_verdict_recognized():
    assert any(v in (BASE / "VERDICT.md").read_text() for v in VERDICTS)


def test_five_ops_named_in_setup():
    setup = (BASE / "SETUP.md").read_text()
    for op in OPS:
        assert op in setup, f"op {op} not in SETUP.md"


def test_each_procedure_doc_has_chain_status_and_mech_count():
    for c in CONTESTS:
        proc = (BASE / f"{c}_PROCEDURE_OUTPUTS.md").read_text()
        assert any(cs in proc for cs in CHAIN_STATUS), f"{c} procedure has no chain-status label"
        assert "plausible mechanisms considered" in proc.lower(), f"{c} missing the P255 mechanism-count metric"


def test_four_mechanism_selection_labels_present():
    metrics = (BASE / "REPLICATION_METRICS.md").read_text()
    for lbl in MECH_LABELS:
        assert lbl in metrics, f"mechanism-selection label missing: {lbl}"


def test_freeze_hashes_echoed_in_reveal_docs():
    for c, hashes in (
        ("basin", ("163de89440bf42c5", "fcc0ebbba610a443", "99e7719bae75824a")),
        ("bakerfi", ("b0075d53808a185b", "737f633786f44c11", "dd18014a70d7c09e")),
    ):
        rev = (BASE / f"{c}_REVEAL_AND_SCORE.md").read_text()
        assert "BEFORE the key was opened" in rev, f"{c} reveal missing freeze-before-reveal statement"
        for h in hashes:
            assert h in rev, f"{c} reveal missing freeze hash {h}"


def test_checkpoint_outputs_zero_conclusions():
    outs = list((BASE / "outputs").glob("*_checkpoint.json"))
    assert len(outs) >= 4, "expected 2 checkpoints x 2 contests"
    for f in outs:
        d = json.loads(f.read_text())
        assert d["emits_findings"] is False and d["concludes_vulnerability"] is False
        assert all(r.get("severity") is None and r.get("concluded") is False for r in d["records"])
