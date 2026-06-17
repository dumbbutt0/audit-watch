# P244 — Part F: Implementation Options (ranked; NOT implemented this phase)

Five packaging options for the deltas in `COVERAGE_REASONING_GATE_SPEC.md` (Δ-A1/A2/A3, Δ-B, Δ-C, Δ-D). Ranked by
**effectiveness · implementation cost · risk · operator burden**. *Nothing is implemented in P244* (Part F rule:
"Do not implement unless explicitly approved"). This document is the input to that future approve/build decision.

## Scoring legend
Effectiveness = expected realized weighted-recall recovery (from `P241_MISS_REPLAY.md`). Cost = engineering effort.
Risk = chance of breaking existing pipeline / new FPs. Burden = added operator work per audit.

| # | Option | Effectiveness | Cost | Risk | Operator burden |
|---|---|---|---|---|---|
| 3 | **Extend the existing CLI coverage gate** (Δ-A1 read_state + Δ-A2 critical-item READ_FULL rule in `coverage_completeness_gate.py`, behind a policy flag, honoring `AUDITWATCH_COVERAGE_OVERRIDE`) | **HIGH** (~31–39 wt — the whole coverage half) | LOW–MED (one field + one blocking rule + a critical-item predicate over existing manifest fields) | LOW (default-off flag; override exists; no schema break) | LOW–MED (must set read_state / justify blockers — but that data should exist) |
| 4 | **Candidate rejection depth-record** (Δ-C/Δ-D: extend `triage_write.py` no-silent-clear to sensitive areas; completeness predicate over existing `triage.schema.json`/`exploitability.schema.json` fields) | MED (~4–7 wt — the diffuse reasoning half; recall-protective) | MED (validation fn + sensitive-area classifier shared with #3) | LOW (only reroutes weak rejections to the *existing* human queue; never fabricates findings) | MED (sensitive-area rejections need a populated chain) |
| 2 | **Dashboard preflight checklist** (render coverage/critical-item/lifecycle status as a pre-triage panel) | MED (visibility only; relies on operator to act) | MED (dashboard work — and dashboard edits are review-gated per the hard constraints) | MED (touches dashboard behavior) | LOW |
| 1 | **Docs-only operator checklist** (write the Part A–D rules into `documentation/coverage_system.md` as a manual pre-triage checklist) | LOW–MED (no enforcement → relies entirely on discipline; this is the failure mode P241 already exhibited) | LOW | NONE | MED (all-manual) |
| 5 | **Fresh-audit prompt wrapper** (inject the lifecycle-matrix + reasoning-checklist asks into Step-0/Step-2 prompts) | MED (drives Δ-B/Δ-C behavior at source) but UNGATED | MED (and risks prompt rewrites — restricted by hard constraints; would need an explicitly reviewed process prompt) | MED (prompt drift; no hard stop) | LOW |

## Recommended minimal-delta combination
**Build #3 + #4 together; defer #1/#2/#5.**

- **#3 (coverage gate extension)** captures the dominant, mechanical 61%-of-misses coverage lever with the least new
  surface — it is a field plus a blocking rule on a gate that already hard-blocks the review gate and already has an
  override. This is the single highest-ROI delta and the spec's Δ-A1 + Δ-A2.
- **#4 (rejection depth-record)** captures the reasoning half as a *recall-protective reroute* by generalizing a
  pattern (`triage_write.py` no-silent-clear) that already ships — so it adds discipline without a new subsystem and
  cannot degrade precision (it only routes weak sensitive-area rejections to the human queue, never invents findings).
- **#3 and #4 share one sensitive-area / critical-item classifier**, so they are cheaper built together than apart.

**Defer:**
- **#1 docs-only** — no enforcement; P241 proves discipline-without-a-gate is exactly the failure. Keep as the *fallback*
  if the gate is judged too heavy (that is verdict B).
- **#2 dashboard preflight** — dashboard edits are review-gated by the hard constraints; visibility is nice-to-have once
  the gate exists, not the first build.
- **#5 prompt wrapper** — prompt rewrites are restricted; the lifecycle matrix (Δ-B) can be produced by the existing
  Step-0 substage machinery without a prompt rewrite. Revisit only if Δ-B needs a reviewed process prompt.

**Δ-A3 (first-class architectural `role` enum)** and **Δ-B (lifecycle matrix artifact)** are MED-priority refinements:
Δ-A2's tag-based critical-item predicate already works without Δ-A3, and Δ-B sharpens the reasoning half but isn't
required for the coverage win. Sequence: ship #3, then #4, then Δ-B, then Δ-A3 if reporting precision demands it.

## Guardrails for the future build (carried from the hard constraints)
- New gate rule **default-off** behind a policy flag until the validation run (`VALIDATION_PLAN.md`) confirms recall-up
  / time-bounded; `AUDITWATCH_COVERAGE_OVERRIDE` continues to apply.
- No severity-policy / routing / dashboard-behavior / detector / taxonomy changes; the forbidden files
  (`dashboard_sync.py`, `deep_trace.md`, `min_confirm_gate.py`, `confirm_gate.py`, `validate_p208_l3_readiness.py`)
  stay byte-identical — Δ-C *reads* `deep_trace.md`'s discipline but does not edit it.
- #4 must be **recall-protective only**: reroute weak rejections to the existing `human_review_queue.jsonl`, never
  auto-create or auto-submit a finding.
