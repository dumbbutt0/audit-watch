# P103 — Selection-layer recall repair

**Date:** 2026-06-03 · **Verdict: ✅ PASS.** Full public/external function inventory now drives autonomous
enumeration (fixing the P102 selection bottleneck) while **every precision gate is unchanged** — recall expands,
promotions do not.

## Context
P102's honest finding: the per-function invariant *enumerator* worked, but *selection* nearly dropped
`LiquidityManager.moveLiquidity` (the M-01 locus). P103 makes coverage independent of the lens: enumeration runs
over **all in-scope public/external functions**.

## What was built (additive, un-wired)
- `scripts/assisted/inventory_public_external_functions.py` — inventories every function (contract · visibility ·
  mutability · file · source_span · is_constructor); public/external = the enumeration surface; constructors a
  separate category; internal/private skipped.
- `auto_validate_invariants.run_subject(src, lens_leads, evidence_by_fn)` — inventory → enumerate every
  public/external function → **same** chain (defense map → frozen `validate_candidate_invariant` incl. severity
  `193abf9f`) → rank. Eight separated buckets: `lens_surfaced_functions`, `full_inventory_functions`,
  `enumerated_functions`, `skipped_functions`, `constructor_candidates`, `generated_invariants`,
  `validated_candidates`, `human_actionable_candidates`.

## Coverage — before vs after (IQ-AI, `/tmp/p102-inscope`)
| | Before (P102 selection) | After (P103 inventory) |
|---|---|---|
| functions enumerated | a hand-picked subset (initially missed `moveLiquidity`) | **55 public/external** (all) |
| inventory-only functions added | — | **17** |
| invariants generated | 224 | **444** |
| constructors | mixed risk of pollution | **7 isolated** in `constructor_candidates` |
| `moveLiquidity` covered | only after manual force-include | **yes, via inventory** (lens-independent) |
| runtime | — | **~21 ms** (negligible) |

## P102 replay (lens-independent) — `p103/replay_scores.json`
Run with `lens_leads=[]` so coverage comes **only** from the inventory, supplying the SAME M-01 evidence as P102
(no new tuning):
- `moveLiquidity` ∈ `enumerated_functions` **via inventory** ✓.
- **M-01** (`moveLiquidity` ordering_race) is the **#1 / only** human-actionable candidate → `NEEDS_EXECUTION` ✓.
- counts: generated **444**, validated_for_poc **0**, human_actionable **1**, **false_promotions 0**.
- **H-01** (TokenGovernor quorum) appears in `constructor_candidates`, not counted as a normal function-invariant
  miss (it's a constructor magic-constant).

## Precision regression (full inventory, NO evidence) — `p103/precision_regression.json`
`generated = 444`, `validated_for_poc = 0`, `human_actionable = 0`, `false_promotions = 0`,
`hypothesis_only_to_poc_handoff = 0`. → Full inventory expands **recall only**; with no source-backed evidence,
nothing is promoted. **False-positive delta: 0.**

## Validation outcomes for inventory-only functions
Inventory-only functions **generate** invariants (recall) but, without supplied trace evidence, **stall at
`NEEDS_CONTEXT`** — they cannot reach `VALIDATED`/PoC-handoff. Proven by tests
(`test_run_subject_no_evidence_no_promotion`, `test_run_subject_evidence_validates_via_same_gates`): only an
evidenced candidate validates, via the same gates; constructors never enter human-actionable ranking.

## Verification
- `inventory_public_external_functions --self-test` OK; `auto_validate_invariants --self-test` OK.
- `tests/assisted` → **67 passed** (incl. inventory + run_subject precision tests).
- Frozen byte-identical (`193abf9f`/`86f944e5`/`5a5aa996`/`b9e18f29`/`9c2c89cb`); P101/P102 artifacts + funnel
  records unchanged; no-wiring CLEAN; no SUBMITTED anywhere.

## Pass criteria — all met
All public/external functions inventoried (55) ✓ · enumeration covers inventory-only functions (17) ✓ · P102
replay keeps M-01 surfaced without relying on lens ✓ · no false promotion introduced (0) ✓ · no frozen file
modified ✓ · no severity/threshold gate weakened ✓ · tests pass ✓.

## Honest notes
- One additive fix carried from P102: the enumerator reads `source_text`; plus `_validate_one`'s
  affected-actor guard now fires only for **bare** hypotheses (no trace) — evidenced candidates aren't penalized;
  bare-hypothesis precision is unchanged. Both are backward-compatible (all P101/P102 tests green).
- The deeper ceiling is unchanged: reaching `VALIDATED`/confirmed still needs source-backed per-candidate trace
  (the capability-bound step). P103 only fixes **coverage/recall**, as intended.
