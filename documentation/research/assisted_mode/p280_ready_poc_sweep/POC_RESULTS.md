# P280 — POC_RESULTS

`pocs/p280/` — `forge test`: **6 passed, 0 failed** (`outputs/command_log.txt`). Machine: `outputs/poc_results.json`.

| candidate | result | observed | evidence sufficient to BUILD? | human invented mechanism facts? |
|---|---|---|---|---|
| V3Vault.transform | **PASS_REFUTED** | unauthorized caller reverts on the inline owner/approval guard; owner can transform | yes | no |
| IBeanstalk.cancelPodListing | **PASS_REFUTED** | non-owner reverts on inline `require(plots[lister][index]>0)`; maker can cancel own listing | yes | no |
| L2Governor.execute | **BENIGN_BY_DESIGN** (+ SAME_AREA_WRONG_MECHANISM) | execute is permissionless by design (anyone executes a SUCCEEDED proposal); REAL anomaly = a DEFEATED proposal is also executable | yes | yes (had to find the Defeated/Expired anomaly myself) |

## Reading
- The PoCs are **runnable** and the auto evidence packets were **sufficient to BUILD** them (the attacker_path +
  assertion told me exactly what to test). That half of the diagnostic passes.
- But **all 3 auto mechanisms are refuted or mis-framed**: transform & cancelPodListing are INLINE-guarded (the auto
  "unauthorized" claim is false); L2Governor.execute is permissionless-by-design (auto ACCESS framing benign) and its
  real bug is a state-machine anomaly (Defeated/Expired executable) the auto claim missed. **0 PASS_SUPPORTED.**
- **severe concluded/reportable FP = 0** (the refutations are advisory diagnostics, not findings).
