# P281 — P280_REGRESSION (the 3 prior auto-READY through the repaired gate)

`outputs/p280_regression.json`.

| candidate | P279/P280 | P281 | repaired by |
|---|---|---|---|
| V3Vault.transform (ACCESS) | READY | **INLINE_GUARD_REFUTED** | D1 — inline owner/approval guard (loanowner/ownerof/transformApprovals/revert Unauthorized) |
| IBeanstalk.cancelPodListing (ORDER) | READY | **NEEDS_SOURCE_SPAN** | D4 — interface declaration (no body) |
| L2Governor.execute (ACCESS) | READY (mis-framed) | **READY_FOR_POC_INTENT** (state-machine, reframed) | D2 — state_machine_detected + or_state_gate; PoC-SUPPORTED (Defeated executable) |

The 2 P280 false-READYs are downgraded with specific, source-span-backed reasons; the 1 genuine anomaly survives and
is now correctly framed as a state-machine candidate (and PoC-supported). Exactly the intended repair.
