# P290 — TARGET_SCREEN

## Method
Content-light protocol (as P287/P288). Pool = local `*-holdout`/`*-fresh` EVM/Solidity targets with source + manifest,
minus exclusions (now incl. kelp + ECG). Screen = external public-report aggregate H/M count only (≥1, prefer ≥2),
source/build feasibility, prior-exposure, `submit_count`/`poc_count`=0, and loss/reward/staking surface plausibility from
contract filenames/scope only. **No issue titles/bodies/severity rows read.**

## H/M-count screen (content-light, finalists)
| target | High | Medium | H/M | fn items | sol | loss/reward surface | decision |
|---|---|---|---|---|---|---|---|
| **salty-2024-01-holdout** (Salty.IO) | 6 | 31 | **37** | 1213 | 129 | staking + rewards + DEX pools + emissions | **SELECTED** |
| renzo-2024-04-bench | 8 | 14 | 22 | 645 | 82 | LRT (≈kelp) | rejected (LRT domain ≈ kelp; `-bench` = prior-exposure risk) |
Source: official C4 report summaries, aggregate count only (`code4rena.com/reports/2024-01-salty`). No titles/bodies.

## Selected: salty-2024-01-holdout (Salty.IO, Code4rena 2024-01)
Reasons: H/M = 6H/31M (well above ≥2) · **ideal lens-fit domain** for the P289 loss/reward lenses (staking/rewards/DEX
pools/emissions — loss-on-stake, reward-index, share-transfer, contagion surfaces; contract tree shows pools/, staking,
Salt emissions) · `submit_count=0`/`poc_count=0` (pipeline never ran it) · source + manifest local (resolves;
`src/AccessManager.sol`) · no local answer key (sealed/external) · low prior-reference count (7) · distinct from kelp
(LRT) and ECG (credit guild). Large (1213 fns) but the pipeline bounds the validation queue (~8).

## Rejected / deferred
renzo (LRT ≈ kelp + `-bench` exposure); predy/bakerfi held as backups; eval-corpus + prior-scoring targets excluded.

## Attestations
- No issue titles/bodies/severity rows read; only the aggregate H/M count.
- salty findings remain SEALED until pre-reveal artifacts are frozen (Phase 6).
- Target decision FROZEN: `salty-2024-01-holdout`.
