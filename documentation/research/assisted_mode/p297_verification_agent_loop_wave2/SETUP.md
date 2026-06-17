# P297 — SETUP

**Phase:** Verification-agent loop, Wave 2 — the remaining 6 backlog loci. Research-only, advisory, authority WITHHELD.
Reuses the P296 loop unchanged (one additive `--out-dir` param so wave-2 results land here, preserving P296's wave-1
snapshot). Builders = 6 spawned `general-purpose` subagents; the P294 verifier is the sole judge.

## Loci (the 6 PENDING from P296)
ecg H-01 ProfitManager.claimGaugeRewards · ecg M-02 RateLimitedMinter.mint · ecg M-03 ProfitManager.totalBorrowedCredit
· kelp M-01 LRTDepositPool.getTotalAssetDeposits · kelp M-02 LRTDepositPool.depositAsset · salty H-05
CollateralAndLiquidity.depositCollateralAndIncreaseShare.

## New files only (one additive loop edit; no hash pin → zero cascade)
- `scripts/research/verification_agent_loop.py` — added `--out-dir` + `judge(out, specs_path)` (additive).
- `pocs/p296/<audit>__<id>/*` — the 6 new subagent PoCs (foundry harness + test + manifest w/ assertion_map + report).
- `tests/research/test_p297_verification_agent_loop_wave2.py` + this docs dir + outputs.

## Reused (byte-identical)
P294 `executed_poc_verifier.py` (the judge), forge 1.5.1, `pocs/p286/lib`, forbidden 5, the P296 config + specs.

## Reproduce
spawn the 6 builders → `python3 scripts/research/verification_agent_loop.py judge --out-dir <this>/outputs`.
