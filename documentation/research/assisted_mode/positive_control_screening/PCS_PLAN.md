# PCS — plan (positive-control corpus screening)

## Goal
Find a fresh sealed corpus with **contract-level, Solidity-source-reachable, permissionless/attacker-controlled
High** findings (theft / insolvency / permanent-loss / unauthorized priv-transition) + enough Mediums, to serve as
a **positive control** for the next validation run — testing whether the refined severity gate *confirms* genuine
Highs (the axis P200/P201 never validated; P201 gave 0 HIGH_CONFIRMED / 0 matched contract-Highs). Screen
decent · munchables · vultisig; recommend one or return DATASET_TOO_THIN. **Not the oracle track.**

## Scope
Read-only / metadata + controlled title/summary-level unseal only. No production edits; no `deep_trace.md` patch;
no blind eval / gate application this phase.

## Firewall
The chosen corpus gets a future blind run where the orchestrator calibrates answer-key-blind, so the orchestrator
must not learn High mechanisms/loci now. Screening is delegated to **firewall subagents** (one per corpus) that read
sealed High titles+summaries + source file list and return **tallies only** (per-High level/source_reachable/actor/
impact tags + counts), never verbatim titles/loci. Orchestrator picks from tallies. (See `SCREENING_PROTOCOL.md`;
partial-leak outcome + mitigation in `integrity_checks.md`.)

## Sequence
Integrity precheck → screening protocol → run 3 firewall screening subagents → viability table → recommendation
(ACCEPT:<corpus> | DATASET_TOO_THIN) → integrity re-check + memory.

## Decision space
`ACCEPT:<corpus>` (≥2–3 qualifying contract-level source-reachable Highs + ≥~4 Mediums) · `DATASET_TOO_THIN`.

## Outcome
`ACCEPT: decent-2024-01-holdout` (4 qualifying contract-level Highs · 5 Mediums). See `PCS_RECOMMENDATION.md`.
