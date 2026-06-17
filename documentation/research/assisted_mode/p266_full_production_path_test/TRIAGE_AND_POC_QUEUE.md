# P266 — TRIAGE_AND_POC_QUEUE (Phase 3)

Triage of the frozen advisory feed (`62275f55f70bd675`). Mechanism hypotheses are formed PRE-REVEAL from the
contest **source only** (the answer key/findings are sealed until Phase 8). Isolated queue:
`outputs/p266_poc_queue.json` (accepts only ADVISORY_RECALL_CANDIDATE; no canonical-record / severity / reportable
writes).

## Selected (3)
| id | advisory locus | recall class | templates | role | pre-reveal mechanism |
|---|---|---|---|---|---|
| **C1** | `CuratorRewardsDistributor.distribute` | NARROW (rank2) | T6/T8 | primary + narrow control | permissionless `distribute()` pays `royaltyfee + dust` to the **arbitrary `_msgSender()`**, not protocol/owner → value misallocation / MEV skim of the curator reward pool |
| **C2** | `Cred._handleTrade` + distribute share basis | RECALL-DELTA (rank5) | T5/T8 | primary recall-delta | distribute splits by **spot** curator share → buy share → call permissionless distribute same-tx → capture `distributeAmount·share/totalNum`, diluting earlier curators; `SHARE_LOCK_PERIOD` blocks resale, attacker exits after lock |
| **C-neg** | `RewardControl.withdrawWithSig` | RECALL-DELTA (rank11) | T2 | negative control | EXPECTED BENIGN: EIP-712 signed (from,to,amount,nonce,deadline), nonce replay-safe, deadline + balance checked |

Mix satisfies the plan rules: ≥1 recall-delta (C2, C-neg) · ≥1 high-risk T8 accounting (C1, C2) · ≥1 narrow-baseline
control (C1) · ≥1 negative control (C-neg).

## Why these / why source supports them
- **C1**: `distribute()` (CuratorRewardsDistributor.sol L77-130) has no access control; `royaltyfee =
  totalBalance·withdrawRoyalty/RATIO_BASE` (1% default) and the rounding dust are transferred to `_msgSender()`
  (L120), while curators get `actualDistributeAmount` via `phiRewardsContract.depositBatch` (L123). The royalty rate
  is owner-governed (`updateRoyalty` onlyOwner) but the **proceeds go to whoever calls** — a clear who-gets-the-fee
  question. Most PoC-feasible (deterministic value delta, no price modeling).
- **C2**: rewards are split on `credContract.getShareNumber(credId,user)` read at call time (L88/L109). Shares are
  bought on a bonding curve in Cred (`buyShareCred → _handleTrade`); `SHARE_LOCK_PERIOD = 10 min` (Cred L33, L625)
  blocks selling within 10 min of a trade but does **not** block `buy → distribute` in the same tx (distribute is a
  separate contract). So a just-in-time curator can capture a share of already-accumulated rewards. Conditional on
  reward magnitude vs bonding-curve cost.
- **C-neg**: `RewardControl.withdrawWithSig` (RewardControl.sol L100-109) verifies an EIP-712 signature over the full
  tuple incl. `nonces[from]`, increments the nonce before withdraw, checks the deadline, and `_withdraw` enforces
  `amount ≤ balance`. No flaw found on inspection → included to confirm the gate does NOT manufacture a finding.

## Skipped high-ranked (recorded)
- `PhiFactory.signatureClaim/merkleClaim` (narrow 0/1): heavier claim-flow + factory/1155 harness; deferred to keep
  the first full-route PoC focused on the self-contained reward subsystem.
- `PhiNFT1155.mint` (delta 8): depends on the claim path; out of focused scope.
- `PhiRewards.depositRewards/handleRewardsAndGetValueSent` (delta 14/15): thin wrappers around RewardControl.deposit;
  exercised indirectly by C1's `depositBatch` and C-neg's withdraw path.

## Expected mechanism + falsifier — frozen in `outputs/p266_poc_queue.json` (hash recorded in Phase 5 freeze).
