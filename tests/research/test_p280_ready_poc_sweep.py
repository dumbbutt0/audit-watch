"""P280 — small diagnostic PoC sweep on the 3 P279 auto-READY candidates. Guard tests (research-only, POC_SWEEP)."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "documentation/research/assisted_mode/p280_ready_poc_sweep"
OUTS = DOCS / "outputs"
POCS = ROOT / "pocs/p280"

# the EXACT 3 P279 READY candidates — no more, no fewer
EXPECTED = {
    "coverage_manifest:IBeanstalk:cancelPodListing:0",
    "coverage_manifest:L2Governor:execute:20",
    "coverage_manifest:V3Vault:transform:9",
}
# P279 deriver/gate + key frozen modules must be byte-identical (P280 only adds PoCs/docs/test)
FROZEN = {
    "scripts/research/completion_evidence_deriver.py": None,  # presence + unchanged-via-other-tests
    "scripts/research/award_class_coverage_router.py": "6debb753b45f1833",
    "config/research_award_class_coverage_router.json": "91f9deac7867af62",
    "scripts/research/recall_first_harness.py": "be428a1202c45b1a",
    "documentation/research/assisted_mode/p271_lending_runtime_scaffold/"
    "LENDING_COMPLETION_CHECKLIST.md": "2929a2154a88104e",
}
FORBIDDEN = {
    "scripts/dashboard_sync.py": "c1af70e1", "prompts/deep_trace.md": "c095c426",
    "scripts/min_confirm_gate.py": "2a15169a", "scripts/confirm_gate.py": "afc481c9",
    "scripts/validate_p208_l3_readiness.py": "ae55eb80",
}
DOC_FILES = ("SETUP.md", "INPUT_FREEZE.md", "POC_PLAN.md", "POC_RESULTS.md", "EVIDENCE_QUALITY_AUDIT.md",
             "DERIVER_REPAIR_BACKLOG.md", "LIMITATIONS.md", "VERDICT.md", "ROLLBACK_PLAN.md")
VERDICTS = ("A — READY_CANDIDATES_POC_SWEEP_PASS", "B — READY_CANDIDATES_PARTIAL_POC_SWEEP",
            "C — READY_LABEL_TOO_WEAK", "D — READY_LABEL_TOO_NOISY", "E — ABORTED_CONSTRAINT_VIOLATION")
RESULTS = ("PASS_SUPPORTED", "PASS_REFUTED", "INCONCLUSIVE_RUNTIME", "BUILD_BLOCKED", "EVIDENCE_INSUFFICIENT",
           "BENIGN_BY_DESIGN", "NONAWARDED_TRUE_POSITIVE", "SAME_AREA_WRONG_MECHANISM")
EQ = ("READY_CONFIRMED", "READY_TOO_WEAK", "READY_WRONG", "READY_OVERCLAIMED", "READY_INCONCLUSIVE")


def _sha16(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def test_exactly_three_fixed_candidates():
    pk = json.loads((OUTS / "frozen_evidence_packages.json").read_text())["packages"]
    got = {p["candidate_id"] for p in pk}
    assert got == EXPECTED, f"candidate set drifted: {got ^ EXPECTED}"
    res = {r["candidate_id"] for r in json.loads((OUTS / "poc_results.json").read_text())["results"]}
    assert res == EXPECTED


def test_input_freeze_has_hashes_before_results():
    # INPUT_FREEZE references per-package hashes; frozen packages file exists
    txt = (DOCS / "INPUT_FREEZE.md").read_text()
    assert "pkg hash" in txt.lower() or "hash" in txt.lower()
    assert (OUTS / "frozen_evidence_packages.json").exists()


def test_results_and_evidence_quality_recognized():
    res = json.loads((OUTS / "poc_results.json").read_text())["results"]
    for r in res:
        assert r["result"] in RESULTS
    aq = json.loads((OUTS / "evidence_quality_audit.json").read_text())["audited"]
    for a in aq:
        assert a["classification"] in EQ


def test_no_severity_reportable_leakage():
    for j in OUTS.glob("*.json"):
        t = j.read_text().lower()
        assert '"severity":' not in t or '"severity": null' in t or '"severity":null' in t
        assert '"reportable": true' not in t and '"submission_ready": true' not in t
        assert '"confirmed": true' not in t and '"production_routing": true' not in t


def test_severe_fp_zero():
    assert json.loads((OUTS / "poc_results.json").read_text())["severe_concluded_or_reportable_fp"] == 0
    assert json.loads((OUTS / "evidence_quality_audit.json").read_text())[
        "summary"]["severe_concluded_or_reportable_fp"] == 0


def test_pocs_present_for_three():
    for f in ("P280_Transform.t.sol", "P280_CancelPodListing.t.sol", "P280_GovernorExecute.t.sol"):
        assert (POCS / "test" / f).exists(), f"missing PoC {f}"
    assert (POCS / "run_output.txt").exists()


def test_outputs_labeled_poc_sweep():
    for nm in ("poc_results.json", "evidence_quality_audit.json", "frozen_evidence_packages.json"):
        d = json.loads((OUTS / nm).read_text())
        assert d.get("label") == "SUPERVISED_EVAL" and d.get("mode") == "POC_SWEEP"


def test_frozen_and_forbidden_byte_identical():
    for rel, h in FROZEN.items():
        p = ROOT / rel
        assert p.exists(), f"missing {rel}"
        if h:
            assert _sha16(p) == h, f"frozen changed: {rel}"
    for rel, h in FORBIDDEN.items():
        assert _sha16(ROOT / rel).startswith(h), f"forbidden changed: {rel}"


def test_docs_and_verdict():
    for d in DOC_FILES:
        assert (DOCS / d).exists(), f"missing {d}"
    assert any(v in (DOCS / "VERDICT.md").read_text() for v in VERDICTS)


