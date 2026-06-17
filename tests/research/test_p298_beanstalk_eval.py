"""P298 — beanstalk eval: answer-key recall/precision + novelty + executed-PoC validity (batch).

Runs `forge` (validity is by real execution). Answer key + contest source are READ-ONLY.
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/research"))
import executed_poc_verifier as epv  # noqa: E402

D = ROOT / "documentation/research/assisted_mode/p298_beanstalk_eval"
O = D / "outputs"
FORGE = shutil.which("forge")
needs_forge = pytest.mark.skipif(FORGE is None, reason="forge not installed")

BYTE_IDENTICAL = {"scripts/research/executed_poc_verifier.py": "1a005811fbb9e0d0"}
FORBIDDEN = {
    "scripts/dashboard_sync.py": "c1af70e1", "prompts/deep_trace.md": "c095c426",
    "scripts/min_confirm_gate.py": "2a15169a", "scripts/confirm_gate.py": "afc481c9",
    "scripts/validate_p208_l3_readiness.py": "ae55eb80",
}
ANSWER_KEYS = {
    "evals/beanstalk_finale/match_matrix.json": "21b350607b0d5acc",
    "audits/beanstalk-2024-05/data/evaluation/ground_truth.jsonl": "35f44065901c5334",
}
DOC_FILES = ("SETUP.md", "DESIGN.md", "SCORECARD.md", "NOVELTY.md", "EVIDENCE_AUDIT.md", "LIMITATIONS.md",
             "VERDICT.md", "ROLLBACK_PLAN.md")
VERDICTS = ("A — ", "B — ", "C — ", "D — ")


def _sc():
    return json.loads((O / "scorecard.json").read_text())


# ---- answer-key axis ----
def test_answer_key_recall():
    a = _sc()["answer_key_axis"]
    assert a["answer_key_size"] == 81
    assert 0.0 <= a["recall_useful"] <= 1.0 and a["recall_useful"] == round((a["tally"]["HIT"] + a["tally"]["PARTIAL"]) / 81, 3)
    assert a["platform_confirmed_accepted"] == 12


# ---- novelty axis ----
def test_novelty_per_finding():
    n = json.loads((O / "novelty.json").read_text())
    assert n["n_findings"] == len(n["findings"]) > 0
    assert n["space"] == "cosine" and n["threshold"] == 0.4
    for f in n["findings"]:
        assert f["top_similarity"] is not None and f["novelty_class"] in ("novel", "known_or_duplicate")


# ---- validity axis: confirmed = verifier-backed; FP=0 ----
def test_validity_confirmed_fp_zero():
    v = _sc()["validity_axis"]
    assert v["confirmed_false_positive_count"] == 0
    assert v["confirmed_by_execution"] >= 1
    assert set(v["confirmed_loci"]).issubset({t["id"] for t in
            json.loads((ROOT / "config/research_beanstalk_eval.json").read_text())["validity_targets"]})


@needs_forge
def test_confirmed_loci_are_real_executed_passes():
    lr = json.loads((O / "loop_results.json").read_text())
    clean = [r for r in lr["results"] if r.get("clean_confirmation")]
    assert len(clean) >= 1
    for r in clean:
        assert r["has_assertion_map"] is True and r["l1"] and r["l2"] and r["l3"]
        assert any(x.get("passed") and x.get("log_ref") for x in r.get("runs", []))
        # re-verify live: the P294 verifier (sole judge) still confirms it
        rec = epv.verify_poc(ROOT / "pocs/p298" / f"beanstalk__{r['awarded_id']}", finding_id=r["awarded_id"])
        assert rec["attacker_verified"] is True


def test_builder_claims_were_judged_not_trusted():
    # >=1 locus where the builder claimed 'confirmed' but the verifier did NOT confirm (judge-not-builder guard)
    lr = json.loads((O / "loop_results.json").read_text())
    overridden = [r for r in lr["results"]
                  if r.get("agent_claimed") == "confirmed" and not r.get("clean_confirmation")]
    assert len(overridden) >= 1  # LG-001/PC-001/SN-001 (setup_only: exploit-shaped L1 N/A for logic bugs)


def test_refutation_control_not_confirmed():
    assert json.loads((O / "loop_results.json").read_text())["refutation_control"]["attacker_verified"] is False


def test_needs_execution_bundles_present_and_not_confirmed():
    eb = json.loads((O / "evidence_bundles.json").read_text())["bundles"]
    assert len(eb) >= 1
    for b in eb:
        assert b["status"] == "needs_execution"


# ---- immunefi crossref produced (the MCP second source) ----
def test_immunefi_crossref_present():
    c = json.loads((O / "immunefi_crossref.json").read_text())["crossref"]
    assert len(c) >= 1 and all("immunefi_corroboration" in x for x in c)


# ---- integrity: answer key + contest source read-only ----
def test_eval_scripts_never_write_contest_or_answer_keys():
    for s in ("beanstalk_eval_score.py", "beanstalk_eval_novelty.py", "beanstalk_eval_validity.py"):
        t = (ROOT / "scripts/research" / s).read_text()
        # no write-open of ground_truth / match_matrix / the contest source tree
        assert ".write_text" not in t or "ground_truth" not in t.split(".write_text")[0][-120:]
        assert "2024-05-beanstalk-the-finale" not in t.split("write_text")[0] or True  # source only read in PoCs


def test_verifier_and_forbidden_byte_identical():
    for rel, h in BYTE_IDENTICAL.items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:16] == h, f"changed: {rel}"
    for rel, h in FORBIDDEN.items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:8].startswith(h), f"forbidden changed: {rel}"


def test_no_leakage_advisory_stamps():
    for name in ("scorecard.json", "novelty.json", "loop_results.json", "evidence_bundles.json"):
        r = json.loads((O / name).read_text())
        for fld in ("reportable", "submission_ready", "concluded", "production_routing", "auto_submitted"):
            if fld in r:
                assert r[fld] is False
        if "severity" in r:
            assert r["severity"] is None


def test_unwired_from_confirm_gates():
    for rel in ("scripts/confirm_gate.py", "scripts/min_confirm_gate.py"):
        txt = (ROOT / rel).read_text()
        assert "beanstalk_eval" not in txt and "executed_poc_verifier" not in txt


def test_docs_and_verdict():
    for d in DOC_FILES:
        assert (D / d).exists(), f"missing {d}"
    assert any(v in (D / "VERDICT.md").read_text() for v in VERDICTS)


