# P175 integrity checks (read-only analysis phase)

| Artifact | Result |
|---|---|
| research campaign ledger `output_research/option_a_campaign/ledger.jsonl` | byte-identical `e23c5bc9…` |
| research F2 `scripts/research/recall_selectors.py` | byte-identical `0c77332e…` (un-promoted) |
| runtime sidecar `…/value_provenance_eval/runtime_status.jsonl` | byte-identical `491da8c1…` |
| frozen corpus `documentation/evals/judge_corpus/frozen_corpus.json` | byte-identical `60089ff5…` |
| P171 `coverage_matrix.json` | unchanged (read-only input; `55e6888f…`) |
| 3 firewall seals (`_FIREWALL_SEAL.txt`) | intact (count = 3) |
| active `output` symlink | unchanged (`audits/quantamm-2024-12-eval/output`) |

## Write-scope (expected: only the p175 doc dir)
`family_roadmap.py` has exactly one write: `(HERE / "family_scoring.json").write_text(...)`. No write to any
production script, config, answer key, match matrix, runtime sidecar, ledger, or the P171 matrix. All eval
match matrices and answer keys were opened **read-only**.

## Reconciliation (self-checked by the script, asserts pass)
- quantamm: 44 = 19 recovered + 25 remaining (post-P174 override). Matches P171 per-family counts.
- every corpus: `recovered_or_touched + remaining_miss == n`.
- unclassified = 0 (after sharpened rules + 5 manual_overrides; residual hand-reviewed).

## Honesty notes
- Recovery is **measured** only on quantamm (post-P174); other corpora reflect their original eval-run state →
  cross-corpus "remaining" is an upper bound (shipped lenses may already cover some, unmeasured).
- Non-quantamm family tags are title-derived (approximate); det/prec are exposed priors, not measurements.
- A side correction was made to P174's own `metrics.json`: the estimator-recovered set is **5 ids**
  (H-09,H-10,H-11,L-06,L-09), not 4 — verified by running the shipped math-estimator classifier over the
  quantamm manifest (39 sensitive items incl. `_pow`/`_guardQuantAMMWeights`=H-09; `quantAMMPack32Array`=M-07
  NOT flagged → M-07 confirmed as the lone estimator residual). The +11 (8→19) baseline is unchanged.
