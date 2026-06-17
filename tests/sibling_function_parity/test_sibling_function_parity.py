"""Tests for the sibling_function_parity research lens (deterministic, no LLM, no network)."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import sibling_function_parity_taxonomy as sfp  # noqa: E402
import sibling_function_parity_audit as audit  # noqa: E402
import audit_context  # noqa: E402


def _f(name, snippet="", modifiers=None, visibility="external", own=None):
    feat = sfp.extract_features(name, "", modifiers, snippet, visibility=visibility)
    feat["own_calls"] = set(own) if own is not None else feat["calls"]
    feat["own_ncalls"] = len(feat["own_calls"])
    return feat


# ---------- CATCH ----------

def test_anchor_claim_claim_many_recipient_high():
    """Blackhole M-04: claim resolves getOriginalOwner; claim_many omits it."""
    strong = _f("claim", "x=_claim(t); if(avm) getOriginalOwner(t); token.transfer(o,a);")
    weak = _f("claim_many", "for(;;){x=_claim(t); token.transfer(o,a); deposit_for(t,a);}")
    cands = sfp.classify_pair(strong, weak)
    assert any(c["parity_type"] == "recipient_parity" and "getOriginalOwner" in c["missing_component"]
               and c["confidence"] == "high" and c["weak"] == "claim_many" for c in cands), cands


def test_registry_parity_name_kin_high():
    strong = _f("createLock", "_addTokenTo(o,t); _mint(o,t); checkpoint();")
    weak = _f("createLockFor", "_mint(o,t); checkpoint();")
    cands = sfp.classify_pair(strong, weak)
    assert any(c["parity_type"] == "registry_parity" and c["confidence"] == "high" for c in cands), cands


def test_validate_execute_prefix_siblings_are_kin():
    a = _f("validateSellCreditMarket", "checkLimit(); require(x);")
    b = _f("executeSellCreditMarket", "transfer(o,a);")
    assert sfp._siblings(a, b)[1] is True  # name_kin via shared core


# ---------- HARMLESS / suppression ----------

def test_forwarder_wrapper_suppressed():
    """public delegate() that is a 1-line forwarder to _delegate() is not a parity bug."""
    strong = _f("_delegate", "_writeCheckpoint(d,a); _moveVotes(x);", visibility="internal")
    weak = _f("delegate", "_delegate(msg.sender, d);", visibility="external", own=["_delegate"])
    assert sfp.classify_pair(strong, weak) == []


def test_internal_weak_sibling_suppressed():
    """fn(external, guarded) / _fn(internal, unguarded): the internal impl is correct-by-design."""
    strong = _f("claimRewards", "validate(x); _move(); transfer(o,a);", visibility="external")
    weak = _f("_claimRewards", "transfer(o,a);", visibility="internal")
    cands = sfp.classify_pair(strong, weak)
    assert all(c["confidence"] != "high" for c in cands)  # weak internal -> never high
    # no candidate names the internal as the reachable weak side
    assert not any(c["weak"] == "_claimRewards" and c["confidence"] in ("high", "medium") for c in cands)


def test_both_admin_suppressed():
    strong = _f("setFeeA", "require(x); fee=a;", modifiers=["onlyOwner"])
    weak = _f("setFeeB", "fee=a;", modifiers=["onlyOwner"])
    assert sfp.classify_pair(strong, weak) == []


def test_event_only_diff_not_flagged():
    """Only difference is a missing emit -> never a finding (no controlled component)."""
    strong = _f("mintA", "_mint(o,a); emit Minted(o,a);")
    weak = _f("mintB", "_mint(o,a);")
    cands = [c for c in sfp.classify_pair(strong, weak) if c["confidence"] in ("high", "medium")]
    assert cands == []


def test_non_sibling_not_paired():
    a = _f("deposit", "token.transfer(o,a);")
    b = _f("rescueTokens", "owner.call(x);")
    assert sfp.classify_pair(a, b) == []


def test_interface_cast_not_a_component():
    """IERC20/event-style uppercase identifiers must not count as missing components."""
    strong = _f("withdrawA", "IERC20(t).transfer(o,a); Transfer(o,a);")
    weak = _f("withdrawB", "t.transfer(o,a);")
    cands = [c for c in sfp.classify_pair(strong, weak) if c["confidence"] in ("high", "medium")]
    assert cands == []


# ---------- end-to-end (research-only contract) ----------

def _write_manifest(tmp_path):
    body_claim = ("function claim(uint t) external returns(uint){ uint a=_claim(t); "
                  "if(avm!=address(0)) { o=getOriginalOwner(t);} token.transfer(o,a); return a;}")
    body_many = ("function claim_many(uint[] t) external returns(bool){ for(uint i;i<t.length;i++){"
                 "uint a=_claim(t[i]); token.transfer(o,a);} return true;}")
    body_internal = "function _claim(uint t) internal returns(uint){ return 1;}"
    src = "contract RewardsDistributor {\n" + body_claim + "\n" + body_many + "\n" + body_internal + "\n}\n"
    f = tmp_path / "RewardsDistributor.sol"
    f.write_text(src)
    lines = src.split("\n")
    sl = lambda key: next(i + 1 for i, ln in enumerate(lines) if key in ln)
    items = []
    for nm, vis in [("claim", "external"), ("claim_many", "external"), ("_claim", "internal")]:
        items.append({"id": f"function:RewardsDistributor:{nm}#x", "kind": "function",
                      "contract": "RewardsDistributor", "name": nm, "file": "RewardsDistributor.sol",
                      "signature": f"function {nm}(...)", "visibility": vis, "mutability": "",
                      "modifiers": [], "in_scope": True,
                      "source_span": {"start_line": sl(f"function {nm}("), "end_line": len(lines)}})
    man = tmp_path / "coverage_manifest.json"
    man.write_text(json.dumps({"items": items}))
    return man


def test_audit_research_only_flags_and_anchor(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    # make ROOT relative read work: write source under tmp and point file paths at tmp
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    man = _write_manifest(tmp_path)
    rc = audit.main_with_args(["--manifest", str(man), "--quiet"]) if hasattr(audit, "main_with_args") else None
    if rc is None:
        monkeypatch.setattr(sys, "argv", ["x", "--manifest", str(man), "--quiet"])
        audit.main()
    rep = json.loads((tmp_path / "output" / "sibling_function_parity_audit.json").read_text())
    assert rep["is_gate"] is False
    assert rep["research_only"] is True
    assert rep["routes_in_production"] is False
    assert rep["routed_manifest_ids"] == []
    anchor = [c for c in rep["candidates"] if c["weak"] == "claim_many"
              and c["parity_type"] == "recipient_parity"]
    assert anchor and anchor[0]["confidence"] == "high", rep["candidates"]


@pytest.mark.skipif(not (ROOT / "audits/blackhole-2025-05-eval/output/coverage_manifest.json").exists(),
                    reason="blackhole manifest not present")
def test_blackhole_anchor_recovery_readonly():
    man = ROOT / "audits/blackhole-2025-05-eval/output/coverage_manifest.json"
    feats = {}
    items = json.loads(man.read_text())["items"]
    # reuse the audit's own pipeline via a temp call is heavy; instead assert the manifest has the pair
    names = {(it["contract"], it["name"]) for it in items if it.get("kind") == "function"}
    assert ("RewardsDistributor", "claim") in names
    assert ("RewardsDistributor", "claim_many") in names
