"""P299 — logic-bug validity mode (corrected-reference differential; no attacker L1).

Runs `forge`. Confirms logic/correctness bugs via a passing bug-vs-control differential WITHOUT an attacker entry;
the exploit track stays byte-for-behavior identical; confirmed-FP = 0.
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

D = ROOT / "documentation/research/assisted_mode/p299_logic_bug_validity_mode"
O = D / "outputs"
FORGE = shutil.which("forge")
needs_forge = pytest.mark.skipif(FORGE is None, reason="forge not installed")
LIB = ROOT / "pocs/p286/lib"
VERIFIER_HASH = "1a005811fbb9e0d0"
FORBIDDEN = {
    "scripts/dashboard_sync.py": "c1af70e1", "prompts/deep_trace.md": "c095c426",
    "scripts/min_confirm_gate.py": "2a15169a", "scripts/confirm_gate.py": "afc481c9",
    "scripts/validate_p208_l3_readiness.py": "ae55eb80",
}
DOC_FILES = ("DESIGN.md", "RESULTS.md", "EVIDENCE_AUDIT.md", "LIMITATIONS.md", "VERDICT.md", "ROLLBACK_PLAN.md")
VERDICTS = ("A — ", "B — ", "C — ", "D — ")


def _mk(tmp: Path, body: str, manifest: dict) -> Path:
    (tmp / "test").mkdir(parents=True)
    (tmp / "lib").symlink_to(LIB)
    (tmp / "foundry.toml").write_text("[profile.default]\nsrc='src'\nout='out'\ntest='test'\nlibs=['lib']\nsolc_version='0.8.21'\n")
    (tmp / "remappings.txt").write_text("forge-std/=lib/forge-std/src/\n")
    (tmp / "test" / "T.t.sol").write_text(body)
    (tmp / "poc_manifest.json").write_text(json.dumps(manifest))
    return tmp


# ---- logic mode confirms the 3 beanstalk logic loci via the differential ----
@needs_forge
@pytest.mark.parametrize("fid", ["LG-001", "PC-001", "SN-001"])
def test_logic_loci_confirmed_by_differential(fid):
    r = epv.verify_poc(ROOT / "pocs/p299" / f"beanstalk__{fid}", finding_id=f"beanstalk-{fid}")
    assert r["status"] == "confirmed_by_logic_differential"
    assert r["validity_confirmed"] is True and r["logic_verified"] is True
    assert r["attacker_verified"] is False  # logic bug: no attacker entry asserted
    assert r["validity_mode"] == "logic_differential"


# ---- FP guards: differential is REQUIRED ----
@needs_forge
def test_logic_mode_needs_a_passing_control(tmp_path):
    body = ("// SPDX-License-Identifier: MIT\npragma solidity ^0.8.21;\nimport 'forge-std/Test.sol';\n"
            "contract T is Test {\n"
            " function test_bug_PASS_SUPPORTED() public { uint reported=1; assertEq(reported, uint(1), 'bug value'); }\n"
            " function test_control_corrected() public { assertTrue(false, 'control FAILS'); } }")
    proj = _mk(tmp_path, body, {"finding_id": "nc", "validity_mode": "logic_differential",
                                "exploit_tests": ["test_bug_PASS_SUPPORTED"],
                                "control_tests": ["test_control_corrected"],
                                "assertion_map": [{"test": "test_bug_PASS_SUPPORTED", "asserts": "reported==1", "proves": "x"}]})
    r = epv.verify_poc(proj, finding_id="nc")
    assert r["validity_confirmed"] is False and r["status"] == "setup_only"


@needs_forge
def test_logic_mode_cannot_rescue_a_failing_bug_test(tmp_path):
    body = ("// SPDX-License-Identifier: MIT\npragma solidity ^0.8.21;\nimport 'forge-std/Test.sol';\n"
            "contract T is Test {\n"
            " function test_bug_PASS_SUPPORTED() public { assertTrue(false, 'bug test FAILS'); }\n"
            " function test_control_corrected() public { assertTrue(true); } }")
    proj = _mk(tmp_path, body, {"finding_id": "fb", "validity_mode": "logic_differential",
                                "exploit_tests": ["test_bug_PASS_SUPPORTED"],
                                "control_tests": ["test_control_corrected"],
                                "assertion_map": [{"test": "test_bug_PASS_SUPPORTED", "asserts": "x", "proves": "y"}]})
    r = epv.verify_poc(proj, finding_id="fb")
    assert r["validity_confirmed"] is False and r["status"] == "refuted_by_execution"


@needs_forge
def test_logic_mode_needs_assertion_map(tmp_path):
    body = ("// SPDX-License-Identifier: MIT\npragma solidity ^0.8.21;\nimport 'forge-std/Test.sol';\n"
            "contract T is Test {\n"
            " function test_bug_PASS_SUPPORTED() public { uint reported=1; assertEq(reported, uint(1)); }\n"
            " function test_control_corrected() public { assertTrue(true); } }")
    proj = _mk(tmp_path, body, {"finding_id": "nm", "validity_mode": "logic_differential",
                                "exploit_tests": ["test_bug_PASS_SUPPORTED"], "control_tests": ["test_control_corrected"]})
    r = epv.verify_poc(proj, finding_id="nm")
    assert r["validity_confirmed"] is False and r["status"] == "setup_only"


# ---- exploit track byte-for-behavior unchanged ----
@needs_forge
def test_exploit_track_unchanged_live():
    assert epv.verify_poc(ROOT / "pocs/p286")["attacker_verified"] is True
    assert epv.verify_poc(ROOT / "pocs/p298/beanstalk__AC-001", finding_id="AC-001")["attacker_verified"] is True
    assert epv.verify_poc(ROOT / "pocs/p290/salty-2024-01-holdout/Pools_deposit")["attacker_verified"] is False


def test_exploit_track_unchanged_recorded():
    e = json.loads((O / "exploit_track_unchanged.json").read_text())
    assert e["all_unchanged"] is True and all(r["unchanged"] for r in e["rows"])


# ---- tally + FP ----
def test_results_and_cumulative_recall():
    lr = json.loads((O / "logic_validity_results.json").read_text())
    assert set(lr["logic_confirmed"]) == {"LG-001", "PC-001", "SN-001"}
    assert lr["confirmed_false_positive_count"] == 0
    f = json.loads((O / "recall_funnel.json").read_text())
    assert f["beanstalk_total_confirmed"] == 5 and f["cumulative_recall_of_confirmed"] == 20
    assert f["confirmed_false_positive_count"] == 0


# ---- P298 snapshot preserved (pre-logic-mode) ----
def test_p298_snapshot_preserved():
    p298 = json.loads((ROOT / "documentation/research/assisted_mode/p298_beanstalk_eval/outputs/loop_results.json").read_text())
    assert p298["confirmed_by_execution"] == 2  # P298 stays the pre-logic-mode snapshot (2 exploit confirms)


# ---- integrity ----
def test_verifier_hash_and_forbidden():
    assert hashlib.sha256((ROOT / "scripts/research/executed_poc_verifier.py").read_bytes()).hexdigest()[:16] == VERIFIER_HASH
    for rel, h in FORBIDDEN.items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:8].startswith(h), f"forbidden changed: {rel}"


def test_unwired_from_confirm_gates():
    for rel in ("scripts/confirm_gate.py", "scripts/min_confirm_gate.py"):
        assert "executed_poc_verifier" not in (ROOT / rel).read_text()


def test_docs_and_verdict():
    for d in DOC_FILES:
        assert (D / d).exists(), f"missing {d}"
    assert any(v in (D / "VERDICT.md").read_text() for v in VERDICTS)


