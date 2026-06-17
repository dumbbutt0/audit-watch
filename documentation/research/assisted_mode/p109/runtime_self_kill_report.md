# P109 — Runtime self-kill: results

**Invariant:** Runtime self-kill exists to falsify exploit hypotheses; a surviving candidate is not a vulnerability — it is merely the next candidate worthy of deeper investigation.
  ·  research-only, un-wired.

## Verdict
- positive-control PASS: True · historical-safety PASS: True · no hard-stop: True
- runtime kills candidates: False · kill-rate exceeds source: False · **OVERALL PASS: False**
- CONTROL/SAFETY PASS · KILL-POWER HARNESS-GATED — the existing positive control (P104) is re-executed live and SURVIVES; no awarded finding is killed; all hard-stops hold. But runtime kill rate = 0 because the 28 candidates have NO per-candidate exploit harness (building one is P104-level effort each). The arc's terminus: discovery+ranking generalize and automate, but the final-mile confirm/kill is bound by EXECUTABLE-HARNESS CONSTRUCTION — human/engineering effort, not more automation. Spec pass criteria 1 & 4 are therefore NOT met, reported honestly.

## Metrics
- total candidates: 30  ·  by state: {'HARNESS_UNAVAILABLE': 28, 'SURVIVED_RUNTIME': 2, 'KILLED_RUNTIME': 0, 'INCONCLUSIVE_RUNTIME': 0}
- runtime_killed=0 survived=2 inconclusive=0 harness_unavailable=28
- runtime_kill_rate=0.0 (of executed=0.0) · survival_rate=0.0667 · source-only kill rate=0.0

## Positive controls (executed)

| Control | fn | state | execution-backed |
|---|---|---|---|
| iq-ai-2025-01 | moveLiquidity | SURVIVED_RUNTIME | True |
| secondswap-2024-12 | spotPurchase | SURVIVED_RUNTIME | True |

## Candidates (28 NEEDS_RUNTIME) — harness discovery

- all 28 resolve to HARNESS_UNAVAILABLE; reasons: {'no_exploit_harness': 27, 'ok': 1}

## Hard stops
- **HS1_positive_control_p104** — tripped: False
- **HS2_historical_safety** — tripped: False
- **HS3_execution_evidence** — tripped: False
- **HS4_no_promotion** — tripped: False

## Reading
- Runtime self-kill is the correct, SAFE final-mile mechanism: the live P104 control SURVIVES and no awarded finding is killed.
- It is GATED by executable-harness construction. The 28 candidates have no exploit harness; building one is the per-candidate effort P104 paid once. So runtime_kill_rate = 0 — not because runtime cannot kill, but because you cannot run what you cannot build.
- This closes the P104→P109 arc: high-recall, well-ranked, safe candidate-prep whose confirm/kill final mile is human/engineering-bound.

