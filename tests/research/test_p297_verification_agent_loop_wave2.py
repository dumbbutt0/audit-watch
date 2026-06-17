"""P297 — verification-agent loop wave 2 (remaining 6 backlog loci). Cumulative funnel; verifier is the judge."""
import hashlib
import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/research"))
import executed_poc_verifier as epv  # noqa: E402

D = ROOT / "documentation/research/assisted_mode/p297_verification_agent_loop_wave2"
O = D / "outputs"
P296 = ROOT / "documentation/research/assisted_mode/p296_verification_agent_loop/outputs"
FORGE = shutil.which("forge")
needs_forge = pytest.mark.skipif(FORGE is None, reason="forge not installed")

BYTE_IDENTICAL = {"scripts/research/executed_poc_verifier.py": "1a005811fbb9e0d0"}
FORBIDDEN = {
    "scripts/dashboard_sync.py": "c1af70e1", "prompts/deep_trace.md": "c095c426",
    "scripts/min_confirm_gate.py": "2a15169a", "scripts/confirm_gate.py": "afc481c9",
    "scripts/validate_p208_l3_readiness.py": "ae55eb80",
}
DOC_FILES = ("SETUP.md", "WAVE2_RESULTS.md", "EVIDENCE_AUDIT.md", "LIMITATIONS.md", "VERDICT.md", "ROLLBACK_PLAN.md")
VERDICTS = ("A — ", "B — ", "C — ", "D — ")
WAVE2_IDS = {"kelp-2023-11-holdout:M-01", "kelp-2023-11-holdout:M-02", "ecg-2023-12-holdout:H-01",
             "ecg-2023-12-holdout:M-02", "ecg-2023-12-holdout:M-03", "salty-2024-01-holdout:H-05"}


def _loop():
    return json.loads((O / "loop_results.json").read_text())


# ---- all 9 attempted + judged; the 6 wave-2 loci built ----
def test_all_nine_attempted_and_judged():
    r = _loop()
    assert r["attempted"] == 9
    built = {f"{x['audit']}:{x['awarded_id']}" for x in r["results"] if x["poc_present"]}
    assert WAVE2_IDS.issubset(built)  # the 6 wave-2 loci now have PoCs


def test_pass_and_new_confirmations():
    r = _loop()
    assert r["pass"] is True
    assert r["new_confirmations"] >= 1  # >=1 new confirmation this phase (cumulatively 9 across waves)


# ---- cumulative recall-of-confirmed climbed beyond P296 ----
def test_cumulative_recall_climbed():
    f = json.loads((O / "recall_funnel.json").read_text())
    p296 = json.loads((P296 / "recall_funnel.json").read_text())
    assert f["total_loci_confirmed_by_execution"] == f["p295_baseline_confirmed_loci"] + f["new_confirmations_this_run"]
    assert f["total_loci_confirmed_by_execution"] > p296["total_loci_confirmed_by_execution"]  # 15 > 9
    assert f["confirmed_false_positive_count"] == 0


# ---- FP=0 tied to the verifier; refutation control not confirmed ----
def test_confirmed_fp_zero_and_control_not_confirmed():
    r = _loop()
    assert r["confirmed_false_positive_count"] == 0
    assert r["refutation_control"]["attacker_verified"] is False


@needs_forge
def test_every_clean_confirmation_has_real_log_and_map():
    r = _loop()
    clean = [x for x in r["results"] if x.get("clean_confirmation")]
    assert len(clean) >= 7
    for x in clean:
        assert x["has_assertion_map"] is True
        assert any(run.get("passed") and run.get("log_ref") for run in x.get("runs", []))


# ---- verifier-authoritative guard (builder claim ignored when exploit fails) ----
@needs_forge
def test_builder_claim_ignored_when_exploit_fails(tmp_path):
    (tmp_path / "test").mkdir(parents=True)
    (tmp_path / "lib").symlink_to(ROOT / "pocs/p286/lib")
    (tmp_path / "foundry.toml").write_text("[profile.default]\nsrc='src'\nout='out'\ntest='test'\nlibs=['lib']\nsolc_version='0.8.21'\n")
    (tmp_path / "remappings.txt").write_text("forge-std/=lib/forge-std/src/\n")
    (tmp_path / "test" / "T.t.sol").write_text(
        "// SPDX-License-Identifier: MIT\npragma solidity ^0.8.21;\nimport 'forge-std/Test.sol';\n"
        "contract T is Test { function test_exploit_PASS_SUPPORTED() public { address a=makeAddr('a');"
        " vm.prank(a); assertEq(1,2,'FAILS'); } }")
    (tmp_path / "poc_manifest.json").write_text(json.dumps(
        {"exploit_tests": ["test_exploit_PASS_SUPPORTED"], "assertion_map": [{"test": "x", "proves": "y"}]}))
    (tmp_path / "agent_report.json").write_text(json.dumps({"agent_claimed": "confirmed"}))
    assert epv.verify_poc(tmp_path, finding_id="fake")["attacker_verified"] is False


# ---- safety / authority ----
def test_subagent_outputs_confined_to_pocs_p296():
    for x in _loop()["results"]:
        if x["poc_present"]:
            assert x["poc_dir"].startswith("pocs/p296/")


def test_unwired_from_confirm_gates():
    for rel in ("scripts/confirm_gate.py", "scripts/min_confirm_gate.py"):
        txt = (ROOT / rel).read_text()
        assert "verification_agent_loop" not in txt and "executed_poc_verifier" not in txt


def test_no_leakage_advisory_stamps():
    for name in ("loop_results.json", "recall_funnel.json", "guard_report.json"):
        r = json.loads((O / name).read_text())
        for fld in ("reportable", "submission_ready", "concluded", "production_routing", "auto_submitted", "emits_findings"):
            if fld in r:
                assert r[fld] is False
        if "severity" in r:
            assert r["severity"] is None


def test_p296_snapshot_preserved():
    # wave 2 wrote to the P297 dir; P296's wave-1 snapshot is intact (3 new confirmations there)
    assert json.loads((P296 / "loop_results.json").read_text())["new_confirmations"] == 3


def test_verifier_and_forbidden_byte_identical():
    for rel, h in BYTE_IDENTICAL.items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:16] == h, f"changed: {rel}"
    for rel, h in FORBIDDEN.items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:8].startswith(h), f"forbidden changed: {rel}"


def test_docs_and_verdict():
    for d in DOC_FILES:
        assert (D / d).exists(), f"missing {d}"
    assert any(v in (D / "VERDICT.md").read_text() for v in VERDICTS)


