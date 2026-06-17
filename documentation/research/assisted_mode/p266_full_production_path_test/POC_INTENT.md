# P266 — POC_INTENT (Phase 5, frozen BEFORE any PoC code)

Exploit claims frozen pre-implementation. PoCs live under `pocs/p266/<id>/`. Contest source imported read-only;
mocks documented. No contest/production source edits.

## C1 — distribute() pays royalty + dust to an arbitrary caller
- **Target:** `CuratorRewardsDistributor.distribute(uint256 credId)`.
- **Root cause:** `_msgSender().safeTransferETH(royaltyfee + distributeAmount - actualDistributeAmount)` with no
  access control on `distribute` → the owner-set royalty (1%) + rounding dust accrue to whoever calls, not protocol.
- **Attacker model:** plain EOA; not owner, not a curator, not the depositor.
- **Setup:** real `CuratorRewardsDistributor` + real `PhiRewards` (RewardControl); `ICred` **mocked** (returns a
  fixed curator set + share numbers — the mock is irrelevant to the value-flow bug, documented). `deposit(credId,R)`
  funds the pool.
- **Steps:** attacker (fresh EOA) calls `distribute(credId)`.
- **Expected invariant/value delta:** attacker ETH balance increases by `royaltyfee + dust` (= `R*1%/... + rounding`);
  curators receive `actualDistributeAmount` into PhiRewards.balanceOf; `balanceOf[credId]→0`.
- **Victim/gainer:** gainer = arbitrary caller (attacker); victim = the curator-reward pool / protocol royalty.
- **Expected assertion:** `attacker.balance` increased by exactly `royaltyfee + dust > 0`, attacker ∉ {owner, curators}.
- **Refutation condition:** `distribute` reverts for a non-owner/non-curator, OR royalty routes to owner/treasury.
- **Match expectation:** candidate AWARDED-or-PARTIAL (intent ambiguity: keeper incentive vs misallocated royalty).

## C2 — just-in-time spot-share curator reward capture
- **Target:** `CuratorRewardsDistributor.distribute` reward split on spot `getShareNumber`, fed by `Cred` shares.
- **Root cause:** rewards split by **instantaneous** curator share at distribute time; acquiring share is not gated
  against participating in an already-accumulated reward pool.
- **Attacker model:** fresh EOA that never curated; buys share just before distribute.
- **Setup (this run, PARTIAL):** `ICred` **mocked** to grant the attacker a share immediately before distribute,
  demonstrating that a just-acquired share captures a proportional cut. Full profitability vs the **real** bonding-
  curve acquisition cost + 10-min `SHARE_LOCK_PERIOD` price risk is NOT modeled here (documented limitation).
- **Steps:** honest curator + attacker hold shares; `deposit` reward; attacker (just-acquired share) is included in
  `distribute`; attacker’s PhiRewards balance rises proportionally.
- **Expected value delta:** attacker captures `distributeAmount·attackerShare/totalNum` despite not having curated
  during accrual; honest curators diluted.
- **Expected assertion:** attacker PhiRewards.balanceOf > 0 and equals the spot-share proportion.
- **Refutation condition:** distribute uses a snapshot/accrual-weighted share (not spot) so a just-acquired share
  earns nothing.
- **Match expectation:** PARTIAL (capture mechanism demonstrated; economic profitability left open).

## C-neg — withdrawWithSig (negative control; EXPECTED BENIGN)
- **Target:** `RewardControl.withdrawWithSig`.
- **Claim under test:** signature replay / wrong-account withdraw is NOT possible.
- **Setup:** real `RewardControl` (via a minimal concrete child); fund `from`; produce a valid EIP-712 withdraw sig.
- **Steps:** (1) valid withdrawWithSig succeeds once; (2) **replay** the same sig → must revert (nonce consumed);
  (3) a signature from a non-owner key for `from` → must revert (invalid sig).
- **Expected assertion:** step 1 succeeds; steps 2 and 3 revert. **A passing negative control = the gate did NOT
  manufacture a finding.**
- **Refutation condition (would turn it positive):** replay or wrong-account withdraw succeeds.
- **Match expectation:** BENIGN (no award).

Frozen alongside `outputs/p266_poc_queue.json`. Hashes recorded at Phase 5→6 boundary (POC_RESULTS.md).
