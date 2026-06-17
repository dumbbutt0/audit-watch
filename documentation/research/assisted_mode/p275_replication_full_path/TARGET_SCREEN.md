# P275 — TARGET_SCREEN (content-safe; existence not content; BLIND)

Replication test: a **second** fresh diverse scored EVM target after the P274 gondi validation. Findings-repo
availability checked by `git ls-remote` (refs only). **No** finding titles / bodies / report tables / severity /
awards opened.

## Decision: **SELECT `code-423n4/2024-10-ronin` — Katana V3**
| criterion | status |
|---|---|
| EVM / Solidity | yes (solc 0.7.6/0.8.x Uniswap-V3-fork; foundry; OZ + forge-std + solidity-lib) |
| **class diversity (the point)** | **rich, different architecture from gondi lending** — concentrated-liquidity **share/math** (KatanaV3Pool) · swap routing + slippage = **order/route validation** (AggregateRouter/V3SwapRouter/Quoter) · **access control** (KatanaGovernance/AuthorizationLib) · pool/position lifecycle + V2→V3 migration = **state machine** (NonfungiblePositionManager/V3Migrator) · fee/treasury = **accounting/fund-management** · **DoS** (pool creation/routing) · **upgrade** (beacon/proxy) |
| answer key retrievable | **PUBLIC** (`2024-10-ronin-findings` exists) |
| in this repo / prior phases? | **NO** — clean: memory/history = 0; only 2 incidental hits = P274 screen note + `kb/chainlist_cache.json` (the chain, not findings) |
| used in P260–P274 scoring/backtest? | **NO** |
| source layout | git submodules (`katana-v3-contracts` @ `03c8017`, `katana-operation-contracts` @ `27f9d28`); fetched with `--recurse-submodules`; 343 in-scope manifest items |
| PoC feasibility | moderate — concentrated-liquidity math is heavy, but per-subsystem **import-closure trimming** (P274 technique) makes single-subsystem PoCs feasible |

## Why ronin (corpus saturation is the constraint)
The in-repo corpus is contamination-saturated. Screened and **rejected for prior exposure** (in P1xx eval corpora /
KB / P260–P274): dittoeth, panoptic, renzo, fenix, kleidi, vultisig, reserve, traitforge, wildcat, salty, dyad,
astaria, basin, loopfi, munchables, decent. **Rejected — Stylus / exposed:** superposition (P263/P268). **Clean
alternative considered:** krystal-defi (2024-06) — clean + retrievable but narrower subsystem spread (weaker
cross-class test). Ronin chosen for diversity + a *different* architecture from gondi.

## Confounds (disclosed)
Training-confound: 2024-10, pre-cutoff, public ⇒ awards may be in training. Mitigated (not eliminated) by doing all
selection/coverage/triage/completion BLIND and freezing+hashing before opening the key. Contest rule recorded:
KatanaGovernance bugs not affecting funds are downgraded one severity level (does not bias blind routing).

## Pre-reveal forbidden (held)
No finding titles / bodies / report tables / severity / award summaries / award-bearing searches before Phase 10.
Leak ⇒ mark contaminated, exclude, verdict H.
