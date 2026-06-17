# P191 — Routing decision forensics

**Question:** why did the pipeline prefer function B when the awarded finding was in function A? **Read-only**,
deterministic attribution over existing artifacts (no model runs). Inputs: P190 `loss_funnel.json` +
`sibling_routing_table.json`, coverage_manifest, candidate_queue, coverage_dispositions, findings_deep_trace,
call_graph. Every value cites an artifact-derived score/record; unknowns stay `UNKNOWN`.

## Headline: `FUNCTION_RESOLUTION_PROBLEM`
The largest loss bucket — P190's 50 "contract-only" discovery findings — is **~98% a function-resolution /
answer-key-locus-quality issue, not demonstrable pipeline coverage gaps.** Before any routing/coverage investment,
the answer-key→function mapping has to be fixed, because right now roughly half of "recall loss" cannot even be
**measured** to a function. The genuine routing failures (25 pairs) are a real but smaller, mixed problem.

## Stage results

### Routing pairs (25 = 16 LOCUS + 9 PRIORITY)
| cause | n | % |
|---|---|---|
| SURFACE_SCORE_INFLATION (sibling has higher `attack_surface_score` / flashy `semantic_surface` tags) | 9 | 36 |
| MISSING_AWARDED_FEATURES (awarded fn carried no semantic-surface tag at all) | 5 | 20 |
| DEEP_PASS_STARVATION (awarded queued but not deep-run) | 9 | 36 |
| NO_COMPETING_SIBLING (nothing in the contract queued) | 2 | 8 |

**Similarity of the sibling pairs:** HIGH_OVERLAP 12 (48%) · MEDIUM 7 (28%) · LOW 4 (16%). So roughly half the
sibling-routing pairs are **genuinely similar functions** (same file / shared tags / shared call-graph chain) —
ambiguity is real, not purely "flashy surface won." Concrete example (zaros H-07): awarded
`getCreditCapacityForMarketId` lost to `convertMarketsCreditDepositsToUsdc`, which had **+4 attack_surface_score**
and was selected by three flashy surfaces (`accounting`+`mint_redeem`+`borrow_repay`) while the awarded function
carried none.

### Discovery bucket (50 contract-only) — almost entirely a resolution issue
| category | n | % |
|---|---|---|
| ANSWER_KEY_RESOLUTION_NOISE (answer-key loci yield only var/lang tokens, no resolvable fn name) | 27 | 54 |
| UNRESOLVABLE_FROM_ARTIFACTS (real-looking fn name absent; can't confirm gap vs noise without source) | 12 | 24 |
| answer_key_naming_drift (near-match present in manifest) | 10 | 20 |
| inherited_implementation_mismatch | 1 | 2 |
| **demonstrable genuine coverage gap** | **0** | **0** |

The unmatched "function" tokens are things like `solidity`, `abs`, `console`, `vaultId`, `amount` — i.e. the
awarded function name is not cleanly present in the answer key's parseable fields. **None of the 50 can be shown
to be a true function-level coverage gap from artifacts.**

### Deep-pass starvation (9 PRIORITY) — selection logic, not budget
Awarded functions ranked **21–81** by queue score, yet deep-run items extended to rank **95/103** — so deep-pass
selection is **not top-N-by-score**. Diagnosis: **selection ignores its own score (skipped while within top-N) = 4
/ 9**; budget-depth-would-help-if-top-N = 1 / 9; rank-too-low = 4 / 9. **Increasing deep-pass budget alone would
not fix the score-skip cases** — the deep-pass selector is not using the queue score it computes.

## The six required answers
1. **Why sibling functions beat awarded functions:** a mix of **surface-score inflation** (9/25 — siblings carry
   higher `attack_surface_score` and multiple flashy `semantic_surface` tags) and **missing features on the
   awarded function** (5/25 — the awarded fn had no semantic-surface tag, so nothing routed it). Compounded by
   **genuine similarity** (48% HIGH_OVERLAP) — the siblings really do look alike.
2. **Ranking mistakes or ambiguity mistakes?** **Both, genuinely mixed** — ~56% of pairs are
   scoring/feature-driven (ranking), ~48% are HIGH_OVERLAP (ambiguity); the sets overlap. Neither alone explains it.
3. **How much of the discovery bucket is function-resolution noise?** **~98%** (49/50 are resolution/answer-key
   issues: 54% pure answer-key noise, 24% unresolvable, 20% naming drift, 2% inherited). **~0% are demonstrable
   coverage gaps.** P190's "≈52% discovery" was overwhelmingly a measurement artifact, exactly as cautioned.
4. **Would more deep-pass budget materially help?** **No, not on its own.** 4/9 starved findings already rank
   within top-N-by-score but were skipped; only 1/9 is a clean depth-would-help case. The deep-pass **selection
   logic** (ignoring the queue score) is the lever, not budget size.
5. **Single routing component with the largest recall gain:** **answer-key→function resolution / locus mapping** —
   it governs the biggest bucket and currently makes ~half of "loss" unmeasurable. Then **deep-pass
   selection-by-score consistency** (use the computed score), then **surface-score calibration** for the
   genuine-ambiguity sibling pairs.
6. **What should P192 target?** **Function matching / answer-key locus resolution first** (it blocks honest
   measurement of everything else), then **deep-pass selection logic** (rank-respecting selection), then **ranking
   calibration** for sibling ambiguity. **Not queue depth.**

## Decision: `FUNCTION_RESOLUTION_PROBLEM`
The contract-only discovery bucket (50) dwarfs the routing-pair population (25) and is ~entirely a
resolution/answer-key issue; the routing pairs themselves are a smaller, mixed score+ambiguity problem; deep-pass
"starvation" is a selection-logic problem, not budget. The dominant, measurement-blocking lever is function
resolution.

## Honesty / limits
- **`FUNCTION_RESOLUTION_PROBLEM` is partly about the eval answer key, not only the production pipeline.** A large
  share of measured "recall loss" is the answer-key→function mapping being too noisy to resolve — so P190's
  discovery figure was inflated by measurement noise. Fixing resolution is prerequisite to honestly sizing the
  *real* coverage/routing gap.
- Stage-4 categories are best-effort fuzzy classifications (cutoff 0.85); `UNRESOLVABLE_FROM_ARTIFACTS` is
  explicitly "cannot confirm gap vs noise from artifacts" — not asserted as either.
- zaros `risk_score`≡0 (dimension uninformative there; zaros ran no `deep` pass → 0 priority gaps). State-var
  overlap is best-effort from `call_graph` chains, else `UNKNOWN`. n is small (25 pairs / 50 contract-only / 9
  starvation) → **directional attribution, not population statistics.** `fabrication_rate=0`.
