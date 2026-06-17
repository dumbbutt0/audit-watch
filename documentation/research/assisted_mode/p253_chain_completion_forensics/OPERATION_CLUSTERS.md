# P253 — Operation Clusters (is there a small recurring set?)

Clustering the 13 first-missing-steps (3 primary P252 + 10 corroborating P248). Hypothesis under test: a
**small recurring set (≤5 operations) explains ≥70–80%** of the completion failures, AND the operations recur
**across multiple contests/families** (scaffoldable, not contest-specific).

| Operation | count | % count | weighted | contests it appears in |
|---|---|---|---|---|
| STATE_TRANSITION_SIMULATION | 4 | 31% | 8 | salty, vultisig, munchables |
| ADVERSARIAL_ACTOR_SUBSTITUTION | 4 | 31% | 6 | salty, vultisig, centrifuge, munchables |
| TERMINAL_STATE_EVALUATION | 2 | 15% | 4 | decent, centrifuge |
| INVARIANT_DELTA_COMPUTATION | 2 | 15% | 2 | kleidi, centrifuge |
| CROSS_CALL_IDENTITY_TRACKING | 1 | 8% | 3 | decent |
| UNKNOWN | 0 | 0% | 0 | — |

## Small-recurring-set test
- **5 operations explain 13/13 = 100% by count and 23/23 = 100% by weighted.** (≤5 operations, ≥70/80% — PASS.)
- **Top 2 (STS + AAS) explain 8/13 = 62% count / 14/23 = 61% weighted.** Top 3 (+TSE) = 77% count / 78% weighted.
- **Cross-contest recurrence:** every operation except CCIT (1 instance) appears across ≥2 contests/families.
  STS and AAS each span 3–4 distinct protocols → genuinely reusable, not overfit to one architecture. CCIT
  (1×, decent cross-chain) is the thinnest — possibly folds into the cross-contract checkpoint's domain.

## Reading
- The completion failures are **NOT diffuse** — they collapse into a small, cross-contest set of reasoning
  operations. The user's hypothesis holds.
- The two dominant operations are **STATE_TRANSITION_SIMULATION** ("instantiate the relevant state — esp. the
  empty/first-actor/edge state — and step it") and **ADVERSARIAL_ACTOR_SUBSTITUTION** ("replace the assumed
  honest/average user with an attacker who chooses inputs / acts on-behalf / isn't the gated party"). Together
  they are ~61% of the lost weight and recover the salty Highs (H-02/H-04 via STS) and vultisig H-02 (AAS).
- Critically, these are exactly the steps the P249/P251 checkpoints' *questions* gestured at ("can an attacker
  choose it? can it be repeated? who is harmed?") but did NOT force the system to *perform* — confirming P252:
  the gap is performing the operation, not asking about it.

## What this implies for architecture
A fixed, ordered **completion procedure** that, for a born candidate, actually executes these operations
(substitute an adversary → instantiate the edge/first state → step the transitions → track identities across
calls → compute the invariant delta → evaluate the terminal state) is the shape the evidence points to — i.e.
a **scaffold**, not another observe-and-ask checkpoint. See SCAFFOLD_SKETCH.md (design only) and the VERDICT's
caveat that "the operation recurs" ≠ "a scaffold can perform it blind."
