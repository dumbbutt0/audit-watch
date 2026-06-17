# P248 — Phase C: Funnel Quantification

The candidate-generation funnel for the 21 reasoning-bound misses (weighted denom 31). Each finding placed at
the stage it died (the first stage NOT reached). "Weighted at stage" = weighted lost at that transition.

```
Read Surface                 (21 findings / 31 wt entered — all in-scope code was read)
   │   loss: 1 finding / 1 wt   ← LOCAL_REASONING_STOP (read, never registered as suspicious)
   ▼
Observed Suspicious Area     (20 / 30 reached)
   │   loss: 10 findings / 12 wt  ← never birthed a candidate for the issue
   ▼
Generated Candidate          (10 / 18 reached)   [10 partial candidates born]
   │   loss: 10 findings / 19 wt  ← born but no exploit chain to the awarded impact (incl 4 of 5 Highs)
   ▼
Exploit Chain                (0 / 0 reached)
   │   loss: 0
   ▼
Validated Finding            (0 / 0)
```

## Weighted loss per transition
| Transition | findings lost | weighted lost | % of 31 wt |
|---|---|---|---|
| Read Surface → Observed-Suspicious | 1 | 1 | 3% |
| Observed-Suspicious → Generated-Candidate | 10 | 12 | 39% |
| **Generated-Candidate → Exploit-Chain** | **10** | **19** | **61%** |
| Exploit-Chain → Validated | 0 | 0 | 0% |

## Which funnel stage loses the most weighted recall?
**Generated-Candidate → Exploit-Chain (19 weighted, 61%)** — the largest single leak, and it holds 4 of the
5 reasoning Highs. The system observes the area and births a *related* candidate, then fails to construct the
exploit chain to the awarded impact (wrong-`from` trace, reserve-shortfall branch, whitelist principal,
unlock-time adversary, rounding direction, shared-escrow contention, …).

The **second leak is Observed → Generated-Candidate (12 weighted, 39%)** — the area is read but no candidate
is born at all (LZ-gas semantics, Stargate caching, fee-gate entrypoint, variable-fee economics, vote dual-
state, expiry logic, permit scope, missing harvest).

## Refinement of the P247 headline
P247 said "20/21 never proposed a candidate." Phase A/B sharpen this: ~half (10, 12 wt) truly never birthed
a candidate (a *birth* failure); the other half (10, 19 wt, most of the High weight) DID birth a related
candidate but it died **building the chain** (a *completion* failure). Both leaks are large; the
completion-stage leak is bigger by weight and carries the High recall.

## Implication for interventions (handoff to Phase D/E)
- A birth-only checkpoint (e.g., "did you enumerate entrypoints / check rounding?") attacks the 12-wt
  Observed→Candidate leak.
- A completion checkpoint ("for this born candidate, construct the full attacker→impact chain") attacks the
  19-wt Candidate→Chain leak — where the Highs are.
- The 4 operation checkpoints (accounting/permission/cross-contract/state-transition) each act at BOTH stages
  for their cluster: the operation that births the candidate is the same operation that completes the chain
  (e.g., a cross-contract trace both *notices* decent H-02 and *completes* decent H-03). So Phase D scores
  each checkpoint over its whole operation cluster, regardless of which stage that finding died at.
