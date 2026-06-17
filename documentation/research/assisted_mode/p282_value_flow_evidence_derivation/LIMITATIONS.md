# P282 — LIMITATIONS

- **0 new READY lifts.** D3 establishes value-flow STRUCTURE (state-write/asset-move/terms) and a div-before-mul anomaly
  heuristic, but no corpus value-class candidate has a source-detectable in-span anomaly — so none lifted. The actual
  invariant VIOLATION lives across function boundaries (wrappers/delegations) or needs a corrected-reference comparison
  the span scan can't do. This is the precision-preserving outcome, not a deriver defect.
- **Span-local only.** The extractor reads the candidate's own function body span; it does NOT follow delegated callees
  (`_claimFees()`, `.compact()`, per-pool loops) — exactly where 4 candidates' value-flow lives (backlog V2).
- **Anomaly heuristic is narrow** (div-before-mul). Other math anomalies (scale mismatch, rounding asymmetry,
  set-vs-increment) are not yet detected → conservative (fewer lifts), not noisy.
- **D1-gap closure is pattern-based** (`only[A-Z]\w*`, either-side msg.sender). Spot-checked 6/36 as genuine guards; a
  pathological identifier like `onlyXyz` as a non-modifier could over-flag, but the default (block) is conservative.
- Supervised/calibration on the P281 corpus; not blind; not production authority; nothing reportable/confirmed.
