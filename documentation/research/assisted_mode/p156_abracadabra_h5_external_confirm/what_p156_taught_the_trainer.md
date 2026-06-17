# P156 — What this taught the trainer

## The last-mile blockers after `reportable_candidate_needs_human_review`
Reaching a reportable candidate (P154) was not the end — two last-mile blockers remained, and P156 shows
they are **different in kind** from the mechanism/reachability work:
- **Novelty** needed an *external* check (the local record was empty but the contest is public). External
  search resolved it to `public_known_but_not_duplicate`.
- **Operator scope / severity** needed an *external operational* fact ("locks released by a Gelato task")
  that is invisible in source. It downgraded severity Medium → Low-bounded.

## Which was the real bottleneck?
**Operator scope, not novelty.** No public duplicate existed, so novelty did not kill it. The binding
constraint was the *automated-keeper liveness* model, which both bounds severity (Low) and makes the
final call a program-policy question. The mechanism was real; its *worth* was gated by an operational
trust assumption.

## Should Option-A selection pre-check operator/keeper liveness earlier?
**Yes.** Had P154 selection flagged "the only remediation path is an `onlyOperators`/keeper function" up
front, the eventual Low-bounded ceiling would have been predictable before building the PoC. Recommend
adding a selection-time pre-check: *"Is the fix/remediation path user-callable, or does it depend on a
trusted/automated operator?"*

## Selection penalty vs severity-bound field?
**Severity-bound field, not a hard selection penalty.** Trusted-operator/keeper dependence should be
*captured* (it predicts a Low/Medium ceiling) but not *exclude* a candidate — the H5 path is still a real,
unprivileged, zero-sum loss worth surfacing for human review. Making it a hard penalty would suppress
legitimate keeper-liveness findings. So: record `remediation_is_operator_or_keeper_gated: true` as a
severity/ceiling signal during selection, and let the human decide scope.

## Discipline preserved
Severity was **downgraded** on new evidence (anti-over-promotion), novelty was held to exactly what the
search supports (`public_known_but_not_duplicate`, not "novel"), and `submission_ready` stayed false. P156
made the candidate *more precisely bounded*, not *more confident*.
