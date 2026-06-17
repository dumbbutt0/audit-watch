# P268 — TRIAGE_AND_POC_QUEUE (Phase 4)

Triage of the frozen advisory feed (`0bfb52b70571c7cf`). Mechanisms formed PRE-REVEAL from karak **source only**
(answer key sealed). Each selected candidate is deliberately a **high-impact-vs-easy-PoC PAIR** — the P266 trap — so
the P267 selector's behavior is the thing under test. Isolated queue: `outputs/p268_poc_queue.json`.

## Selected (3)
| id | advisory locus | recall class | role | M1 (high-impact, harder PoC) | M2 (easy, lower-impact) |
|---|---|---|---|---|---|
| **C1** | `Vault.finishRedeem/startRedeem` | RECALL-DELTA (#9) | primary | permissionless `finishRedeem` + finish-time spot `convertToAssets` (totalAssets=balanceOf, no virtual-share offset) → queued-withdrawer payout manipulable / value stranded | `startRedeem`'s `this.transferFrom(msg.sender,…)` needs `allowance[staker][vault]`; no self-approval → revert (UX/griefing) |
| **C2** | `Vault.mint/deposit` | RECALL-DELTA (#5) | secondary | first-depositor **share-inflation** via donation (solady ERC4626, no `_decimalsOffset` override, `totalAssets`=balanceOf) → victim deposit rounds to 0 shares → theft | tiny-deposit **zero-share rounding** (dust mints 0 shares) |
| **C-neg** | `SlasherLib.requestSlashing` | narrow (#4) | negative control | slashing manipulates vault accounting | `requestSlashing` is Core/operator-**gated** → no permissionless path |

Mix: ≥2 recall-delta (C1, C2) · ≥2 high-impact accounting/state (C1, C2) · ≥1 control (C-neg). Each is a B/C pair.

## Source basis (pre-reveal)
- **C1**: `Vault.startRedeem` (L125) records `shares` + start time, `this.transferFrom(msg.sender,address(this),shares)`
  (needs staker→vault allowance). `finishRedeem` (L157) is **external, callable by anyone**, computes
  `redeemableAssets = convertToAssets(shares)` at finish (L168) after `MIN_WITHDRAWAL_DELAY`. `totalAssets()` =
  `super.totalAssets()` = `asset.balanceOf(this)` (donatable). M1 = the high-impact accounting manipulation; M2 = the
  trivially-demonstrable approval revert.
- **C2**: `Vault` extends solady `ERC4626` and does **not** override `_decimalsOffset()`; `totalAssets` = balanceOf.
  M1 = classic first-depositor inflation (donation); M2 = dust zero-share rounding. (Dependency flagged: solady's
  default `_useVirtualShares()` could neutralize M1 — a falsifier to resolve in completion/PoC.)
- **C-neg**: `SlasherLib.requestSlashing` is reached via Core (operator/DSS gated) — expected benign control.

## Skipped high-ranked (recorded)
- `NativeVault.validateWithdrawalCredentials/finishWithdrawal` (narrow #0/#1) + `BeaconProofs/Merkle` (delta):
  native-ETH beacon-restaking needs beacon-chain proof fixtures → heavy harness; deferred to keep the first
  selector-in-loop run on the self-contained ERC20 Vault subsystem.

## Why these pairs matter for P268
Each pair has the exact shape that defeated P266: a **higher-impact mechanism (M1)** alongside an **easier-to-PoC,
lower-impact rival (M2)**. The test is whether P267, inserted after B/C ranking, **keeps M1 alive** (SELECT_M1 or
KEEP_BOTH) instead of dropping it for M2 — and whether that preservation then yields exact/strong recovery.
Frozen in `outputs/p268_poc_queue.json`.
