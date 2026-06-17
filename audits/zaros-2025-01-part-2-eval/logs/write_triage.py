#!/usr/bin/env python3
"""Write data/triage/_decisions.json for the 6 Zaros merged findings (eval mode, recall-first).
Schema per triage_write.py: finding_id/triage_status/recommended_severity/decision_reason/ice.
DOS-001 = duplicate root cause of DT-003 → merged (not double-counted)."""
import json, sys
sys.path.insert(0,"scripts")
from audit_context import audit_path

D=[
 {"finding_id":"DT-001","triage_status":"poc_required","recommended_severity":"High",
  "ice":{"impact":"High","confidence":"High","exploitability":"Permissionless"},
  "decision_reason":"redeem L556-563 unlocked-credit guard uses .lte and compares delta to locked (intended: revert when capacityAfter<locked). As written it reverts small redeems and permits redeems whose capacity delta exceeds locked → LPs withdraw market-backing locked credit. High; PoC to confirm exact comparison semantics.",
  "follow_up_packet":"Foundry test: vault with locked credit; redeem amount with delta>locked passes, small redeem reverts."},
 {"finding_id":"DT-002","triage_status":"submit","recommended_severity":"Medium",
  "ice":{"impact":"Medium","confidence":"Medium","exploitability":"Conditional"},
  "decision_reason":"getVaultCreditCapacity converts a possibly-negative SD59x18 net (assets-debt) to uint256; for underwater vaults this reverts, DoSing deposit/redeem/stake/unstake. Bounded DoS → Medium.",
  "follow_up_packet":"Test: drive vault net debt>assets, assert deposit/redeem revert on conversion."},
 {"finding_id":"DT-003","triage_status":"submit","recommended_severity":"Medium",
  "ice":{"impact":"Medium","confidence":"Medium","exploitability":"Permissionless"},
  "decision_reason":"Protocol swaps derive amountOutMin from owner-set global slippageToleranceBps (min 1%) and pass a single persistent storage deadline; both enable sandwich extraction and remove per-tx expiry. Economic leak → Medium.",
  "follow_up_packet":"Test: sandwich settleVaultsDebt swap within tolerance; show value extracted."},
 {"finding_id":"EZ-001","triage_status":"poc_required","recommended_severity":"Medium",
  "ice":{"impact":"Medium","confidence":"Medium","exploitability":"Conditional"},
  "decision_reason":"ZlpVault overrides ERC4626 conversions to MM-engine debt-aware swap rate whose +10**decimalOffset virtual term differs from ERC4626 _decimalsOffset; inconsistent virtual offsets widen first-deposit/rounding inflation. Medium; PoC to quantify.",
  "follow_up_packet":"Test: first-depositor + donation; measure share-price skew vs later depositor."},
 {"finding_id":"TI-001","triage_status":"submit","recommended_severity":"Low",
  "ice":{"impact":"Low","confidence":"Medium","exploitability":"Conditional"},
  "decision_reason":"deposit() assumes exact-amount ERC20 receipt (no balance-delta); FoT/rebasing collateral over-credits shares. Current collateral set has no FoT → Low latent issue.",
  "follow_up_packet":"N/A unless FoT collateral onboarded."},
 {"finding_id":"DOS-001","triage_status":"merged","recommended_severity":"Medium",
  "ice":{"impact":"Medium","confidence":"Medium","exploitability":"Permissionless"},
  "decision_reason":"Same root cause as DT-003 (DEX adapter global slippage + persistent deadline MEV). Merged into DT-003 to avoid double-counting.",
  "follow_up_packet":"See DT-003.","disproof":"Identical root cause/contract as DT-003; merged, not rejected."},
]
audit_path("data/triage/_decisions.json").write_text(json.dumps({"decisions":D}, indent=2))
print("wrote _decisions.json with", len(D), "decisions")
