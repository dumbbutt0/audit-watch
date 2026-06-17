# P288 — TARGET_SCREEN

## Method
Same content-light protocol as P287. Candidate pool = local `*-holdout`/`*-fresh`/`*-bench` EVM/Solidity targets with
source + `output/coverage_manifest.json`, minus exclusions (incl. now **kelp**). Screen = external public-report
aggregate H/M count only (require ≥1, prefer ≥2), source/build feasibility, prior-exposure, `submit_count`/`poc_count`=0.
**No issue titles/bodies/severity rows read** — only "High: X, Medium: Y".

## Exclusions applied
Gondi, Ronin/Katana, Wise, Init, Karak, Phi, BendDAO, Blackhole, **Kelp (P287)**; the 13 eval-corpus audits + size
(active); any P260–P287 scoring/backtest target.

## H/M-count screen (content-light, finalists)
| target | High | Medium | H/M total | manifest fn items | sol | decision |
|---|---|---|---|---|---|---|
| **ecg-2023-12-holdout** (Ethereum Credit Guild) | 4 | 25 | **29** | 271 | 22 | **SELECTED** |
| spectra-2024-02-holdout | 0 | 2 | 2 | 585 | 48 | backup (no Highs) |
| dittoeth-2024-03 | — | — | (report fetch exceeded 10MB) | 711 | 62 | deferred (large report) |
Source: official Code4rena report summaries, aggregate count only
(`code4rena.com/reports/2023-12-ethereumcreditguild`). No finding titles/bodies accessed.

## Selected: ecg-2023-12-holdout (Ethereum Credit Guild, Code4rena 2023-12)
Reasons: H/M = 4H/25M (≥2 with Highs — stricter than P287's brittleness bar) · **distinct domain** from kelp
(lending/credit/gauges vs LRT/oracle) → tests generalization breadth · tractable (271 functions, 22 sol) · source +
manifest local (resolves; sample `src/core/Core.sol`) · no local answer key (sealed/external) · `submit_count=0`/
`poc_count=0` (pipeline never ran it) · low prior-reference count (15).

## Rejected / deferred
spectra (no Highs — kept as backup); dittoeth (report too large to fetch cleanly this run); large-surface targets
(salty/badger/loopfi/abracadabra, 1.3–1.5k items) deferred; higher-exposure targets (zetachain/vultisig/decent/
munchables/pooltogether) avoided. No finalist had H/M=0.

## Attestations
- No issue titles/bodies/severity-table rows read; only aggregate H/M counts.
- ECG findings remain SEALED until pre-reveal artifacts are frozen (Phase 6).
- Target decision FROZEN: `ecg-2023-12-holdout`.
