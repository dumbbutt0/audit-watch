# Maximal-Consequence Impact Prompt (P90-C)

Apply this **before assigning a severity label** to any promoted finding, during the deep pass / adversarial
review. It targets the recurring under-rating miss (P87 H-01, P89 H-05 rated Medium vs awarded High), the
admin-footgun misclassification (P87 H-03), and the self-inflicted-vs-involuntary misread (P87 M-18, P85 M-01).

> **Reject-first:** escalation to High requires **source-backed** evidence. A bounded/lazy/accounting issue
> with no concrete consequence is **never** escalated — it defers to the severity gate's bounded-demote. This
> prompt only adds markers the existing gate (`193abf9f`) already consumes; it changes no machinery.

## Step 1 — Test the MAXIMAL plausible consequence (not the first one you see)
Before writing "Medium", ask — and answer with a source line:
1. Can this affect **many or all users**, not just the actor?
2. Does it brick a **core protocol function / lifecycle phase / generation**?
3. Is the bad state **permanent / unrecoverable** without privileged intervention, migration, or upgrade?
4. Can it cause **mass DoS or permanent state corruption**?
5. Are **funds / rewards / rights permanently inaccessible**?

If **any** is YES **and source-backed** → recommend **High** and attach the matching gate marker(s):
`many_or_all_users_affected`, `core_protocol_lifecycle_function`,
`unrecoverable_without_privileged_intervention`, `bricks_major_phase_or_generation`,
`funds_or_rewards_permanently_inaccessible`, `requires_migration_or_upgrade`.
(These are the gate's `high_liveness_markers` — attaching them lets the unchanged P88 gate report `high`.)

## Step 2 — Admin footgun vs externally-consequential user harm
- ONLY a privileged admin action, no external trigger, trivially reversible, no user funds at risk in the
  interim → **admin footgun** (do not promote as user harm).
- A **normal/plausible admin action** that produces a **user-facing consequence** (mis-distributed fees,
  blocked path, lost funds — e.g. P87 H-03 `taxCut` change mis-distributing every fee flow) → **NOT a mere
  footgun**; assess on the consequence (≥ Medium).

## Step 3 — Self-inflicted vs involuntary
Do **not** demote as "self-inflicted" when the harmed party is hit by another user's tx ordering, a race, a
third-party listing/mint/forge action, global state mutation by someone else, a stale flag/counter changed by
another, or unavoidable sequencing (e.g. P87 M-18 fee-reduction race; P85 M-01 protocol tax loss). Attach an
`involuntary` marker. A finding may stay Low/demoted only if the harmed actor voluntarily caused it, it is
avoidable with no race, there is no material loss, or it is pure UI/config/admin inconvenience.

## Step 4 — Hand off to the gate
Attach the recommended `impact_class` + markers to the `impact_assessment` and run the **unchanged**
`severity_impact_gate`. The check (`scripts/investigation/maximal_consequence_check.py`, `assess(...)`) returns
`{recommended_impact_class, escalate, attach_high_markers, attach_involuntary, footgun_flag, reason}` to
mechanize Steps 1–3. It never demotes, never sets production severity, and never escalates without source
backing.

## Worked regression targets
| Case | Before | With this prompt |
|---|---|---|
| P89 H-05 (public helpers, all+upcoming holders, permanent corruption) | Medium | escalate **High** (+ markers) |
| P87 H-01 (`mintWithBudget` global-counter brick, core mint, all users) | Medium | escalate **High** |
| P87 H-03 (`taxCut` wrong-%) | rejected "admin footgun" | NOT a footgun → ≥ Medium |
| P87 M-18 (involuntary fee-reduction race → stuck) | demoted "self-inflicted" | keep + `involuntary` |
| updateTaxRate (bounded, misrouted_funds only, no source) | — | **no escalation** (gate still demotes) |
