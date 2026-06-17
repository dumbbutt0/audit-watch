"""P260 — locus-prioritization + shape-discovery module. Behavior + docs guard (research-only, default-off)."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/research/locus_shape_prioritizer.py"
CONFIG = ROOT / "config/research_locus_shape_prioritizer.json"
DOCS = ROOT / "documentation/research/assisted_mode/p260_locus_shape_prioritizer"
OUTS = DOCS / "outputs"
PROMPT = ROOT / "prompts/research/locus_shape_prioritizer.md"
TEMPLATES = ("T1_external_dependency_availability", "T2_redemption_withdrawal_state_coupling",
             "T3_reentrancy_accounting_boundary", "T4_migration_conversion_residue",
             "T5_statemachine_liveness_terminality", "T6_cross_transaction_drift",
             "T7_liquidation_solvency_boundary", "T8_shareprice_donation_inflation")
ACTIONS = ("APPLY_RANKING", "APPLY_COMPLETION", "REFUTE_FIRST", "LOW_PRIORITY", "NEEDS_MANUAL_REVIEW")
VERDICTS = ("A — MODULE_READY_FOR_FRESH_HELDOUT", "B — MODULE_PROMISING_NEEDS_REFINEMENT",
            "C — MODULE_NOT_USEFUL", "D — BUILD_ABORTED_CONSTRAINT_VIOLATION")


def test_module_and_config_and_prompt_exist():
    assert SCRIPT.exists() and CONFIG.exists() and PROMPT.exists()
    cfg = json.loads(CONFIG.read_text())
    assert cfg["is_gate"] is False and cfg["research_only"] is True and cfg["routes_in_production"] is False
    assert set(cfg["marker_templates"].keys()) == set(TEMPLATES)


def test_deliverable_docs_exist_and_verdict():
    for d in ("SETUP.md", "MODULE_SPEC.md", "IMPLEMENTATION_NOTES.md", "SAMPLE_OUTPUTS.md",
              "BACKTEST_RESULTS.md", "LIMITATIONS.md", "VERDICT.md"):
        assert (DOCS / d).exists(), f"missing {d}"
    assert any(v in (DOCS / "VERDICT.md").read_text() for v in VERDICTS)


def test_module_is_unwired_research_only():
    src = SCRIPT.read_text()
    # must not import/reference production pipeline wiring
    for forbidden in ("run_pipeline", "agent_policy", "dashboard_sync", "confirm_gate", "record_outcome"):
        assert forbidden not in src, f"module references production wiring: {forbidden}"


def test_backtest_outputs_present_and_invariants():
    outs = list(OUTS.glob("*_prioritizer.json"))
    assert len(outs) >= 3, "expected backtest outputs for >=3 contests"
    for f in outs:
        d = json.loads(f.read_text())
        assert d["is_gate"] is False and d["research_only"] is True and d["routes_in_production"] is False
        assert d["emits_findings"] is False and d["concludes_vulnerability"] is False
        assert d["routed_manifest_ids"] == []
        assert len(d["prioritized_loci"]) <= d["top_n"]  # bounded output (no flood)
        for lc in d["prioritized_loci"]:
            assert set(lc["applied_shape_templates"]).issubset(set(TEMPLATES))
            assert lc["downstream_recommended_action"] in ACTIONS
            assert "bc_ranking_handoff" in lc and "top_2_mechanisms" in lc
            for m in lc["generated_mechanism_hypotheses"]:
                assert m["severity"] is None and m["concluded"] is False  # never concludes


def test_core_p259_fix_hybra_deposit_top_ranked():
    """The headline backtest: GrowthHYBR.deposit (P259 skipped award locus) is prioritized with T8."""
    d = json.loads((OUTS / "hybra_prioritizer.json").read_text())
    deposit = [lc for lc in d["prioritized_loci"] if lc["function"].lower() == "deposit"]
    assert deposit, "hybra deposit (GrowthHYBR.deposit) not prioritized"
    assert "T8_shareprice_donation_inflation" in deposit[0]["applied_shape_templates"]


