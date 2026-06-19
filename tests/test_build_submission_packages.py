"""build_submission_packages.py — materializes a real-world audit's findings into reports/<dir>/submissions/
NON-DESTRUCTIVELY. Pins: real-world gate (eval/blind no-op), scaffold + copies for a new finding, human prose
never overwritten, idempotent clean re-run, and REVIEW_QUEUE status (NEEDS REVIEW vs HUMAN-EDITED)."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_submission_packages as bsp  # noqa: E402
import sync_audit_to_ledger as sal  # noqa: E402


def _audit(tmp, audit_id, meta, candidates, poc_rows, report_dir="reports/r1"):
    a = tmp / "audits" / audit_id
    (a / "output" / "candidates").mkdir(parents=True, exist_ok=True)
    (a / "data" / "runtime_poc").mkdir(parents=True, exist_ok=True)
    meta = {**meta, "report_dir": report_dir}
    (a / "meta.json").write_text(json.dumps(meta))
    for c in candidates:
        (a / "output" / "candidates" / f"{c['id']}.json").write_text(json.dumps(c))
    (a / "data" / "runtime_poc" / "results.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in poc_rows))
    # harness src + test that the builder copies from
    h = tmp / report_dir / "harness"
    (h / "src").mkdir(parents=True, exist_ok=True)
    (h / "test").mkdir(parents=True, exist_ok=True)
    (h / "src" / "Foo.sol").write_text("// vulnerable Foo\ncontract Foo {}\n")
    (h / "test" / "PoC_Foo.t.sol").write_text("// PoC\ncontract PoC_Foo {}\n")
    return a


def _cand(fid, sev="High", proved=True, state="ready", score=0.9):
    return {"id": fid, "state": state, "title": f"{fid} finding",
            "classification": {"severity": sev}, "location": {"file": "Foo.sol", "contract": "Foo"},
            "manifest_refs": ["src/Foo.sol:bar"], "poc": {"proved": proved},
            "confirmation": {"score": score},
            "ice": {"exploit_path": "do X then assert Y"},
            "evidence": {"impact": "drains", "who_loses": "users", "who_gains": "attacker",
                         "suggested_fix": "add a check"},
            "readiness_advisories": ["confirm deployment reachability"]}


@pytest.fixture
def patched(tmp_path, monkeypatch):
    monkeypatch.setattr(bsp, "ROOT", tmp_path)
    monkeypatch.setattr(sal, "ROOT", tmp_path)
    return tmp_path


def test_realworld_gate_skips_eval(patched):
    tmp = patched
    _audit(tmp, "x-eval", {"platform": "C4"}, [_cand("F1")],
           [{"finding_id": "F1", "test_contract": "PoC_Foo", "test_file": "reports/r1/harness/test/PoC_Foo.t.sol"}])
    res, _ = bsp.build("x-eval", dry=False)
    assert res.get("skipped") is True
    assert not (tmp / "reports" / "r1" / "submissions").exists()  # eval audit writes nothing


def test_new_finding_scaffolded_and_routed(patched):
    tmp = patched
    _audit(tmp, "rw-1", {"platform": "HackenProof", "ledger_target": "T", "ledger_sync": True,
                         "ledger_report_ids": {"BSA-1": "N-1"}},
           [_cand("BSA-1")],
           [{"finding_id": "BSA-1", "test_contract": "PoC_Foo", "test_file": "reports/r1/harness/test/PoC_Foo.t.sol"}])
    bsp.build("rw-1", dry=False)
    pkg = tmp / "reports" / "r1" / "submissions" / "N-1"
    assert (pkg / "candidate_record.generated.json").exists()      # generated machine snapshot
    assert (pkg / "poc" / "PoC_Foo.t.sol").exists()                # copied from the gitignored harness
    assert (pkg / "vulnerable" / "Foo.sol").exists()               # copied vulnerable source
    report = (pkg / "report.md").read_text()
    assert bsp.SCAFFOLD_BANNER in report                           # scaffold is banner-stamped NEEDS REVIEW
    assert (pkg / "SUBMISSION.md").exists() and (pkg / "repro.md").exists()
    sc = json.loads((pkg / "submission_candidate.json").read_text())
    assert sc["recommended_status"] == "NEEDS_HUMAN_REVIEW" and sc["_auto_scaffold"] is True
    # routed in the review queue as NEEDS REVIEW (no poc_output.log captured -> flagged)
    q = (tmp / "reports" / "r1" / "submissions" / "REVIEW_QUEUE.md").read_text()
    row = next(ln for ln in q.splitlines() if ln.startswith("| N-1 "))
    assert "NEEDS REVIEW" in row and "NEEDS POC LOG" in row


def test_human_prose_never_overwritten(patched):
    tmp = patched
    _audit(tmp, "rw-1", {"platform": "HackenProof", "ledger_sync": True, "ledger_report_ids": {"BSA-1": "N-1"}},
           [_cand("BSA-1")],
           [{"finding_id": "BSA-1", "test_contract": "PoC_Foo", "test_file": "reports/r1/harness/test/PoC_Foo.t.sol"}])
    bsp.build("rw-1", dry=False)
    pkg = tmp / "reports" / "r1" / "submissions" / "N-1"
    # human finalizes the report (removes the banner) and captures a poc log
    human = "# N-1 — finalized by a human\n\nReal analysis here.\n"
    (pkg / "report.md").write_text(human)
    (pkg / "poc_output.log").write_text("[PASS] real run\n")
    res, _ = bsp.build("rw-1", dry=False)
    assert (pkg / "report.md").read_text() == human               # human prose byte-for-byte preserved
    # the only thing that may change is the builder-owned status table (NEEDS REVIEW -> HUMAN-EDITED); no prose write
    assert all("REVIEW_QUEUE.md" in p for _, p in res["planned"])
    q = (tmp / "reports" / "r1" / "submissions" / "REVIEW_QUEUE.md").read_text()
    row = next(ln for ln in q.splitlines() if ln.startswith("| N-1 "))
    assert "HUMAN-EDITED" in row and "NEEDS POC LOG" not in row   # status flips once edited + log present
    third, _ = bsp.build("rw-1", dry=False)
    assert third["planned"] == []                                # and settles to a clean no-op


def test_idempotent_clean_second_run(patched):
    tmp = patched
    _audit(tmp, "rw-1", {"platform": "HackenProof", "ledger_sync": True},
           [_cand("ECON-2", sev="Low")],
           [{"finding_id": "ECON-2", "test_contract": "PoC_Foo", "test_file": "reports/r1/harness/test/PoC_Foo.t.sol"}])
    first, _ = bsp.build("rw-1", dry=False)
    assert first["planned"]                                        # first run creates files
    second, _ = bsp.build("rw-1", dry=False)
    assert second["planned"] == []                                # second run is a clean no-op
