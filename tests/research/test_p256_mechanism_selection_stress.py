"""P256 — subtle accounting/state mechanism-selection stress test. Docs guard (no pipeline behavior)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "documentation/research/assisted_mode/p256_mechanism_selection_stress"
CONTESTS = ("plaza", "concrete")
PER_CONTEST = ("_BASE_FREEZE.md", "_MECHANISM_GATE.md", "_PROCEDURE_OUTPUTS.md", "_REVEAL_AND_SCORE.md")
TOP_DOCS = ("SETUP.md", "SELECTION_DIAGNOSIS.md", "VERDICT.md")
VERDICTS = ("A — MECHANISM_SELECTION_SOLVED_BUILD_READY", "B — SELECTION_PROMISING_NEEDS_MORE_HELDOUT",
            "C — DISCOVERY_GAP_DOMINATES", "D — RANKING_GAP_DOMINATES",
            "E — COMPLETION_GAP_DOMINATES", "F — NOT_USEFUL")
OPS = ("STATE_TRANSITION_SIMULATION", "ADVERSARIAL_ACTOR_SUBSTITUTION", "TERMINAL_STATE_EVALUATION",
       "INVARIANT_DELTA_COMPUTATION", "CROSS_CALL_IDENTITY_TRACKING")
GATE_DIMS = ("controllability", "value-delta", "victim/gainer", "comparand", "terminality",
             "amplification", "simplicity", "award-likeness")
AWARDED_CLASSES = ("NOT_ENUMERATED", "ENUMERATED_BUT_RANKED_TOO_LOW",
                   "RANKED_HIGH_BUT_NOT_COMPLETED", "COMPLETED_CORRECTLY")
GATE_FIELDS = ("SELECTED_MECHANISM", "RUNNER_UP", "WHY_SELECTED_OVER_RUNNER_UP",
               "WHAT_WOULD_FALSIFY")


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


def test_eight_gate_dimensions_present():
    setup = (BASE / "SETUP.md").read_text()
    for dim in GATE_DIMS:
        assert dim in setup, f"gate dimension missing in SETUP.md: {dim}"


def test_four_awarded_classes_present():
    diag = (BASE / "SELECTION_DIAGNOSIS.md").read_text()
    for c in AWARDED_CLASSES:
        assert c in diag, f"awarded-mechanism class missing in diagnosis: {c}"


def test_gate_records_required_fields():
    for c in CONTESTS:
        gate = (BASE / f"{c}_MECHANISM_GATE.md").read_text()
        for f in GATE_FIELDS:
            assert f in gate, f"{c} gate missing field {f}"


def test_freeze_hashes_echoed_in_reveal_docs():
    for c, hashes in (
        ("plaza", ("2359a935bab4b85c", "ec5c64c68a4ec626", "a6454e434598d94d")),
        ("concrete", ("41625ef5c312ee3d", "731f2de10fa87296", "e99520861a9f02ed")),
    ):
        rev = (BASE / f"{c}_REVEAL_AND_SCORE.md").read_text()
        for h in hashes:
            assert h in rev, f"{c} reveal missing freeze hash {h}"


def test_checkpoint_outputs_zero_conclusions():
    outs = list((BASE / "outputs").glob("*_checkpoint.json"))
    assert len(outs) >= 4, "expected 2 checkpoints x 2 contests"
    for f in outs:
        d = json.loads(f.read_text())
        assert d["emits_findings"] is False and d["concludes_vulnerability"] is False
        assert all(r.get("severity") is None and r.get("concluded") is False for r in d["records"])
