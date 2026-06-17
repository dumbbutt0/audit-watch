"""P248 — examine-time reasoning replay (forensic). Read-only docs guard (no pipeline behavior)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "documentation/research/assisted_mode/p248_examine_time_replay"
DOCS = ("CANDIDATE_BIRTH_ANALYSIS.md", "CANDIDATE_DEATH_CLASSIFICATION.md", "FUNNEL_QUANTIFICATION.md",
        "INTERVENTION_SIMULATION.md", "RANKING.md", "VERDICT.md")
VERDICTS = ("A — ACCOUNTING_FIRST", "B — PERMISSION_FIRST", "C — CROSS_CONTRACT_FIRST",
            "D — STATE_MACHINE_FIRST", "E — COMBINATION_REQUIRED")
DEATH_LABELS = ("LOCAL_REASONING_STOP", "NO_EXPLOIT_CHAIN_CONSTRUCTION", "NO_STATE_TRANSITION_TRACE",
                "NO_CROSS_CONTRACT_TRACE", "NO_ACTOR_MODEL", "NO_ACCOUNTING_CHECK", "NO_PERMISSION_CHECK",
                "OTHER")
FUNNEL_STAGES = ("Read Surface", "Observed", "Generated Candidate", "Exploit Chain", "Validated")


def test_all_docs_exist():
    for d in DOCS:
        assert (BASE / d).exists(), f"missing P248 doc: {d}"


def test_verdict_recognized():
    assert any(v in (BASE / "VERDICT.md").read_text() for v in VERDICTS), "no recognized P248 verdict"


def test_eight_death_labels_present():
    txt = (BASE / "CANDIDATE_DEATH_CLASSIFICATION.md").read_text()
    present = [l for l in DEATH_LABELS if l in txt]
    assert len(present) >= 8, f"expected the 8 death labels, found {len(present)}"


def test_funnel_five_stages_and_biggest_loss():
    txt = (BASE / "FUNNEL_QUANTIFICATION.md").read_text()
    for s in FUNNEL_STAGES:
        assert s in txt, f"missing funnel stage: {s}"
    assert "most" in txt.lower() and "Generated-Candidate → Exploit-Chain" in txt


def test_birth_analysis_has_21_and_intervention_table():
    birth = (BASE / "CANDIDATE_BIRTH_ANALYSIS.md").read_text()
    assert "21" in birth, "21-finding birth analysis not present"
    sim = (BASE / "INTERVENTION_SIMULATION.md").read_text()
    for cp in ("Accounting", "Permission", "Cross-contract", "State-transition"):
        assert cp in sim, f"intervention missing: {cp}"
    assert "Recovery %" in sim
