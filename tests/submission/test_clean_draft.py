"""
Tests for the clean-copy helper (submission/renderers/clean.py).

The cleaner strips internal-only blocks (the DRAFT watermark and the Human
Review Checklist) from an already-allowed, watermarked platform draft. It is
one-way and non-authoritative: it refuses anything that is not a non-blocking
gated draft, never rewrites content, never re-runs the gate, and never touches
the original draft.

Run: /home/dummy/.local/bin/pytest tests/submission/test_clean_draft.py -v
"""
import importlib
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
clean = importlib.import_module("submission.renderers.clean")
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


# --------------------------------------------------------------------------- #
# helpers                                                                      #
# --------------------------------------------------------------------------- #

def _author_candidate(fixture: str, tmp_path: Path) -> dict:
    import json
    d = FIXTURES / fixture
    argv = []
    for fname, flag in FILE_TO_ARG.items():
        if (d / fname).exists():
            argv += [flag, str(d / fname)]
    out = tmp_path / f"{fixture}.json"
    argv += ["--out", str(out), "--no-timestamp", "--quiet"]
    assert ca.main(argv) == 0
    return json.loads(out.read_text())


def _draft(fixture: str, tmp_path: Path, platform="immunefi") -> str:
    candidate = _author_candidate(fixture, tmp_path)
    report = submission_gate.evaluate_candidate(candidate)
    ok, draft = pr.emit_draft(candidate, report, platform)
    assert ok, draft
    return draft


# --------------------------------------------------------------------------- #
# refusals                                                                     #
# --------------------------------------------------------------------------- #

def test_refuses_without_watermark():
    res = clean.validate_clean_draft("# Some report\n\nNo watermark here.\n")
    assert res.ok is False
    assert "watermark" in res.reason.lower()


def test_refuses_already_clean(tmp_path):
    draft = _draft("valid_medium_reward_bug", tmp_path)
    _, cleaned = clean.clean_markdown(draft)
    res = clean.validate_clean_draft(cleaned)
    assert res.ok is False
    assert "already a clean copy" in res.reason.lower()


@pytest.mark.parametrize("status", ["DO_NOT_SUBMIT", "NEEDS_MORE_PROOF"])
def test_refuses_blocking_status(status):
    # synthesise a watermark with a blocking status (defense in depth: the
    # renderer never emits these, but the cleaner must still refuse them)
    md = (
        "> **DRAFT ONLY — NOT SUBMITTED**\n"
        ">\n"
        f"> Gate status: {status}\n"
        "> Human approval required: true\n"
        "\n# Title\n\n## Severity\nHigh\n"
    )
    res = clean.validate_clean_draft(md)
    assert res.ok is False
    assert status in res.reason


def test_cli_refuses_no_watermark(tmp_path):
    src = tmp_path / "plain.md"
    src.write_text("# plain\n\nnothing internal here\n")
    out = tmp_path / "plain.clean.md"
    rc = clean.main(["--draft", str(src), "--out", str(out), "--quiet"])
    assert rc == 3
    assert not out.exists()


def test_cli_refuses_same_path(tmp_path):
    src = tmp_path / "d.md"
    src.write_text("anything")
    rc = clean.main(["--draft", str(src), "--out", str(src), "--quiet"])
    assert rc == 1


# --------------------------------------------------------------------------- #
# stripping behaviour                                                          #
# --------------------------------------------------------------------------- #

def test_removes_watermark_and_checklist(tmp_path):
    draft = _draft("valid_medium_reward_bug", tmp_path)
    assert "## Human Review Checklist" in draft  # precondition (immunefi)
    _, cleaned = clean.clean_markdown(draft)
    assert "DRAFT ONLY — NOT SUBMITTED" not in cleaned
    assert "Gate status:" not in cleaned
    assert "Human approval required:" not in cleaned
    assert "Remove this block" not in cleaned
    assert "## Human Review Checklist" not in cleaned


def test_preserves_core_sections(tmp_path):
    candidate = _author_candidate("valid_medium_reward_bug", tmp_path)
    report = submission_gate.evaluate_candidate(candidate)
    ok, draft = pr.emit_draft(candidate, report, "immunefi")
    _, cleaned = clean.clean_markdown(draft)
    for section in ["## Severity", "## Impact", "## Proof of Concept",
                    "## Evidence", "## Assumptions / Limitations",
                    "## Vulnerability Details", "## Recommended Mitigation"]:
        assert section in cleaned, section
    # title survives
    assert candidate["title"] in cleaned


def test_does_not_modify_severity_text(tmp_path):
    candidate = _author_candidate("valid_medium_reward_bug", tmp_path)
    report = submission_gate.evaluate_candidate(candidate)
    _, draft = pr.emit_draft(candidate, report, "immunefi")
    _, cleaned = clean.clean_markdown(draft)
    # the exact severity value is preserved
    assert f"## Severity\n{candidate['severity_claim']}" in cleaned


def test_preserves_limitations_caveats(tmp_path):
    # the review-draft fixture has assumptions/limitations content that must survive
    candidate = _author_candidate("duplicate_possible", tmp_path)
    report = submission_gate.evaluate_candidate(candidate)
    _, draft = pr.emit_draft(candidate, report, "immunefi")
    _, cleaned = clean.clean_markdown(draft)
    # a real assumption from the report survives the clean
    assert "small-staker" in cleaned.lower() or "Realistic small-staker" in cleaned \
        or any(a in cleaned for a in candidate["assumptions"])
    # but the watermark's own "> Warnings:" lines are gone
    assert "> Warnings:" not in cleaned


def test_clean_has_provenance_comment(tmp_path):
    draft = _draft("valid_medium_reward_bug", tmp_path)
    _, cleaned = clean.clean_markdown(draft)
    assert cleaned.startswith(clean.CLEAN_PROVENANCE)


def test_strip_requires_watermark():
    with pytest.raises(ValueError):
        clean.strip_draft_artifacts("# no watermark\n")


def test_deterministic(tmp_path):
    draft = _draft("valid_medium_reward_bug", tmp_path)
    _, c1 = clean.clean_markdown(draft)
    _, c2 = clean.clean_markdown(draft)
    assert c1 == c2


def test_code4rena_clean_has_no_checklist_anyway(tmp_path):
    # code4rena drafts have no checklist; cleaning still removes the watermark
    draft = _draft("valid_medium_reward_bug", tmp_path, platform="code4rena")
    assert "## Human Review Checklist" not in draft
    ok, cleaned = clean.clean_markdown(draft)
    assert ok
    assert "DRAFT ONLY — NOT SUBMITTED" not in cleaned
    assert "## Links to Affected Code" in cleaned


# --------------------------------------------------------------------------- #
# original-file safety + CLI                                                   #
# --------------------------------------------------------------------------- #

def test_original_draft_untouched_cli(tmp_path):
    draft = _draft("valid_medium_reward_bug", tmp_path)
    src = tmp_path / "draft.md"
    src.write_text(draft)
    before = src.read_bytes()
    out = tmp_path / "draft.clean.md"
    rc = clean.main(["--draft", str(src), "--out", str(out), "--quiet"])
    assert rc == 0
    assert out.exists()
    assert src.read_bytes() == before  # byte-identical


def test_cli_allowed_writes_clean(tmp_path):
    draft = _draft("duplicate_possible", tmp_path)
    src = tmp_path / "draft.md"
    src.write_text(draft)
    out = tmp_path / "draft.clean.md"
    rc = clean.main(["--draft", str(src), "--out", str(out), "--quiet"])
    assert rc == 0
    text = out.read_text()
    assert clean.CLEAN_PROVENANCE in text
    assert "DRAFT ONLY — NOT SUBMITTED" not in text


# --------------------------------------------------------------------------- #
# platform_renderer --clean-out wiring                                         #
# --------------------------------------------------------------------------- #

def _candidate_path(fixture, tmp_path):
    import json
    candidate = _author_candidate(fixture, tmp_path)
    p = tmp_path / "cand.json"
    p.write_text(json.dumps(candidate))
    return p


def test_renderer_clean_out_writes_both(tmp_path):
    cand = _candidate_path("valid_medium_reward_bug", tmp_path)
    draft = tmp_path / "d.md"
    cleaned = tmp_path / "d.clean.md"
    rc = pr.main(["--candidate", str(cand), "--platform", "immunefi", "--run-gate",
                  "--out", str(draft), "--clean-out", str(cleaned), "--quiet"])
    assert rc == 0
    assert draft.exists() and cleaned.exists()
    assert "DRAFT ONLY — NOT SUBMITTED" in draft.read_text()      # original keeps watermark
    assert "DRAFT ONLY — NOT SUBMITTED" not in cleaned.read_text()
    assert clean.CLEAN_PROVENANCE in cleaned.read_text()


def test_renderer_clean_out_requires_out(tmp_path):
    cand = _candidate_path("valid_medium_reward_bug", tmp_path)
    cleaned = tmp_path / "d.clean.md"
    rc = pr.main(["--candidate", str(cand), "--platform", "immunefi", "--run-gate",
                  "--clean-out", str(cleaned), "--quiet"])
    assert rc == 1
    assert not cleaned.exists()


def test_renderer_blocked_writes_no_clean(tmp_path):
    cand = _candidate_path("invalid_privileged_bug", tmp_path)
    draft = tmp_path / "d.md"
    cleaned = tmp_path / "d.clean.md"
    rc = pr.main(["--candidate", str(cand), "--platform", "immunefi", "--run-gate",
                  "--out", str(draft), "--clean-out", str(cleaned), "--quiet"])
    assert rc == 3  # blocking gate status
    assert not draft.exists()
    assert not cleaned.exists()


# --------------------------------------------------------------------------- #
# isolation                                                                    #
# --------------------------------------------------------------------------- #

FORBIDDEN_TOKENS = [
    "submission_gate", "audit_context", "run_pipeline", "data/triage", "output/",
    "auto_submit", "submit_to_immunefi", "submit_to_code4rena",
    "selenium", "playwright", "webdriver",
]


def test_clean_isolation():
    text = (RENDERERS_DIR / "clean.py").read_text()
    offenders = [tok for tok in FORBIDDEN_TOKENS if tok in text]
    assert not offenders, offenders
