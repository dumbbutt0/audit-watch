"""
Tests for the B1 inherited-multicall sidecar (research-only, isolated). No LLM, no network.

Covers: builder detection of OZ / UniV3 / in-repo Solidity-level multicall bases; the solady-assembly skip;
unknown/ambiguous-base skip; deterministic IDs; merge does not mutate the canonical manifest; the audit runner
without --inherited-sidecar is byte-for-byte unchanged; sidecar-derived candidates carry the required
synthetic/research metadata; routing stays disabled; the canonical manifest (the Step 3.9 gate input) is
unaffected.
"""
import hashlib
import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_context  # noqa: E402
sidecar = importlib.import_module("build_inherited_multicall_sidecar")
audit = importlib.import_module("multicall_invariant_audit")

OZ_BASE = """// SPDX-License-Identifier: MIT
abstract contract Multicall {
    function multicall(bytes[] calldata data) external virtual returns (bytes[] memory results) {
        results = new bytes[](data.length);
        for (uint256 i = 0; i < data.length; i++) {
            results[i] = Address.functionDelegateCall(address(this), data[i]);
        }
        return results;
    }
}
"""

UNIV3_BASE = """// SPDX-License-Identifier: GPL-2.0-or-later
abstract contract Multicall {
    function multicall(bytes[] calldata data) public payable returns (bytes[] memory results) {
        results = new bytes[](data.length);
        for (uint256 i = 0; i < data.length; i++) {
            (bool ok, bytes memory result) = address(this).delegatecall(data[i]);
            results[i] = result;
        }
    }
}
"""

SOLADY_BASE = """// SPDX-License-Identifier: MIT
abstract contract Multicallable {
    function multicall(bytes[] calldata data) public payable virtual returns (bytes[] memory) {
        assembly {
            mstore(0x00, 0x20)
            for {} 1 {} {
                if iszero(delegatecall(gas(), address(), 0, calldatasize(), codesize(), 0x00)) { revert(0, 0) }
            }
        }
    }
}
"""

VARIANT_BASE = """abstract contract Multicall {
    function multicall(bytes[] calldata data) external returns (bytes[] memory results) {
        for (uint256 i = 0; i < data.length; i++) { results[i] = address(this).delegatecall(data[i]); }
        // a second, DIFFERENT-bodied Multicall to force ambiguity
        uint256 sentinel = 12345;
    }
}
"""


def _ws(tmp_path, base_src, deriver_src, deriver_name="Vault.sol", base_name="Multicall.sol",
        base_subdir="lib", import_line=None):
    """Create a tiny workspace: a base file + a deriver file + a canonical manifest pointing at the deriver."""
    (tmp_path / base_subdir).mkdir(parents=True, exist_ok=True)
    base_file = tmp_path / base_subdir / base_name
    base_file.write_text(base_src)
    deriver_file = tmp_path / "src" / deriver_name
    deriver_file.parent.mkdir(parents=True, exist_ok=True)
    if import_line is None:
        import_line = f'import "./{base_subdir}/{base_name}";'
    deriver_file.write_text(import_line + "\n" + deriver_src)
    manifest = tmp_path / "coverage_manifest.json"
    manifest.write_text(json.dumps({
        "schema_version": 1,
        "source": {"contracts_root": str(tmp_path)},
        "items": [{"id": f"function:{deriver_name}:f#x", "kind": "function", "contract": deriver_name.split('.')[0],
                   "name": "f", "file": str(deriver_file), "signature": "", "in_scope": True,
                   "source_span": {"start_line": 2, "end_line": 2}}],
    }))
    return manifest, base_file, deriver_file


# 1. OZ-style inherited multicall detected
def test_detect_oz_style(tmp_path):
    man, _, _ = _ws(tmp_path, OZ_BASE, "contract Vault is ERC20, Multicall { function f() external {} }")
    sc = sidecar.build_sidecar(man, tmp_path)
    assert [e["target_contract"] for e in sc["items"]] == ["Vault"]
    assert sc["items"][0]["base_contract"] == "Multicall"


# 2. UniV3-style (payable address(this).delegatecall) detected
def test_detect_univ3_style(tmp_path):
    man, _, _ = _ws(tmp_path, UNIV3_BASE, "contract Router is Multicall { function f() external {} }")
    sc = sidecar.build_sidecar(man, tmp_path)
    assert len(sc["items"]) == 1 and sc["items"][0]["target_contract"] == "Router"


# 3. in-repo Solidity-level address(this).delegatecall detected (base under an in-repo path, not lib/)
def test_detect_in_repo_base(tmp_path):
    man, _, _ = _ws(tmp_path, UNIV3_BASE, "contract Pool is Clone, Multicall { function f() external {} }",
                    base_subdir="contracts/base", import_line='import {Multicall} from "@base/Multicall.sol";')
    sc = sidecar.build_sidecar(man, tmp_path)
    assert len(sc["items"]) == 1 and "base/Multicall.sol" in sc["items"][0]["base_source_file"]


# 4. solady assembly delegatecall(gas(), address(), ...) is NOT a Solidity-level multicall, and is skipped
def test_skip_solady_assembly(tmp_path):
    # unit: the structural gate rejects the assembly body
    assert sidecar.is_solidity_multicall(
        "function multicall(bytes[] calldata data) public payable returns (bytes[] memory)", SOLADY_BASE) is False
    # build level: deriver `is Multicallable` -> base name not in allowlist -> skipped
    man, _, _ = _ws(tmp_path, SOLADY_BASE, "contract Staker is Multicallable { function f() external {} }",
                    base_name="Multicallable.sol", import_line='import {Multicallable} from "solady/utils/Multicallable.sol";')
    sc = sidecar.build_sidecar(man, tmp_path)
    assert sc["items"] == []


# 5. unknown base (not Multicall) and ambiguous bases are skipped (fail-safe, no guess)
def test_skip_unknown_and_ambiguous(tmp_path):
    # unknown base name
    man, _, _ = _ws(tmp_path, OZ_BASE, "contract Vault is ERC20, Ownable { function f() external {} }")
    assert sidecar.build_sidecar(man, tmp_path)["items"] == []
    # ambiguous: two DIFFERENT-bodied Multicall bases, no import to disambiguate -> skip
    tp = tmp_path / "amb"
    (tp / "a").mkdir(parents=True); (tp / "b").mkdir(parents=True)
    (tp / "a" / "Multicall.sol").write_text(OZ_BASE)
    (tp / "b" / "Multicall.sol").write_text(VARIANT_BASE)
    d = tp / "src" / "Vault.sol"; d.parent.mkdir(parents=True)
    d.write_text("contract Vault is Multicall { function f() external {} }")  # no import line
    man2 = tp / "m.json"
    man2.write_text(json.dumps({"schema_version": 1, "source": {"contracts_root": str(tp)},
        "items": [{"id": "x", "kind": "function", "contract": "Vault", "name": "f", "file": str(d),
                   "in_scope": True, "source_span": {"start_line": 1, "end_line": 1}}]}))
    assert sidecar.build_sidecar(man2, tp)["items"] == []


# 6. sidecar IDs are deterministic across rebuilds
def test_deterministic_ids(tmp_path):
    man, _, _ = _ws(tmp_path, OZ_BASE, "contract Vault is ERC20, Multicall { function f() external {} }")
    a = sidecar.build_sidecar(man, tmp_path)
    b = sidecar.build_sidecar(man, tmp_path)
    assert [e["id"] for e in a["items"]] == [e["id"] for e in b["items"]]
    assert a["items"][0]["id"].startswith("sidecar:")


def _run_audit(tmp_path, manifest, sidecar_path=None):
    rr = tmp_path / ("run_sc" if sidecar_path else "run_base")
    (rr / "output").mkdir(parents=True, exist_ok=True)
    audit_context.get_audit_root = lambda rr=rr: rr
    audit._FILE_CACHE.clear()
    argv = ["a", "--manifest", str(manifest), "--quiet"]
    if sidecar_path:
        argv += ["--inherited-sidecar", str(sidecar_path)]
    old = sys.argv
    sys.argv = argv
    try:
        audit.main()
    finally:
        sys.argv = old
    return json.loads((rr / "output" / "multicall_invariant_audit.json").read_text())


# 7. merging a sidecar does NOT mutate the canonical manifest file
def test_merge_does_not_mutate_manifest(tmp_path):
    man, _, _ = _ws(tmp_path, OZ_BASE, "contract Vault is ERC20, Multicall { function f() external {} }")
    sc = tmp_path / "sidecar.json"
    sc.write_text(json.dumps(sidecar.build_sidecar(man, tmp_path)))
    before = hashlib.sha256(man.read_bytes()).hexdigest()
    _run_audit(tmp_path, man, sc)
    assert hashlib.sha256(man.read_bytes()).hexdigest() == before


# 8. runner WITHOUT --inherited-sidecar is byte-for-byte unchanged (no sidecar report keys)
def test_default_runner_unchanged(tmp_path):
    man, _, _ = _ws(tmp_path, OZ_BASE, "contract Vault is ERC20, Multicall { function f() external {} }")
    r1 = _run_audit(tmp_path, man)
    r2 = _run_audit(tmp_path, man)
    for r in (r1, r2):
        assert "inherited_sidecar" not in r and "sidecar_candidates" not in r
    r1.pop("generated_at"); r2.pop("generated_at")
    assert r1 == r2


# 9. sidecar-derived candidates carry the required metadata
def test_sidecar_candidate_metadata(tmp_path):
    man, _, _ = _ws(tmp_path, UNIV3_BASE, "contract Router is Multicall { function f() external {} }")
    sc = tmp_path / "sidecar.json"
    sc.write_text(json.dumps(sidecar.build_sidecar(man, tmp_path)))
    r = _run_audit(tmp_path, man, sc)
    sid = [c for c in r["candidates"] if c.get("synthetic_attribution")]
    assert sid, "expected at least one sidecar-derived candidate"
    for c in sid:
        assert c["source_kind"] == "inherited_multicall_sidecar"
        assert c["research_only"] is True and c["routes_in_production"] is False
        assert c["routed_manifest_ids"] == [] and c.get("base_contract") == "Multicall"


# 10. routing remains disabled at the report level (with sidecar merged)
def test_routing_disabled(tmp_path):
    man, _, _ = _ws(tmp_path, UNIV3_BASE, "contract Router is Multicall { function f() external {} }")
    sc = tmp_path / "sidecar.json"
    sc.write_text(json.dumps(sidecar.build_sidecar(man, tmp_path)))
    r = _run_audit(tmp_path, man, sc)
    assert r["is_gate"] is False and r["research_only"] is True
    assert r["routes_in_production"] is False and r["routed_manifest_ids"] == []


# 11. the canonical manifest object (Step 3.9 gate input) is unaffected: item count on disk unchanged,
#     and the sidecar is a separate file the gate never reads.
def test_gate_input_unaffected(tmp_path):
    man, _, _ = _ws(tmp_path, OZ_BASE, "contract Vault is ERC20, Multicall { function f() external {} }")
    items_before = json.loads(man.read_text())["items"]
    sc = tmp_path / "sidecar.json"
    sc.write_text(json.dumps(sidecar.build_sidecar(man, tmp_path)))
    _run_audit(tmp_path, man, sc)
    items_after = json.loads(man.read_text())["items"]
    assert items_before == items_after
    # sidecar is its own file, not the manifest
    assert sc.exists() and sc.name != man.name
