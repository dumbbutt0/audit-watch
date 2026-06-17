# P284 — SETUP

**Phase:** P284 — Corrected-Reference & Invariant-Delta Derivation (REPAIR; not blind; production authority WITHHELD).
**Status:** RESEARCH-ONLY · ADVISORY · UN-WIRED · default-off · fail-closed.

## What this phase is
P283 proved lexical anomaly detection is exhausted: cross-function tracing found value-flow but lifted 0 READY because
the bug is a RELATIONSHIP error, not a token error. P284 derives value-bug evidence from **corrected-reference /
invariant-delta** comparisons (conservation · symmetric-ledger · sibling-function · before/after equation · oracle
normalization · state-machine value gate) so a value/state candidate can EARN READY when an observed value-flow
DEVIATES from a source-backed reference — never on similarity or an invented expression.

## Precision spine — reuse of existing 0-FP detectors (read-only)
P284 imports the PURE classifiers of the repo's validated detector platform as evidence helpers (it never edits, routes,
or wires them):
- `sibling_function_parity_taxonomy.extract_features` / `classify_pair` → D4.3 sibling-reference (weak sibling +
  named missing_component; high/medium tier is corpus-validated 0-FP).
- `registry_position_lifecycle_taxonomy.extract_registry_features` / `classify_contract` → D4.2 symmetric-ledger /
  position-vs-global desync.
- `omitted_term_dataflow_gate._term_flow` → D4.4 computed-value-not-applied (dataflow, not spelling).
- `bound_semantics_gate._rounding_evidence` / `_genuine_bound_use` → D4.4 rounding-direction / bound semantics.
- P281 `source_span_guard_extractor` state-machine evidence → D4.7.
D4.1 / D4.5 (conservation / before-after equation) and D4.6 (oracle normalization) use a **local bounded-SSA** equation
extractor (internal method only — no compiler-grade SSA / alias analysis / symbolic execution / SMT).

## Components
- NEW `scripts/research/invariant_delta_deriver.py` + `config/research_invariant_delta_deriver.json`.
- `completion_evidence_deriver.py` attaches `invariant_delta_evidence` (when no in-span/trace anomaly) and, ONLY on a
  FOUND result with HIGH/MEDIUM confidence, upgrades the core readiness fields from the source-backed reference.
- `poc_readiness_evidence_gate.py` adds the value/state-class lift path consuming invariant-delta evidence.

## Reproduce the corpus remap
Per audit (12 eval audits): run `completion_evidence_deriver.py` (manifest + P278 `evidence_packages.json`) then
`poc_readiness_evidence_gate.py`; aggregate into `outputs/{invariant_delta_evidence,remap_metrics,audit,guard_report}.json`.

## Standing constraints (in force)
Research-only; no production authority / auto-submit / severity / reportable / submission / confirmed. No production or
contest source edits. The reused detector modules + their configs are byte-identical (read-only import). Active audit
`size-credit-2024-06-blind` symlink unchanged. No answer-key / target hard-coding; award titles/bodies never read.
Frozen P260/P262/P264/P267/P269/P271/P273 (router `6debb753`, config `91f9deac`) + forbidden 5 byte-identical.
