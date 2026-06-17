# P260 — Locus-Prioritization + Shape Discovery Module — SETUP
First BUILD of the arc. Research-only, default-off, un-wired module that fixes the P259 LOCUS_SELECTION gap:
prioritize highest-risk loci (preferring skipped high-risk checkpoint-hit loci over completed base candidates),
apply the 8 shape templates, emit top-2 mechanism hypotheses + B/C ranking handoff. NOT a scaffold/severity/
submission path. Evaluated by BACKTEST on frozen P254–P259 artifacts only (no new answer keys).

## Files (allowed edits only)
- scripts/research/locus_shape_prioritizer.py (module; deterministic; no key; no source-read required)
- config/research_locus_shape_prioritizer.json (weights/keyword→dimension/marker→template maps)
- prompts/research/locus_shape_prioritizer.md (isolated spec)
- tests/research/test_p260_locus_shape_prioritizer.py
- documentation/research/assisted_mode/p260_locus_shape_prioritizer/ (this dir) + outputs/

## Inputs (no answer keys)
coverage_manifest.json (manifest fields: external_calls/has_loop/in_tainted_sink/risk_score/attack_surface_score/
tags/visibility/signature/source_span) + accounting & state-transition checkpoint JSON (per contract:function
families fired) + optional base candidates (BASE_BORN_INCOMPLETE boost / BASE_COMPLETED penalty).

## Invariants (self-tripwire)
is_gate:false · research_only:true · routes_in_production:false · routed_manifest_ids:[] · emits_findings:false ·
concludes_vulnerability:false · runtime assert no record carries severity/concluded. Never sets severity/reportability.
