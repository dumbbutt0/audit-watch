# P283 — SETUP

**Phase:** P283 — V2 Cross-Function Value-Flow Evidence Tracing (REPAIR; not blind; not production authority).
**Status:** RESEARCH-ONLY · ADVISORY · UN-WIRED · default-off · fail-closed.

## What this phase is
P282 (D3, span-local value-flow) lifted 0 READY because the value-flow VIOLATION for accounting/share-math/oracle/
reward candidates usually lives **across a function boundary** (wrapper→internal, public→library, deposit→accounting,
oracle-read→valuation). P283 adds a **bounded static cross-function tracer** so a value-class candidate can *earn*
READY by following a resolvable value path into a callee where the value math actually lives — **not** by loosening the
gate.

## Components (all new/edited under the allow-list)
- NEW `scripts/research/cross_function_value_tracer.py` + `config/research_cross_function_value_tracer.json` — the
  bounded tracer (depth 2 · ≤5 callees/fn · ≤8 spans/candidate · fail-closed on external/dynamic/ambiguous edges).
- `scripts/research/source_span_guard_extractor.py` — comment-stripping (correctness) + the P283 div-before-mul
  `**`-exponent exclusion (correctness; see IMPLEMENTATION_NOTES).
- `scripts/research/completion_evidence_deriver.py` — attaches `trace_evidence` when the in-span scan finds no anomaly.
- `scripts/research/poc_readiness_evidence_gate.py` — consumes trace evidence for the V2 value-class lift rule
  (anomaly + HIGH/MEDIUM confidence only); strictness preserved.

## How to reproduce the corpus remap
```
# per audit a (12 eval audits):
python scripts/research/completion_evidence_deriver.py \
  --manifest audits/<a>/output/coverage_manifest.json \
  --packages documentation/research/assisted_mode/p278_expanded_discovery_validation/outputs/<a>/evidence_packages.json \
  --out documentation/research/assisted_mode/p283_cross_function_value_tracing/outputs/<a>/derived.json --quiet
python scripts/research/poc_readiness_evidence_gate.py \
  --packages .../<a>/derived.json --out .../<a>/readiness.json --quiet
```
Aggregates: `outputs/remap_metrics.json`, `outputs/trace_evidence.json`, `outputs/guard_report.json`.

## Standing constraints (in force)
Research-only; no production authority / auto-submit / severity / reportable / submission / confirmed. No production or
contest source edits. Active audit `size-credit-2024-06-blind` symlink unchanged. No answer-key / target hard-coding;
award titles/bodies never read. Frozen P260/P262/P264/P267/P269/P271/P273 (router code `6debb753`, config `91f9deac`) +
forbidden 5 byte-identical.
