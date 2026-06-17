# Value-Flow Chain — Research-Only REVIEW_ONLY Integration Spec

**Status: research_only · review_only · NO production wiring · NO promotion.** This spec integrates the consolidated
P33–P59 value-flow mechanism chain into Audit-Watch as a **precision-heavy, REVIEW_ONLY candidate generator for human
review** — never a production verdict engine. It adds **no logic** and modifies **no validated module**; it is config +
docs + schema only. Config: `config/research_modules/value_flow_chain.json`.

## Final chain summary
`P35 value_flow_surface → P42 value_state_shadow_ranker → P36 library_mechanism_extractors + P33 mechanism_enumerator →
P32 root_cause_discriminator → P34 comparand_parity_gate → P45 mechanism_advancement_gate → P47 omitted_term_dataflow_gate
→ P49 bound_semantics_gate → P52 native_eth_sink_gate.` P40 mask-opcode lens = diagnostic-only. P41 cap-policy = archived.
All modules **byte-identical** (hashes in `_p60/final_module_inventory.json` / `config/research_modules/value_flow_chain.json`).

## Module inputs and outputs
- **Input:** an in-scope coverage manifest (built by `build_coverage_manifest.py`) + source. The chain surfaces (P35),
  ranks (P42), enumerates/extracts candidate mechanisms (P33/P36), discriminates root cause (P32), and tightens via the
  gate stack (P34→P45→P47→P49→P52).
- **Output:** structured **REVIEW_ONLY** artifacts (schema in `value_flow_review_schema.md`). A candidate that survives
  the gate stack is `REVIEW_ONLY_ADVANCE` (a human-review candidate), **not** a confirmed bug.

## Output states
**Allowed:** `REVIEW_ONLY_ADVANCE` · `REVIEW_ONLY_ABSTAIN` · `REVIEW_ONLY_NEEDS_IMPACT` · `REVIEW_ONLY_REJECTED` ·
`REGRESSION_FAILURE`. **Forbidden:** `CONFIRMED_BUG` · `READY_TO_SUBMIT` · `AUTO_SUBMIT`.
- `REVIEW_ONLY_ADVANCE` — survived the gate stack; route to a human.
- `REVIEW_ONLY_NEEDS_IMPACT` — mechanism plausible but no source-backed impact path proven (the chain has no impact-path
  proof layer); a human must establish impact before any submission consideration.
- `REVIEW_ONLY_ABSTAIN` / `REVIEW_ONLY_REJECTED` — gated out (abstain = insufficient evidence; rejected = gate demotion).
- `REGRESSION_FAILURE` — a standing-regression check failed; output is blocked until investigated.

## REVIEW_ONLY schema
See `value_flow_review_schema.md`. Every artifact carries: candidate id; target file/function/lines; mechanism class;
source evidence; downstream value/authority effect; per-gate decisions (P34/P45/P47/P49/P52); why advanced/abstained;
confidence; impact-proof status; required human-review steps; recommended next manual action; regression status.

## Exact regression suite
See `value_flow_regression_suite.md` (runner `run_p52.py`). Must be green before any REVIEW_ONLY output is trusted.

## Stop conditions
- Any regression-suite check fails → `REGRESSION_FAILURE`, block output.
- Engine module hash drift (vs the recorded hashes) → block; the chain is only valid byte-identical.
- Any request for a forbidden output state → reject.

## Rollback plan
Doc/config-only: delete `config/research_modules/value_flow_chain.json` + the `documentation/research/value_flow_*` docs.
The validated engine modules are never modified (byte-identical), so rollback touches nothing in `scripts/`.

## Dashboard integration notes
Surface REVIEW_ONLY candidates on a **research-only** dashboard lane (schema in `research_module_dashboard_schema.md`):
read-only, clearly labelled "research / review-only — not a verdict", with the forbidden states structurally absent.
No write-back into production submission artifacts.

## Human review checklist (per REVIEW_ONLY_ADVANCE)
1. Re-derive the source evidence from the cited file/function/lines (no-trust).
2. Confirm the downstream value/authority effect is real and reachable from an EOA.
3. Establish or refute an impact path (the chain does not prove impact).
4. Check against the protocol's intent / NatSpec / docs (is the behaviour by-design?).
5. Cross-check the regression class (is this the same shape as a known false-positive family?).
6. Decide: escalate to PoC / human-review queue, or reject — **the human owns the verdict.**

## What this module must NEVER claim
Confirmed bug · ready to submit · auto-submit · general bug-finding · broad H/M recall · a production verdict. It is a
research-only, precision-heavy value-flow review lane with one fresh source-backed PARTIAL (SecondSwap) and thin recall.
