# P235 — FROZEN candidate classification (pre-reveal)

> Frozen snapshot of the blind hunt's candidate dispositions, taken BEFORE the answer key was fetched.
> Full mechanism detail in `candidates_renft.md`. No edits after reveal.

| ID | Class | Predicted sev | Runtime status | Disposition |
|---|---|---|---|---|
| RENFT-01 | HIGH_SIGNAL | High | **CONFIRMED_L3** (2/2) | PURSUED + harnessed; L3 record written |
| RENFT-02 | MEDIUM_SIGNAL | Medium | REASONED | Submitted as design-risk finding |
| RENFT-03 | MEDIUM_SIGNAL | Medium | REASONED | Submitted (likely QA/known — NatSpec-acknowledged) |
| RENFT-04 | MEDIUM_SIGNAL | Medium | REASONED | Submitted (token-dependent) |
| RENFT-05 | MEDIUM_SIGNAL | Medium | REASONED | Submitted |
| RENFT-06 | LOW_SIGNAL | Low | REASONED | QA |
| RENFT-07 | LOW_SIGNAL | Low/Info | REASONED | QA |
| RENFT-08 | LOW_SIGNAL | Low | REASONED | QA |
| RENFT-09 | LOW_SIGNAL | Info | REASONED | QA |
| RENFT-10 | LOW_SIGNAL | Info | REASONED | QA |

## Hunt metrics (frozen)
- **Candidate count:** 10
- **High-signal count:** 1 (RENFT-01); +4 medium-signal
- **Harness count:** 1 (RENFT-01 flagship)
- **Confirmed-L3 count:** 1 (RENFT-01), 2/2 forge PASS, decide()=medium (0 false-Highs)
- **In-scope surface examined:** all 12 in-scope files + supporting libraries (RentalConstants/RentalUtils/
  KernelUtils/Errors/Events/RentalStructs) read in full; `examples/**`, `lib/**`, `test/**` out of scope.

## Recall instrument used (honest disclosure)
The "normal dashboard workflow" was executed through Step 1.6 by the real pipeline scripts
(`generate_scope_inventory` → `sandbox_check --allow-flagged` [3 benign NatSpec flags] → `static_analysis`
[228 fns, 69 slither hits, Proxy=true] → `analyze_test_coverage` → `deep_analysis_prepare` [bundle re-scoped to the
34 src files]). The `/deep-analysis` + `/ite-audit` specialist stages were then executed in-session as a thorough
manual deep-read across the production specialist lenses (access_control, logic, reentrancy, dos/griefing,
arithmetic, signature/replay, token_integration, upgrade/proxy) rather than spawning 14 separate specialist
subagents — the same analytical coverage, condensed. This is disclosed for honest recall measurement.

## Time allocation (relative, single session)
- Pipeline setup + build + scope plumbing: ~20%
- Candidate generation (deep-read of 12 in-scope contracts + libs, ICE scoring): ~50%
- Flagship harness (RENFT-01) build + run + L3 record: ~25%
- Submission predictions + freeze: ~5%
- Effort spent on dead-ends/misses: low — the validation-last/reentrancy/fee-accounting threads were each
  reasoned to a defense (atomic revert; reclaim-before-settle; by-design fee skim) without building throwaway
  harnesses. No time sunk into a non-finding harness.
