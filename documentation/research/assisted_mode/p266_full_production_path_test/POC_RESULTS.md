# P266 — POC_RESULTS (Phase 6)

Isolated foundry project `pocs/p266/phi/` — `forge test`. The contest's own `lib/` submodules were empty (cloned
without submodules), so phi `src` was copied read-only to `pocs/p266/phi/phi_src` (contest tree unmodified) and deps
were cloned locally at pinned versions: **forge-std v1.9.6 · OpenZeppelin contracts v5.0.2** (contest pins ^5.0.1)
**· solady v0.0.228** (Aug-2024 era). solc 0.8.25 / evm paris (mirrors the contest).

```
cd pocs/p266/phi && forge test -vv
```

## Results — 3/3 pass (built BEFORE reveal; intents frozen)
| id | test | result | observed | supports pre-reveal claim? |
|---|---|---|---|---|
| **C1** | `test_arbitrary_caller_skims_royalty_and_dust` | **PASS** | attacker (no role) captured **1.0 ETH** = the 1% royalty of a 100 ETH pool; curators got 99 ETH; conservation held | **YES** — permissionless royalty/dust → arbitrary caller proven |
| **C2** | `test_jit_acquired_share_captures_accrued_rewards` | **PASS** | a just-acquired equal share captured **49.5 ETH**, equal to the honest curator's 49.5 ETH, despite never curating during accrual | **PARTIAL** — capture proven; profitability vs real bonding-curve cost not modeled |
| **C-neg** | `test_valid_withdraw_succeeds_then_replay_and_forgery_revert` | **PASS** | valid signed withdraw paid out once; **replay reverts** (nonce); **forged sig reverts** | **YES (benign)** — negative control held; the layer did NOT manufacture a finding |

## L1/L2/L3 evidence (Level-3 standard)
- **C1** — L1 attacker EOA calls permissionless `distribute` (no privileged setup) · L2 named deltas asserted
  (`attacker.balance` 0→royaltyfee+dust; `PhiRewards.balanceOf[curator]` credited; `balanceOf[credId]→0`;
  conservation `cap + curated == REWARD`) · L3 outcome asserted (`cap ≥ royaltyfee`, attacker ∉ {owner, curators}).
- **C2** — L1 attacker holds a just-acquired share · L2 `PhiRewards.balanceOf[attacker]` 0→49.5 ETH asserted equal
  to honest curator's cut · L3 spot-share captures accrued reward it did not help accrue. (Cred mocked → economic
  profitability is the open leg = PARTIAL, see LIMITATIONS.)
- **C-neg** — L1/L2/L3 confirm replay+forgery revert; benign.

## Mocks / assumptions (documented)
- `MockCred` implements only the three ICred selectors `distribute()` calls (`isExist`/`getCuratorAddresses`/
  `getShareNumber`). C1's value-flow bug is independent of how shares are computed, so the mock does not affect it.
  For C2 the mock grants the attacker a just-acquired share to isolate the *capture* mechanism; it does NOT model
  bonding-curve acquisition cost or the 10-min `SHARE_LOCK_PERIOD` (those bound profitability — left open).
- `PhiRewards` (real, concrete `RewardControl` child) is used unmodified for the curator-credit leg (C1), the reward
  sink (C2), and the signed-withdraw control (C-neg).

## Freeze hashes (sha256[:16])
POC_INTENT.md `9fea23943038fe6b` · p266_poc_queue.json `b4e5dec6e0a61f39` · C1 `1d30864a72a3b857` ·
C2 `0816aa1c6ea5ba6a` · C-neg `3d20a9d4c3603fec` · MockCred `7d984ed40aa44a36`.
No answer key consulted up to here.
