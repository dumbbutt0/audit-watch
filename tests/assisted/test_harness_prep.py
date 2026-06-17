"""P111: per-candidate harness preparation for the assisted runbook — RESEARCH-ONLY, un-wired.

Proves the per-candidate wrapper reuses P110 (classification flows through), emits a 3-file bundle with an INERT
scaffold, carries an advisory effort classification but NO candidate-status / severity / submission field, is
deterministic, and ABORTS if a non-inert scaffold is ever produced.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "assisted"))
import harness_prep as P  # noqa: E402
import generate_harness_scaffold as GEN  # noqa: E402


def _fixture(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "Dep.sol").write_text("pragma solidity ^0.8.0;\ncontract Dep { uint x; }\n")
    (src / "M.sol").write_text("pragma solidity ^0.8.0;\nimport './Dep.sol';\n"
                               "contract M { address owner; function initialize() public {} "
                               "function g() external { require(msg.sender==owner); } }\n")
    (src / "C.sol").write_text("pragma solidity ^0.8.0;\nimport 'dev-fraxswap/x.sol';\n"
                               "contract C { address constant F = 0xE30521fe7f3bEB6Ad556887b50739d6C7CA667E6; "
                               "function h() external {} }\n")
    return [str(src)]


def test_flags_unwired():
    assert P.FLAGS["is_gate"] is False
    assert P.FLAGS["routes_in_production"] is False
    assert P.FLAGS["routed_manifest_ids"] == []


def test_self_test_passes():
    assert P._self_test() == 0


def test_classification_flows_through(tmp_path):
    roots = _fixture(tmp_path)
    assert P.prepare("fx", "M", "g", source_roots=roots)["harness_classification"] == "HARNESS_MODERATE"
    pc = P.prepare("fx", "C", "h", source_roots=roots)
    assert pc["harness_classification"] == "HARNESS_COMPLEX" and pc["environment"]["fork_required"]


def test_scaffold_is_inert(tmp_path):
    prep = P.prepare("fx", "M", "g", source_roots=_fixture(tmp_path))
    assert prep["scaffold_inert"] is True
    assert GEN.assert_scaffold_is_inert(prep["scaffold"])


def test_no_status_or_promotion_fields(tmp_path):
    prep = P.prepare("fx", "M", "g", source_roots=_fixture(tmp_path))
    assert "candidate_status" not in prep and "status" not in prep
    blob = json.dumps({k: v for k, v in prep.items() if k != "boundary"}).lower()
    for tok in ("severity", "submission", "report_ready", "poc_ready", "validated_for_poc"):
        assert tok not in blob, f"{tok} must not appear in harness_prep output"
    # the classification is present but it is an EFFORT signal, not a status
    assert prep["harness_classification"].startswith("HARNESS_")


def test_bundle_writes_three_files_and_inert_scaffold(tmp_path):
    prep = P.prepare("fx", "M", "g", source_roots=_fixture(tmp_path))
    out = P.write_bundle(prep, out_dir=tmp_path / "bundle")
    assert Path(out["feasibility"]).is_file()
    assert Path(out["scaffold"]).is_file()
    assert Path(out["summary"]).is_file()
    assert GEN.assert_scaffold_is_inert(Path(out["scaffold"]).read_text())
    # feasibility json must not embed the raw scaffold (kept as its own file) but must carry classification
    feas = json.loads(Path(out["feasibility"]).read_text())
    assert feas["harness_classification"] == "HARNESS_MODERATE" and "scaffold" not in feas


def test_deterministic(tmp_path):
    roots = _fixture(tmp_path)
    a = P.prepare("fx", "M", "g", source_roots=roots)
    b = P.prepare("fx", "M", "g", source_roots=roots)
    assert a["scaffold"] == b["scaffold"]
    assert a["harness_classification"] == b["harness_classification"]


def test_abort_on_non_inert_scaffold(tmp_path, monkeypatch):
    roots = _fixture(tmp_path)
    monkeypatch.setattr(GEN, "generate_scaffold",
                        lambda a: "// SCAFFOLD ONLY\nfunction t() public { x.call(abi.encode(1)); } // TODO")
    with pytest.raises(RuntimeError):
        P.prepare("fx", "M", "g", source_roots=roots)


def test_from_intake_parses_fields():
    spec = P._from_intake({"subject": "s", "contract": "Cd", "entrypoint": "fn",
                           "source_refs": ["/tmp/x/src/Cd.sol:42"]})
    assert spec["subject"] == "s" and spec["contract"] == "Cd" and spec["function"] == "fn"
    assert spec["source_roots"] == ["/tmp/x/src"]
