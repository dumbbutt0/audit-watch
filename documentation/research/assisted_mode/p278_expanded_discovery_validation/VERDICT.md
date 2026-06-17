# P278 — VERDICT

## Verdict: **B — EXPANDED_VALIDATION_PROMISING_NEEDS_REFINEMENT**

### Why B
Breadth expansion works and is safe:
- **class_routed 41.7% → 53.5%** (+11.8pp, clears the ≥50% intent) via handoff budget 10 + the P277 body signals.
- **Validation queue fills** (avg 7.0, reaches 10), **classes/contest 4.2**, anti-monoculture(40%) satisfied 11/12.
- **severe concluded/reportable FP = 0**; incremental noise (~+24 advisory candidates) is bounded and all
  NEEDS_MORE_EVIDENCE (advisory-only).
- **READY_FOR_POC_INTENT is reachable**: 2 hand-authored corpus samples pass the strict 10-point gate with PoC-intent
  records (the standard is not vacuous), and fail-closed is verified (incomplete evidence can never become READY).

But not **A**, because corpus-wide **auto** READY_FOR_POC_INTENT is **0**: the harness leaves the exploitability
evidence (attacker path / delta / victim / terminality / tx / assertion) as `operator-to-derive`, so the pipeline
routes wide but does not auto-complete the evidence PoC requires. The binding constraint moved cleanly from
discovery/routing to **completion-stage evidence auto-derivation** (backlog R-A). "Ready for the PoC sweep" (A) would
overclaim while READY is operator-only.

### Not C / D
- Not **C** (TOO_NOISY): severe FP = 0; noise is bounded (advisory-only, NEEDS_MORE_EVIDENCE); the gate is strict and
  fail-closed.
- Not **D** (ABORTED): research-only; only the authorized router CONFIG + new p278 files + downstream config-pins
  changed; router CODE + P260/P262/P264/P267/P269 + configs + P271 + forbidden 5 byte-identical; active audit unchanged.

### The mantra held
**More candidates entered validation (queue avg 7.0, class_routed 53.5%); none became PoC-ready without complete
evidence (84 → NEEDS_MORE_EVIDENCE; only the 2 fully-evidenced hand samples → READY).**

### Next
Land **R-A (completion-stage evidence auto-derivation)** as the next repair (separate approval) — it is the binding
constraint on PoC-readiness breadth. Then R-B (PoC-intent scaffolds) + R-C (recall, for the 31.9% missed). Re-run the
map; if auto READY rises with FP=0, proceed toward a PoC sweep, then a fresh blind target. Production authority WITHHELD.
