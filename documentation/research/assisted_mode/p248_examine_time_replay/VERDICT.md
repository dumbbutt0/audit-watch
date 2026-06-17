# P248 — Verdict

## Funnel finding (where candidates disappear)
Two comparable leaks, both large:
- **Generated-Candidate → Exploit-Chain: 19 wt (61%)** — candidate born, chain to the awarded impact not
  built; holds 4 of 5 reasoning Highs. Largest single leak.
- **Observed-Suspicious → Generated-Candidate: 12 wt (39%)** — area read, no candidate born.
The single largest *proximate death class* is NO_EXPLOIT_CHAIN_CONSTRUCTION (10 findings / 19 wt). The four
operation checkpoints each act at both leaks for their cluster (the operation that births the candidate also
completes its chain).

## Verdict (exactly one)

# A — ACCOUNTING_FIRST

**Highest risk-adjusted ROI for the first build.** Accounting has the top ROI ratio (2.80), the lowest
implementation complexity (LOW), and the tightest FP profile (its checks — rounding direction, value
conservation, no double-count across calls, exact index/length, pre-decrement of shared balances — are
mechanical rules, not speculative arguments). It recovers ~2.8 weighted (5 Mediums: kleidi M-02, centrifuge
M-05/M-07, munchables M-03/M-04). As a *first* insertion point it does the most important job: it validates
the examine-time-checkpoint architecture at minimal risk and near-zero FP before any MED-cost checkpoint is
attempted.

### Why A over D / B / C / E
- **Not D (state-machine):** highest *absolute* recovery (~4.5, 2 Highs) and a strong second build, but ~2×
  the complexity and marginally higher FP risk (adversarial state exploration can spawn speculative
  candidates). It is the right *second* move, not the lowest-risk *first* move. (At gross, its ROI ties
  accounting within noise — so the determinism/FP tie-breaker decides for accounting.)
- **Not B (permission):** equally cheap and the most FP-tight, and it recovers a High (vultisig H-02) — a
  legitimate *co-first* if High-recall is prioritized — but its absolute recovery is the smallest (~2.1).
- **Not C (cross-contract):** highest weight but lowest ROI (1.50, MED-HIGH cost, hardest to make reliable on
  cross-chain semantics) — last of the four.
- **Not E (combination):** a single point cleanly leads risk-adjusted ROI; no combination is *required* to
  start. (The full sequence accounting → state-transition → permission → cross-contract is the build order,
  but the *first* checkpoint is singular.)

### Honest qualifier
- Accounting recovers **Mediums only**; the reasoning **Highs live in state-transition + cross-contract**, so
  competitiveness gains require the second build (state-transition). A is the *lowest-risk, highest-ROI start*,
  not the largest single recovery.
- The #1-ROI margin over state-transition is realization-sensitive (ties at gross); accounting wins on
  determinism/FP, which is the correct tie-breaker for a first build.
- All recovery figures are estimates with the standing training-confound caveat; the first build should be
  followed by a **forward blind run** to measure real lift before committing to the rest of the sequence.

## Success condition met
Nothing was built. The single highest-ROI insertion point for the first checkpoint is identified:
**ACCOUNTING** (with state-transition as the highest-absolute-recovery second). Implementation remains a
separate, explicitly-approved phase.
