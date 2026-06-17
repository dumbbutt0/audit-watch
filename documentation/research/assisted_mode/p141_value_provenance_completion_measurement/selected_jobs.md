# P141 — Selected Jobs

| # | Arch | Job (advisory_id) | Source of completion | Label | Expected role |
|---|---|---|---|---|---|
| A1 | noya | `VP-SolvencyV2.convertAmountsToValues` | **fresh blind subagent** `aa6d4aac2a89ed1b9` (P141) | buggy? → clean | clean control (fresh) |
| A2 | noya | `VP-NoyaValueOracle._getValue` | P137 blind result (carried from P140) | buggy (loop var) | finding |
| B1 | blackhole | `VP-RewardsDistributor.claim_many` | P138 blind `a67fb918317d02d07` (B5) | buggy (wrong recipient) | finding |
| B2 | blackhole | `VP-RewardsDistributor.claim` | P138 blind `a8b0c3cd763de3d36` (C1) | clean HIGH | clean control |
| B3 | blackhole | `VP-RewardsDistributor.claimable` | P138 blind `af34d02a9bfb2d68a` (C3) | clean MEDIUM | clean control |
| C1 | size | `VP-SellCreditMarket.validateSellCreditMarket` | P138 blind `a281e3db7ab349438` (B4) | buggy (wrong basis) | needs_human |
| C2 | size | `VP-AccountingLibrary.debtTokenAmountToCollateralTokenAmount` | P138 blind `a403bf1955e6383ae` (C5) | clean MEDIUM | clean control |

## Queue provenance
- **Noya (A1/A2):** real P139-trigger jobs — `run_value_provenance_advisories.py` produced exactly these two from
  noya's `mechanism_advisory_context.json` (8 config-setter recs skipped).
- **Blackhole/Size (B*/C*):** created as **`queue_origin: eval_only_manual_queue`** — these audits have no
  `mechanism_advisory_context.json`, so the jobs were authored from the P138 neutral packets purely to exercise
  the completion loop on a second/third architecture. Clearly NOT a production P139 trigger.

## Why these
- Decision-type coverage in one pass: finding (A2, B1) · needs_human (C1) · strong_clear ×4 (A1, B2, B3, C2).
- Clean-control coverage: A1 (fresh), B2 (HIGH), B3 (MEDIUM), C2 (MEDIUM) → measures clean false-finding rate.
- Reuse-only except the one genuinely-required fresh run (A1, absent from the P138 corpus) — no corpus rebuild.
