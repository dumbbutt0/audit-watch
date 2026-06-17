# P246 — Contest Selection

## Selection constraints (all satisfied)
- Local **sealed answer key** present (chosen for max freeze-before-reveal integrity, fully offline).
- **Not** used for candidate generation in a prior recall benchmark; **not** P235 reNFT, P240 PoolTogether,
  or the P241 set (kelp/nextgen/dittoeth/predy/fenix).
- Fully readable at full coverage (P245 enforces READ_FULL) — depth over breadth (operator decision).
- Diverse architectures.

## The 6 contests
| Contest | LOC | in-scope / critical | Architecture | Key |
|---|---|---|---|---|
| decent-2024-01-holdout | 1.4k | 72 / 52 | cross-chain / NFT bridge (LayerZero UTB/UTBExecutor) | sealed |
| vultisig-2024-06-holdout | 2.4k | 69 / 47 | multisig token / vesting / whitelist (governance) | sealed |
| kleidi-2024-10-holdout | 3.3k | 132 / 64 | Gnosis-Safe module/guard + timelock (governance) | sealed |
| centrifuge-2023-09-holdout | 4.4k | 448 / 329 | RWA / cross-chain liquidity pools / vault | sealed |
| munchables-2024-05-holdout | 6.8k | 322 / 224 | GameFi / NFT / staking (L2/Blast) | sealed |
| badger-2024-06-holdout | 21k | 1313 / 722 | lending / CDP / vault (eBTC) — LARGE | sealed |

Architecture spread: cross-chain, NFT, governance/Safe, RWA/vault, GameFi/staking, lending/CDP. Size spread:
3 small (≤3.3k), 2 medium (4.4–6.8k), 1 large (21k).

## Caveats (honesty)
- **P239 lens-replay caveat:** kleidi, vultisig, badger, munchables were run through the P237/P238 advisory
  lenses in P239 (precision campaign) and returned ~0 candidates. Their **answer keys were never revealed**
  in P239, and no base candidate-generation hunt was done. So this P246 base hunt is genuinely blind for
  recall; the advisory layer is part of the frozen system being measured anyway.
- **badger size:** 722 critical items / 21k LOC. Under P245's full-read enforcement a complete read may be
  infeasible in one pass; the honest outcome is that the gate marks it coverage-incomplete (triage blocked).
  Recorded as a Coverage-bound outcome, not forced/inflated — it is the deliberate "large contest under the
  gate" datapoint.
- **Proof conversion:** expected ~0 across the set (BLOCKED_BY_BUILD — fresh workspaces ship no vendored
  foundry deps), consistent with P228/P241. Recorded, not fixed.

## Why local-sealed-only narrows architecture diversity
Pure AMM / perps / ve-tokenomics / EIP4626 contests in the corpus lack local sealed keys; including them
would require web key fetch (declined for integrity). The selected 6 still span 6 distinct architectures.
