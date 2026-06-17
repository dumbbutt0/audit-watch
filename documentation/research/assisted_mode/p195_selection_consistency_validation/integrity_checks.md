# P195 integrity checks (read-only selection-consistency validation)

Hashes are md5sum first-8. P195 wrote only its deliverable dir + `scripts/validate_p195.py`. No production /
prompt / detector / routing / selection / scoring / answer-key / corpus / disposition / manifest edits.

## Byte-identical (untouched)
| Artifact | Result |
|---|---|
| `prompts/deep_trace.md` (P188) | `ef93a6c2` |
| `scripts/validate_deep_pass_mechanisms.py` (P188) | `5d2a97f9` |
| `scripts/eval_locus_resolver.py` (P194) | `3b0b2c02` (unchanged; imported read-only) |
| research ledger `output_research/option_a_campaign/ledger.jsonl` | `e23c5bc9` |
| research F2 `scripts/research/recall_selectors.py` | `0c77332e` |
| corpus manifests / candidate_queue / dispositions / deep-trace / budget-summaries / answer-keys | read-only, unchanged |
| P190–P194 deliverables | unchanged |
| active `output` symlink | unchanged (`audits/quantamm-2024-12-eval/output`) |

## Read-only / evidence discipline
- `scripts/validate_p195.py` reads budget summaries, skip-reason records, dispositions, queues, deep-trace, answer
  keys + the P194 resolver; writes only the P195 JSON deliverables. No model runs; no mutation.
- **Both signal readings reported** (assignment `assigned_pass=='deep'` vs execution
  `deep_pass_budget_summary.executed` / `executed_deep_passes` / `findings_deep_trace`). Every count cites its
  artifact. Counterfactual top-N is explicitly labelled an upper bound on deep-pass **entry**, not catches.
- Unknowns stay `UNKNOWN`. `fabrication_rate=0`. All P195 JSON validates.
- **No production routing/conduct change** (the phase is read-only; the decision is *not* to ship a change).

## Key recorded facts
- `deep_pass_executed_anywhere = false` (execution_rate 0.0 in every eval run with a budget summary).
- `assigned_pass=='deep'` has 0 `finding_refs` (revert-lend) → it is a tier-assignment label, not execution.
- Decision: `EXECUTION_BUDGET_IS_THE_REAL_LEVER`; burden of proof for a selection-order fix = **not met**.

## Deliverables
`SELECTION_VALIDATION_REPORT.md`, `inversion_analysis.json`, `counterfactual_topN.json`,
`selection_policy_evidence.json`, `metrics.json`, `integrity_checks.md` + `scripts/validate_p195.py`.
