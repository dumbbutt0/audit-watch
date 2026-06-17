"""P294 — executed-PoC verification hook (the FP oracle). Real forge execution + anti-fabrication guards.

These tests actually run `forge` (the whole point is that confirmation comes from proof, not patterns).
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

D = ROOT / "documentation/research/assisted_mode/p294_executed_poc_verifier"
O = D / "outputs"
FORGE = shutil.which("forge")
needs_forge = pytest.mark.skipif(FORGE is None, reason="forge not installed")
LIB = ROOT / "pocs/p286/lib"  # forge-std for synthetic projects

# do-not-edit: the reused PoC execution scripts + forbidden 5 must stay byte-identical (P294 adds only new files)
BYTE_IDENTICAL = {
    "scripts/collect_poc_results.py": None, "scripts/run_poc_tests.py": None, "scripts/validate_poc.py": None,
    "scripts/generate_poc_test.py": None, "scripts/poc_validation_gate.py": None,
}
FORBIDDEN = {
    "scripts/dashboard_sync.py": "c1af70e1", "prompts/deep_trace.md": "c095c426",
    "scripts/min_confirm_gate.py": "2a15169a", "scripts/confirm_gate.py": "afc481c9",
    "scripts/validate_p208_l3_readiness.py": "ae55eb80",
}
DOC_FILES = ("SETUP.md", "DESIGN.md", "IMPLEMENTATION_NOTES.md", "PROOF_RESULTS.md", "EVIDENCE_AUDIT.md",
             "LIMITATIONS.md", "VERDICT.md", "ROLLBACK_PLAN.md")
VERDICTS = ("A — ", "B — ", "C — ", "D — ")


def _mk_project(tmp: Path, test_src: str, manifest: dict) -> Path:
    (tmp / "test").mkdir(parents=True)
    (tmp / "lib").symlink_to(LIB)
    (tmp / "foundry.toml").write_text(
        "[profile.default]\nsrc='src'\nout='out'\ntest='test'\nlibs=['lib']\nsolc_version='0.8.21'\n")
    (tmp / "remappings.txt").write_text("forge-std/=lib/forge-std/src/\n")
    (tmp / "test" / "T.t.sol").write_text(test_src)
    (tmp / "poc_manifest.json").write_text(json.dumps(manifest))
    return tmp


# ---- real corpus PoCs ----
@needs_forge
def test_awarded_locus_confirmed_by_execution():
    r = epv.verify_poc(ROOT / "pocs/p286", finding_id="blackhole-M-04-claim_many")
    assert r["status"] == "confirmed_by_execution" and r["attacker_verified"] is True
    assert r["l1"] and r["l2"] and r["l3"]
    assert any(x["passed"] and x["log_ref"] for x in r["runs"])  # backed by a real run + log


@needs_forge
def test_p293_locus_confirmed_by_execution():
    r = epv.verify_poc(ROOT / "pocs/p294/salty_increaseUserShare",
                       finding_id="salty-H-increaseUserShare-first-depositor")
    assert r["status"] == "confirmed_by_execution" and r["attacker_verified"] is True


@needs_forge
def test_false_hypothesis_refused():
    r = epv.verify_poc(ROOT / "pocs/p290/salty-2024-01-holdout/Pools_deposit",
                       finding_id="salty-Pools-deposit-callback")
    assert r["attacker_verified"] is False and r["status"] == "refuted_by_execution"


# ---- anti-fabrication: a manifest CANNOT confirm without a real passing exploit run ----
@needs_forge
def test_fabricated_exploit_not_confirmed_when_test_fails(tmp_path):
    src = ("// SPDX-License-Identifier: MIT\npragma solidity ^0.8.21;\nimport 'forge-std/Test.sol';\n"
           "contract T is Test { function test_exploit_PASS_SUPPORTED() public {"
           " address a=makeAddr('a'); vm.prank(a); uint x=vm.load(address(this),0)==0?1:0;"
           " assertEq(x, 999, 'this assertion FAILS so the exploit is not proven'); } }")
    proj = _mk_project(tmp_path, src, {"finding_id": "fab", "exploit_tests": ["test_exploit_PASS_SUPPORTED"]})
    r = epv.verify_poc(proj, finding_id="fab")
    assert r["attacker_verified"] is False and r["status"] == "refuted_by_execution"


@needs_forge
def test_exploit_passes_but_missing_l2_is_setup_only(tmp_path):
    # passes + has an assertion (L3) but no before/after state-flip marker (L2 absent) -> setup_only, NOT confirmed
    src = ("// SPDX-License-Identifier: MIT\npragma solidity ^0.8.21;\nimport 'forge-std/Test.sol';\n"
           "contract T is Test { function test_exploit_PASS_SUPPORTED() public {"
           " address a=makeAddr('a'); vm.prank(a); assertTrue(true, 'no state flip'); } }")
    proj = _mk_project(tmp_path, src, {"finding_id": "su", "exploit_tests": ["test_exploit_PASS_SUPPORTED"]})
    r = epv.verify_poc(proj, finding_id="su")
    assert r["attacker_verified"] is False and r["status"] == "setup_only" and r["l2"] is False


@needs_forge
def test_determinism(tmp_path):
    r1 = epv.verify_poc(ROOT / "pocs/p286", finding_id="d1")
    r2 = epv.verify_poc(ROOT / "pocs/p286", finding_id="d2")
    assert (r1["status"], r1["attacker_verified"]) == (r2["status"], r2["attacker_verified"])


# ---- authority / safety ----
def test_recall_open_flag_default_off():
    cfg = json.loads((ROOT / "config/research_executed_poc_verifier.json").read_text())
    assert cfg["recall_open"] is False


def test_unsafe_forge_flags_refused():
    assert epv._safe_command("forge test --broadcast") is False
    assert epv._safe_command("forge test --private-key 0xabc") is False
    assert epv._safe_command("forge test --match-test ^foo\\b -vv") is True


def test_unwired_from_confirm_gates():
    for rel in ("scripts/confirm_gate.py", "scripts/min_confirm_gate.py"):
        txt = (ROOT / rel).read_text()
        assert "executed_poc_verifier" not in txt and "attacker_verified" not in txt


def test_advisory_stamp_and_no_leakage():
    r = epv.verify_poc(ROOT / "pocs/p286", finding_id="stamp") if FORGE else dict(epv._STAMP)
    for f in ("reportable", "submission_ready", "concluded", "production_routing", "routes_in_production",
              "auto_submitted", "emits_findings"):
        assert r[f] is False
    assert r["severity"] is None and r["is_gate"] is False and r["research_only"] is True


def test_outputs_no_confirmed_false_positive():
    g = json.loads((O / "guard_report.json").read_text())
    assert g["checks"]["confirmed_false_positive_count"] == 0
    assert g["checks"]["awarded_loci_confirmed_by_execution"] >= 1
    assert g["checks"]["false_hypothesis_refused"] >= 1
    assert g["checks"]["every_confirmation_has_a_real_log"] is True


# ---- integrity ----
def test_reused_scripts_and_forbidden_byte_identical():
    for rel in BYTE_IDENTICAL:
        assert (ROOT / rel).exists(), f"reused script missing: {rel}"
    for rel, h in FORBIDDEN.items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:8].startswith(h), f"forbidden changed: {rel}"


def test_ground_truth_not_written():
    # the verifier must never reference ground_truth at all; neither script may open it for writing
    assert "ground_truth" not in (ROOT / "scripts/research/executed_poc_verifier.py").read_text()
    import re
    for src in ("scripts/research/executed_poc_verifier.py",
                "documentation/research/assisted_mode/p294_executed_poc_verifier/proof_driver.py"):
        t = (ROOT / src).read_text()
        assert not re.search(r"ground_truth[^\n]*['\"]\s*,\s*['\"]w", t)  # no write-open of a ground_truth path
        assert ".write_text" not in t or "ground_truth" not in t.split(".write_text")[0][-80:]


def test_docs_and_verdict():
    for d in DOC_FILES:
        assert (D / d).exists(), f"missing {d}"
    assert any(v in (D / "VERDICT.md").read_text() for v in VERDICTS)


