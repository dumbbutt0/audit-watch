"""
Tests for the abi_getter_mismatch lens (cross-file interface vs public-getter ABI mismatch — Hybra M-07).
No LLM, no network.

Covers: getter-signature inference, interface-decl parsing, selector/arity + return compare, the FP controls
(struct getter / address≡interface / explicit override / no-binding), the route threshold, a fixture
integration through the detector, the prompt clear-contract, the strict route through advisory_escalation_gate,
and a read-only Hybra M-07 end-to-end check.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_context  # noqa: E402
agm = importlib.import_module("abi_getter_mismatch_taxonomy")
audit = importlib.import_module("abi_getter_mismatch_audit")
gate = importlib.import_module("advisory_escalation_gate")

FIX_REL = "tests/fixtures/abi_getter_mismatch/sample.sol"
FIX = ROOT / FIX_REL
DEEP_PASS = ROOT / "prompts" / "deep_pass_packet.md"


def _sv(line):
    return agm.parse_public_state_var(line)


def _getter(line):
    return agm.generated_getter_signature(_sv(line))


# ---------------------------------------------------------------- 1. generated getter inference
def test_getter_signature_inference():
    assert _getter("mapping(uint256 => address[]) public poolVote;")["arg_types"] == ["uint256", "uint256"]
    assert _getter("mapping(uint256 => address[]) public poolVote;")["return_types"] == ["address"]
    assert _getter("address[] public tokens;")["arg_types"] == ["uint256"]
    assert _getter("address[] public tokens;")["return_types"] == ["address"]
    assert _getter("uint256 public totalSupply;")["arg_types"] == []
    assert _getter("mapping(address => mapping(uint256 => uint256)) public votes;")["arg_types"] == ["address", "uint256"]
    # uint normalizes to uint256
    assert _getter("mapping(uint => address) public g;")["arg_types"] == ["uint256"]


# ---------------------------------------------------------------- 8. visibility FP guard
def test_internal_private_constant_not_a_getter():
    assert _sv("mapping(uint256 => address[]) internal poolVote;") is None
    assert _sv("mapping(uint256 => address[]) private poolVote;") is None
    assert _sv("function poolVote(uint tokenId) external view returns(address[] memory);") is None


# ---------------------------------------------------------------- decl parsing + 1. Hybra positive
def test_decl_parsing_and_hybra_positive():
    d1 = agm.parse_decl_signature("function poolVote(uint tokenId) external view returns(address[] memory);")
    assert d1["arg_types"] == ["uint256"] and d1["return_types"] == ["address[]"]
    g = _getter("mapping(uint256 => address[]) public poolVote;")
    res = agm.classify_pair(d1, g)
    assert res["mismatch"] and res["mismatch_type"] == "arity_mismatch" and res["selector_match"] is False
    assert agm.confidence(has_call_site=True, has_name_pairing=True, needs_context=g["needs_context"]) == "high"


# ---------------------------------------------------------------- 3. matching getter safe
def test_matching_getter_is_safe():
    d = agm.parse_decl_signature("function cell(uint a, uint b) external view returns(address);")
    g = _getter("mapping(uint256 => address[]) public cell;")  # getter cell(uint256,uint256)->address
    assert agm.classify_pair(d, g)["mismatch"] is False


# ---------------------------------------------------------------- selector vs arity distinction
def test_selector_vs_arity():
    g = _getter("mapping(address => uint256) public bal;")  # bal(address)->uint256
    arity = agm.classify_pair(agm.parse_decl_signature("function bal() external view returns(uint256);"), g)
    assert arity["mismatch_type"] == "arity_mismatch"
    selector = agm.classify_pair(agm.parse_decl_signature("function bal(uint256 id) external view returns(uint256);"), g)
    assert selector["mismatch_type"] == "selector_mismatch"  # same arity, address vs uint256


# ---------------------------------------------------------------- 5. scalar safe + scalar mismatch
def test_scalar_getter():
    g = _getter("uint256 public totalSupply;")
    assert agm.classify_pair(agm.parse_decl_signature("function totalSupply() external view returns(uint256);"), g)["mismatch"] is False
    bad = agm.classify_pair(agm.parse_decl_signature("function totalSupply(uint256 i) external view returns(uint256);"), g)
    assert bad["mismatch"] and bad["mismatch_type"] == "arity_mismatch"


# ---------------------------------------------------------------- 6/7. nested mapping + public array mismatch
def test_nested_mapping_and_array_mismatch():
    nested = _getter("mapping(address => mapping(uint256 => uint256)) public votes;")
    assert agm.classify_pair(agm.parse_decl_signature("function votes(address a) external view returns(uint256[] memory);"), nested)["mismatch_type"] == "arity_mismatch"
    arr = _getter("address[] public tokens;")
    assert agm.classify_pair(agm.parse_decl_signature("function tokens() external view returns(address[] memory);"), arr)["mismatch_type"] == "arity_mismatch"


# ---------------------------------------------------------------- FP: address ≡ interface, struct getter
def test_fp_address_equiv_and_struct_getter():
    assert agm._ret_compatible("address", "IFactory") is True
    assert agm._ret_compatible("address", "uint256") is False
    # scalar interface-typed var: getter factory()->IFactory vs interface factory()->address → no mismatch
    g = _getter("IFactory public factory;")
    assert g["needs_context"] is True
    assert agm.classify_pair(agm.parse_decl_signature("function factory() external view returns(address);"), g)["mismatch"] is False
    # struct-valued mapping getter is not flagged on return shape (Solidity expands it to a tuple)
    gs = _getter("mapping(bytes32 => PositionInfo) public positions;")
    assert agm.classify_pair(agm.parse_decl_signature("function positions(bytes32 k) external view returns(uint256,uint256);"), gs)["mismatch"] is False


# ---------------------------------------------------------------- 4. route threshold + no-binding low
def test_route_threshold():
    assert agm.ROUTED_CONFIDENCE == {"high", "medium"}
    assert agm.confidence(has_call_site=False, has_name_pairing=False, needs_context=False) == "low"   # no binding
    assert agm.confidence(has_call_site=False, has_name_pairing=True, needs_context=False) == "medium"
    assert agm.confidence(has_call_site=True, has_name_pairing=False, needs_context=False) == "low"     # call but no pairing


# ---------------------------------------------------------------- explicit override resolves
def test_explicit_override_resolves():
    d = agm.parse_decl_signature("function items(uint id) external view returns(address[] memory);")
    fn = agm.parse_decl_signature("function items(uint256 id) external view returns(address[] memory) {")
    assert agm.explicit_fn_resolves(d, fn) is True


# ---------------------------------------------------------------- fixture integration (detector end-to-end)
def _ws(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    return tmp_path


def _line_of(needle: str) -> int:
    for i, l in enumerate(FIX.read_text().splitlines(), 1):
        if needle in l:
            return i
    raise AssertionError(f"fixture missing: {needle}")


def _item(contract, name, sig, start, end=None, in_scope=True):
    return {"id": f"function:{contract}:{name}#x", "kind": "function", "contract": contract,
            "file": FIX_REL, "name": name, "signature": sig,
            "source_span": {"start_line": start, "end_line": end or start},
            "in_scope": in_scope, "attack_surface_score": 3}


def _fixture_manifest():
    return {"schema_version": 1, "source": {}, "items": [
        _item("IVoter", "poolVote", "function poolVote(uint tokenId) external view returns (address[] memory);",
              _line_of("function poolVote(uint tokenId)")),
        _item("IReg", "items", "function items(uint id) external view returns (address[] memory);",
              _line_of("function items(uint id)")),
        _item("IMatch", "cell", "function cell(uint a, uint b) external view returns (address);",
              _line_of("function cell(uint a, uint b)")),
        _item("IOrphan", "orphan", "function orphan(uint id) external view returns (address[] memory);",
              _line_of("function orphan(uint id)")),
        _item("RegImpl", "items", "function items(uint256 id) external view returns (address[] memory) {",
              _line_of("function items(uint256 id)"), _line_of("function items(uint256 id)") + 2),
        _item("Caller", "claimRewards", "function claimRewards() external view returns (address[] memory) {",
              _line_of("function claimRewards"), _line_of("IVoter(voter).poolVote") + 1),
    ]}


def test_fixture_integration(tmp_path, monkeypatch):
    ws = _ws(tmp_path, monkeypatch)
    (ws / "output" / "coverage_manifest.json").write_text(json.dumps(_fixture_manifest()))
    old = sys.argv
    sys.argv = ["abi_getter_mismatch_audit"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((ws / "output" / "abi_getter_mismatch_audit.json").read_text())
    det = {d["state_variable"]: d for d in r["detected"]}

    # A. positive → high, arity_mismatch, routes the call-site function Caller.claimRewards
    assert det["poolVote"]["confidence"] == "high"
    assert det["poolVote"]["mismatch_type"] == "arity_mismatch"
    assert det["poolVote"]["route_manifest_id"] == "function:Caller:claimRewards#x"
    assert "function:Caller:claimRewards#x" in r["routed_manifest_ids"]
    # B. explicit override → suppressed (no detection for items)
    assert "items" not in det
    # C. matching getter → safe (no detection for cell)
    assert "cell" not in det
    # D. no binding → low, recorded as context, NOT routed
    assert det["orphan"]["confidence"] == "low"
    assert det["orphan"]["lens_id"] in r["context_only"]
    assert "function:IOrphan:orphan#x" not in r["routed_manifest_ids"]
    # only the positive routes
    assert r["routed_manifest_ids"] == ["function:Caller:claimRewards#x"]
    assert r["route_rate"] < 0.5


# ---------------------------------------------------------------- strict route through advisory_escalation_gate
def test_gate_routes_abi_mismatch_strict(tmp_path, monkeypatch):
    ws = _ws(tmp_path, monkeypatch)
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")
    mid = "function:Caller:claimRewards#x"
    (ws / "output" / "coverage_manifest.json").write_text(json.dumps({"schema_version": 1, "items": [
        _item("Caller", "claimRewards", "function claimRewards() external {", 1, 3)]}))
    (ws / "output" / "coverage_dispositions.json").write_text(json.dumps({"dispositions": [
        {"manifest_id": mid, "status": "cleared", "evidence": ["x.sol:1"], "finding_refs": [], "clear_reason": "ok"}]}))
    (ws / "output" / "abi_getter_mismatch_audit.json").write_text(json.dumps({"routed_manifest_ids": [mid]}))
    old = sys.argv
    sys.argv = ["advisory_escalation_gate"]
    try:
        assert gate.main() == 0
    finally:
        sys.argv = old
    disp = {d["manifest_id"]: d for d in
            json.loads((ws / "output" / "coverage_dispositions.json").read_text())["dispositions"]}
    assert disp[mid]["status"] == "assigned"
    assert disp[mid]["assigned_agent"] == "abi_getter_mismatch_review"


# ---------------------------------------------------------------- prompt clear-contract
def test_prompt_has_abi_getter_mismatch_contract():
    t = " ".join(DEEP_PASS.read_text().split())
    assert "abi_getter_mismatch contract" in t
    assert "generated getter ABI" in t
    assert "selector/arity comparison" in t
    assert "explicit implementation function" in t
    for field in ("interface signature", "generated getter signature", "call site", "impact"):
        assert field in t


# ---------------------------------------------------------------- read-only Hybra M-07 end-to-end
def test_hybra_m07_routes(monkeypatch):
    hy = ROOT / "audits" / "hybra-finance-2025-10-strict-eval"
    if not (hy / "output" / "coverage_manifest.json").exists():
        pytest.skip("Hybra manifest not present")
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: hy)
    old = sys.argv
    sys.argv = ["abi_getter_mismatch_audit", "--quiet"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((hy / "output" / "abi_getter_mismatch_audit.json").read_text())
    assert "function:GrowthHYBR:claimRewards#7c235721" in r["routed_manifest_ids"]
    assert r["route_rate"] < 0.5
    poolv = [d for d in r["detected"] if d["state_variable"] == "poolVote" and d["confidence"] == "high"]
    assert poolv, "M-07 poolVote not detected high-confidence"
    assert "address[]" in poolv[0]["interface_signature"]
    assert "poolVote(uint256,uint256)" in poolv[0]["generated_getter_signature"]
    assert poolv[0]["mismatch_type"] == "arity_mismatch"
