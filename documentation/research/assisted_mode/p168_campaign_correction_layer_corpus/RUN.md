# P168 — Blind campaign on a correction-layer-rich corpus (maia-talos)

Hygiene-filtered (protocol_src only), reject-first, predictions logged before investigation. **0 harnesses
built** (all candidates source-refuted — never forced). Success metric = reportables per harness.

## Corpus selection
Pre-scan (protocol_src correction-layer signals): **maia-talos 167** · renzo 88 · tokemak 15 · recall 11 ·
munchables 5. Chose **maia-talos-2023-05-semantic-tvl** — rich in managed-NFT (UniV3Staker), wrapper (bHermes),
per-user account (VirtualAccount), and bridge-port recipient surfaces. No `corpus_depleted` needed (corpus was
live). 4 candidates investigated (within the 3–5 target).

## H14 — UniswapV3Staker (managed-NFT deposit.owner) → SOURCE_REFUTED  ★ the prime converting shape
Predicted `static_false_positive`. This is the exact B5 shape (managed-NFT owner correction). **The correction
is applied consistently in every sibling**, so there is no divergence to exploit:
- `withdrawToken` owner-gated: `if (deposit.owner != msg.sender) revert NotCalledByOwner()` (:248).
- `claimReward`/`claimAllRewards` pay `rewards[msg.sender]` (:263/:278) — own rewards.
- Both public `unstakeToken` overloads call `_unstakeToken(..., isNotRestake=true)`, so :374
  `(true || …) && owner != msg.sender` is **always owner-gated**; only `restakeToken` uses the
  permissionless-post-end path and re-stakes the *same* owner's token.
- `_unstakeToken` credits `rewards[owner]` (:446) — the correction, not the caller.
Bucket **SOURCE_REFUTED** (first failed gate **G1** — path-divergence absent: the owner correction is present
in all siblings). A high-quality refutation: the converting shape exists but is correctly applied (unlike B5,
where `claim_many` omitted it). Outcome matched prediction.

## H15 — bHermes `UtilityManager.claim{Weight,Boost,Governance}` → NO_ATTACKER_PROFIT
Predicted `static_false_positive`. No recipient param: `userClaimed*[msg.sender] += amount; safeTransfer(
msg.sender, amount)` under `check*(amount)` (caller's own bHermes-derived allowance). Always pays the caller
their own utility tokens. Bucket **NO_ATTACKER_PROFIT** (G3). Matched.

## H16 — `VirtualAccount.withdrawERC20/721` → PRIVILEGED_ONLY
Predicted `static_false_positive`. `external requiresApprovedCaller` (modifier :69) → `safeTransfer(msg.sender,
…)`; only the account's approved caller can withdraw. Bucket **PRIVILEGED_ONLY** (G2). Matched.

## H17 — `BranchPort.withdraw(_recipient, …)` → PRIVILEGED_ONLY
Predicted `static_false_positive`. `external requiresBridgeAgent` (:209); only the bridge agent calls it and
supplies `_recipient`. Bucket **PRIVILEGED_ONLY** (G2). Matched.

## Result vs the success metric
- **reportables_per_harness 1/1** (unchanged) · **0 new harnesses** · **prediction_accuracy 8/8** ·
  **fabrication_rate 0/13**.
- Refutation quality is high and *meaningful*: H14 in particular is the strongest possible negative — the prime
  converting shape (managed-NFT owner correction) was found in a correction-layer-rich corpus and shown to be
  **consistently applied**. The other three are own-funds / approved-caller / bridge-agent gated.
- **0 reportables.** Honest reading: even a correction-layer-rich corpus did not contain a *correction-layer
  divergence* (one sibling omitting the correction). The converting profile remains scarce; B5 may be a rare
  instance.

## Scorecard after P168
candidates 13 · reportable 1 · runtime_confirmed 1 · harnesses_built 1 · harnesses_avoided 12 ·
source_refutations 4 · gate_refutations 8 · reportables_per_harness 1/1 · prediction_accuracy 8/8 ·
fabrication_rate 0/13.

## Note for the next campaign
maia-talos's correction layers are correctly applied. Remaining fallback corpora with correction-layer signals:
renzo (88), tokemak (15), recall (11), munchables (5). The high-value hunt is specifically for a *divergence*
(single vs batch / one path vs sibling) of an owner/beneficiary correction — grep the correction call-site,
then look for an economically-equivalent path that omits it.
