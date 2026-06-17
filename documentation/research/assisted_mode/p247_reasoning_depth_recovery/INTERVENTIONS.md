# P247 — Phase D: Candidate Interventions (designed on paper; NOT implemented)

One smallest-possible GENERIC intervention per cluster (from the allowed set: mandatory reasoning
checkpoints · exploit-chain construction · defense-dismissal requirements · lifecycle tracing ·
cross-contract dependency mapping · economic actor modeling). Forbidden: contest-specific heuristics,
detector families, answer-key matching, architecture-specific rules. Estimates: weighted recovery / cost /
FP risk.

## Why the already-built P245 reroute does NOT close this (critical)
P245's reasoning-depth gate forces a *depth record before a candidate is REJECTED*. But Phase A shows **0
DEFENSE_MISUNDERSTOOD and 20/21 cases where the system never proposed a candidate at all** — it read the
code and moved on. P245 protects against shallow *rejection*; these are failures of **hypothesis
generation** at *examine-time*. The interventions below are therefore **examine-time reasoning checkpoints
applied to critical items as they are read**, producing candidates that then flow through the existing
precision gates (so FP stays ≈0). This is a different insertion point than P245.

## Interventions
| Cluster | Wt | Intervention (smallest generic) | Allowed type | Weighted recovery (est.) | Cost | FP risk |
|---|---|---|---|---|---|---|
| Cross-contract (9) | | **Cross-contract terminal-state trace:** for each value/identity/control leaving a function (external call, bridge, msg.sender, signature scope), require naming the counterparty and tracing to terminal state / failure branch before clearing. | cross-contract dependency mapping + exploit-chain construction | 4–5 of 9 | MED–HIGH (cross-chain semantics hard) | LOW (routes through precision gate) |
| State-machine (9) | | **Adversarial transition checklist:** for each state write on a critical item, answer who-else-can-trigger / can-repeat / ordering / the "else" branch. | mandatory reasoning checkpoint + lifecycle tracing | 5–6 of 9 | MED | LOW |
| Accounting (5) | | **Conservation+rounding+index check:** for each arithmetic/accounting expression, assert rounding direction, no double-count across calls, exact index/length, pre-decrement of shared balances. | mandatory reasoning checkpoint | 3–4 of 5 | LOW | LOW (deterministic-ish) |
| Permission (5) | | **Entrypoint principal map:** enumerate every public/external entrypoint; verify gated-principal == affected-principal; flag every on-behalf-of param. | cross-contract dependency mapping + reasoning checkpoint | 3–4 of 5 | LOW | LOW |
| Economic (2) | | **Actor + external-market model:** for any call reading an external price/fee or paying an actor, evaluate frontrunning + incentive compatibility (not just conservation). | economic actor modeling | 1 of 2 | MED | MED (speculative econ candidates) |

**Sequencing (highest ROI first):** Accounting + Permission (cheap, FP-tight, ~6–8 wt) → State-machine
(MED, carries High recall, ~5–6 wt) → Cross-contract (hardest, carries the most High wt, ~4–5 wt) →
Economic (lowest yield, highest FP risk — last).

## FP-safety design (the user's hard requirement)
- All interventions are **examine-time checkpoints that PRODUCE candidates**, not auto-submitters. Candidates
  flow through the existing pre-submission / confirm / min-confirm gates and (for sensitive areas) the P245
  depth-record reroute. So a forced reasoning step that yields a weak hypothesis is *gated*, not submitted →
  FP rate stays ≈0 (matching P246's 0-FP result).
- They are **generic reasoning prompts keyed to code structure** (state writes, external calls, arithmetic,
  entrypoints) — not contest patterns, not answer-key strings, not architecture rules → no overfitting.
- The Economic checkpoint carries the only real FP risk (speculative incentive arguments) → lowest priority,
  and must be the most tightly gated.

## Relationship to coverage (P245)
These are reasoning interventions for the *fully-read* regime. They do nothing for coverage-bound contests
(centrifuge unread layers, badger) — that remains P245's coverage gate's job. The two are complementary:
coverage gate gets the surface read; these checkpoints get the read surface reasoned to a complete chain.
