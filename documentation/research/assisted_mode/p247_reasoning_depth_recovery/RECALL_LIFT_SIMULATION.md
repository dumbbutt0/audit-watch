# P247 — Phase E: Simulated Recall Lift

Estimated using P246 findings ONLY. Weights H=3/M=1; full P246 denom = 52 weighted. These are **estimates
with explicit uncertainty**, not measured results.

## Decomposition of the P246 denominator (52 weighted)
| Segment | weighted | currently credited | note |
|---|---|---|---|
| Direct/root hits (non-reasoning) | 13.5 | 13.5 | unchanged by reasoning fixes |
| **Reasoning-bound set (21 findings)** | **31** | **6.25** | the recoverable target of P247 |
| Coverage-bound misses (centrifuge unread + badger) | 7.5 | 0 | NOT recoverable by reasoning (P245's job) |
| **Total** | **52** | **19.75 (=38.0%)** | strict credited 13 (=25.0%) |

Reasoning-recoverable headroom = 31 − 6.25 = **24.75 weighted**. Absolute ceiling if reasoning were perfect
= (13.5 + 31)/52 = **85.6%** (the 7.5 coverage-bound weighted caps it below 100%).

## Counterfactual recall (raw, per-cluster recovery from INTERVENTIONS.md)
| Scenario | reasoning recovered (of 24.75) | reasoning-set credit | **overall weighted** | overall strict (est.) |
|---|---|---|---|---|
| **Current** | — | 6.25 | **38.0%** | **25.0%** |
| Conservative (~35%) | ~8.7 | ~15 / 31 | **~55%** | ~42% |
| Expected (~55%) | ~13.6 | ~20 / 31 | **~64%** | ~54% |
| Best (~75%) | ~18.6 | ~25 / 31 | **~74%** | ~63% |

## Honesty discount — confound-adjusted band (what to actually believe)
The raw numbers assume the minimum reasoning step (Phase C) *fires and lands* — but those steps were derived
with knowledge of the ground truth, and on public contests the LLM may have prior exposure (P246's standing
training-data confound). Discounting ~10–15 points for true-blind performance:

| Scenario | **confound-adjusted overall weighted** |
|---|---|
| Conservative | **~42–48%** |
| Expected | **~50–58%** |
| Best | **~62–68%** |

## Reading
- Even **conservative confound-adjusted (~42–48%)** beats the current 38% and approaches the competitive
  band; **expected (~50–58%)** crosses it. The user's hypothesis ("3–5 reasoning clusters → path toward
  60–70%+") is **supported in the best/expected raw case and the best confound-adjusted case**, and is
  *approached* in the expected confound-adjusted case.
- The lift is **front-loaded in High recall**: cross-contract + state-machine clusters carry all 5 reasoning
  Highs (15 of the 31 reasoning weighted). Recovering those two clusters is most of the value.
- **The coverage-bound 7.5 weighted (badger, centrifuge unread) is untouched** — reasoning fixes cannot move
  oversized-target recall; that ceiling stays with the P245 coverage regime.

## Uncertainty statement (explicit)
- n = 21 reasoning findings across 6 contests → cluster shares are directional, magnitudes are rough.
- Recovery fractions are judgement, not measurement; the only way to confirm is a forward blind run with the
  interventions live (a future, separately-approved phase).
- FP assumption (≈0) holds **only if** interventions feed candidates through existing precision gates rather
  than auto-submitting (INTERVENTIONS.md §FP-safety). If wired as auto-submitters, the Economic checkpoint in
  particular would raise FP and the net competitive gain could reverse.
