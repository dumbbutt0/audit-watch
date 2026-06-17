# P287 — TARGET_SCREEN

## Method
Candidate pool = local `audits/*-holdout` / `*-fresh` / `*-bench` EVM/Solidity targets with source + an already-built
`output/coverage_manifest.json`, minus the exclusion list. Screen is **content-light only**: external public-report
aggregate H/M count (require ≥1), source/build feasibility, prior-exposure check, and `submit_count`/`poc_count` (our
pipeline's own counts) = 0. **No issue titles/bodies/severity rows were read** — only the aggregate "High: X, Medium: Y"
count from the report summary.

## Exclusions applied
Gondi, Ronin/Katana, Wise, Init, Karak, Phi, BendDAO, Blackhole; the 13 eval-corpus audits (zaros, revert-lend,
panoptic, recall, ark, hybra, silo, swan, quantamm, noya, beanstalk) + size (active audit); any P260–P286 scoring target.

## Candidates considered (22 with source+manifest, not excluded)
abracadabra, badger, bakerfi, basin, centrifuge, decent, dittoeth, ecg, kelp, kleidi, looksrare, loopfi, munchables,
pooltogether, predy, renzo, salty, spectra, velodrome, vultisig, wildcat, zetachain. Higher prior-reference counts
(zetachain/vultisig/decent/munchables/pooltogether) were de-prioritized to keep exposure minimal.

## H/M-count screen (content-light, finalists)
| target | High | Medium | H/M total | manifest items | sol | decision |
|---|---|---|---|---|---|---|
| **kelp-2023-11-holdout** | 3 | 2 | **5** | 107 (86 fn) | 17 | **SELECTED** |
| spectra-2024-02-holdout | 0 | 2 | 2 | 585 | 48 | backup (smaller H/M, larger surface) |
Source: official Code4rena report summaries, aggregate count only (`code4rena.com/reports/2023-11-kelp`,
`.../2024-02-spectra`). No finding titles/bodies accessed.

## Selected: kelp-2023-11-holdout (Kelp DAO / rsETH LRT, Code4rena 2023-11)
Reasons: confirmed H/M ≥1 (5 awarded: 3H/2M — enough to measure recall) · small tractable surface (86 functions, 17 sol →
full chain + Tier-C PoC feasible) · low prior-reference count (13) · `submit_count=0`/`poc_count=0` (our pipeline never
ran/scored it) · no local answer key (sealed; external report not opened pre-reveal) · manifest file paths resolve.

## Rejected (reasons)
- All non-selected pool members: not chosen this run (single-target test). salty/badger/loopfi/abracadabra: large surface
  (1.3k–1.5k items) — heavier, deferred. spectra: viable backup, fewer awarded H (0H/2M). decent/zetachain/vultisig/
  munchables/pooltogether: higher prior-reference counts → exposure caution.
- No candidate had H/M count 0 among finalists; none rejected for unconfirmable count (both finalists confirmed).

## Attestations
- No issue titles/bodies/severity-table rows read; only aggregate H/M counts.
- Findings for kelp remain SEALED until pre-reveal artifacts are frozen (Phase 6).
- Target decision FROZEN: `kelp-2023-11-holdout`.
