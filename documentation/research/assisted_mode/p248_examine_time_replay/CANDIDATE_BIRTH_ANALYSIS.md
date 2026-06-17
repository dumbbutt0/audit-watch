# P248 — Phase A: Candidate Birth Analysis

For each of the 21 reasoning-bound misses (P247), what the hunt actually observed, the funnel stage where the
candidate died, and the minimum reasoning step that would have birthed/completed it. Funnel stages: Read
Surface → Observed-Suspicious → Generated-Candidate → Exploit-Chain → Validated. ("Died at X" = the first
stage NOT reached.) Read-only reconstruction from P246 frozen candidates + P247 forensics.

| Finding | Suspicious observation (what the hunt noticed) | Candidate died at | Missing step |
|---|---|---|---|
| decent H-02 | read `_getCallParams` (GAS_FOR_RELAY hardcoded); not flagged | Generated-Candidate | trace user `_dstGasForCall` to the dst-chain execution outcome (delivered-but-failed) |
| decent H-03 | flagged refund-on-failure path (D-M2) | Exploit-Chain | trace `from` across UTB→adapter→router→executor → it's the wrong address |
| decent H-04 | flagged reserve check (D-L1, as off-by-one) | Exploit-Chain | follow the `reserves < amount` branch → user gets unbacked dcntEth, loses ETH |
| decent M-01 | did not flag postBridge staleness | Generated-Candidate | ask "what does Stargate do if sgReceive reverts?" → cached/stuck |
| decent M-02 | flagged a different fee bypass (receiveFromBridge) | Generated-Candidate | enumerate router entrypoints → bridgeWithPayload is outside the fee gate |
| decent M-04 | read fixed `SG_FEE_BPS`; accepted | Generated-Candidate | model external variable Stargate fee → surplus stranded in adapter |
| decent M-05 | read `refundAddress=msg.sender`; not flagged | Generated-Candidate | resolve msg.sender identity at this hop → it's the adapter (stuck) |
| vultisig H-02 | noted whitelist on `recipient` not buyer (V-L1, Low) | Exploit-Chain | check gated-principal vs affected-principal → non-WL buyer bypasses + splits cap |
| vultisig M-02 | did not flag claim slippage | Observed-Suspicious | model frontrun on pool.burn (no slippage bound) → value extraction |
| vultisig M-03 | examined maxCapPerUser/buy (no transfer reasoning) | Exploit-Chain | trace NFT-ownership transition → transfer resets per-user cap |
| kleidi M-01 | read pause() proposal loop; dismissed | Generated-Candidate | adversarial: can an authorized-compromised actor grow `_liveProposals`? → grief |
| kleidi M-02 | flagged calldata-index logic fragile (K-M3) | Exploit-Chain | check index arithmetic exactness → `end−start` needs `+1` (full-width param reverts) |
| kleidi M-03 | did not flag | Generated-Candidate | walk expiry state: newPeriod<currentPeriod for an existing proposal → revert |
| centrifuge M-02 | read LP permit fns; not flagged | Generated-Candidate | scope the permit sig (token not pool) → reuse across pools sharing tranche token |
| centrifuge M-04 | noted deposit/mint callable for others (C-L1) | Exploit-Chain | check access control on deposit/mint → free dust-deposit DoS for a victim |
| centrifuge M-05 | flagged orderbook/decrease-limits (C-H1) | Exploit-Chain | trace shared-escrow share balance → deposit() starves others' claims |
| centrifuge M-07 | flagged rounding drift generally (C-H1) | Exploit-Chain | apply EIP4626 rounding-direction rule → withdraw must round UP |
| munchables H-01 | read lockOnBehalf/_lock; flagged setLockDuration | Exploit-Chain | adversarial: attacker calls lockOnBehalf(victim) → resets unlockTime, freezes |
| munchables M-01 | read approve/disapprove; dismissed | Generated-Candidate | walk the vote state machine → no mutual exclusion → approve+disapprove |
| munchables M-03 | flagged remainder reset (MU-M2, loss direction) | Exploit-Chain | check remainder double-count across locks → extra NFTs minted |
| munchables M-04 | read setLockDuration; not flagged | Generated-Candidate | check pre-state harvest → setLockDuration omits forceHarvest → stale rewards |

## Summary of where candidates died
- **Died at Generated-Candidate** (observed area but birthed NO candidate for the issue): decent H-02, M-01,
  M-02, M-04, M-05; kleidi M-01, M-03; centrifuge M-02; munchables M-01, M-04 = **10 findings**.
- **Died at Exploit-Chain** (birthed a related/partial candidate but never built the chain to the awarded
  impact): decent H-03, H-04; vultisig H-02, M-03; kleidi M-02; centrifuge M-04, M-05, M-07; munchables
  H-01, M-03 = **10 findings**.
- **Died at Observed-Suspicious** (read but never registered as suspicious at all): vultisig M-02 = **1**.
- **Validated:** 0 / 21.
