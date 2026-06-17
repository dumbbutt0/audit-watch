# P184 integrity checks (measurement only — blind-subagent run)

| Artifact | Result |
|---|---|
| research ledger `output_research/option_a_campaign/ledger.jsonl` | byte-identical `e23c5bc9…` |
| research F2 `scripts/research/recall_selectors.py` | byte-identical `0c77332e…` |
| runtime sidecar | byte-identical `491da8c1…` |
| frozen corpus | byte-identical `60089ff5…` |
| `prompts/deep_trace.md` (P183 version) | byte-identical `45d42ca4…` — used read-only, NOT edited |
| routing `scripts/dependency_clear_utils.py` | byte-identical `f15886103…` |
| quantamm `normalized_answer_key.json` / `coverage_dispositions.json` | unchanged (`2e9dee7f…` / `a17f1ac7…`) |
| 3 firewall seals | intact |
| active `output` symlink | unchanged (`audits/quantamm-2024-12-eval/output`) |

## Guardrails honored
- **Measurement only.** No prompt edit (`deep_trace.md` used as-is; the schema gap was FLAGGED, not fixed). No
  selector/taxonomy/routing/severity/submission change. No corpus / answer-key / disposition mutation — the
  blind subagents got NO answer key; all P184 outputs are written ONLY to the p184 dir.
- **Blindness:** subagent prompts contained no finding IDs / "awarded" / answer-key text (source + P183 prompt
  only); no subagent output cited an answer-key ID; 2/9 genuine misses are positive evidence of blindness.
- **No scoring backfill / `fabrication_rate=0`:** raw subagent outputs are preserved verbatim in
  `mechanism_selection_trace.json`; misses (M-17 not enumerated, M-02 not selected) are recorded honestly;
  the loose H-03 match is flagged and excluded in the conservative count.
- **Residual caveat disclosed:** same model family → faint training priors not fully excludable; n=9 single run;
  firewall-sealed fresh-model run remains the gold standard.

## Validation
Both JSON deliverables validate. Headline `awarded_mechanism_selected = 7/9` (conservative 6/9) vs `0/9` at eval
time. Deliverables: `MECHANISM_SELECTION_REPORT.md`, `mechanism_selection_trace.json`, `metrics.json`,
`integrity_checks.md`.
