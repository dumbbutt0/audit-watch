"""
Tests for the liquidation_health_accounting RESEARCH prototype (Size Credit seed). No LLM, no network.

Covers the 5 shapes + Size seed recovery (H-03/H-04/M-09/M-11), the name-gate FP controls
(transfer/deposit/reward/oracle/admin/generic suppressed), the config/init exclusion, the needs_context
demotion, the research-only (no-gate / no-route) guarantee, and a read-only Size end-to-end check.
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
lha = importlib.import_module("liquidation_health_accounting_taxonomy")
audit = importlib.import_module("liquidation_health_accounting_audit")
gate = importlib.import_module("advisory_escalation_gate")
DEEP_PASS = ROOT / "prompts" / "deep_pass_packet.md"

_LIQ = """function executeLiquidate(P p) external returns (uint256 liquidatorProfitCollateralToken) {
  uint256 debtInCollateralToken = state.debtTokenAmountToCollateralTokenAmount(p.futureValue);
  liquidatorProfitCollateralToken = debtInCollateralToken + liquidatorReward;
  uint256 collateralRemainder = assignedCollateral - liquidatorProfitCollateralToken;
  uint256 collateralRemainderCap = Math.mulDivDown(debtInCollateralToken, crLiquidation, PERCENT);
  collateralToken.transferFrom(p.borrower, msg.sender, liquidatorProfitCollateralToken); }"""
_LWR = """function executeLiquidateWithReplacement(P p) external returns (uint256 issuanceValue) {
  uint256 tenor = debtPosition.dueDate - block.timestamp;
  debtPosition.borrower = p.borrower; debtToken.mint(p.borrower, futureValue);
  borrowAToken.transferFrom(address(this), feeRecipient, liquidatorProfitBorrowToken); }"""
_COMP = """function executeCompensate(P p) external {
  uint256 amountToCompensate = Math.min(p.amount, creditPositionWithDebtToRepay.credit);
  state.reduceDebtAndCredit(debtPositionId, creditId, amountToCompensate);
  uint256 fragmentationFee = state.feeConfig.fragmentationFee;
  collateralToken.transferFrom(msg.sender, feeRecipient, fragmentationFee); }"""


def _shapes(name, body):
    return {c["finding_shape"]: c["confidence"] for c in lha.classify(name, "", "f.sol", "C", snippet=body)}


# 1. H-03 collateral remainder cap → high
def test_h03_collateral_remainder_cap():
    assert _shapes("executeLiquidate", _LIQ).get("collateral_remainder_cap") == "high"


# 2. H-04 liquidator profit → high
def test_h04_liquidator_profit_bound():
    assert _shapes("executeLiquidate", _LIQ).get("liquidator_profit_bound") == "high"


# 3. M-09 compensate underwater CR (no health check) → high
def test_m09_health_factor_after_action():
    assert _shapes("executeCompensate", _COMP).get("health_factor_after_action") == "high"


# 4. M-11 replacement swap fee → high/medium (spec); the real Size fn (with a collateral return term) is
#    high — asserted in test_size_seed_recovery_readonly below.
def test_m11_replacement_swap_fee():
    assert _shapes("executeLiquidateWithReplacement", _LWR).get("replacement_swap_fee_accounting") in ("high", "medium")


# 5. credit-sale bypass → high/medium
def test_credit_sale_bypass():
    assert _shapes("executeCompensate", _COMP).get("credit_sale_bypass") in ("high", "medium")


# 6-9, 11. negatives — not name-gated → no candidates
@pytest.mark.parametrize("name,body", [
    ("transfer", "function transfer(address to,uint256 a) public { _b[to]+=a; }"),
    ("deposit", "function deposit(uint256 a) external { token.transferFrom(msg.sender, address(this), a); }"),
    ("claimRewards", "function claimRewards() external { reward.transfer(msg.sender, pending); }"),
    ("getPrice", "function getPrice() external view returns(uint256){ return oracle.latestAnswer(); }"),
    ("computeCollateralValue", "function computeCollateralValue(uint256 a) public view returns(uint256){ return a*price/1e18; }"),
])
def test_negatives_not_name_gated(name, body):
    assert lha.classify(name, "", "f.sol", "C", snippet=body) == []


# 10. admin/config setter → excluded even though it contains "config"/CR terms
def test_admin_config_setter_excluded():
    body = "function updateConfig(uint256 crLiquidation, uint256 minTenor) external onlyOwner { riskConfig.crLiquidation = crLiquidation; }"
    assert lha.classify("updateConfig", "", "f.sol", "C", snippet=body) == []
    # an Initialize risk-config validator must also be excluded (matches "risk" but is config)
    assert lha.classify("validateInitializeRiskConfigParams", "", "f.sol", "C",
                        snippet="function validateInitializeRiskConfigParams(I c) { require(c.crLiquidation>c.crOpening); require(c.minTenor<c.maxTenor); }") == []


# 12. needs_context demotion: a STRONG-PATH (liquidation) mutator whose CR check is in an unresolved validate*
def test_needs_context_when_cr_in_unresolved_helper():
    body = """function liquidateAndSettle(P p) external {
      validateSomething(p);
      uint256 net = p.coll.sub(p.debt);
      debtToken.burn(p.borrower, net);
      collateralToken.transferFrom(address(this), p.borrower, p.coll); }"""
    sh = _shapes("liquidateAndSettle", body)
    assert sh.get("health_factor_after_action") == "needs_context"


# ----------------------------------------------------------------- Ethos-informed CDP additions
def test_ethos_redeem_collateral_routes():
    body = """function redeemCollateral(address _collateral, uint _maxFeePercentage) external {
      totals.price = priceFeed.fetchPrice(_collateral);
      totals.totalCollDrawn = totals.totalCollDrawn.add(singleRedemption.collLot);
      uint redemptionFee = _getRedemptionFee(totals.totalCollDrawn);
      contractsCache.activePool.sendCollateral(_collateral, msg.sender, totals.totalCollDrawn.sub(redemptionFee)); }"""
    sh = _shapes("redeemCollateral", body)
    assert sh.get("collateral_remainder_cap") in ("high", "medium")


def test_ethos_stability_pool_offset_routes():
    body = """function offset(uint _debtToOffset, uint _collToAdd, address _collateral) external {
      uint LUSDLossPerUnitStaked = _debtToOffset.mul(DECIMAL_PRECISION).div(totalLUSD);
      uint collateralGainPerUnitStaked = _collToAdd.mul(DECIMAL_PRECISION).div(totalLUSD);
      _moveOffsetCollAndDebt(_collateral, _collToAdd, _debtToOffset); }"""
    sh = _shapes("offset", body)
    assert sh.get("stability_pool_redistribution") in ("high", "medium")


def test_icr_word_boundary_no_false_match():
    # "tcr" must NOT match inside "getCreditPosition" (the substring trap that suppressed Size M-09) — a plain
    # credit-position read with no real CR/liquidation shape does not route.
    assert lha.classify("viewCreditPosition", "", "f.sol", "C",
                        snippet="function viewCreditPosition(uint id) external view returns(uint){ return state.getCreditPosition(id).credit; }") == []
    # a bare ICR getter view -> no state, no shape -> no candidate
    assert lha.classify("getCurrentICR", "", "f.sol", "TroveManager",
                        snippet="function getCurrentICR(address a, uint price) external view returns(uint){ return LiquityMath._computeCR(coll, debt, price); }") == []


def test_generic_offset_math_no_route():
    # offset-named fn with NO collateral/debt and no SP context -> two-term gate suppresses it
    assert lha.classify("offset", "", "f.sol", "MathLib",
                        snippet="function offset(uint a, uint b) internal pure returns(uint){ return a.sub(b); }") == []


def test_generic_repay_improves_health_no_route():
    # a plain debt-repay that improves health, NOT on a liquidation/recovery path -> health_factor suppressed
    body = "function repayDebt(uint amount) external { debt = debt.sub(amount); debtToken.burn(msg.sender, amount); }"
    sh = _shapes("repayDebt", body)
    assert sh.get("health_factor_after_action") is None


def test_thin_wrapper_suppressed():
    # name-gated delegate with no accounting -> suppressed
    assert lha.classify("liquidate", "", "f.sol", "TroveManagerScript",
                        snippet="function liquidate(address _borrower) external { troveManager.liquidate(_borrower); }") == []


def test_ethos_seed_recovery_readonly(monkeypatch):
    eth = ROOT / "audits" / "ethos-reserve-2023-02-liquidation-health"
    if not (eth / "output" / "coverage_manifest.json").exists():
        pytest.skip("Ethos manifest not present")
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: eth)
    old = sys.argv
    sys.argv = ["liquidation_health_accounting_audit", "--quiet"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((eth / "output" / "liquidation_health_accounting_audit.json").read_text())
    byfn = {}
    for c in r["candidates"]:
        byfn.setdefault((c["contract"], c["function"]), set()).add(c["finding_shape"])
    # M-09 redemption host + H-01 stability-pool host recovered; 0 wrong-domain FP (all in liq/SP/redemption)
    assert "collateral_remainder_cap" in byfn.get(("RedemptionHelper", "redeemCollateral"), set())
    assert "stability_pool_redistribution" in byfn.get(("StabilityPool", "updateRewardSum"), set())
    assert r["routes_in_production"] is True
    domains = ("TroveManager", "StabilityPool", "RedemptionHelper", "BorrowerOperations", "ActivePool", "CollSurplusPool")
    assert all(c["contract"] in domains for c in r["candidates"]), "wrong-domain FP present"
    # H-01 + M-09 entrypoints route; internal helpers (_redeemCollateralFromTrove / _computeRewardsPerUnitStaked)
    # are attached as context, not routed independently (volume control); routed ≪ raw candidates.
    cand = {c["manifest_id"]: c for c in r["candidates"]}
    routed_fns = {(cand[m]["contract"], cand[m]["function"]) for m in r["routed_manifest_ids"]}
    assert ("RedemptionHelper", "redeemCollateral") in routed_fns          # M-09
    assert ("StabilityPool", "updateRewardSum") in routed_fns              # H-01
    assert ("StabilityPool", "offset") in routed_fns                       # H-01
    assert ("TroveManager", "liquidate") in routed_fns                     # M-10 host
    assert len(r["routed_manifest_ids"]) < r["raw_candidates"]            # helpers folded into context
    assert r["helper_attachments"], "expected helper attachments (volume control)"
    # every attached helper is absent from routed_manifest_ids
    attached = {h["manifest_id"] for v in r["helper_attachments"].values() for h in v}
    assert attached and not (attached & set(r["routed_manifest_ids"]))


def test_routed_confidence_and_research_constants():
    assert lha.ROUTED_CONFIDENCE == {"high", "medium"}
    assert "low" not in lha.ROUTED_CONFIDENCE


# ----------------------------------------------------------------- promoted (advisory high-only) flags
def test_audit_promoted_advisory_flags(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    mid = "function:Seed:executeLiquidate#x"
    (tmp_path / "output" / "coverage_manifest.json").write_text(json.dumps({"schema_version": 1, "items": [
        {"id": mid, "kind": "function", "contract": "Seed", "visibility": "external",
         "name": "executeLiquidate", "file": "tests/fixtures/liquidation_health_accounting/sample.sol",
         "signature": "", "source_span": {"start_line": 7, "end_line": 15}, "in_scope": True}]}))
    old = sys.argv
    sys.argv = ["liquidation_health_accounting_audit"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((tmp_path / "output" / "liquidation_health_accounting_audit.json").read_text())
    # advisory: is_gate stays False (never blocks); promoted to production routing, high-only entrypoint routes.
    assert r["is_gate"] is False and r["research_only"] is False and r["routes_in_production"] is True
    assert r["routed_manifest_ids"] == [mid]


def test_size_seed_recovery_readonly(monkeypatch):
    size = ROOT / "audits" / "size-credit-2024-06"
    if not (size / "output" / "coverage_manifest.json").exists():
        pytest.skip("Size manifest not present")
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: size)
    old = sys.argv
    sys.argv = ["liquidation_health_accounting_audit", "--quiet"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    r = json.loads((size / "output" / "liquidation_health_accounting_audit.json").read_text())
    byfn = {}
    for c in r["candidates"]:
        byfn.setdefault((c["contract"], c["function"]), set()).add((c["finding_shape"], c["confidence"]))
    assert ("collateral_remainder_cap", "high") in byfn[("Liquidate", "executeLiquidate")]          # H-03
    assert ("liquidator_profit_bound", "high") in byfn[("Liquidate", "executeLiquidate")]           # H-04
    assert ("health_factor_after_action", "high") in byfn[("Compensate", "executeCompensate")]      # M-09
    assert ("replacement_swap_fee_accounting", "high") in \
        byfn[("LiquidateWithReplacement", "executeLiquidateWithReplacement")]                       # M-11
    assert r["routes_in_production"] is True
    # 4/4 mandated seed entrypoints route (all execute* externals; no `_` helpers in Size → none demoted)
    cand = {c["manifest_id"]: c for c in r["candidates"]}
    routed_fns = {(cand[m]["contract"], cand[m]["function"]) for m in r["routed_manifest_ids"]}
    assert ("Liquidate", "executeLiquidate") in routed_fns                                          # H-03 + H-04
    assert ("Compensate", "executeCompensate") in routed_fns                                        # M-09
    assert ("LiquidateWithReplacement", "executeLiquidateWithReplacement") in routed_fns            # M-11


# ================================================================= promotion wiring (helper-volume + gate)
_ROUTING_FIX = "tests/fixtures/liquidation_health_accounting/routing.sol"
_BANK_ITEMS = [
    {"id": "function:Bank:liquidate#x", "kind": "function", "contract": "Bank", "name": "liquidate",
     "visibility": "external", "file": _ROUTING_FIX, "signature": "", "in_scope": True,
     "source_span": {"start_line": 9, "end_line": 14}},
    {"id": "function:Bank:_seize#x", "kind": "function", "contract": "Bank", "name": "_seize",
     "visibility": "internal", "file": _ROUTING_FIX, "signature": "", "in_scope": True,
     "source_span": {"start_line": 15, "end_line": 18}},
    {"id": "function:Bank:_redeemOrphan#x", "kind": "function", "contract": "Bank", "name": "_redeemOrphan",
     "visibility": "internal", "file": _ROUTING_FIX, "signature": "", "in_scope": True,
     "source_span": {"start_line": 19, "end_line": 22}},
]


def _run_audit(ws, monkeypatch):
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: ws)
    old = sys.argv
    sys.argv = ["liquidation_health_accounting_audit", "--quiet"]
    try:
        assert audit.main() == 0
    finally:
        sys.argv = old
    return json.loads((ws / "output" / "liquidation_health_accounting_audit.json").read_text())


def test_helper_volume_control_attach_and_orphan(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    (tmp_path / "output" / "coverage_manifest.json").write_text(
        json.dumps({"schema_version": 1, "items": _BANK_ITEMS}))
    r = _run_audit(tmp_path, monkeypatch)
    routed = set(r["routed_manifest_ids"])
    # high external entrypoint routes; the helper it calls is attached (NOT routed); the orphan helper routes.
    assert "function:Bank:liquidate#x" in routed
    assert "function:Bank:_redeemOrphan#x" in routed                       # orphan: no entrypoint caller
    assert "function:Bank:_seize#x" not in routed                          # attached as context to liquidate
    ha = r["helper_attachments"]
    assert "function:Bank:liquidate#x" in ha
    assert any(h["function"] == "_seize" for h in ha["function:Bank:liquidate#x"])
    # every routed id is a HIGH, in-scope candidate (high-only contract)
    cand = {c["manifest_id"]: c for c in r["candidates"]}
    assert all(cand[m]["confidence"] == "high" and cand[m]["in_scope"] for m in routed)


def test_routing_is_high_only():
    # a candidate with collateral + remainder + liquidator but NO debt/credit dimension is non-high (medium),
    # so the high-only router must exclude it. (Routing keys on confidence == "high".)
    src = ("function liquidateSurplus() external {\n"
           "  uint256 collateralRemainder = assignedCollateral - liquidatorShare;\n"
           "  collateralToken.transfer(msg.sender, collateralRemainder); }")
    sh = {c["finding_shape"]: c["confidence"]
          for c in lha.classify("liquidateSurplus", "", "f.sol", "C", snippet=src)}
    assert sh and all(v != "high" for v in sh.values())


def test_gate_routes_lha_strict_full_audit(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")
    mid = "function:Bank:liquidate#x"
    helper = "function:Bank:_seize#x"
    (tmp_path / "output" / "coverage_manifest.json").write_text(json.dumps({"schema_version": 1, "items": [
        {"id": mid, "kind": "function", "contract": "Bank", "name": "liquidate", "file": "f.sol",
         "signature": "", "source_span": {"start_line": 1, "end_line": 3}, "in_scope": True}]}))
    (tmp_path / "output" / "coverage_dispositions.json").write_text(json.dumps({"dispositions": [
        {"manifest_id": mid, "status": "unassigned", "evidence": [], "finding_refs": []}]}))
    (tmp_path / "output" / "liquidation_health_accounting_audit.json").write_text(json.dumps({
        "routed_manifest_ids": [mid],
        "helper_attachments": {mid: [{"manifest_id": helper, "function": "_seize",
                                      "finding_shape": "collateral_remainder_cap"}]}}))
    old = sys.argv
    sys.argv = ["advisory_escalation_gate"]
    try:
        assert gate.main() == 0
    finally:
        sys.argv = old
    disp = {d["manifest_id"]: d for d in
            json.loads((tmp_path / "output" / "coverage_dispositions.json").read_text())["dispositions"]}
    # routed to a DEEP PASS — never minted as a finding
    assert disp[mid]["status"] == "assigned"
    assert disp[mid]["assigned_pass"] == "deep"
    assert disp[mid]["assigned_agent"] == "liquidation_health_accounting_review"
    assert disp[mid]["status"] != "finding"
    # context_helpers carried into provenance
    assert disp[mid]["liquidation_health_accounting"]["context_helpers"][0]["function"] == "_seize"
    rep = json.loads((tmp_path / "output" / "advisory_escalation_gate.json").read_text())
    assert rep["liquidation_health_accounting_strict"] is True
    assert rep["liquidation_health_accounting_routed"] == 1


def test_gate_advisory_only_without_strict(tmp_path, monkeypatch):
    # no AUDITWATCH_FULL_AUDIT + strict flag false → advisory only, disposition untouched, nothing routed.
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    monkeypatch.delenv("AUDITWATCH_FULL_AUDIT", raising=False)
    monkeypatch.setattr(gate, "_policy", lambda: {"advisory_escalation_strict_full_audit": False,
                                                  "liquidation_health_accounting_strict": False,
                                                  "liquidation_health_accounting_strict_full_audit": False})
    mid = "function:Bank:liquidate#x"
    (tmp_path / "output" / "coverage_manifest.json").write_text(json.dumps({"schema_version": 1, "items": [
        {"id": mid, "kind": "function", "contract": "Bank", "name": "liquidate", "file": "f.sol",
         "signature": "", "source_span": {"start_line": 1, "end_line": 3}, "in_scope": True}]}))
    (tmp_path / "output" / "coverage_dispositions.json").write_text(json.dumps({"dispositions": [
        {"manifest_id": mid, "status": "unassigned", "evidence": [], "finding_refs": []}]}))
    (tmp_path / "output" / "liquidation_health_accounting_audit.json").write_text(
        json.dumps({"routed_manifest_ids": [mid], "helper_attachments": {}}))
    old = sys.argv
    sys.argv = ["advisory_escalation_gate"]
    try:
        assert gate.main() == 0
    finally:
        sys.argv = old
    disp = {d["manifest_id"]: d for d in
            json.loads((tmp_path / "output" / "coverage_dispositions.json").read_text())["dispositions"]}
    assert disp[mid]["status"] == "unassigned"                             # untouched, NOT routed, NOT minted
    rep = json.loads((tmp_path / "output" / "advisory_escalation_gate.json").read_text())
    assert rep["liquidation_health_accounting_strict"] is False
    assert rep["liquidation_health_accounting_routed"] == 0


def test_prompt_has_lha_clear_contract():
    t = " ".join(DEEP_PASS.read_text().split())
    assert "liquidation_health_accounting contract" in t
    assert "liquidation_health_accounting_review" in t
    assert "context_helpers" in t
    assert "before AND after" in t and "converted collateral-token" in t
