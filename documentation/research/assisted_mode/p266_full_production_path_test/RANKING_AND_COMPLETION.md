# P266 — RANKING_AND_COMPLETION (Phase 4)

Profile B (messy-reconciliation weighting) + Profile C (runner-up challenge) ranking, then the five completion
operations (STS state-transition-sim · AAS adversarial-actor-substitution · TSE terminal-state-eval · IDC
invariant-delta-computation · CCIT cross-call-identity-tracking). Pre-reveal; source-grounded.

## C1 — CuratorRewardsDistributor.distribute (royalty/dust → arbitrary caller)
**Enumerated mechanisms:** m1a value-misallocation (royalty+dust to arbitrary `_msgSender()`); m1b intended keeper
incentive (benign); m1c unbounded-curator gas DoS.
- **Profile B top-2:** [m1a, m1c] — B weights "value exits the intended pool via an off-nominal recipient path".
- **Profile C top-2:** [m1a, m1b] — C challenges the benign reading: there is **no** access control, no treasury/
  owner routing of the royalty, and `updateRoyalty` is onlyOwner yet the **proceeds** go to the caller → m1a survives
  the runner-up challenge over m1b.
- **Selected: m1a** (both profiles rank it #1; source-backed: L120 `_msgSender().safeTransferETH(royaltyfee + dust)`,
  no access control on `distribute`). Runner-up m1b (intent) flagged for reveal adjudication.
- **Five-op:** STS `balanceOf[credId]: 0→D→0`; caller ETH `+royaltyfee+dust`. · AAS caller = attacker EOA (not owner,
  not curator) → still paid (permissionless). · TSE attacker net `+royaltyfee+dust` per distribution; reward pool
  short by that. · IDC violates "owner-set royalty accrues to protocol"; ETH delta = royaltyfee+dust to arbitrary
  caller. · CCIT `_msgSender()` = external caller = attacker (no meta-tx). 
- **Status: COMPLETED_CHAIN** (value flow fully traced, deterministic). Caveat: whether m1a is *awarded* depends on
  intended design (keeper incentive vs protocol royalty) — adjudicated at reveal.

## C2 — Cred._handleTrade + distribute spot-share basis (just-in-time curator reward capture)
**Enumerated mechanisms:** m2a JIT share capture; m2b lock makes it unprofitable (benign); m2c inherent share
dilution (design).
- **Profile B top-2:** [m2a, m2c] — B weights the reconciliation gap between reward *accrual time* and reward
  *split time* (spot `getShareNumber`).
- **Profile C top-2:** [m2a, m2b] — C challenges m2b: `SHARE_LOCK_PERIOD` only blocks *resale*; `buy → distribute`
  is same-tx, so capture is immediate; only the exit waits out 10 min → m2a survives.
- **Selected: m2a.** Runner-up m2b (profitability) is the open economic question.
- **Five-op:** STS attacker `buyShareCred` raises `shareBalance[credId][attacker]`; distribute reads spot share →
  attacker credited `distributeAmount·share/totalNum` in PhiRewards. · AAS attacker = fresh EOA, never curated. ·
  TSE attacker reward vs cost = bonding-curve buy price + protocol fee + 10-min price risk. · IDC honest curators'
  share diluted by attacker's just-bought share. · CCIT `getShareNumber(credId, attacker)` = just-bought share. 
- **Status: PARTIAL_CHAIN** — capture is real and traceable; **profitability is conditional** (requires accumulated
  rewards > acquisition cost across the lock) and is NOT proven without economic parameters. Honest partial.

## C-neg — RewardControl.withdrawWithSig (negative control)
**Enumerated:** mn-a signature replay; mn-b wrong-account withdraw; mn-c benign.
- **Profile B/C:** both challenge for replay/forgery; the EIP-712 digest binds `from,to,amount,nonces[from],deadline`,
  the nonce is incremented before `_withdraw`, the deadline is checked, and `_withdraw` enforces `amount ≤ balance`.
- **Five-op:** STS `nonces[from]++` each call (replay-closed). · AAS attacker cannot produce `from`'s signature. ·
  TSE no value extractable without `from`'s key / consent. · IDC balance conserved. · CCIT signer = `from`.
- **Status: REFUTED (benign)** — correctly NO chain. The negative control is working: the layer does not manufacture
  a finding here.

## Summary
| candidate | selected mechanism | B top-2 | C top-2 | completion |
|---|---|---|---|---|
| C1 | m1a royalty/dust → arbitrary caller | m1a,m1c | m1a,m1b | **COMPLETED_CHAIN** |
| C2 | m2a JIT spot-share reward capture | m2a,m2c | m2a,m2b | **PARTIAL_CHAIN** |
| C-neg | (none) | — | — | **REFUTED / benign** |
