# P247 — Phase C: Counterfactual Reasoning Replays

For each cluster, the MINIMUM additional reasoning step — startable from exactly the information available
during the hunt (source already read; no answer key) — that would have reached the awarded finding. Concrete
and mechanism-specific.

## Cluster 1 — CROSS_CONTRACT_REASONING_FAILURE (9 wt)
**Minimum step:** for every value/identity/control that crosses a contract or chain boundary, name the
*concrete actor on the other side* and trace the value to its terminal state.
- decent H-03: "the refund goes to `from` — *who set `from`, and through which hops?*" Tracing UTB→adapter→
  router→executor shows `from` is not the original payer → refunds land on a wrong address (loss).
- decent M-05: "`refundAddress = msg.sender` — *who is msg.sender at this hop?*" It is the DecentBridgeAdapter
  (a contract), not the EOA → native refund is unrecoverable.
- decent H-02 / M-01: "after the message leaves this chain, *what does the destination/composer do if the
  call fails?*" LayerZero marks delivered-but-failed; Stargate caches with the same stale data → stuck.
- centrifuge M-02: "this permit signature authorizes *what scope* — token or pool? If token, *what else
  shares this token?*" Multiple pools share a tranche token → signature replay on another pool.
- **Generic step:** *complete the call chain to the counterparty and to the terminal state of every bridged
  value/identity; never stop at the local function boundary.*

## Cluster 2 — STATE_MACHINE_MISUNDERSTOOD (9 wt)
**Minimum step:** for every state variable a function writes, ask "*who else can drive this transition, how
often, and what does an adversary gain by repeating/combining transitions?*"
- munchables H-01: "`unlockTime = now + duration` is rewritten on every `lockOnBehalf` — *can someone other
  than the owner trigger this for the owner?*" Yes (on-behalf) → repeated calls freeze withdrawal.
- munchables M-01: "a price feed sets approval state — *can the same actor also occupy the disapproval
  state?*" No mutual-exclusion check → both.
- kleidi M-01: "`_liveProposals` only grows until executed/cancelled — *can an authorized-but-compromised
  actor grow it unbounded?*" Yes → pause/cancel-loop griefing.
- decent H-04: "the `reserves < amount` branch exists — *what does the user actually receive in that branch,
  and is it backed?*" Unbacked dcntEth; bridged ETH lost.
- **Generic step:** *walk each state transition adversarially — repetition, ordering, who-can-trigger, and
  the "else" branch — not just the happy path.*

## Cluster 3 — ACCOUNTING_REASONING_FAILURE (5 wt)
**Minimum step:** for every arithmetic conversion, ask "*which direction must rounding favor, is any quantity
double-counted across calls, and is the index/length arithmetic exact?*"
- centrifuge M-07: "withdraw computes shares via Rounding.Down — *does EIP-4626 require rounding toward the
  vault here?*" Yes → must round up.
- munchables M-03: "`remainder` is carried and re-added next lock — *is it counted toward NFTs twice?*" Yes.
- kleidi M-02: "length = `end − start` — *is the +1 needed for an inclusive byte range?*" Yes → full-width
  param reverts.
- centrifuge M-05 / munchables M-04: "*is a shared balance / a harvest decremented/triggered before this
  state change?*" No → contention / stale rewards.
- **Generic step:** *run a conservation + rounding-direction + index-exactness check on every accounting
  expression.*

## Cluster 4 — PERMISSION_MODEL_FAILURE (5 wt)
**Minimum step:** for every external entrypoint, ask "*who can call this, on whose behalf, and is the gated
party the same as the affected party?*"
- vultisig H-02: the whitelist gates `recipient`, but the *buyer* is the affected/limited party → mismatch.
- centrifuge M-04: `deposit`/`mint` have no caller restriction and need no tokens → callable for a victim.
- decent M-02: `bridgeWithPayload` is a public entrypoint *outside* the fee modifier → fee bypass.
- **Generic step:** *enumerate every public/external entrypoint and verify the gated principal == the
  principal whose funds/limits/state are affected; flag any "on-behalf-of" parameter.*

## Cluster 5 — ECONOMIC_REASONING_FAILURE (2 wt)
**Minimum step:** model the rational actor and the external market — "*can a price be moved before this call;
can an external fee vary; what does a profit-maximizing actor do?*"
- vultisig M-02: an attacker can move the Uniswap pool before `claim` (no slippage bound) → value extraction.
- decent M-04: the external Stargate fee varies; a fixed-bps assumption strands surplus.
- **Generic step:** *for any call reading an external price/fee or paying an actor, evaluate frontrunning and
  incentive-compatibility, not just value conservation.*

## (LIFECYCLE_MISUNDERSTOOD, 1 wt) vultisig M-03
**Minimum step:** "the cap is enforced on a transferable NFT position — *what happens to the invariant when
the NFT is transferred?*" The cap resets per token → per-user invariant broken. (Folds into the
state-machine/lifecycle family.)
