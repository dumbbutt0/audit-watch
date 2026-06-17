# basin — Phase 3: Five-operation routine (PRE-REVEAL, FROZEN)

Same five ops as P254. Labels PASS/NO_EFFECT/UNCLEAR/CANDIDATE_STRENGTHENED; chain status COMPLETED_CHAIN/
PARTIAL_CHAIN/NO_CHAIN/REFUTED. New P255 metric: **plausible mechanisms considered (pre-reveal)** per locus.

## L1 — `Stable2.decodeWellData` → **PARTIAL_CHAIN** · plausible mechanisms considered: **2**
Mechanisms enumerated pre-reveal: (a) default-to-18 path broken for token1 ⇒ a well whose token1 decimals are
left unset (0 in well data) over/mis-scales reserves[1] ⇒ corrupted `calcRate`/`calcLpTokenSupply`; (b) dead
code / harmless if every well always encodes real non-zero decimals.
- **STS — PASS.** decimals[1]=0 → `getScaledReserves` multiplies reserves[1] by 1e18; all downstream Stable2 math uses a reserve inflated/mis-scaled by 1e18.
- **AAS — UNCLEAR.** Well data is set at boring by the deployer, not attacker-chosen; bites a misconfigured/0-decimal-defaulted well rather than via a permissionless attacker.
- **TSE — PASS.** Terminal: `calcRate` (consumed by the MultiFlowPump → oracle) returns a wrong rate for the affected well ⇒ mispriced swaps / manipulable oracle reading.
- **IDC — CANDIDATE_STRENGTHENED.** Invariant: rate reflects true reserve ratio. Delta: off by ~1e18 scaling on token1 ⇒ systematic mispricing; loser = LPs / oracle consumers.
- **CCIT — NO_EFFECT.**
- Selected mechanism: (a) token1 default-decimals mis-scale. **Completing op: STS/IDC.**

## L2 — `Stable2` silent non-convergence → **PARTIAL_CHAIN** · plausible mechanisms considered: **3**
Enumerated: (a) loop exhausts 255 iters → returns 0 (calcReserveAtRatio*) ⇒ consumer treats 0 as a real reserve;
(b) `calcLpTokenSupply` returns last unconverged iterate (not 0) ⇒ small pricing error; (c) harmless (stableswap
always converges for valid reserves).
- **STS — PASS.** Traced the loops: no terminal `revert` (unlike `calcReserve`); fall-through returns default/last value.
- **AAS — UNCLEAR.** Could an attacker craft reserves/ratios that fail to converge in 255 steps? Plausible at extreme ratios but not demonstrated blind.
- **TSE — CANDIDATE_STRENGTHENED.** Terminal: `calcReserveAtRatioSwap`/`Liquidity` return **0** on non-convergence → a pump/oracle consuming it could read a 0 reserve → severe mispricing.
- **IDC — NO_EFFECT.** No direct conserved-value delta without a concrete consumer.
- **CCIT — NO_EFFECT.**
- Selected mechanism: (a) silent-0 on non-convergence. **Completing op: TSE/STS (impact bounded by unproven trigger).**

## L3 — `WellUpgradeable.init`/upgrade → **NO_CHAIN (REFUTED)** · plausible mechanisms considered: **3**
Enumerated: (a) uninitialized implementation takeover (attacker calls `init` on `___self`); (b) `reinitializer(2)`
re-init of a bored well; (c) minimal-proxy UUPS upgrade-auth bypass.
- **STS — PASS.** `init` sets `__Ownable_init` (owner = caller). On the implementation, `address(this)==___self`.
- **AAS — UNCLEAR→refute.** Attacker calling `init` on the implementation becomes "owner" of the impl, but `_authorizeUpgrade` requires `address(this) != ___self` (must be delegatecall) → a direct impl call **cannot** `upgradeTo`/`upgradeToAndCall`; `proxiableUUID` is `notDelegatedOrIsMinimalProxy`. So impl ownership yields no upgrade/brick power.
- **TSE — PASS (benign).** Terminal state of an impl-takeover: no fund/upgrade authority gained.
- **IDC — NO_EFFECT.**
- **CCIT — NO_EFFECT.**
- Selected outcome: the routine **refutes** the standard UUPS-impl attack here (auth checks block it). Honest negative. **Completing op: AAS (refute).**

## Pre-reveal summary (frozen)
| locus | chain status | completing op | plausible mechs | blind sev |
|---|---|---|---|---|
| L1 decodeWellData | PARTIAL_CHAIN | STS/IDC | 2 | Med |
| L2 non-convergence | PARTIAL_CHAIN | TSE/STS | 3 | Low/Med |
| L3 WellUpgradeable init | REFUTED/NO_CHAIN | AAS(refute) | 3 | — |

0 COMPLETED, 2 PARTIAL, 1 REFUTED. **FREEZE** before key opened; hashes in basin_REVEAL_AND_SCORE.md.
