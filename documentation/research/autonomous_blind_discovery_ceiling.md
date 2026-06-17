# The Autonomous Blind-Discovery Ceiling (honest assessment)

**Status:** RESEARCH-ONLY. Written 2026-06-03 after the P97 decision run. This document does not hide the P97
negative result and makes no claim of autonomous blind-discovery reliability.

## What the system proved (real, repeatable)
Across eight fresh sealed-key blind runs (P81e, P85, P87, P89, P91, P93, P95, P97) and the calibration phases
between them, these properties held:

- **0 severity false-positives after the gate** in every run — the severity calibration (P86 consequence
  tiering + P88 liveness/involuntary elevation, gate frozen `193abf9f`) is stable and trustworthy.
- **Clean privileged-control rejection** — controls were rejected in every run (P97: 3/3 designated + ~10 other
  onlyAdmin setters); 0 controls promoted incorrectly.
- **Reject-first discipline** — no fabricated passes; 0 SOURCE_FALSE, 0 unsupported-READY, 0 HARD_FAIL,
  0 detector→finding across the depth-equipped runs; well-formed abstains.
- **End-to-end handoff** — P81e→P82: a blind CLEAN_HIT (Vultisig H-01) converted to an **executable** Foundry
  PoC that fails on vulnerable source and passes under a minimal patch.
- **Genuine hits when the surface is reached** — P89 H-05, P87 H-01, P85 H-05, and P97 M-14 (referral fee) were
  real CLEAN_HITs; P97's was confirmed by an isolated key-blind adversarial review.
- **Advisory checks behave as specified** — depth-trace completion (P92/P94), maximal-consequence (P90), and
  adversarial-ordering (P96) all do exactly what they claim, with 0 false escalations.

## Where it failed
P97 (SecondSwap, 3H + 20M) produced **three completed-but-wrong false-rejects of true Highs** (H-01/H-02
`stepsClaimed` inheritance, H-03 `releaseRate`) plus a Medium (M-11), and one probable severity FP (F2). The
mechanisms were correctly **localized** and **traced** — but rejected against the wrong property. Four prior
depth-equipped runs (P91, P93, P95, Kleidi) had already produced 0 High conversions.

## Why wrong-invariant selection is the current boundary
P92/P94 proved a trace can be *done* but *wrong*. P96 added a forced adversarial-ordering enumeration — and P97
proved that enumeration can be *complete* but *aimed at the wrong invariant*: fed `relied_upon_invariant =
"token sum is conserved"` (which **is** preserved) with orderings that probe it, `adversarial_ordering_check`
correctly returned `REJECT_CONFIRMED`. The bug broke a **different** invariant (per-buyer claim-schedule
correctness). Every advisory gate validates the invariant it is **given**; none can supply the *right* one.

> The bottleneck is upstream of every gate: **selecting the correct invariant and discovering the breaking
> ordering** on hardened, well-engineered code. This is a reasoning-correctness limit, not a process,
> selection-policy, or calibration limit — and no gate added in P92–P96 moved it.

## Why the tool is repositioned
Because the failing step is exactly the one a competent human or a good static/fuzzing tool can supply, the
highest-leverage move is to **take the invariant as input** and apply the proven validation/handoff machinery to
it. See `assisted_mode_operating_model.md`.

## Use cases that remain strong
- Validating a human/tool-supplied invariant or hypothesis (triage → depth trace → adversarial ordering).
- Severity calibration and FP suppression (0-FP gate).
- Privileged-vs-permissionless classification and control rejection.
- PoC handoff scaffolding and submission-readiness packaging (reject-first, human-gated).
- Funnel/dashboard lifecycle tracking that never auto-submits.

## Claims no longer made
- **No claim** that Audit-Watch reliably *discovers* the correct invariant for subtle accounting/lifecycle Highs
  on hardened code, autonomously and blind.
- **No claim** that completing a trace or an ordering enumeration implies the conclusion is correct.
- Autonomous blind discovery is **paused**, not declared impossible; it would require a capability advance in
  invariant selection, not another advisory gate.
