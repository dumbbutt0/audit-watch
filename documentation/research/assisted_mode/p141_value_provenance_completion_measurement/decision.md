# P141 — Decision

## Decision: **MEASUREMENT_EXPANDS_LOOP**

The noya pending job was **completed honestly** (fresh blind subagent → `strong_clear`), and the completion loop
was **extended to two more architectures** (blackhole 3/3, size 2/2) via reused genuine P138 blind outputs — all
through the **unchanged P140 loop**. Across 3 architectures / 7 jobs: 7/7 completed, 0 rejected, 0 unmatched,
**0 clean false findings**, confirmed count 0 and Validated Findings unchanged everywhere, every result
advisory-only.

### Rubric
- **MEASUREMENT_EXPANDS_LOOP** ✅: noya pending resolved + ≥1 second-architecture job completed + rendering safe +
  **no clean false finding** (0/4).
- Not MEASUREMENT_PARTIAL: every selected job completed (noya 2/2, blackhole 3/3, size 2/2).
- Not PROMPT_COMPLETION_TOO_NOISY: all 4 clean controls cleared (incl. the fresh SolvencyV2 and the HIGH-confidence
  blackhole control); 0 false findings.
- Not BLOCKED_BY_CONTEXT: fair packets existed (noya queued packet + P138 neutral packets).
- Not REVERT_OR_DEFAULT_OFF: nothing prompt-derived can be mistaken for confirmed/submission-ready (findings
  tagged NOT confirmed, excluded from Validated Findings, gated behind human + PoC).

## Final response

**What this phase measured** — the completion loop end-to-end across noya/blackhole/size, with one fresh blind run
(SolvencyV2) and reused real P138 blind outputs; the decision distribution and advisory-only safety.

**Jobs selected** — noya: SolvencyV2 (fresh), NoyaValueOracle._getValue (carried); blackhole: claim_many, claim,
claimable; size: validateSellCreditMarket, debtTokenAmountToCollateralTokenAmount.

**Manual deep-pass results** — SolvencyV2 strong_clear (fresh `aa6d4aac2a89ed1b9`); the rest reused verbatim from
P137/P138 blind subagents; no fabrication.

**Ingestion results** — 7 queued / 7 accepted / 0 rejected / 0 unmatched / 7 completed / 0 pending after.

**Conversion scorecard** — finding 2 · likely_exploitable 0 · needs_human 1 · strong_clear 4 · error 0; clean
false findings 0/4; confirmed Δ 0; Validated Δ 0; render OK 3/3.

**Second-architecture result** — blackhole 3/3 (1 finding + 2 clean strong_clear), size 2/2 (1 needs_human + 1
clean strong_clear); identical advisory-only behavior to noya.

**Safety** — all 15 constraints met; 7/7 advisory-only; 0 runtime-confirmed; 0 unsafe promotions; state restored.

**Tests / integrity** — no production code changed → full suite identical at 1637 passed / 2 pre-existing
snapshot fails / 4 skipped; `bash -n` clean; self-test OK.

**Decision** — MEASUREMENT_EXPANDS_LOOP.

**Next recommended phase (P142)** — turn the loop into a standing eval instrument: a small reusable
`eval_only_manual_queue` harness (config-gated, research-only, un-wired) that seeds VP jobs from any audit's P138-
style packets + ingests reused/blind outputs, so cross-architecture finding/strong_clear/needs_human conversion
can be tracked over time; OR advance one P141 `finding` (NoyaValueOracle._getValue or RewardsDistributor.claim_many)
to a runtime PoC harness (Level-3) to convert one prompt-derived advisory into a runtime-confirmed result —
keeping prompt-derived and runtime-confirmed strictly separate.
