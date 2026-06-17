# P222 — Sorting and filtering

## Sort (findings_overview.load_overview)
The single sort key becomes `(_effective_rank(row), glance_rank, track, subject)` (stable).
`_effective_rank` is **boost-only** — it never demotes a row below its natural pipeline rank:

```
base = glance_rank
if base <= 1:                       return base          # reportable-ready / ready-for-human-review stay on top
if priority in {HIGH, CRITICAL}:    return min(base, 1.5) # just below reportable-ready, above ordinary
if priority == MEDIUM:              return min(base, 4.5)
else:                               return base
```

Observed funnel ordering after backfill:

```
H-01                 glance=1  eff=1.0  NONE     <- reportable-ready (top)
ASSISTED-M11         glance=1  eff=1.0  NONE
ZETA-04              glance=2  eff=1.5  HIGH      <- boosted above ordinary, below reportable-ready
ZETA-11              glance=2  eff=2.0  MEDIUM    <- natural rank preserved (boost is min, not demote)
ZETA-07              glance=2  eff=2.0  NONE
… rank-6 ordinary noise …
ZETA-09 / ZETA-10    glance=6  eff=6.0  LOW       <- residual/refuted stay at the bottom
```

Acceptance: HIGH_PRIORITY_HUMAN_REVIEW (ZETA-04) appears above ordinary Medium/noise; reportable-ready stay
above it; refuted/source-false (LOW) stay below. ✅

## Filter (dashboard.py, read-only)
`GET /api/findings?human_review_priority=HIGH` and `GET /api/candidates?human_review_priority=HIGH` narrow the
returned rows to the requested priority (case-insensitive). Display-only; payloads keep
`routing_allowed:false` / `research_only:true`; no side effects, no POST. Verified: `HIGH` filter → `[ZETA-04]`.

## API fields
Every overview/funnel/candidate row now exposes `human_review_priority`, `human_review_reason_codes`,
`reachability_class`, `should_surface_above_noise`, so a UI (or a downstream consumer) can sort/filter without
re-deriving anything.
