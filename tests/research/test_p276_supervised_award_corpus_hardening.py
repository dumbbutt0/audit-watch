"""P276 — SUPERVISED_EVAL award-corpus recall hardening. Guard tests (research-only, advisory, maps+proposes only)."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "documentation/research/assisted_mode/p276_supervised_award_corpus_hardening"
OUTS = DOCS / "outputs"
SCRIPTS = ROOT / "scripts/research"

FROZEN = {
    "scripts/research/locus_shape_prioritizer.py": "d6b494bc3c0cc746",
    "scripts/research/recall_first_shape_sweep.py": "a48336275cb65a4f",
    "scripts/research/recall_first_harness.py": "be428a1202c45b1a",
    "scripts/research/mechanism_pairwise_selector.py": "b0623b8c88752059",
    "scripts/research/impact_first_poc_triage.py": "63c88d02d2c7eefa",
    "scripts/research/award_class_coverage_router.py": "6debb753b45f1833",
    "config/research_award_class_coverage_router.json": "91f9deac7867af62",
    "config/research_impact_first_poc_triage.json": "7c174b5d1ae6b52f",
    "config/research_mechanism_pairwise_selector.json": "9dab060dca027c24",
    "documentation/research/assisted_mode/p271_lending_runtime_scaffold/"
    "LENDING_COMPLETION_CHECKLIST.md": "2929a2154a88104e",
}
FORBIDDEN = {
    "scripts/dashboard_sync.py": "c1af70e1", "prompts/deep_trace.md": "c095c426",
    "scripts/min_confirm_gate.py": "2a15169a", "scripts/confirm_gate.py": "afc481c9",
    "scripts/validate_p208_l3_readiness.py": "ae55eb80",
}
DOC_FILES = ("SETUP.md", "CORPUS_SELECTION.md", "PIPELINE_REPLAY_RESULTS.md", "AWARD_FUNNEL_MAP.md",
             "CLASS_BREAKDOWN.md", "FALSE_POSITIVE_REPORT.md", "REPAIR_BACKLOG.md", "METRICS_SUMMARY.md",
             "LIMITATIONS.md", "VERDICT.md", "ROLLBACK_PLAN.md")
VERDICTS = ("A — CORPUS_MAP_READY_REPAIR_BACKLOG_CLEAR", "B — EVAL_USEFUL_NEEDS_MORE_CORPUS",
            "C — PIPELINE_TOO_NOISY_RECALL_HARDENING_BLOCKED", "D — ABORTED_CONSTRAINT_VIOLATION")
# contest-name literals that must NOT appear in repair-backlog signals (target-specific hard-coding)
CONTEST_LITERALS = ("gondi", "ronin", "zaros", "panoptic", "revert-lend", "revertlend", "silo", "hybra", "ark",
                    "recall-2025", "swan", "quantamm", "beanstalk", "noya", "blackhole", "katana")
PROMO_FALSE = ("reportable", "submission_ready", "concluded", "emits_finding", "production_routing")


def _sha16(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def test_frozen_and_forbidden_byte_identical():
    for rel, h in FROZEN.items():
        assert _sha16(ROOT / rel) == h, f"frozen changed: {rel}"
    for rel, h in FORBIDDEN.items():
        assert _sha16(ROOT / rel).startswith(h), f"forbidden changed: {rel}"


def test_docs_present():
    for d in DOC_FILES:
        assert (DOCS / d).exists(), f"missing {d}"


def test_outputs_labeled_supervised_eval_no_blind_credit():
    metrics = json.loads((OUTS / "corpus_metrics.json").read_text())
    assert metrics["label"] == "SUPERVISED_EVAL"
    # every map/bundle carries the supervised label (not a discovery run)
    for j in list(OUTS.glob("*/award_funnel_map.json")) + list(OUTS.glob("*/replay_bundle.json")):
        assert json.loads(j.read_text()).get("label") == "SUPERVISED_EVAL"
    # no blind-CREDIT phrasing in the narrative docs (bare word "blind" may legitimately appear in award titles)
    for d in ("VERDICT.md", "METRICS_SUMMARY.md", "AWARD_FUNNEL_MAP.md", "SETUP.md"):
        txt = (DOCS / d).read_text().lower()
        for phrase in ("blind discovery", "blind recovery", "blind credit", "fresh blind"):
            assert phrase not in txt, f"blind-credit phrasing '{phrase}' in {d}"


def test_every_locus_mapped_award_has_first_failed_or_terminal_stage():
    maps = list(OUTS.glob("*/award_funnel_map.json"))
    assert maps, "no funnel maps"
    seen_award = False
    for j in maps:
        d = json.loads(j.read_text())
        for f in d["findings"]:
            seen_award = True
            # each award has a stage AND (a first_failed_stage OR a terminal recovered/sampled stage)
            assert "stage" in f
            assert f.get("first_failed_stage") is not None or f["stage"] in (
                "EXACT_RECOVERED", "STRONG_RECOVERED", "FAMILY_RECOVERED")
    assert seen_award


def test_fp_report_tracks_severe_zero():
    m = json.loads((OUTS / "corpus_metrics.json").read_text())
    fp = m["false_positive_report"]
    assert fp["severe_concluded_or_reportable_fp"] == 0
    assert "advisory_only_nonawarded_survivors" in fp
    assert (DOCS / "FALSE_POSITIVE_REPORT.md").exists()


def test_repair_backlog_general_no_target_hardcoding():
    rb = json.loads((OUTS / "repair_backlog.json").read_text())
    assert rb["emits_findings"] is False
    assert rb["repairs"], "no repairs"
    for r in rb["repairs"]:
        assert r["failed_stage"] and r["general_signal"] and r["knob"]
        blob = (r["general_signal"] + " " + str(r.get("affected_classes", "")) + " " + r["knob"]).lower()
        for lit in CONTEST_LITERALS:
            assert not re.search(rf"\b{re.escape(lit)}\b", blob), f"repair {r['id']} signal hard-codes target '{lit}'"


def test_glue_scripts_advisory_only_and_unwired():
    for s in ("p276_corpus_replay.py", "p276_award_funnel_map.py", "p276_metrics.py"):
        src = (SCRIPTS / s).read_text()
        assert 'LABEL = "SUPERVISED_EVAL"' in src or "SUPERVISED_EVAL" in src
        # un-wired: no production routing/gate imports
        for bad in ("run_pipeline", "dashboard_sync", "confirm_gate", "record_outcome"):
            assert bad not in src, f"{s} references {bad}"
    # metrics output stamps advisory contract
    m = json.loads((OUTS / "corpus_metrics.json").read_text())
    assert m["is_gate"] is False and m["research_only"] is True and m["emits_findings"] is False


def test_recognized_verdict():
    v = (DOCS / "VERDICT.md").read_text()
    assert any(x in v for x in VERDICTS)


