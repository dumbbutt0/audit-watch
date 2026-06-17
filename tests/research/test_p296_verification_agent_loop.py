"""P296 — verification-agent loop. Spec→PoC→verifier-judged; verifier is the SOLE confirmer (FP=0 tied to it).

Runs `forge` (confirmation is by real execution). Builder self-reports are untrusted.
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

D = ROOT / "documentation/research/assisted_mode/p296_verification_agent_loop"
O = D / "outputs"
FORGE = shutil.which("forge")
needs_forge = pytest.mark.skipif(FORGE is None, reason="forge not installed")
LIB = ROOT / "pocs/p286/lib"

BYTE_IDENTICAL = {"scripts/research/executed_poc_verifier.py": "1a005811fbb9e0d0"}
FORBIDDEN = {
    "scripts/dashboard_sync.py": "c1af70e1", "prompts/deep_trace.md": "c095c426",
    "scripts/min_confirm_gate.py": "2a15169a", "scripts/confirm_gate.py": "afc481c9",
    "scripts/validate_p208_l3_readiness.py": "ae55eb80",
}
DOC_FILES = ("SETUP.md", "DESIGN.md", "IMPLEMENTATION_NOTES.md", "LOOP_RESULTS.md", "EVIDENCE_AUDIT.md",
             "LIMITATIONS.md", "VERDICT.md", "ROLLBACK_PLAN.md")
VERDICTS = ("A — ", "B — ", "C — ", "D — ")


def _loop():
    return json.loads((O / "loop_results.json").read_text())


def _mk_project(tmp: Path, test_src: str, manifest: dict) -> Path:
    (tmp / "test").mkdir(parents=True)
    (tmp / "lib").symlink_to(LIB)
    (tmp / "foundry.toml").write_text("[profile.default]\nsrc='src'\nout='out'\ntest='test'\nlibs=['lib']\nsolc_version='0.8.21'\n")
    (tmp / "remappings.txt").write_text("forge-std/=lib/forge-std/src/\n")
    (tmp / "test" / "T.t.sol").write_text(test_src)
    (tmp / "poc_manifest.json").write_text(json.dumps(manifest))
    return tmp


# ---- the loop emitted specs + ran end-to-end ----
def test_loop_passed_with_new_confirmation():
    r = _loop()
    assert r["attempted"] >= 3
    assert r["new_confirmations"] >= 1
    assert r["pass"] is True


# ---- FP=0 tied to the VERIFIER (not builder claims) ----
def test_confirmed_fp_zero_and_refutation_control_not_confirmed():
    r = _loop()
    assert r["confirmed_false_positive_count"] == 0
    assert r["refutation_control"]["attacker_verified"] is False


@needs_forge
def test_every_clean_confirmation_has_real_log_and_assertion_map():
    r = _loop()
    clean = [x for x in r["results"] if x.get("clean_confirmation")]
    assert len(clean) >= 1
    for x in clean:
        assert x["has_assertion_map"] is True
        assert any(run.get("passed") and run.get("log_ref") for run in x.get("runs", []))
        man = json.loads((ROOT / x["poc_dir"] / "poc_manifest.json").read_text())
        assert man.get("assertion_map") and man["assertion_map"][0].get("proves")


# ---- verifier-authoritative: a builder claiming 'confirmed' on a FAILING exploit is NOT confirmed ----
@needs_forge
def test_builder_claim_ignored_when_exploit_fails(tmp_path):
    src = ("// SPDX-License-Identifier: MIT\npragma solidity ^0.8.21;\nimport 'forge-std/Test.sol';\n"
           "contract T is Test { function test_exploit_PASS_SUPPORTED() public { address a=makeAddr('a');"
           " vm.prank(a); uint x=vm.load(address(this),0)==0?1:0; assertEq(x,999,'FAILS'); } }")
    proj = _mk_project(tmp_path, src, {"finding_id": "fake", "exploit_tests": ["test_exploit_PASS_SUPPORTED"],
                                       "assertion_map": [{"test": "test_exploit_PASS_SUPPORTED", "asserts": "x==999",
                                                          "proves": "claims the bug"}]})
    (proj / "agent_report.json").write_text(json.dumps({"agent_claimed": "confirmed"}))
    rec = epv.verify_poc(proj, finding_id="fake")
    assert rec["attacker_verified"] is False  # verifier overrides the builder's 'confirmed' claim


# ---- assertion_map requirement: a verifier-PASS without a map is NOT a clean confirmation ----
@needs_forge
def test_pass_without_assertion_map_is_unmapped(tmp_path):
    src = ("// SPDX-License-Identifier: MIT\npragma solidity ^0.8.21;\nimport 'forge-std/Test.sol';\n"
           "contract T is Test { function test_exploit_PASS_SUPPORTED() public { address a=makeAddr('a');"
           " vm.prank(a); uint before_=vm.load(address(this),bytes32(0))==0?1:0; uint after_=2;"
           " assertEq(before_,1); assertEq(after_,2,'flip'); } }")
    proj = _mk_project(tmp_path, src, {"finding_id": "nomap", "exploit_tests": ["test_exploit_PASS_SUPPORTED"]})
    rec = epv.verify_poc(proj, finding_id="nomap")
    man = json.loads((proj / "poc_manifest.json").read_text())
    has_map = bool(man.get("assertion_map"))
    # the loop's clean-confirmation rule: clean = verified AND has_map; here verified may be True but has_map is False
    assert has_map is False
    assert (rec["attacker_verified"] and not has_map) is True  # -> confirmed_but_unmapped, NOT a clean confirmation


# ---- recall climbed (cumulative) ----
def test_recall_funnel_climbed():
    f = json.loads((O / "recall_funnel.json").read_text())
    assert f["total_loci_confirmed_by_execution"] == f["p295_baseline_confirmed_loci"] + f["p296_new_confirmations"]
    assert f["total_loci_confirmed_by_execution"] > f["p295_baseline_confirmed_loci"]
    assert f["confirmed_false_positive_count"] == 0


# ---- safety / authority ----
def test_subagent_outputs_confined_to_pocs_p296():
    for x in _loop()["results"]:
        if x["poc_present"]:
            assert x["poc_dir"].startswith("pocs/p296/")


def test_loop_never_writes_answer_keys():
    t = (ROOT / "scripts/research/verification_agent_loop.py").read_text()
    assert "ground_truth" not in t and "reveal_score" not in t.split("recall_funnel")[0]  # reads p295 funnel only


def test_unwired_from_confirm_gates():
    for rel in ("scripts/confirm_gate.py", "scripts/min_confirm_gate.py"):
        txt = (ROOT / rel).read_text()
        assert "verification_agent_loop" not in txt and "executed_poc_verifier" not in txt


def test_no_leakage_advisory_stamps():
    for name in ("loop_results.json", "recall_funnel.json", "guard_report.json", "build_specs.json"):
        r = json.loads((O / name).read_text())
        for fld in ("reportable", "submission_ready", "concluded", "production_routing", "auto_submitted", "emits_findings"):
            if fld in r:
                assert r[fld] is False
        if "severity" in r:
            assert r["severity"] is None


def test_verifier_and_forbidden_byte_identical():
    for rel, h in BYTE_IDENTICAL.items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:16] == h, f"changed: {rel}"
    for rel, h in FORBIDDEN.items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:8].startswith(h), f"forbidden changed: {rel}"


def test_docs_and_verdict():
    for d in DOC_FILES:
        assert (D / d).exists(), f"missing {d}"
    assert any(v in (D / "VERDICT.md").read_text() for v in VERDICTS)


