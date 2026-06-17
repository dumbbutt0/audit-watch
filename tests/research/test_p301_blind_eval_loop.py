"""P301 — standing blind-eval recall-gap /loop. Mine misses -> recover by executed PoC -> stage. Gates stay tight.

Runs `forge` (recovery is by real execution). Answer keys + ground_truth + contest source READ-ONLY.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/research"))
import executed_poc_verifier as epv  # noqa: E402
import submission_filter as sf  # noqa: E402
import shutil

D = ROOT / "documentation/research/assisted_mode/p301_blind_eval_loop"
O = D / "outputs"
STATE = O / "loop_state.json"
BACKLOG = ROOT / "data/learning/_proposed/recall_gap_backlog.jsonl"
FORGE = shutil.which("forge")
needs_forge = pytest.mark.skipif(FORGE is None, reason="forge not installed")

VERIFIER_HASH = "1a005811fbb9e0d0"
FORBIDDEN = {
    "scripts/dashboard_sync.py": "c1af70e1", "prompts/deep_trace.md": "c095c426",
    "scripts/min_confirm_gate.py": "2a15169a", "scripts/confirm_gate.py": "afc481c9",
    "scripts/validate_p208_l3_readiness.py": "ae55eb80",
}
READ_ONLY = {
    "data/fp_autopsies/rejection_rules.jsonl": "a9f393935ab349d5",
    "audits/beanstalk-2024-05/data/evaluation/ground_truth.jsonl": "35f44065901c5334",
}
DOC_FILES = ("DESIGN.md", "RESULTS.md", "EVIDENCE_AUDIT.md", "PRE_HUNT_CHECKLIST.md", "LIMITATIONS.md",
             "VERDICT.md", "ROLLBACK_PLAN.md")
VERDICTS = ("A — ", "B — ", "C — ", "D — ")


def _state():
    return json.loads(STATE.read_text())


# ---- the standing queue + state ----
def test_suite_has_target_queue():
    cfg = json.loads((ROOT / "config/research_blind_eval_suite.json").read_text())
    assert len(cfg["queue"]) >= 13 and all("audit_id" in q and "key_source" in q for q in cfg["queue"])


def test_state_scored_and_resumable():
    st = _state()
    scored = [q for q in st["queue"] if q["status"] in ("scored", "recovered")]
    assert len(scored) >= 3
    # resumable: every queue entry has a status
    assert all(q.get("status") for q in st["queue"])


# ---- score mined the recall gap (the missed awarded findings) into the staged backlog ----
def test_recall_gap_mined_and_staged():
    st = _state()
    gap = sum(len(q.get("missed", [])) for q in st["queue"])
    assert gap >= 50  # 58 across the first 3 targets (revert-lend 31 + panoptic 22 + silo 5)
    rows = [json.loads(l) for l in BACKLOG.read_text().splitlines() if l.strip()]
    assert len(rows) >= 50 and all(r["promoted"] is False and r["status"] == "STAGED_RECALL_GAP" for r in rows)


# ---- recover: executed-PoC, gates tight ----
def test_recoveries_are_verifier_backed():
    st = _state()
    recovered = [(q["audit_id"], i) for q in st["queue"] for i in q.get("recovered", [])]
    assert len(recovered) >= 1  # >=1 missed/under-recalled awarded finding recovered by executed PoC


@needs_forge
def test_recovered_loci_verify_live_fp_zero():
    st = _state()
    records = []
    for q in st["queue"]:
        slug = q["audit_id"].split("-")[0]
        for i in q.get("recovered", []):
            safe = str(i).replace("/", "_")  # combined ids like M-05/M-06 -> filesystem-safe dir
            d = ROOT / "pocs/p301" / f"{slug}__{safe}"
            rec = epv.verify_poc(d, finding_id=f"{q['audit_id']}-{safe}")
            assert rec["validity_confirmed"] is True  # a recovery is a real executed confirmation
            records.append(rec)
    filt = sf.filter_many(records)
    assert filt["filter_leaks"] == 0 and filt["submit"] == len(records)  # gates tight: confirmed-FP=0


def test_submission_filter_gate_tight():
    assert sf.filter_record({"validity_confirmed": True, "status": "confirmed_by_logic_differential"})["label"] == "submit"
    assert sf.filter_record({"validity_confirmed": False, "status": "needs_execution"})["label"] == "needs_human"


# ---- authority: human-only artifacts untouched; no auto-submit ----
def test_loop_never_writes_ground_truth_or_promotes():
    t = (ROOT / "scripts/research/blind_eval_loop.py").read_text()
    # no write-open of ground_truth / promoted rules; mentions allowed only in docstring/notes
    assert not re.search(r"ground_truth[^\n]*['\"]\s*,\s*['\"][wa]", t)
    assert "promote_learning(" not in t and ".jsonl\", \"w" not in t.replace("recall_gap_backlog", "")


def test_recoveries_and_backlog_staged_only():
    st = _state()
    for q in st["queue"]:
        for i in q.get("recovered", []):
            safe = str(i).replace("/", "_")
            assert (ROOT / "pocs/p301" / f"{q['audit_id'].split('-')[0]}__{safe}").exists()
    assert str(BACKLOG).startswith(str(ROOT / "data/learning/_proposed"))


# ---- integrity ----
def test_verifier_and_forbidden_byte_identical():
    assert hashlib.sha256((ROOT / "scripts/research/executed_poc_verifier.py").read_bytes()).hexdigest()[:16] == VERIFIER_HASH
    for rel, h in FORBIDDEN.items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:8].startswith(h), f"forbidden changed: {rel}"


def test_unwired_from_confirm_gates():
    for rel in ("scripts/confirm_gate.py", "scripts/min_confirm_gate.py"):
        assert "blind_eval_loop" not in (ROOT / rel).read_text()


def test_docs_and_verdict():
    for d in DOC_FILES:
        assert (D / d).exists(), f"missing {d}"
    assert any(v in (D / "VERDICT.md").read_text() for v in VERDICTS)


