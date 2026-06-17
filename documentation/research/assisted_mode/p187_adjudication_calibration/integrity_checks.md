# P187 integrity checks (calibration / design — read-only on frozen data)

Hashes are md5sum first-8 (the convention used since P176). All production artifacts below are **byte-identical**
to the values recorded in P185/P186 — P187 wrote only new files under
`documentation/research/assisted_mode/p187_adjudication_calibration/` and `scripts/research/`.

| Artifact | Result |
|---|---|
| research ledger `output_research/option_a_campaign/ledger.jsonl` | byte-identical `e23c5bc9` |
| research F2 `scripts/research/recall_selectors.py` | byte-identical `0c77332e` |
| `prompts/deep_trace.md` (P185 version) | unchanged `dc7928f2` — **not edited** (recommendation only) |
| `scripts/validate_deep_pass_mechanisms.py` (P185 version) | unchanged `1cddd73f` — **not edited** |
| routing `scripts/dependency_clear_utils.py` | byte-identical `f1588610` |
| quantamm `normalized_answer_key.json` (eval) | unchanged `2e9dee7f` (read-only input) |
| P185 deliverable `metrics.json` | unchanged `c39bc803` |
| P186 frozen inputs (`raw_outputs/*.json`, `metrics.json`, `selection_scoring.json`) | read-only; mtimes (08:04–08:06) precede all P187 writes; not modified |
| firewall seals (`_sealed_answer_key/_FIREWALL_SEAL.txt`) | intact |
| active `output` symlink | unchanged (`audits/quantamm-2024-12-eval/output`) |

## Research-platform discipline (CLAUDE.md hard rule)
- `scripts/research/adjudication_rubric.py` carries `research_only:true / routes_in_production:false /
  is_gate:false / re_surface_only:true`; the emitted `adjudication_matrix.json` carries the same flags +
  `no_recall_claim:true`.
- **Un-wired:** `grep -rn "adjudication_rubric" run_pipeline.sh scripts/ prompts/ config/ agents/` returns only the
  module itself and its test — no routing / gate / pipeline / agent reference. No production `.py` imports it.
- The module **never** sets severity, routes, gates, mints findings, or writes dispositions / corpus / answer-key.
  It reads frozen P186 artifacts + the answer key and writes one research matrix under `documentation/research/`.

## Read-only / honesty
- No prompt / checker / selector / routing / severity / submission edit; no corpus / answer-key / disposition write.
- The answer-aware inputs in `CASES` (alleged failure-mode, locus tokens, severity tier) are legitimate
  calibration inputs; the model dispositions + rejecting facts are transcribed verbatim from the **frozen** P186
  `raw_outputs/`. `_verify_against_frozen_outputs()` confirms each transcribed disposition still matches the
  frozen output bucket → `consistent: true`.
- `adjudication_matrix.json` is **byte-stable** across re-runs (`md5 18842dad` before == after).
- The rubric was **designed against** M-02/M-06 → success on them is partly by construction (disclosed in
  `VALIDITY_RUBRIC.md`); the in-phase anti-overfit control is the 6 stable selections (none rejected, no patch).
  **No recall claim.** n=9, one corpus.
- `fabrication_rate=0` — every cell is anchored to a frozen rejecting fact, a source line, or an answer-key field.

## Tests
`pytest scripts/research/test_adjudication_rubric.py -q` → **11 passed** (incl. #8 non-responsive detector,
#7 severity-floor rule, anti-overfit "no stable selection is rejected", "only the two flips are rejected").
