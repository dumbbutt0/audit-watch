"""
Tests for the gated platform-draft renderer (submission/renderers).

Headline guarantee: a candidate whose gate status is blocking (DO_NOT_SUBMIT or
NEEDS_MORE_PROOF) can NEVER produce an Immunefi/Code4rena draft. Drafts are
emitted only for READY_FOR_HUMAN_REVIEW / READY_TO_SUBMIT_AFTER_APPROVAL, always
carry the DRAFT-ONLY watermark, require a gate result, and never submit.

Run: /home/dummy/.local/bin/pytest tests/submission/test_platform_renderer.py -v
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
GATES = REPO / "submission" / "gates"
FIXTURES = REPO / "tests" / "fixtures" / "submission_author"
RENDERERS_DIR = REPO / "submission" / "renderers"

sys.path.insert(0, str(REPO))
sys.path.insert(0, str(GATES))

ca = importlib.import_module("submission.author.candidate_author")
pr = importlib.import_module("submission.renderers.platform_renderer")
submission_gate = importlib.import_module("submission_gate")

FILE_TO_ARG = {
    "report.md": "--report",
    "triage_notes.md": "--triage",
    "poc.log": "--poc-output",
    "scope.md": "--scope",
    "program.json": "--program",
    "duplicate_search.md": "--duplicate-search",
    "defense_notes.md": "--defense-notes",
}

# fixture -> expected gate status (from the author fixtures)
EXPECTED_STATUS = {
    "valid_medium_reward_bug": "READY_TO_SUBMIT_AFTER_APPROVAL",
    "duplicate_possible": "READY_FOR_HUMAN_REVIEW",
    "needs_proof_no_trace": "NEEDS_MORE_PROOF",
    "missing_scope": "NEEDS_MORE_PROOF",
    "invalid_privileged_bug": "DO_NOT_SUBMIT",
    "severity_inflated_critical": "DO_NOT_SUBMIT",
}
ALLOWED = [f for f, s in EXPECTED_STATUS.items() if s in pr.ALLOWED_STATUSES]
BLOCKED = [f for f, s in EXPECTED_STATUS.items() if s in pr.BLOCKING_STATUSES]
PLATFORMS = ["immunefi", "code4rena"]


# --------------------------------------------------------------------------- #
# helpers                                                                      #
# --------------------------------------------------------------------------- #

def _author_candidate(fixture: str, tmp_path: Path) -> Path:
    d = FIXTURES / fixture
    argv = []
    for fname, flag in FILE_TO_ARG.items():
        if (d / fname).exists():
            argv += [flag, str(d / fname)]
    out = tmp_path / f"{fixture}.json"
    argv += ["--out", str(out), "--no-timestamp", "--quiet"]
    rc = ca.main(argv)
    assert rc == 0
    return out


def _candidate_and_report(fixture: str, tmp_path: Path):
    path = _author_candidate(fixture, tmp_path)
    candidate = json.loads(path.read_text())
    report = submission_gate.evaluate_candidate(candidate)
    return candidate, report, path


# --------------------------------------------------------------------------- #
# HEADLINE: blocking statuses can never emit a draft                           #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("fixture", BLOCKED)
@pytest.mark.parametrize("platform", PLATFORMS)
def test_blocking_status_cannot_emit_draft(fixture, platform, tmp_path):
    candidate, report, _ = _candidate_and_report(fixture, tmp_path)
    assert report["recommended_status"] in pr.BLOCKING_STATUSES
    ok, payload = pr.emit_draft(candidate, report, platform)
    assert ok is False
    assert "refused" in payload.lower()


@pytest.mark.parametrize("fixture", BLOCKED)
def test_cli_blocked_returns_3_and_writes_no_file(fixture, tmp_path):
    path = _author_candidate(fixture, tmp_path)
    out = tmp_path / "draft.md"
    rc = pr.main(["--candidate", str(path), "--platform", "immunefi",
                  "--run-gate", "--out", str(out), "--quiet"])
    assert rc == 3
    assert not out.exists()


# --------------------------------------------------------------------------- #
# allowed statuses emit a watermarked draft                                    #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("fixture", ALLOWED)
@pytest.mark.parametrize("platform", PLATFORMS)
def test_allowed_status_emits_draft(fixture, platform, tmp_path):
    candidate, report, _ = _candidate_and_report(fixture, tmp_path)
    ok, draft = pr.emit_draft(candidate, report, platform)
    assert ok is True
    assert "DRAFT ONLY — NOT SUBMITTED" in draft
    assert f"Gate status: {report['recommended_status']}" in draft
    assert "Human approval required: true" in draft
    assert candidate["title"] in draft
    # Immunefi has a Severity section; Code4rena sets severity in its own UI.
    if platform == "immunefi":
        assert candidate["severity_claim"] in draft


def test_review_draft_lists_warnings(tmp_path):
    candidate, report, _ = _candidate_and_report("duplicate_possible", tmp_path)
    assert report["recommended_status"] == "READY_FOR_HUMAN_REVIEW"
    ok, draft = pr.emit_draft(candidate, report, "immunefi")
    assert ok
    assert "REVIEW DRAFT" in draft
    assert "Warnings:" in draft
    # at least one of the gate's warnings is surfaced verbatim
    assert any(w in draft for w in report["warnings"])


def test_ready_draft_requires_final_review(tmp_path):
    candidate, report, _ = _candidate_and_report("valid_medium_reward_bug", tmp_path)
    assert report["recommended_status"] == "READY_TO_SUBMIT_AFTER_APPROVAL"
    ok, draft = pr.emit_draft(candidate, report, "immunefi")
    assert ok
    assert "Final manual review still required before submission." in draft


def test_immunefi_required_sections(tmp_path):
    candidate, report, _ = _candidate_and_report("valid_medium_reward_bug", tmp_path)
    _, draft = pr.emit_draft(candidate, report, "immunefi")
    for section in ["## Program", "## Asset / Target", "## Impact", "## Severity",
                    "## Title", "## Description", "## Vulnerability Details",
                    "## Impact Details", "## Proof of Concept", "## Recommended Mitigation",
                    "## Evidence", "## Assumptions / Limitations", "## Human Review Checklist"]:
        assert section in draft, section


def test_code4rena_required_sections(tmp_path):
    candidate, report, _ = _candidate_and_report("valid_medium_reward_bug", tmp_path)
    _, draft = pr.emit_draft(candidate, report, "code4rena")
    for section in ["## Title", "## Summary", "## Vulnerability Details", "## Impact",
                    "## Proof of Concept", "## Recommended Mitigation",
                    "## Links to Affected Code"]:
        assert section in draft, section


def test_mitigation_is_placeholder_not_fabricated(tmp_path):
    candidate, report, _ = _candidate_and_report("valid_medium_reward_bug", tmp_path)
    for platform in PLATFORMS:
        _, draft = pr.emit_draft(candidate, report, platform)
        assert "To be completed by the human reviewer" in draft


# --------------------------------------------------------------------------- #
# safety: no submission / automation, gate result required                     #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("fixture", ALLOWED)
@pytest.mark.parametrize("platform", PLATFORMS)
def test_no_submission_or_automation_tokens(fixture, platform, tmp_path):
    candidate, report, _ = _candidate_and_report(fixture, tmp_path)
    _, draft = pr.emit_draft(candidate, report, platform)
    low = draft.lower()
    for tok in ["auto_submit", "submit_to_immunefi", "submit_to_code4rena",
                "selenium", "playwright", "webdriver", "has been submitted",
                "was submitted"]:
        assert tok not in low, tok


def test_resolve_gate_report_requires_validation(tmp_path):
    candidate, _, _ = _candidate_and_report("valid_medium_reward_bug", tmp_path)
    with pytest.raises(pr.RenderError):
        pr.resolve_gate_report(candidate, gate_result_path=None, run_gate=False)


def test_cli_without_gate_result_errors(tmp_path):
    path = _author_candidate("valid_medium_reward_bug", tmp_path)
    out = tmp_path / "draft.md"
    rc = pr.main(["--candidate", str(path), "--platform", "immunefi",
                  "--out", str(out), "--quiet"])
    assert rc == 1
    assert not out.exists()


def test_cli_allowed_writes_draft(tmp_path):
    path = _author_candidate("valid_medium_reward_bug", tmp_path)
    out = tmp_path / "draft.md"
    rc = pr.main(["--candidate", str(path), "--platform", "code4rena",
                  "--run-gate", "--out", str(out), "--quiet"])
    assert rc == 0
    assert out.exists()
    assert "DRAFT ONLY — NOT SUBMITTED" in out.read_text()


def test_cli_accepts_gate_result_file(tmp_path):
    candidate, report, path = _candidate_and_report("valid_medium_reward_bug", tmp_path)
    gr = tmp_path / "gate.json"
    gr.write_text(json.dumps({"candidates": [report]}))
    out = tmp_path / "draft.md"
    rc = pr.main(["--candidate", str(path), "--platform", "immunefi",
                  "--gate-result", str(gr), "--out", str(out), "--quiet"])
    assert rc == 0
    assert out.exists()


def test_cli_rejects_both_gate_sources(tmp_path):
    candidate, report, path = _candidate_and_report("valid_medium_reward_bug", tmp_path)
    gr = tmp_path / "gate.json"
    gr.write_text(json.dumps(report))
    rc = pr.main(["--candidate", str(path), "--platform", "immunefi",
                  "--gate-result", str(gr), "--run-gate", "--quiet"])
    assert rc == 1


# --------------------------------------------------------------------------- #
# candidate_author --emit-platform wiring                                      #
# --------------------------------------------------------------------------- #

def _author_emit(fixture, tmp_path, platform):
    d = FIXTURES / fixture
    argv = []
    for fname, flag in FILE_TO_ARG.items():
        if (d / fname).exists():
            argv += [flag, str(d / fname)]
    out = tmp_path / "c.json"
    draft = tmp_path / "draft.md"
    argv += ["--out", str(out), "--no-timestamp", "--quiet",
             "--emit-platform", platform, "--platform-out", str(draft)]
    rc = ca.main(argv)
    return rc, draft


@pytest.mark.parametrize("fixture", BLOCKED)
def test_author_emit_blocked_writes_no_draft_but_exits_zero(fixture, tmp_path):
    rc, draft = _author_emit(fixture, tmp_path, "immunefi")
    assert rc == 0  # authoring succeeded; draft refused
    assert not draft.exists()


@pytest.mark.parametrize("fixture", ALLOWED)
def test_author_emit_allowed_writes_draft(fixture, tmp_path):
    rc, draft = _author_emit(fixture, tmp_path, "code4rena")
    assert rc == 0
    assert draft.exists()
    assert "DRAFT ONLY — NOT SUBMITTED" in draft.read_text()


# --------------------------------------------------------------------------- #
# round-trip + isolation + determinism                                         #
# --------------------------------------------------------------------------- #

def test_round_trip_author_gate_draft(tmp_path):
    rc, draft = _author_emit("valid_medium_reward_bug", tmp_path, "immunefi")
    assert rc == 0 and draft.exists()
    text = draft.read_text()
    assert "Gate status: READY_TO_SUBMIT_AFTER_APPROVAL" in text
    assert "## Proof of Concept" in text


FORBIDDEN_TOKENS = [
    "audit_context", "run_pipeline", "output/", "data/triage", "program_scope.json",
    "auto_submit", "submit_to_immunefi", "submit_to_code4rena",
    "selenium", "playwright", "webdriver",
]


def test_renderers_isolation():
    py_files = list(RENDERERS_DIR.glob("*.py"))
    assert py_files
    offenders = []
    for f in py_files:
        text = f.read_text()
        for tok in FORBIDDEN_TOKENS:
            if tok in text:
                offenders.append(f"{f.name}: {tok}")
    assert not offenders, offenders


def test_draft_is_deterministic(tmp_path):
    # author twice independently, render, compare — no wall-clock time in the draft
    p1 = _author_candidate("valid_medium_reward_bug", tmp_path / "a")
    p2 = _author_candidate("valid_medium_reward_bug", tmp_path / "b")
    cand1 = json.loads(p1.read_text())
    cand2 = json.loads(p2.read_text())
    r1 = submission_gate.evaluate_candidate(cand1)
    r2 = submission_gate.evaluate_candidate(cand2)
    _, d1 = pr.emit_draft(cand1, r1, "immunefi")
    _, d2 = pr.emit_draft(cand2, r2, "immunefi")
    assert d1 == d2  # no wall-clock time embedded in the draft
