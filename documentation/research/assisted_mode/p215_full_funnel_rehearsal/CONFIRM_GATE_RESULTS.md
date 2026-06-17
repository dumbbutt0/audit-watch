# P215 — CONFIRM GATE RESULTS

Real chain: `confirm_inventory.py` → `confirm_reachability.py` → `confirm_gate.py` (both modes) + `min_confirm_gate.py`.

## min_confirm_gate (field-presence skeleton)
`output/min_confirm_gate.json`: **PASS** — candidates 7 (submit 2 + poc_required 5), confirmed 7, blocking 0. Every
submission-track candidate carries attacker_entrypoint / preconditions / expected_impact / guards / smallest_poc /
severity_ceiling / confidence / manifest_refs.

## confirm_inventory
12 candidates inventoried (12 merged + 0 eval); 0 with missing confirmation fields.

## confirm_reachability (deterministic classifier)
`by_status: {uncertain: 9, likely_reachable: 3}` · `by_action: {needs_manual_review: 8, keep: 3, needs_runtime_poc: 1}`.

## confirm_gate
| mode | result | candidates | blocking | warnings | exit |
|------|--------|-----------|----------|----------|------|
| eval (advisory) | PASS | 12 | 0 | 9 | 0 |
| submission (hard-fail High/Crit non-credible) | PASS | 12 | 0 | 9 | 0 |

## Honest observation (→ FUNNEL_EFFECTIVENESS)
`confirm_gate --mode submission` did **not** hard-fail the privileged TSS-gated Highs (ZETA-03/05/08), because the
deterministic reachability classifier labelled them `uncertain` (a WARN status) rather than `privileged_only` (a FAIL
status). The classifier is heuristic and does not model TSS/FUNGIBLE_MODULE gating. **The privileged calibration is
therefore enforced one layer later, at L3 readiness** (where attacker_model=privileged blocks High). This is a
defensible division of labour (confirm_gate = reachability credibility; L3 = realized-impact + privilege), but it means
confirm_gate alone is not sufficient to demote privileged Highs — worth noting for the real hunt.
