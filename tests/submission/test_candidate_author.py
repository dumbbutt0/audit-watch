"""
Tests for the candidate-authoring layer (submission/author).

The author is a TRANSLATOR: raw artifacts -> schema-shaped submission_candidate.json.
These tests prove it never fabricates evidence, never decides readiness, always
requires human approval, has no auto-submit path, and that its output is consumed
by the existing submission gate which produces the cautious verdict.

Run: /home/dummy/.local/bin/pytest tests/submission/test_candidate_author.py -v
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
GATES = REPO / "submission" / "gates"
FIXTURES = REPO / "tests" / "fixtures" / "submission_author"
AUTHOR_DIR = REPO / "submission" / "author"

# import the author as a package, and the gate as flat sibling modules
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(GATES))

ca = importlib.import_module("submission.author.candidate_author")
submission_gate = importlib.import_module("submission_gate")
_common = importlib.import_module("_common")

# fixture filename -> CLI flag (should_not_read.md is deliberately excluded)
FILE_TO_ARG = {
    "report.md": "--report",
    "triage_notes.md": "--triage",
    "poc.log": "--poc-output",
    "scope.md": "--scope",
    "program.json": "--program",
    "duplicate_search.md": "--duplicate-search",
    "defense_notes.md": "--defense-notes",
}

FIXTURE_NAMES = sorted(p.name for p in FIXTURES.iterdir() if p.is_dir())


# --------------------------------------------------------------------------- #
# helpers                                                                      #
# --------------------------------------------------------------------------- #

def _argv_for(fixture: str, out_path: Path, extra=None):
    d = FIXTURES / fixture
    argv = []
    for fname, flag in FILE_TO_ARG.items():
        if (d / fname).exists():
            argv += [flag, str(d / fname)]
    argv += ["--out", str(out_path), "--no-timestamp", "--quiet"]
    if extra:
        argv += extra
    return argv


def _author(fixture: str, tmp_path: Path, extra=None):
    """Run the author CLI over a fixture; return (rc, candidate_dict)."""
    out = tmp_path / f"{fixture}.json"
    rc = ca.main(_argv_for(fixture, out, extra))
    candidate = json.loads(out.read_text()) if out.exists() else None
    return rc, candidate


def _expected(fixture: str) -> dict:
    return json.loads((FIXTURES / fixture / "expected_properties.json").read_text())


def _gate_status(candidate: dict) -> dict:
    return submission_gate.evaluate_candidate(candidate)


# --------------------------------------------------------------------------- #
# per-fixture: candidate properties + gate status                             #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("fixture", FIXTURE_NAMES)
def test_candidate_properties(fixture, tmp_path):
    rc, candidate = _author(fixture, tmp_path)
    assert rc == 0
    assert candidate is not None
    expected = _expected(fixture)["candidate"]
    for key, val in expected.items():
        assert candidate[key] == val, f"{fixture}: {key} = {candidate[key]!r}, want {val!r}"


@pytest.mark.parametrize("fixture", FIXTURE_NAMES)
def test_candidate_is_schema_valid(fixture, tmp_path):
    _, candidate = _author(fixture, tmp_path)
    assert _common.validate_schema(candidate) == []


@pytest.mark.parametrize("fixture", FIXTURE_NAMES)
def test_gate_status_matches_expected(fixture, tmp_path):
    _, candidate = _author(fixture, tmp_path)
    report = _gate_status(candidate)
    assert report["recommended_status"] == _expected(fixture)["expected_gate_status"], report


@pytest.mark.parametrize("fixture", FIXTURE_NAMES)
def test_blocker_contains_when_expected(fixture, tmp_path):
    exp = _expected(fixture)
    if "expect_blocker_contains" not in exp:
        pytest.skip("no blocker expectation")
    _, candidate = _author(fixture, tmp_path)
    report = _gate_status(candidate)
    needle = exp["expect_blocker_contains"].lower()
    assert any(needle in b.lower() for b in report.get("blockers", [])), report.get("blockers")


# --------------------------------------------------------------------------- #
# safety rules (brief items 1-15)                                              #
# --------------------------------------------------------------------------- #

def test_severity_preserved_not_corrected(tmp_path):
    # author keeps the inflated Critical claim; the GATE downgrades/blocks it
    _, candidate = _author("severity_inflated_critical", tmp_path)
    assert candidate["severity_claim"] == "Critical"
    report = _gate_status(candidate)
    assert report["recommended_status"] == "DO_NOT_SUBMIT"
    assert any("inflation" in b.lower() for b in report["blockers"])


def test_no_invented_poc_trace(tmp_path):
    _, candidate = _author("needs_proof_no_trace", tmp_path)
    assert candidate["poc_status"] == "none"
    assert candidate["proof_type"] == "reasoning_only"
    assert candidate["poc_path"] == ""
    assert candidate["reproduction_steps"] == []


def test_no_invented_scope(tmp_path):
    _, candidate = _author("missing_scope", tmp_path)
    assert candidate["scope_status"] == "uncertain"
    assert candidate["in_scope_asset"] == ""
    # the unknown program booleans are omitted, not asserted True
    assert candidate["bounty_program_mapping"].get("impact_in_scope") is None


def test_no_invented_duplicate_search(tmp_path):
    _, candidate = _author("missing_scope", tmp_path)  # no duplicate_search.md
    assert candidate["duplicate_check_status"] == "not_searched"
    assert candidate["known_issue_check_status"] == "not_searched"


def test_no_invented_line_numbers(tmp_path):
    # report names a contract but NO line numbers -> no file:line must appear
    _, candidate = _author("needs_proof_no_trace", tmp_path)
    import re
    for link in candidate["evidence_links"]:
        assert not re.search(r":\d", link), f"invented line number in {link!r}"


@pytest.mark.parametrize("fixture", FIXTURE_NAMES)
def test_human_approval_always_required(fixture, tmp_path):
    _, candidate = _author(fixture, tmp_path)
    assert candidate["human_approval_required"] is True


@pytest.mark.parametrize("fixture", FIXTURE_NAMES)
def test_author_never_emits_ready(fixture, tmp_path):
    _, candidate = _author(fixture, tmp_path)
    assert candidate["recommended_status"] != "READY_TO_SUBMIT_AFTER_APPROVAL"
    assert candidate["recommended_status"] == "NEEDS_MORE_PROOF"


@pytest.mark.parametrize("fixture", FIXTURE_NAMES)
def test_no_auto_submit_field(fixture, tmp_path):
    _, candidate = _author(fixture, tmp_path)
    blob = json.dumps(candidate).lower()
    assert "auto_submit" not in blob
    assert "submit_to_immunefi" not in blob
    assert "submit_to_code4rena" not in blob


@pytest.mark.parametrize("fixture", FIXTURE_NAMES)
def test_gate_consumes_candidate(fixture, tmp_path):
    _, candidate = _author(fixture, tmp_path)
    report = _gate_status(candidate)
    assert report["recommended_status"] in _common.STATUSES
    assert report["human_approval_required"] is True


def test_do_not_submit_does_not_crash_author(tmp_path):
    # gate verdict DO_NOT_SUBMIT must NOT make authoring fail
    rc, _ = _author("invalid_privileged_bug", tmp_path, extra=["--run-gate"])
    assert rc == 0


def test_missing_optional_inputs_become_evidence_gaps(tmp_path):
    _, candidate = _author("needs_proof_no_trace", tmp_path)
    gaps = candidate["authoring_metadata"]["evidence_gaps"]
    joined = " ".join(gaps).lower()
    assert gaps, "expected recorded evidence gaps"
    assert "poc" in joined
    assert "duplicate" in joined or "not_searched" in joined
    assert "defense" in joined


def test_only_passed_files_are_read(tmp_path):
    # the valid fixture has should_not_read.md which we never pass on the CLI
    _, candidate = _author("valid_medium_reward_bug", tmp_path)
    blob = json.dumps(candidate)
    assert "SENTINEL_DO_NOT_READ" not in blob
    for src in candidate["authoring_metadata"]["source_files"]:
        assert "should_not_read" not in src


def test_author_confidence_never_high(tmp_path):
    for fixture in FIXTURE_NAMES:
        _, candidate = _author(fixture, tmp_path)
        assert candidate["authoring_metadata"]["author_confidence"] in ("low", "medium")


# --------------------------------------------------------------------------- #
# isolation: submission/author runtime code must not touch the pipeline       #
# --------------------------------------------------------------------------- #

FORBIDDEN_TOKENS = [
    "audit_context",
    "run_pipeline",
    "output/",
    "data/triage",
    "program_scope.json",
    "auto_submit",
    "submit_to_immunefi",
    "submit_to_code4rena",
    "selenium",
    "playwright",
    "webdriver",
]


def test_author_isolation():
    py_files = list(AUTHOR_DIR.glob("*.py"))
    assert py_files, "no author python files found"
    offenders = []
    for f in py_files:
        text = f.read_text()
        for tok in FORBIDDEN_TOKENS:
            if tok in text:
                offenders.append(f"{f.name}: {tok}")
    assert not offenders, offenders


def test_author_does_not_import_pipeline():
    # the only cross-package imports allowed are the sibling submission gate modules
    for f in AUTHOR_DIR.glob("*.py"):
        text = f.read_text()
        assert "import audit_context" not in text
        assert "from audit_context" not in text


# --------------------------------------------------------------------------- #
# round-trip: author -> gate -> readiness report                              #
# --------------------------------------------------------------------------- #

def test_round_trip_valid(tmp_path):
    out = tmp_path / "candidate.json"
    readiness = tmp_path / "readiness.md"
    argv = _argv_for("valid_medium_reward_bug", out, extra=["--run-gate",
                                                            "--readiness-out", str(readiness)])
    rc = ca.main(argv)
    assert rc == 0
    assert out.exists() and readiness.exists()

    candidate = json.loads(out.read_text())
    assert _common.validate_schema(candidate) == []

    report = submission_gate.evaluate_candidate(candidate)
    assert report["recommended_status"] == "READY_TO_SUBMIT_AFTER_APPROVAL"

    md = readiness.read_text()
    assert "Human approval required" in md
    # no submission action anywhere in the rendered report
    low = md.lower()
    assert "auto_submit" not in low
    assert "submit_to_immunefi" not in low


def test_round_trip_do_not_submit_reports_downgrade(tmp_path):
    out = tmp_path / "c.json"
    readiness = tmp_path / "r.md"
    argv = _argv_for("severity_inflated_critical", out,
                     extra=["--run-gate", "--readiness-out", str(readiness)])
    rc = ca.main(argv)
    assert rc == 0  # DO_NOT_SUBMIT is not an authoring failure
    md = readiness.read_text()
    assert "DO_NOT_SUBMIT" in md
    assert "Re-file as" in md  # downgrade note from the impact/severity gate


def test_round_trip_missing_evidence_in_report(tmp_path):
    out = tmp_path / "c.json"
    readiness = tmp_path / "r.md"
    argv = _argv_for("needs_proof_no_trace", out,
                     extra=["--run-gate", "--readiness-out", str(readiness)])
    rc = ca.main(argv)
    assert rc == 0
    md = readiness.read_text()
    assert "NEEDS_MORE_PROOF" in md
    assert "Needs more proof" in md


# --------------------------------------------------------------------------- #
# authoring failure modes (exit code 1)                                        #
# --------------------------------------------------------------------------- #

def test_missing_report_file_fails(tmp_path):
    out = tmp_path / "c.json"
    rc = ca.main(["--report", str(tmp_path / "does_not_exist.md"),
                  "--out", str(out), "--no-timestamp", "--quiet"])
    assert rc == 1
    assert not out.exists()
