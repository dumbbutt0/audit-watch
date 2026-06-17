#!/usr/bin/env python3
"""P215 — author per-candidate L3 readiness records at output_research/l3_readiness/ZETA-*.json
(schema = p208 L3_READINESS_SCHEMA.json). Records reflect the bounded blind pass: one executed harness
(ZETA-07), the rest NEEDS_HARNESS / privileged. None promote to High without executed realized-impact proof.
research_only / routes_in_production:false. Source-derived; answer key never read.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[4] / "output_research" / "l3_readiness"
OUT.mkdir(parents=True, exist_ok=True)

COMMON = {"research_only": True, "routes_in_production": False, "production_source_modified": False}

records = {
 # executed harness — real ZRC20; PASS mechanism but privileged precondition => not permissionless => Medium
 "ZETA-07": dict(threat_ceiling="MEDIUM_THREAD", impact_class="accounting", attacker_model="conditional",
    l3_status="PASS", poc_tier="L3_REAL_CONTRACT_POC",
    affected_asset_or_state="ZRC20 outbound gas-fee collection",
    actual_delta="withdraw() succeeds with gasFee==0 when GAS_LIMIT=0", victim_or_protocol_loss="protocol foregoes gas-fee revenue",
    magnitude_basis="executed: gasFee=gasPrice*0+0=0; user gas-coin balance unchanged after withdraw",
    expected_delta_or_control="control test: GAS_LIMIT=21000 -> fee=gasPrice*21000>0 charged",
    dependency_mocks="external_only (mock ISystem; real unmodified ZRC20)",
    poc_path="pocs/p215/test/ZETA07_zeroGasFee.t.sol", poc_command="forge test --match-contract ZETA07 -vv",
    poc_result="2/2 PASS: zero-fee withdrawal confirmed; control charges non-zero fee",
    source_validity_notes="real ZRC20 source; mechanism CONFIRMED; severity floored by privileged GAS_LIMIT precondition"),

 # permissionless High theft claim — NO executed PoC built; analytic refutation (no inter-call balances) => blocked from High
 "ZETA-10": dict(threat_ceiling="HIGH_THREAD", impact_class="theft", attacker_model="permissionless",
    l3_status="NEEDS_HARNESS", poc_tier="STATIC_ONLY",
    affected_asset_or_state="ZetaTokenConsumerUniV3/PancakeV3 swap proceeds",
    actual_delta="", victim_or_protocol_loss="", magnitude_basis="",
    expected_delta_or_control="control would compare attacker net-gain reentrant vs guarded path",
    dependency_mocks="not_built",
    poc_path="", poc_command="",
    poc_result="NOT EXECUTED. Source analysis: getEthFromZeta pulls exactly the caller's amount and forwards proceeds; the consumer holds NO pooled user balances between calls, so cross-function reentrancy yields no realized theft. High theft claim UNSUBSTANTIATED without an executed PoC.",
    source_validity_notes="missing nonReentrant is real (code-quality), but realized fund impact not demonstrated; needs executed harness for any High"),

 # privileged trust-root rotation (centralization) — blocked from High (privileged)
 "ZETA-03": dict(threat_ceiling="CRITICAL_THREAD", impact_class="access_control", attacker_model="privileged",
    l3_status="NOT_ATTEMPTED", poc_tier="STATIC_ONLY",
    affected_asset_or_state="custody funds / ZetaNonEth mint authority",
    actual_delta="", victim_or_protocol_loss="full drain/mint IF privileged key compromised", magnitude_basis="centralization risk",
    expected_delta_or_control="", dependency_mocks="not_built", poc_path="", poc_command="",
    poc_result="NOT EXECUTED. Requires compromise of a PRIVILEGED key (TSS/updater/FUNGIBLE_MODULE).",
    source_validity_notes="trust/centralization; privileged exploitability -> not permissionless High"),

 "ZETA-01": dict(threat_ceiling="HIGH_THREAD", impact_class="accounting", attacker_model="conditional",
    l3_status="NEEDS_HARNESS", poc_tier="STATIC_ONLY",
    affected_asset_or_state="ERC20Custody balance for fee-on-transfer assets",
    actual_delta="", victim_or_protocol_loss="", magnitude_basis="",
    expected_delta_or_control="control: non-FoT token withdraws cleanly", dependency_mocks="not_built",
    poc_path="", poc_command="", poc_result="NOT EXECUTED. Conditional on a FoT token being whitelisted.",
    source_validity_notes="real asymmetry deposit(delta) vs withdraw(raw); needs executed insolvency PoC for High"),

 "ZETA-04": dict(threat_ceiling="HIGH_THREAD", impact_class="auth_only", attacker_model="conditional",
    l3_status="NEEDS_HARNESS", poc_tier="STATIC_ONLY",
    affected_asset_or_state="connector pause control over inbound delivery",
    actual_delta="", victim_or_protocol_loss="", magnitude_basis="",
    expected_delta_or_control="", dependency_mocks="not_built", poc_path="", poc_command="",
    poc_result="NOT EXECUTED. onReceive lacks whenNotPaused (source-confirmed asymmetry); availability impact.",
    source_validity_notes="source-proven modifier asymmetry; severity availability/Medium, not theft"),

 "ZETA-05": dict(threat_ceiling="HIGH_THREAD", impact_class="theft", attacker_model="privileged",
    l3_status="NEEDS_HARNESS", poc_tier="STATIC_ONLY",
    affected_asset_or_state="connector token delivery (replay)",
    actual_delta="", victim_or_protocol_loss="", magnitude_basis="",
    expected_delta_or_control="", dependency_mocks="not_built", poc_path="", poc_command="",
    poc_result="NOT EXECUTED. Double-delivery requires TSS to replay (privileged precondition).",
    source_validity_notes="no internalSendHash dedup (defense-in-depth gap); privileged exploitability"),

 "ZETA-06": dict(threat_ceiling="HIGH_THREAD", impact_class="auth_only", attacker_model="conditional",
    l3_status="NEEDS_HARNESS", poc_tier="STATIC_ONLY",
    affected_asset_or_state="ZetaInteractor sender allow-list",
    actual_delta="", victim_or_protocol_loss="", magnitude_basis="",
    expected_delta_or_control="", dependency_mocks="not_built", poc_path="", poc_command="",
    poc_result="NOT EXECUTED. Requires unregistered interactor entry + TSS-relayed empty-sender message.",
    source_validity_notes="empty-bytes comparison gap is real; impact depends on inheriting onZetaMessage"),

 "ZETA-08": dict(threat_ceiling="HIGH_THREAD", impact_class="access_control", attacker_model="privileged",
    l3_status="NOT_ATTEMPTED", poc_tier="STATIC_ONLY",
    affected_asset_or_state="ZRC20 mint authority",
    actual_delta="", victim_or_protocol_loss="unbounded mint IF FUNGIBLE_MODULE compromised", magnitude_basis="centralization risk",
    expected_delta_or_control="", dependency_mocks="not_built", poc_path="", poc_command="",
    poc_result="NOT EXECUTED. Requires FUNGIBLE_MODULE compromise; missing zero-address guard is QA.",
    source_validity_notes="centralization/QA; privileged exploitability -> not permissionless High"),

 "ZETA-11": dict(threat_ceiling="HIGH_THREAD", impact_class="theft", attacker_model="conditional",
    l3_status="NEEDS_HARNESS", poc_tier="STATIC_ONLY",
    affected_asset_or_state="Trident consumer swap routing",
    actual_delta="", victim_or_protocol_loss="", magnitude_basis="",
    expected_delta_or_control="control: legit pool routes correctly", dependency_mocks="not_built",
    poc_path="", poc_command="", poc_result="NOT EXECUTED. Fund-loss conditional on Trident factory permissionlessness; empty -> DoS.",
    source_validity_notes="unvalidated getPools()[0]; conditional; needs executed PoC for High"),
}

for cid, r in records.items():
    rec = {"candidate_id": cid}
    rec.update(COMMON)
    rec.update(r)
    (OUT / f"{cid}.json").write_text(json.dumps(rec, indent=2))
print("wrote", len(records), "L3 records to", OUT)
print("ids:", ",".join(sorted(records)))
