# P186 integrity checks (measurement only — fresh-model blind run)

| Artifact | Result |
|---|---|
| research ledger `output_research/option_a_campaign/ledger.jsonl` | byte-identical `e23c5bc9…` |
| research F2 `scripts/research/recall_selectors.py` | byte-identical `0c77332e…` |
| runtime sidecar | byte-identical `491da8c1…` |
| frozen corpus | byte-identical `60089ff5…` |
| `prompts/deep_trace.md` (P185 version) | unchanged `dc7928f2…` — used read-only, NOT edited |
| `scripts/validate_deep_pass_mechanisms.py` (P185 version) | unchanged `1cddd73f…` — used read-only, NOT edited |
| routing `scripts/dependency_clear_utils.py` | byte-identical `f15886103…` |
| quantamm `normalized_answer_key.json` | unchanged `2e9dee7f…` |
| P185 deliverable `metrics.json` | unchanged `c39bc803…` |
| 3 firewall seals | intact |
| active `output` symlink | unchanged (`audits/quantamm-2024-12-eval/output`) |

## Firewall (the point of this phase)
- Blind prompts frozen to `blind_prompts/` BEFORE the run; token-scan = zero finding-IDs / answer-key / phase
  refs / awarded descriptions (only the production prompt's generic `awarded`/`recall` header words appear).
- Blind selector = **Sonnet** (different from campaign Opus 4.8), given ONLY the frozen prompt; no campaign
  memory, no answer key.
- Raw outputs preserved verbatim in `raw_outputs/`; token-scan of outputs = zero answer-key IDs cited.
- Scorer answer-aware only AFTER outputs frozen; **no backfill**; misses (M-02, M-06) recorded honestly.
- `fabrication_rate=0`.

## Guardrails honored
Measurement only — no prompt/checker/selector/routing/severity/submission edit; no corpus/answer-key/disposition
write. The P185 checker was run read-only on the frozen outputs (5/5 complete, 0 demoted). JSON deliverables all
validate.

## Residual caveat
Sonnet is still Claude/same-vendor; vendor-level training priors cannot be fully excluded (a different-vendor
model would be required). n=9, single run per model.
