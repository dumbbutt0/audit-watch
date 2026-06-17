# P281 — VERDICT

## Verdict: **A — READY_GATE_REPAIRED_FOR_POC_SWEEP**

### Why A
- **P280 inline-guard false-READYs downgraded:** V3Vault.transform → INLINE_GUARD_REFUTED (D1), IBeanstalk.
  cancelPodListing → NEEDS_SOURCE_SPAN (D4). The manifest-`modifiers` blind spot is closed by reading the body.
- **State-machine candidate correctly reframed:** L2Governor.execute → READY as a STATE_MACHINE candidate (D2:
  state_machine + or_state_gate), and **PoC-SUPPORTED** (a DEFEATED proposal executes; control rejects Pending/Active).
- **READY candidates carry source spans** (gate_evidence_summary.source_span).
- **≥1 repaired READY is PoC-supported** (the single survivor) — and the gate honestly blocks the rest with specific
  reasons (17 inline-guard, 11 state, 11 value-flow, 1 source-span).
- **severe concluded/reportable FP = 0**; READY precision proxy **0/3 → 1/1**; no production-authority leakage; P260–
  P278 modules + router code/config + forbidden 5 byte-identical; back-compat (P279/P280 tests green); tests green.

### Not B / C / D / E
- Not **B** (needs more refinement): the core repairs all fire correctly and the one survivor is PoC-supported; the
  remaining value-flow gap is a *separate, named* next repair (D3), not a deficiency of this one.
- Not **C** (too strict): it did not block a known-good candidate — the only PoC-supported mechanism passed.
- Not **D** (still too noisy): READY precision went 0/3 → 1/1; the 2 false-READYs are gone.
- Not **E**: research-only; only the gate/deriver + extractor/config/test/docs/pocs changed; active audit unchanged.

### Next
Now that READY is source-span-backed and trustworthy: a small PoC sweep on the repaired READY set (here: 1), then the
**D3 value-flow evidence derivation** to unlock the 11 NEEDS_VALUE_FLOW_EVIDENCE (accounting/math/oracle) candidates,
then re-map, then a fresh blind target. Production authority WITHHELD.
