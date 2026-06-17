# P264 — DEPLOYMENT_SPEC
## Entrypoint
scripts/research/recall_first_harness.py --manifest --accounting --state-transition [--base-candidates]
[--suspicious-loci] --out-dir <dir> --mode {disabled,shadow,research_eval} [--config <p>]
## Modes
- disabled (DEFAULT; no --mode ⇒ disabled): no-op, exit 0, emits nothing.
- shadow: run P262 sweep → map to advisory contract → emit 4 files; advisory only.
- research_eval: same emission, for offline eval/backtest.
- unknown mode ⇒ treated as disabled (no-op).
## Pipeline (shadow/research_eval)
validate config (fail closed) → require inputs (fail closed) → rfs.sweep() [runs P260 prioritize + P262 inclusion]
→ map swept_loci → ADVISORY_RECALL_CANDIDATE records → _enforce_guards() → if violations: write guard report, exit 2,
NO advisory output → else emit 4 files + metrics + reproducibility.
## Composition
Imports frozen lsp (P260) + rfs (P262); never modifies them (byte-identical asserted in tests). B/C ranking +
five-op completion + refutation are DOWNSTREAM (operator/LLM), not in this module — the harness only prepares +
labels advisory candidates and hands off bc_ranking inputs.
