"""
Task 5 — scope-file ingestion. When a scope.txt is present, the coverage manifest restricts the
denominator to exactly the listed files (and honors out_of_scope.txt), recording the rationale — so
pointing analyze at the repo contracts/ dir no longer needs a manually-staged in_scope/ view (the
Panoptic friction). With no scope file, legacy exclude-glob behavior is unchanged.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import audit_context  # noqa: E402
build_manifest = importlib.import_module("build_coverage_manifest")


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    return tmp_path


def _contract(c):
    return ("// SPDX-License-Identifier: MIT\npragma solidity ^0.8.20;\n"
            f"contract {c} {{ function act(uint256 a) external {{ x += a; }} uint256 x; }}\n")


def _src(ws):
    src = ws / "contracts"
    (src / "types").mkdir(parents=True, exist_ok=True)
    (src / "InScope.sol").write_text(_contract("InScope"))
    (src / "OutOfScope.sol").write_text(_contract("OutOfScope"))
    (src / "types" / "Helper.sol").write_text(_contract("Helper"))
    (ws / "output" / "static.json").write_text(json.dumps(
        {"contract_path": str(src), "functions": [], "external_calls": [], "tainted_sinks": [], "slither_findings": []}))
    return src


def _run(src):
    old = sys.argv
    sys.argv = ["build_coverage_manifest", "--contract", str(src)]
    try:
        return build_manifest.main()
    finally:
        sys.argv = old


def _manifest(ws):
    return json.loads((ws / "output" / "coverage_manifest.json").read_text())


def test_scope_txt_restricts_denominator(ws):
    src = _src(ws)
    (ws / "scope.txt").write_text("./contracts/InScope.sol\n# a comment\n./contracts/types/Helper.sol\n")
    assert _run(src) == 0
    man = _manifest(ws)
    in_scope_files = {i["file"] for i in man["items"] if i["in_scope"]}
    out_files = {i["file"] for i in man["items"] if not i["in_scope"]}
    assert any(f.endswith("InScope.sol") for f in in_scope_files)
    assert any(f.endswith("types/Helper.sol") for f in in_scope_files)
    assert any(f.endswith("OutOfScope.sol") for f in out_files)         # not listed → excluded
    assert man["source"]["scope_file"] == "scope.txt"
    reasons = {i["scope_reason"] for i in man["items"]}
    assert "in scope.txt" in reasons and "not listed in scope.txt" in reasons


def test_out_of_scope_txt_overrides(ws):
    src = _src(ws)
    (ws / "scope.txt").write_text("./contracts/InScope.sol\n./contracts/OutOfScope.sol\n")
    (ws / "out_of_scope.txt").write_text("./contracts/OutOfScope.sol\n")
    assert _run(src) == 0
    man = _manifest(ws)
    byfile = {}
    for i in man["items"]:
        byfile.setdefault(Path(i["file"]).name, i["in_scope"])
    assert byfile["InScope.sol"] is True
    assert byfile["OutOfScope.sol"] is False                            # deny overrides allow


def test_no_scope_file_legacy_behavior(ws):
    src = _src(ws)
    assert _run(src) == 0
    man = _manifest(ws)
    # no scope.txt → all three production contracts in-scope (legacy exclude-glob behavior)
    in_scope_files = {Path(i["file"]).name for i in man["items"] if i["in_scope"]}
    assert {"InScope.sol", "OutOfScope.sol", "Helper.sol"}.issubset(in_scope_files)
    assert man["source"]["scope_file"] is None
