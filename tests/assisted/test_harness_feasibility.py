"""P110: harness feasibility — RESEARCH-ONLY, un-wired.

Proves classification (SIMPLE/MODERATE/COMPLEX/BLOCKED) from source, dependency/actor extraction (incl. the
contract-under-test in the deploy plan and interface->concrete resolution), that a missing INTERFACE does not BLOCK
(only a missing deployable does), determinism, and that no candidate-status/severity is produced.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "assisted"))
import harness_feasibility as F  # noqa: E402

P109 = ROOT / "documentation" / "research" / "assisted_mode" / "p109" / "runtime_self_kill_results.json"


def _fixture(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "A.sol").write_text("pragma solidity ^0.8.0;\ncontract A { function f() external pure returns(uint){return 1;} }\n")
    (src / "Dep.sol").write_text("pragma solidity ^0.8.0;\ncontract Dep { uint x; }\n")
    (src / "Token.sol").write_text("pragma solidity ^0.8.0;\ncontract Token { }\n")
    (src / "M.sol").write_text("pragma solidity ^0.8.0;\nimport './Dep.sol';\n"
                               "contract M { address owner; function initialize() public {} "
                               "function g() external { require(msg.sender==owner); } }\n")
    (src / "C.sol").write_text("pragma solidity ^0.8.0;\nimport 'dev-fraxswap/x.sol';\n"
                               "contract C { address constant FAC = 0xE30521fe7f3bEB6Ad556887b50739d6C7CA667E6; "
                               "function h() external {} }\n")
    (src / "B.sol").write_text("pragma solidity ^0.8.0;\nimport './GoneContract.sol';\ncontract B { function k() external {} }\n")
    # interface import whose concrete sibling EXISTS -> resolvable, NOT a blocker
    (src / "IToken.sol").write_text("pragma solidity ^0.8.0;\ninterface IToken { }\n")
    (src / "V.sol").write_text("pragma solidity ^0.8.0;\nimport './IToken.sol';\n"
                               "contract V { function w() external {} }\n")
    # interface import whose file is MISSING but it's an interface -> NOT a blocker
    (src / "W.sol").write_text("pragma solidity ^0.8.0;\nimport './IGhost.sol';\ncontract W { function q() external {} }\n")
    return [str(src)]


def test_flags_unwired():
    assert F.FLAGS["is_gate"] is False
    assert F.FLAGS["routes_in_production"] is False
    assert F.FLAGS["routed_manifest_ids"] == []


def test_self_test_passes():
    assert F._self_test() == 0


def test_four_classes():
    assert F.CLASSES == {"HARNESS_SIMPLE", "HARNESS_MODERATE", "HARNESS_COMPLEX", "HARNESS_BLOCKED"}


def test_simple(tmp_path):
    assert F.assess("x", "A", "f", _fixture(tmp_path))["classification"] == "HARNESS_SIMPLE"


def test_moderate_local_multi_with_init(tmp_path):
    a = F.assess("x", "M", "g", _fixture(tmp_path))
    assert a["classification"] == "HARNESS_MODERATE"
    assert "M" in a["environment"]["deployment_sequence"], "contract-under-test is in the deploy plan"
    assert "Dep" in a["environment"]["deployment_sequence"]


def test_complex_fork(tmp_path):
    a = F.assess("x", "C", "h", _fixture(tmp_path))
    assert a["classification"] == "HARNESS_COMPLEX"
    assert a["environment"]["fork_required"] is True


def test_blocked_missing_deployable(tmp_path):
    a = F.assess("x", "B", "k", _fixture(tmp_path))
    assert a["classification"] == "HARNESS_BLOCKED"
    assert a["blockers"]


def test_missing_interface_does_not_block(tmp_path):
    a = F.assess("x", "W", "q", _fixture(tmp_path))
    assert a["classification"] != "HARNESS_BLOCKED", "a missing INTERFACE import must not BLOCK the harness"


def test_interface_resolves_to_concrete_sibling(tmp_path):
    a = F.assess("x", "V", "w", _fixture(tmp_path))
    # IToken -> Token concrete sibling exists -> should appear as a resolved deployable
    assert "Token" in a["dependency_map"]["resolved_concrete_from_interfaces"]


def test_admin_actor_inferred(tmp_path):
    a = F.assess("x", "M", "g", _fixture(tmp_path))
    assert any(act["role"] == "admin" for act in a["actor_model"])


def test_no_severity_or_status_fields(tmp_path):
    a = F.assess("x", "M", "g", _fixture(tmp_path))
    a.pop("source_file", None)  # the pytest tmp path can contain the test's own name; check content not paths
    blob = json.dumps(a).lower()
    assert "severity" not in blob and "submission" not in blob and "report_ready" not in blob
    assert "classification" in a and a["classification"] in F.CLASSES


def test_deterministic(tmp_path):
    roots = _fixture(tmp_path)
    assert json.dumps(F.assess("x", "M", "g", roots), sort_keys=True) == \
        json.dumps(F.assess("x", "M", "g", roots), sort_keys=True)


@pytest.mark.skipif(not P109.exists(), reason="P109 results not present")
def test_loads_28_p109_candidates():
    cands = F._load_p109_unavailable()
    assert len(cands) == 28
