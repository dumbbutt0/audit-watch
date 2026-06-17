"""P253 — exploit-chain completion forensics. Read-only docs guard (no pipeline behavior)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "documentation/research/assisted_mode/p253_chain_completion_forensics"
DOCS = ("CHAIN_COMPLETION_FORENSICS.md", "OPERATION_CLUSTERS.md", "SCAFFOLD_SKETCH.md", "VERDICT.md")
VERDICTS = ("A — SCAFFOLD_WARRANTED", "B — OPERATIONS_RECUR_BUT_SCAFFOLD_UNPROVEN",
            "C — NO_RECURRING_SET", "D — COMPLETION_NOT_DOMINANT")
OPS = ("ADVERSARIAL_ACTOR_SUBSTITUTION", "STATE_TRANSITION_SIMULATION", "CROSS_CALL_IDENTITY_TRACKING",
       "TERMINAL_STATE_EVALUATION", "INVARIANT_DELTA_COMPUTATION", "UNKNOWN")


def test_all_docs_exist():
    for d in DOCS:
        assert (BASE / d).exists(), f"missing P253 doc: {d}"


def test_verdict_recognized():
    assert any(v in (BASE / "VERDICT.md").read_text() for v in VERDICTS)


def test_six_operation_labels_present():
    txt = (BASE / "CHAIN_COMPLETION_FORENSICS.md").read_text()
    present = [o for o in OPS if o in txt]
    assert len(present) >= 6, f"expected the operation taxonomy, found {len(present)}"


def test_small_set_check_and_five_step_present():
    clusters = (BASE / "OPERATION_CLUSTERS.md").read_text()
    assert "small" in clusters.lower() and ("70" in clusters or "80" in clusters)
    forensics = (BASE / "CHAIN_COMPLETION_FORENSICS.md").read_text()
    assert "First missing step" in forensics


def test_scaffold_is_design_only():
    sk = (BASE / "SCAFFOLD_SKETCH.md").read_text()
    assert "DESIGN SKETCH ONLY" in sk or "design-only" in sk.lower()
    assert "nothing built" in sk.lower() or "not built" in sk.lower()
