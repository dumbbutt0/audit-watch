# P277 — FP_REPORT

## Severe concluded/reportable FP: **0** (before and after)
The repair touches only the upstream coverage router; the strict late gate (exact mechanism + attacker path + delta +
victim/gainer + runtime + FP refutation) is untouched and never reached in this phase. Nothing is concluded/reported/
given severity. Advisory contract intact on every decision (severity null, all promotion flags false).

## Advisory-only candidate pressure: bounded, reduced
Advisory-only non-awarded survivors (triage-selected candidates matching no award) **dropped 39 → 35** with the body
repair at budget 5 — body's locus-gap-fill is more precise than name-token noise, so it did not increase PoC-queue
pressure; it slightly reduced it.

## Anti-drama held
A high-drama body ("oracle price manipulation drains all funds") with `impact_supported=false` is **deferred**, not
routed (regression-tested). Body signals cannot route an unsupported dramatic class.

## Award-text never used
Award-text fields (`award_title`/`title`/`root_cause`-as-award/etc.) are denylisted and never enter the signal path
(regression-tested). No contest/award literals in the router or config.
