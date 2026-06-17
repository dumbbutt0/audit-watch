# P215 — TARGET SELECTION

## Chosen target: `zetachain-2023-10-holdout`

| Attribute | Value |
|---|---|
| Contest | ZetaChain (Code4rena `2023-10-zetachain`) |
| Platform | Code4rena |
| Status | **Finished** (closed Oct 2023) |
| Workspace | `audits/zetachain-2023-10-holdout/` (already registered in `audits/registry.json`) |
| Source | 37 in-scope `.sol`; ~3411 LOC; EVM (custody/connector/consumer strategies) + ZEVM (ZRC20/SystemContract/WZETA/Uniswap) |
| Answer key | `_sealed_answer_key/` — own `.git`, `report.md` (401 KB), sealed; **14 High + 34 Medium** per prior recon |
| Solc | 0.8.7 (core); WZETA legacy ^0.4.18 |
| In L3 avoid-list? | **No** (avoid-list: sophon, vultisig, decent, munchables, quantamm, size, noya, blackhole) |
| Pre-staged blind upstream | `output/coverage_manifest.json` + 34 deep_pass bundles + `candidate_queue.json` (key-blind, source-derived) |

## Why suitable for a full-funnel rehearsal
1. **Finished + sealed answer key** → can score after freeze without live-submission risk.
2. **Rich High/Medium set (14H/34M)** → exercises both the L3 High gate *and* the DoS carve-out / under-rating path,
   and gives a real denominator for recall/precision scoring.
3. **Manageable size (~3411 LOC, 37 files)** → a bounded run (≤12 candidates / ≤5 deep traces / ≤3 harnesses) is
   tractable while still touching custody, cross-chain message validation, fee/gas accounting, and AMM-consumer
   slippage surfaces.
4. **Upstream already staged blind** → coverage manifest + deep_pass bundles exist (key-blind, source-derived), so the
   rehearsal can focus on the *funnel routing* (the P215 thesis) rather than re-deriving the denominator.
5. **Not contaminated** → sealed key has its own git and was never opened; `data/triage/` empty at START.

## Considered and rejected
- **predy-2024-05** — cleaner slate but larger (68 files / 7619 LOC) and only 4H/8M; heavier for one phase.
- **centrifuge-2023-09** — Medium-only (0 High → wouldn't exercise the L3 High gate); `pocs/` recently modified
  (possible contamination).
- Avoid-list targets — already used in the L3 validation loop; reuse would bias scoring.
