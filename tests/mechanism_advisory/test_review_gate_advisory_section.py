"""P136 — generate_review_gate advisory section (NOT-confirmed) tests.

Proves: advisories render in a separate NOT-confirmed section; they do NOT appear in the Validated Findings
table; confirmed-findings count is unchanged; missing/malformed/disabled/empty context renders no section
without error.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import generate_review_gate as g  # noqa: E402

ADV = {"source_detector": "units_invariant", "detector_status": "report_only", "contract": "OracleX",
       "function": "getValue", "mechanism_class": "chainlink_decimals", "confidence": "high",
       "route_reason": "mechanism layer flagged this surface", "advisory_only": True, "submission_ready": False}
REC = {"contract": "OracleX", "function": "_getValue", "recommended_prompt": "deep_pass_value_provenance",
       "prompt_reason": "multi-hop oracle/value loop"}


def _setup(tmp_path, monkeypatch, *, advisories=None, recs=None, surfaced=True, write_ctx=True,
           ctx_raw=None, confirmed=0):
    out = tmp_path / "output"; out.mkdir()
    tri = tmp_path / "data" / "triage"; tri.mkdir(parents=True)
    for i in range(confirmed):
        (tri / f"F-{i}.md").write_text(f"# Confirmed Finding {i}\n\nCONFIRMED\n\n## Triage Notes\nok\n")

    def ap(*parts):
        p = tmp_path.joinpath(*parts)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p
    monkeypatch.setattr(g, "audit_path", ap)
    monkeypatch.setattr(g, "get_audit_meta", lambda: {"audit_id": "t", "name": "T"})
    monkeypatch.setattr(g, "write_session", lambda d: None)
    if write_ctx:
        raw = ctx_raw if ctx_raw is not None else json.dumps(
            {"surfaced": surfaced, "advisories": advisories or [], "deep_pass_recommendations": recs or []})
        (out / "mechanism_advisory_context.json").write_text(raw)
    return out


def _run(tmp_path):
    with pytest.raises(SystemExit):
        g.main()
    return (tmp_path / "output" / "review_gate.md").read_text()


def test_advisory_section_rendered(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, advisories=[ADV])
    doc = _run(tmp_path)
    assert "## Advisory Context — NOT confirmed (mechanism detectors)" in doc
    assert "OracleX.getValue" in doc
    assert "advisory_only=true" in doc and "submission_ready=false" in doc


def test_advisory_not_in_validated_findings(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, advisories=[ADV], confirmed=1)
    doc = _run(tmp_path)
    validated = doc.split("## Validated Findings")[1].split("## Advisory Context")[0]
    # the advisory location must NOT appear in the Validated Findings table
    assert "OracleX.getValue" not in validated
    # the advisory appears only in the advisory section
    assert "OracleX.getValue" in doc.split("## Advisory Context")[1]


def test_confirmed_count_unchanged_by_advisories(tmp_path, monkeypatch, capsys):
    _setup(tmp_path, monkeypatch, advisories=[ADV, dict(ADV, contract="B")], confirmed=2)
    _run(tmp_path)
    out = capsys.readouterr().out
    assert "Confirmed findings: 2" in out  # 2 confirmed, advisories excluded from the count


def test_missing_context_no_section_no_error(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, write_ctx=False)
    doc = _run(tmp_path)
    assert "Advisory Context" not in doc


def test_malformed_context_no_error(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, ctx_raw="{ not json ]")
    doc = _run(tmp_path)
    assert "Advisory Context" not in doc


def test_disabled_context_no_section(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, advisories=[ADV], surfaced=False)
    doc = _run(tmp_path)
    assert "Advisory Context" not in doc


def test_empty_context_no_section(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, advisories=[], recs=[])
    doc = _run(tmp_path)
    assert "Advisory Context" not in doc


def test_deep_pass_recommendations_rendered(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, advisories=[ADV], recs=[REC])
    doc = _run(tmp_path)
    assert "Deep-pass recommendations" in doc
    assert "deep_pass_value_provenance" in doc and "OracleX._getValue" in doc
