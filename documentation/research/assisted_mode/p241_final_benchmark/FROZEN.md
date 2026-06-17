# P241 — Campaign FREEZE MARKER (anti-hindsight gate)

**FROZEN_AT:** 2026-06-08, before any answer key opened. Frozen-system measurement (no detector/lens/prompt/routing/
severity edits). Both lenses research-advisory (routing_allowed:false).

## Frozen content hashes (per-contest candidates + lens outputs)
| Artifact | sha256 |
|---|---|
| kelp candidates.md | `76a57f5133444d64b152a6952e8d295a83278d84201473693462ba8c867b8490` |
| kelp safe / hostile | `26552e38…` / `52b038f4…` |
| nextgen candidates.md | `db333a33296c655bffd8e617618562d8a7e6c74af41a297a1d60b7bb27fac258` |
| nextgen safe / hostile | `d3db2153…` / `02536115…` |
| dittoeth candidates.md | `1339b1e10d97abba4eb85050f912794550b8df0591f5e5b82455272808d7f9d1` |
| dittoeth safe / hostile | `84ebea2b…` / `35be526e…` |
| predy candidates.md | `df8426b09b8947109a2b484fc07e49e264246532b3cbfe9a791f86f49a6dcbb8` |
| predy safe / hostile | `1e65a436…` / `49075a5c…` |
| fenix candidates.md | `329dfcdf2e4b088bdee98e7fc4631963eed1e1ab889c248979ddf2f96f2aec10` |
| fenix safe / hostile | `d2a3a078…` / `c7277560…` |

## Sealed answer-key witnesses (re-verified = never opened during the hunt)
| Sealed | sha256 |
|---|---|
| predy `_sealed_answer_key/report.md` | `46460346198ef74c78a5381552554705991a5aa9f3407da48f775d621806f455` |
| nextgen `_src/bot-report.md` | `b6d372f6…` · `_src/4naly3er-report.md` `5b958119…` |
| fenix `_src/4naly3er-report.md` | `53b1c2f2…` |

## Advisory-lens summary (frozen)
| Contest | Safe lens | Hostile lens |
|---|---|---|
| kelp | 0 | 0 |
| nextgen | 0 | 0 |
| dittoeth | 0 | 0 |
| predy | 0 | **1 HIGH** (LiquidationLogic.liquidate) |
| fenix | 0 | 0 |
Total advisory candidates across 5 contests: **1** (predy hostile). Safe lens: 0/5 (no Safe guards present).

## Read-depth bounds (honesty — base recall is a LOWER BOUND where bounded)
- kelp: FULL (9 files / 46 fns read).
- nextgen: AuctionDemo full; MinterContract/NextGenCore (large) NOT read → bounded.
- dittoeth: LibOracle full; order/redemption/liquidation facets (large) NOT read → bounded.
- predy: LiquidationLogic partial + lens; trade/perp libs NOT read → bounded.
- fenix: minimal base read (lens-primary) → near-floor.

Harnesses: 0 attempted (all targets BLOCKED_BY_BUILD — no foundry deps shipped). Proof conversion = N/A (0/0).
FROZEN. Proceed to reveal.
