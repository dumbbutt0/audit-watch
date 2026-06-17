# P182 — Downstream triage/routing recall-loss trace (quantamm, 44 answer-key findings)

**Question answered:** *where did recall die?* (not "can we find another selector?"). Per-finding lifecycle
trace: affected fn/contract → manifest item → disposition → shipped-lens touch → specialist/deep coverage →
eval finding → match outcome → FIRST loss point. Read-only. Reproduce:
`python …/p182_downstream_recall_loss/trace_recall_loss.py`.

Resolution: 24 function-level (precise), 19 contract-level (coarse — answer key named only a contract),
1 unresolved (`L-09` affected `rules/*`).

## Loss funnel
**As-run (eval time):** 44 → **8 reportable** (3 HIT · 4 PARTIAL · 1 ADJACENT) · 36 MISS · 0 FP.

**With the shipped P174–P178 gates re-applied to the recorded run:**
```
44 answer-key findings
→ 36 surfaced by current shipped lenses (F1 / math_estimator / dependency)   [was 8 at eval time]
→ of the 36 MISS:
     12  already_fixed_by_shipped   (a shipped gate would now re-route the cleared site)
     18  still_open_downstream
      5  true_discovery_gap (low-sev / out-of-scope)
      1  unmappable
→  8 actually reportable at eval time
```

## Recommendation buckets (the 4-way split)
| bucket | count | sev-weighted | High findings |
|---|--:|--:|---|
| reportable (landed) | 8 | 16 | H-01, H-02, H-06 |
| **already_fixed_by_shipped** | **12** | 27 | H-08, H-09, H-10, H-11 |
| **still_open_downstream** | **18** | 36 | H-03, H-04, H-05, H-07 |
| true_discovery_gap | 5 | 5 | — (all Low) |
| unmappable | 1 | 1 | — |

## already_fixed_by_shipped (12) — the biggest historical class is solved
The "rule-math over-clearance" class `failure_analysis.md` flagged as the #1 miss cause is **already addressed**
by the shipped P174 F1 + math_estimator proof-gate (P177 made guarded-downstream prose advisory; the actual
re-routers are F1/math_estimator). These cleared-too-shallow findings would NOW be re-routed to deep-pass:
- via **math_estimator proof-gate:** H-09, H-10, H-11 (estimator family), L-06, **H-08, M-13** (auth functions
  that are also math/guard-shaped).
- via **F1 lifecycle re-surface:** M-04, M-08, M-09, M-12, M-14 (weight-set lifecycle), M-19.
**Do not rebuild this** — the shipped arc covers it.

## still_open_downstream (18) — dominated by DEEP_RUN_BUT_WRONG_MECHANISM
17 of 18 are **DEEP_RUN_BUT_WRONG_MECHANISM**: the surface was deep-read / a finding was produced there, but the
awarded mechanism was not the one reported. The **9 function-level** cases are the high-confidence core — each
function IS in `eval_findings` yet the match note is *"no blind finding addressed this root cause"*:

| finding | sev | function deep-read & reported (wrong bug) | family |
|---|---|---|---|
| H-03 | High | (fee accounting fn) | fee_accounting |
| H-07 | High | onAfterRemoveLiquidity (reported H-06 underflow, missed unauthorized-deletion) | hook_lifecycle |
| M-02 | Med | (recipient fn) | recipient_beneficiary |
| M-03 | Med | afterUpdate (reported other, missed 100-cap) | hook_lifecycle |
| M-06 | Med | (oracle fn) | oracle_robustness |
| M-10 | Med | (LP-NFT fn) | hook_lifecycle |
| M-17 | Med | (fee fn) | fee_accounting |
| L-01, L-02 | Low | — | lifecycle_hygiene / oracle |

(8 more are contract-level/coarse: H-04, H-05, M-05, M-11, M-15, M-18, L-08, L-12 — the contract was deep-read
but exact-function fate is lower-confidence.) The lone non-DEEP_RUN still-open is **M-07** (SURFACED_BUT_CLEARED,
function-level): `quantAMMPack32Array` precision — math_estimator's known P174 residual (it does not flag the
pack helper), so the proof-gate doesn't re-route it.

**This is the decisive finding:** the top remaining loss is NOT clear-policy and NOT detection — it is
**mechanism selection within an already-deep-read surface** (and exploit-framing / impact-direction, cf. H-02
PARTIAL "wrong impact direction", M-08 "read the guard but did not test the bypass").

## Recommendation (analysis-only — recommend, not implement)
**Improve deep-pass / specialist mechanism-enumeration + exploit framing** — the #1 still-open lever:
- require the deep-pass/specialist on a hot surface to **enumerate candidate mechanisms** (not stop at the first
  bug found) and apply **attacker / who-gains / who-loses / impact-direction** framing before clearing the rest
  of the surface;
- this directly targets the 9 function-level DEEP_RUN_BUT_WRONG_MECHANISM losses (incl. H-03, H-07 High).

Do **not**: add a new selector (detection reaches 36/44) or further tighten clear-policy for the rule-math class
(already fixed). Tiny residual: extend math_estimator to the `quantAMMPack32*` helper to also re-route **M-07**.
Discovery/unmappable (6, all Low) are minor; `L-09` needs answer-key `affected` mapping (`rules/*` wildcard).

## Limitations
- Contract-level resolutions (19/44) are coarse: "covered" means a finding was produced in the same contract,
  not necessarily at the exact function — those DEEP_RUN attributions are lower-confidence (flagged above).
- `already_addressed_by_shipped_gates` is a re-run of the shipped classifiers on the recorded disposition; it
  proves the clear would be **re-routed to deep-pass**, not that deep-pass would then confirm the bug
  (re-surfacing ≠ confirmation — and P182 shows the next bottleneck is exactly that deep-pass step).
- `fabrication_rate=0`: every loss point is anchored to an on-disk artifact; `L-09` reported unmappable, not guessed.
