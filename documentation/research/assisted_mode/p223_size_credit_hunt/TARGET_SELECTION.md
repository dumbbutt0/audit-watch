# P223 — Target selection (clean-reportable scorecard)

## Goal of the score
P215 proved the funnel routes safely, but on a target (ZetaChain) whose findings were mostly
Go/off-chain/TSS — outside the pipeline's Solidity+Foundry strength. P223 selects a **Solidity-heavy**
finished contest scored for **clean-reportable probability**, not architecture diversity.

## Criteria (user-stated bar)
≥5 Med/High Solidity findings · ≥2 permissionless/user-reachable · buildable deps · local harness feasibility ·
clear custody/accounting impact · NOT trusted-system-dominated · clean/blind answer key available in-repo.

## Shortlist (frozen Solidity corpora with answer keys)
| Target | Findings | Surface | Permissionless paths | Harness feasibility | Key in-repo | Verdict |
|--------|----------|---------|----------------------|---------------------|-------------|---------|
| **Size Credit 2024-06** | **4H / 12M** | lending/credit-market: liquidation math, fee/validation, multicall invariants | High (liquidation, deposit/withdraw, market orders are user-callable) | High (Foundry 0.8.23, self-contained libs) | Yes (frozen) | **WINNER** |
| Blackhole 2025-05 | 2H / 13M | ve(3,3) reward/gauge/genesis emission | Medium (some keeper/gauge-admin gated) | Medium | Yes | strong runner-up |
| Revert Lend 2024-03 | permit/delegation/multicall | NFT-LP lending; #1 for multicall research | Medium-High | High | **No** (needs C4 collection) | deferred (key setup cost) |

## Why Size Credit wins
- **Custody/accounting core**: a lending protocol where liquidation/accounting math errors map directly to
  fund-loss — the cleanest "permissionless reportable" shape for our L3 harness standard.
- **User-reachable entrypoints**: deposit, withdraw, buy/sell credit (limit+market), liquidate, self-liquidate,
  compensate, claim, repay — abundant EOA-callable surface (L1 entry is trivial to craft).
- **Not trusted-system-dominated**: admin is limited to config; the value-bearing paths are permissionless.
- **Buildable & harnessable**: single solc 0.8.23, Foundry, self-contained libraries → real-source L3 harness
  is feasible without a large dependency swamp.
- **Clean blind key**: 4H/12M frozen answer key already in-repo (sealed), enabling honest scoring.

Decision: **Size Credit 2024-06** for the P223 full key-blind funnel hunt.
