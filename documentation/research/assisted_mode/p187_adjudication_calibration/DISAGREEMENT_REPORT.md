# P187 — Disagreement report: M-02 and M-06

Focused write-up of the two P186 model-dependent flips, the objective rubric verdict, and the recommended
resolution path. **Calibration only — nothing implemented in production this phase.**

## The full 9-case matrix (from `adjudication_matrix.json`)

| finding | sev | Opus view | Sonnet view | rubric outcome | settled by |
|---|---|---|---|---|---|
| H-07 | High | selected | selected | `SELECTED_VALID` | — |
| M-02 | Medium | carried/selected (P185) | **rejected** | **`REJECTED_INCORRECTLY` (non-responsive)** | differential (execution) |
| M-17 | Medium | carried (P185) | unresolved | `SELECTED_NEEDS_HARNESS` | static bound check |
| M-03 | Medium | selected | unresolved | `SELECTED_NEEDS_HARNESS` | harness |
| M-10 | Medium | selected (loose) | unresolved | `SELECTED_NEEDS_HARNESS` | harness |
| L-01 | Low | selected | selected | `SELECTED_VALID` | — |
| H-03 | High | selected (loose) | selected | `SELECTED_VALID` | — |
| M-06 | Medium | selected | **rejected** | **`REJECTED_INCORRECTLY` (severity-floor)** | static (severity scale) |
| L-02 | Low | selected | selected | `SELECTED_VALID` | — |

**Anti-overfit control holds:** none of the 6 stable selections (H-07, M-03, M-10, L-01, L-02, H-03) is rejected;
only the 2 genuine flips are `REJECTED_INCORRECTLY`. The three carried mechanisms (M-17, M-03, M-10) are
recall-preserving (`SELECTED_NEEDS_HARNESS`), never demoted to a rejection.

## M-02 — non-responsive rejection
- **Locus (alleged):** `UpliftOnlyExample.onAfterRemoveLiquidity` lines 241–243 —
  `lpTokenDepositValueChange = (int256(lpTokenDepositValueNow) - int256(lpTokenDepositValue)) / int256(lpTokenDepositValue)`.
  Integer division with no 1e18 scaling: for any pool-value increase below the deposit value, the ratio truncates
  toward zero, so the uplift-fee path is mis-set/bypassed. Awarded Medium "lpTokenDepositValueChange logic
  underflow in uplift fee calc."
- **Sonnet rejecting fact (verbatim, frozen):** *"feePerLP 1e18 units, feeAmount 1e18 units, mulDown cancels
  scale; floors favour LP (documented)."*
- **Why it is a mis-rejection:** the rejecting fact argues **unit consistency** of `feePerLP`/`feeAmount`/`mulDown`
  — a *different expression* (the fee multiply / admin `mulDown`) and a *different failure-mode family* (UNITS) than
  the alleged **value-direction/truncation** at `lpTokenDepositValueChange`. The rejecting fact **never names the
  alleged locus**. Rubric check #8: `locus_referenced=false` → non-responsive.
- **What settles it (objective, does not pick a model):** a **corrected-reference / differential** test —
  recompute `lpTokenDepositValueChange` with explicit 1e18 scaling and compare to the on-chain integer-division
  result on one concrete `(lpTokenDepositValueNow, lpTokenDepositValue)` input; assert the uplift fee differs
  (i.e. truncation is real and material). **Resolution path: execution required.**

## M-06 — severity-floor rejection
- **Locus (alleged):** `ChainlinkOracle._getData` line 201 `priceFeed.latestRoundData()` (no try/catch); a feed
  revert (or the `require(data>0)`) propagates through `_getOracleData` → `UpdateWeightRunner._getData` →
  `revert("No fresh oracle values available")` (line 157), locking all oracle access. Awarded **Medium** "unhandled
  Chainlink revert locks all price-oracle access."
- **Sonnet rejecting fact (verbatim, frozen):** *"revert propagates and reverts the weight-update; view function,
  no state mutation before/after — liveness/DoS not fund-loss; no inconsistent state (view)."*
- **Why it is a mis-rejection:** the characterization is *correct* (it is a DoS on a view path) — but the rejection
  rests on a **fund-loss / High** bar. Per the CLAUDE.md severity scale, **Medium = "Incorrect behaviour,
  significant griefing, DoS."** A total-oracle-lockout DoS **clears Medium**; "not fund-loss" only rebuts the High
  tier. Rubric check #7: `applies_too_high_severity_bar=true`.
- **What settles it:** **static** — the severity scale already places this class at Medium. No harness needed; the
  fix is calibration of the rejection bar, not new evidence. **Resolution path: severity-boundary (static).**

## Decision (per the spec's branch logic)
The two flips resolve by **different** mechanisms — report honestly as a **blend**, not one rule:

| flip | cause | resolution path | recommended future change (separately approved) |
|---|---|---|---|
| **M-06** | severity floor (#7) | **static / rubric-resolvable** | (a) deep-pass **checker** extension: a `severity_floor_misrejection` flag — fire when a rejected mechanism is a DoS/griefing class that clears Medium but the `rejecting_source_fact` invokes a fund-loss/High bar; (b) deep-pass **prompt** + **severity-calibration examples** so a DoS is adjudicated at its own tier, not the High bar. **No selector change.** |
| **M-02** | non-responsive (#8) | **execution required** | a **targeted harness-escalation rule**: when a rejection fails responsiveness (wrong locus / wrong family / unproven guard) on a value-direction claim, do **not** accept the rejection — route the mechanism to `SELECTED_NEEDS_HARNESS` and emit a minimal **differential / corrected-reference** test request. Also a checker extension: a `non_responsive_rejection` flag (rejecting fact does not reference the alleged locus token) extending the P185 `demoted_unresolved_mechanism` detector. |

Both are **recommendations for a later, human-approved phase.** This phase changes nothing in the production
pipeline.

## Honesty / limits
- The rubric was **designed against** M-02/M-06, so its success on them is partly by construction (see the
  anti-overfit note in `VALIDITY_RUBRIC.md`). The in-phase control is the 6 stable selections (none rejected,
  no patch); the **real** test is a future **blind apply on a different corpus / fresh disagreements**.
- n=9, one corpus, frozen single runs per model. **No recall claim.**
- The two checks are necessary signals, not a proof of bug-validity: a *responsive, proven, correctly-tiered*
  rejection still passes as `REJECTED_VALIDLY`. The rubric raises the bar on *rejections of real bugs*; it does not
  manufacture findings.
