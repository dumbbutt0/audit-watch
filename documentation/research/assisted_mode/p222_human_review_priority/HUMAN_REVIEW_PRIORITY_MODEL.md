# Human-review priority model (P222)

A **review-priority layer**, not a submission layer. It answers one question: *of the candidates that are
not auto-reportable, which ones must a human adjudicate first?* It never auto-submits, never routes, never
moves severity. `human_review_priority` and `submission_ready` are **independent axes** — a candidate can be
not-submission-ready, blocked from auto-High, **and** high-priority for human review at the same time.

## `human_review_priority` (display/prioritization only)
| value | meaning |
|-------|---------|
| `NONE` | nothing for a human to prioritize (default; refuted, no-impact, or already covered by another lane) |
| `LOW` | a real but minor residual (e.g. a code-quality fact left after an impact was refuted) |
| `MEDIUM` | L3-proven but needs a scope / program-rule / severity-policy decision before it can advance |
| `HIGH` | L3-proven core-safety/control impact, not auto-reportable only because a **program threat-model decision is required** (the trusted-system lane) |
| `CRITICAL_HUMAN_REVIEW` | reserved: HIGH lane **and** a direct fund-loss impact class — escalate immediately. No example in the current corpus; defined so a future finding can use it without inventing a value |

The dashboard surfaces `HIGH` (and `CRITICAL_HUMAN_REVIEW`) as **`HIGH_PRIORITY_HUMAN_REVIEW`** above
ordinary Medium/noise, below any genuinely reportable-ready candidate.

## `human_review_reason_codes` (one or more)
| code | when |
|------|------|
| `PROGRAM_THREAT_MODEL_DECISION_REQUIRED` | not auto-reportable purely because a program-specific threat-model call is needed (the canonical HIGH reason) |
| `TRUSTED_SYSTEM_ACTOR_REACHABLE` | the trigger is an authorized trusted-system actor (TSS / bridge executor / gateway / module) |
| `CORE_SAFETY_CONTROL_BYPASS` | the proven impact bypasses a core safety/control (e.g. emergency pause) |
| `L3_PASS_BUT_PRIVILEGED_TRIGGER` | L3 PASS, but the entry needs a privileged/trusted caller (blocks auto-High, not human priority) |
| `L3_PASS_BUT_SCOPE_DECISION_REQUIRED` | L3 PASS, but in/out-of-scope status depends on a boundary call |
| `NEEDS_PROGRAM_RULE_INTERPRETATION` | depends on an external/program rule not assertable from in-scope source |
| `NEEDS_DUPLICATE_OR_NOVELTY_CHECK` | a human must confirm it is not a duplicate / is novel |
| `NEEDS_SEVERITY_POLICY_DECISION` | severity floor (e.g. availability/DoS) is a policy call |
| `NEEDS_HARNESS` | mechanism plausible but not yet executed to L3 |
| `LOW_CONFIDENCE_NOISE` | weak signal / residual; de-prioritize |

## Hard invariants
- Setting any priority value **never** changes `submission_ready`, `routing_allowed`, `high_promotion_allowed`,
  `attacker_model`, or any severity field. Those remain machine-owned / L3-owned.
- `human_review_priority=HIGH` (or `CRITICAL_HUMAN_REVIEW`) **requires** `l3_status=PASS` and a qualifying
  `impact_type` + `reachability_class` (see `PRIORITY_RULES.md`). It can never arise from a static-only,
  refuted, self-inflicted, mock-created, or code-quality-only candidate.
- `should_surface_above_noise=true` iff priority ∈ {MEDIUM, HIGH, CRITICAL_HUMAN_REVIEW}; it is a sort hint,
  not a routing flag.
