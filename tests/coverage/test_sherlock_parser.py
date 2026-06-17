"""Recall Lab — awarded-report parser handles BOTH C4 (`## [[M-01] t](url)`) and Sherlock (`# Issue M-1: t`)
formats. The Sherlock gap silently produced awarded=[] which wiped hand adjudications on re-scaffold (the
Cap wart). C4 takes precedence; Sherlock is the fallback (severity from the ID prefix, Low excluded).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import adjudicate as adj  # noqa: E402


def _parse(tmp_path, text):
    p = tmp_path / "report.md"
    p.write_text(text)
    return adj.parse_awarded(p)


def test_sherlock_issue_headers(tmp_path):
    rows = _parse(tmp_path, "# Issue M-1: First medium bug\n\nbody\n\n# Issue H-2: A high bug\n\nbody\n")
    ids = {r["id"]: r for r in rows}
    assert set(ids) == {"M-1", "H-2"}
    assert ids["M-1"]["severity"] == "Medium" and ids["H-2"]["severity"] == "High"
    assert ids["M-1"]["title"] == "First medium bug"


def test_sherlock_excludes_low(tmp_path):
    rows = _parse(tmp_path, "# Issue M-1: keep\n# Issue L-1: drop low\n")
    assert {r["id"] for r in rows} == {"M-1"}


def test_sherlock_dedup_repeated_header(tmp_path):
    # reports often repeat the header (TOC + body); keep one row per id
    rows = _parse(tmp_path, "# Issue M-1: title\nbody mentions # Issue M-1: title again\n")
    assert sum(1 for r in rows if r["id"] == "M-1") == 1


def test_c4_format_still_parses_and_takes_precedence(tmp_path):
    txt = "# Medium Risk Findings\n\n## [[M-01] C4 style bug](https://x)\n\nbody\n"
    rows = _parse(tmp_path, txt)
    assert len(rows) == 1 and rows[0]["id"] == "M-01" and rows[0]["severity"] == "Medium"
    assert rows[0]["title"] == "C4 style bug"


def test_real_cap_report_yields_ten(tmp_path):
    rp = Path(__file__).resolve().parents[2] / "audits" / "cap-2025-07-eval" / "_sealed_answer_key" / "report.md"
    if rp.exists():
        rows = adj.parse_awarded(rp)
        assert len(rows) == 10 and all(r["severity"] == "Medium" for r in rows)
