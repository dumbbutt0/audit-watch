"""
Tests for the safe_management_coverage RESEARCH prototype (Gnosis-Safe self-management selector coverage +
calldata-decode correctness in guard contracts). No LLM, no network.

8 synthetic guard cases (per the P237 spec) exercised through the pure classifier, plus a mechanism-based reNFT
replay that runs the audit runner over the REAL frozen reNFT Guard.sol + RentalConstants.sol source (recovers
H-04 decode-offset-mismatch + H-02 setFallbackHandler missing). Recovery is by offset value / selector-set
difference — never answer-key string matching.
"""
import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

smc = importlib.import_module("safe_management_coverage_taxonomy")
audit = importlib.import_module("safe_management_coverage_audit")

GUARD_CTX = "function checkTransaction(address to, uint256 value, bytes memory data) external {\n  bytes4 selector;\n  assembly { selector := mload(add(data, 0x20)) }\n"


def _shapes(cands):
    return [c["finding_shape"] for c in cands]


# 1. blocks disableModule but decodes prevModule (offset 0x24) instead of module (0x44) -> ADVANCE
def test_1_disable_module_wrong_offset_advances():
    body = GUARD_CTX + """
      if (selector == enableModule_selector) { _revertNonWhitelisted(_loadValueFromCalldata(data, 0x24)); }
      else if (selector == disableModule_selector) { _revertNonWhitelisted(_loadValueFromCalldata(data, 0x24)); }
      else if (selector == setGuard_selector) { revert(); }
      else if (selector == setFallbackHandler_selector) { revert(); }
    }"""
    cands = smc.classify("Guard", body)
    mism = [c for c in cands if c["finding_shape"] == "decode_offset_mismatch" and c["selector"] == "disableModule"]
    assert mism, _shapes(cands)
    assert mism[0]["used_offset"] == "0x24" and mism[0]["expected_offset"] == "0x44"
    assert mism[0]["confidence"] == "high"


# 2. blocks disableModule CORRECTLY (offset 0x44) -> no decode_offset_mismatch (REJECT for this signal)
def test_2_disable_module_correct_offset_no_mismatch():
    body = GUARD_CTX + """
      if (selector == enableModule_selector) { _revertNonWhitelisted(_loadValueFromCalldata(data, 0x24)); }
      else if (selector == disableModule_selector) { _revertNonWhitelisted(_loadValueFromCalldata(data, 0x44)); }
      else if (selector == setGuard_selector) { revert(); }
    }"""
    cands = smc.classify("Guard", body)
    assert not [c for c in cands if c["finding_shape"] == "decode_offset_mismatch"], _shapes(cands)


# 3. blocks disableModule but MISSES setFallbackHandler -> ADVANCE (incomplete, high)
def test_3_missing_set_fallback_handler_advances():
    body = GUARD_CTX + """
      if (selector == enableModule_selector) { revert(); }
      else if (selector == disableModule_selector) { _revertNonWhitelisted(_loadValueFromCalldata(data, 0x44)); }
      else if (selector == setGuard_selector) { revert(); }
    }"""
    cands = smc.classify("Guard", body)
    fb = [c for c in cands if c["finding_shape"] == "incomplete_selector_coverage" and c["selector"] == "setFallbackHandler"]
    assert fb and fb[0]["confidence"] == "high", _shapes(cands)


# 4. MISSES setGuard -> ADVANCE (incomplete, high)
def test_4_missing_set_guard_advances():
    body = GUARD_CTX + """
      if (selector == enableModule_selector) { revert(); }
      else if (selector == disableModule_selector) { _revertNonWhitelisted(_loadValueFromCalldata(data, 0x44)); }
      else if (selector == setFallbackHandler_selector) { revert(); }
    }"""
    cands = smc.classify("Guard", body)
    sg = [c for c in cands if c["finding_shape"] == "incomplete_selector_coverage" and c["selector"] == "setGuard"]
    assert sg and sg[0]["confidence"] == "high", _shapes(cands)


# 5. blocks the FULL self-management set correctly -> REJECT (zero candidates)
def test_5_full_coverage_rejects():
    body = GUARD_CTX + """
      if (selector == enableModule_selector) { revert(); }
      else if (selector == disableModule_selector) { _revertNonWhitelisted(_loadValueFromCalldata(data, 0x44)); }
      else if (selector == setGuard_selector) { revert(); }
      else if (selector == setFallbackHandler_selector) { revert(); }
      else if (selector == execTransactionFromModule_selector) { revert(); }
      else if (selector == execTransactionFromModuleReturnData_selector) { revert(); }
      else if (selector == multiSend_selector) { revert(); }
      else if (selector == addOwnerWithThreshold_selector) { revert(); }
      else if (selector == removeOwner_selector) { revert(); }
      else if (selector == swapOwner_selector) { revert(); }
      else if (selector == changeThreshold_selector) { revert(); }
      else if (selector == setApprovalForAll_selector) { revert(); }
      else if (selector == increaseAllowance_selector) { revert(); }
      else if (selector == _permit_selector) { revert(); }
    }"""
    cands = smc.classify("Guard", body)
    assert cands == [], _shapes(cands)


# 6. irrelevant contract with same selector NAMES but NO Safe-guard context -> REJECT
def test_6_no_guard_context_rejects():
    body = """function enableModule(address m) external { modules[m] = true; }
      function disableModule(address p, address m) external { modules[m] = false; }"""
    assert smc.classify("ModuleRegistry", body) == []


# 6b. guard context but ZERO Safe-specific selectors (only approval) -> REJECT (coverage gate)
def test_6b_only_approval_selectors_rejects():
    body = GUARD_CTX + """
      if (selector == setApprovalForAll_selector) { revert(); }
      else if (selector == _approve_selector) { revert(); }
    }"""
    assert smc.classify("TokenGuard", body) == []


# 7. admin-only / trusted path -> downgrade to LOW
def test_7_admin_only_downgrades_to_low():
    body = GUARD_CTX + """
      if (selector == disableModule_selector) { _revertNonWhitelisted(_loadValueFromCalldata(data, 0x24)); }
      else if (selector == enableModule_selector) { revert(); }
    }"""
    cands = smc.classify("Guard", body, context={"admin_only": True})
    assert cands, "expected candidates"
    assert all(c["confidence"] == "low" for c in cands), [(c["finding_shape"], c["confidence"]) for c in cands]


# 8. module execution path (execTransactionFromModule) reachable / uncovered -> ADVANCE
def test_8_missing_module_execution_advances():
    body = GUARD_CTX + """
      if (selector == enableModule_selector) { revert(); }
      else if (selector == disableModule_selector) { _revertNonWhitelisted(_loadValueFromCalldata(data, 0x44)); }
      else if (selector == setGuard_selector) { revert(); }
      else if (selector == setFallbackHandler_selector) { revert(); }
    }"""
    cands = smc.classify("Guard", body)
    grp = [c for c in cands if c["finding_shape"] == "incomplete_selector_coverage"
           and "execTransactionFromModule" in (c.get("signals", {}).get("missing_selectors") or [])]
    assert grp, _shapes(cands)


# ---- mechanism-based reNFT replay (real frozen source) ----
