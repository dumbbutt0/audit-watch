# P261 — BASE_FREEZE (fresh monetrix; PRE-REVEAL)
## Generation basis (exact)
- Source: git clone --depth 1 https://github.com/code-423n4/2026-04-monetrix → /tmp/p261_fresh/monetrix (source only).
- Manifest: `python scripts/build_coverage_manifest.py --contract /tmp/p261_fresh/monetrix/src --out outputs/monetrix_coverage_manifest.json` → 254 items (232 in-scope; 185 in-scope functions).
- Checkpoints: `accounting_checkpoint_audit.py`/`state_transition_checkpoint_audit.py --manifest <above> --out outputs/monetrix_*_checkpoint.json` (invariants emits_findings:false/0 concluded).
## Architecture (subtle-accounting-fit)
MonetrixVault (43 fns: deposit/claimRedeem/settle/distributeYield/fundRedemptions/emergencyBridge…), sUSDM (26;
staked-USDM share vault w/ cooldownShares/cooldownAssets), MonetrixAccountant (22), MonetrixConfig (17), USDM
(stablecoin), RedeemEscrow, InsuranceFund, TokenMath. = synthetic-dollar mint/redeem + staked-share + yield +
solvency accounting.
## Base candidates / tags
Base hunt was NOT performed separately (P261 tests the MODULE's prioritization, not a manual base hunt). All
prioritized loci tagged CHECKPOINT_HIT_ONLY or (manifest high-surface). BASE_COMPLETED_CHAIN: 0; no base candidates
to compare against (this run feeds the module directly). FREEZE: manifest + checkpoint outputs are the frozen base.
