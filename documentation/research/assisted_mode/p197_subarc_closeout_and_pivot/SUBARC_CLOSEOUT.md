# P190–P196 measurement/routing sub-arc — closeout

**Status: CLOSED.** The sub-arc investigated P190's apparent "87.7% upstream routing/discovery bottleneck" and,
phase by phase, **dissolved it**. Net result: **zero confirmed production routing / coverage / selection /
execution defects.** The campaign's validated production wins remain the **P183–P188 adjudication stack**.

## What was tested
| phase | question | mode |
|---|---|---|
| P190 | where does recall die? (6-stage funnel attribution, 114 unresolved findings) | read-only |
| P191 | why did the router prefer function B over awarded A? (routing forensics) | read-only |
| P192 | is locus-resolution recoverable? does deep-pass follow queue score? | read-only |
| P193 | why did extraction miss names already present? (failure taxonomy) | read-only |
| P194 | safe extraction repair + residual source audit | eval-harness code + read-only |
| P195 | do the revert-lend selection inversions justify a production fix? (burden of proof) | read-only |
| P196 | is deep-pass zero-execution an eval artifact or a production gap? | read-only |

## What was refuted
- **"87.7% upstream loss is a production discovery/routing problem"** — REFUTED. P191: ~98% of the discovery
  bucket was function-resolution noise. P192: 54.2% deterministically recoverable (measurement noise). P193:
  root-caused to a naive backtick regex in the answer-key extractor (75% of recoverable names were present
  verbatim). P194: safe repair recovered 42.4% and found **0 artifact-confirmable production coverage gaps** (the
  9 candidates were source-refuted as contracts/events/state-vars).
- **"revert-lend score inversions warrant a selection-by-score fix"** — REFUTED. P195: the inversions compared the
  queue `score` against a *different* tier/cluster assignment axis, and the deep-pass **executed 0** — max gain
  from reordering = 0.
- **"deep-pass execution is a production gap"** — REFUTED. P196: the budgeted auto-executor executes 0 in **every**
  run by api-free design (no non-interactive LLM runner; deep routes to the in-session skill); the real deep path
  (`run_deep_analysis` → `findings_deep_trace`) ran in 11 eval runs. Not a gap.

## What remains validated (retained)
- **P183–P188 adjudication stack** — mechanism inventory · multi-mechanism carry-forward · non-responsive-rejection
  + severity-floor advisory detectors · harness-escalation. Cross-corpus-general (P189: selection improvement in
  3/4 architectures, 0 false carries). Production hashes: `prompts/deep_trace.md ef93a6c2`,
  `scripts/validate_deep_pass_mechanisms.py 5d2a97f9`.
- **P194 `scripts/eval_locus_resolver.py`** (`3b0b2c02`) — eval-harness, un-wired, tested; the canonical
  answer-key → manifest function resolver (safe tiers + guardrails).
- **P196 distinction** — `assigned_pass=='deep'` is a tier *assignment* label, NOT execution (0 finding_refs);
  budgeted executor (A) vs in-session deep-analysis (B) are artifact-distinguishable.

## Closed hypotheses (do not reopen without new evidence)
| hypothesis | closed by | evidence |
|---|---|---|
| `production_coverage_gap_hypothesis` | P194 | 0 artifact-confirmable coverage gaps; residual 27 = answer-key/locus noise + 5 needs-human-map |
| `selection_by_score_fix` | P195 | inversions are an axis-mismatch artifact; max gain 0 at 0% execution |
| `execution_budget_fix` | P196 | auto-executor zero is api-free architectural; deep runs via in-session skill |
| `generic_routing_bottleneck` | P190→P196 | the "routing bottleneck" decomposed into measurement noise + extraction defect + by-design deep-pass |

## What should NOT be optimized next
Generic routing · candidate ranking / selection-by-score · deep-pass execution budget · production coverage
breadth · **more detector / taxonomy / normalizer / router tooling**. The measurement and routing frontier is
empirically closed. The open frontier is **adjudication quality on structurally harder corpora** — i.e. test the
*validated* P183–P188 stack on a new architecture, not build another tooling layer.

## Methodological note (process win)
The reviewer's escalating burden-of-proof (P195/P196 mandated as read-only validation before any production change)
prevented spending effort optimizing a bottleneck that did not exist. Read-only validation is cheaper than a
weeks-long optimization of a phantom lever — the discipline is retained going forward.
