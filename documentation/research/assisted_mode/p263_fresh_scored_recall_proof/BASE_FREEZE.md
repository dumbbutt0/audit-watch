# P263 — BASE_FREEZE (benddao; PRE-REVEAL)
- Source: git clone --depth1 code-423n4/2024-07-benddao → /tmp/p263_fresh/benddao (source only).
- Manifest: build_coverage_manifest.py --contract src --out outputs/benddao_coverage_manifest.json (uses scope.txt; 93 prioritizer-candidate fns).
- Checkpoints: accounting + state-transition --out isolated (invariants emits_findings:false/0 concluded).
- Architecture: LiquidationLogic/CrossLiquidation/IsolateLogic (cross+isolate liquidation), GenericLogic
  (account-data/health), InterestLogic (Supply/BorrowIndex accrual, _accrueFeeToTreasury), ValidateLogic,
  YieldStakingBase/YieldSavingsDai/Etherfi/Eigen (restaking yield unstake/repay), VaultLogic.
- Three-way tags: all loci CHECKPOINT_HIT_ONLY or manifest-high-surface; base completed 0 (this run feeds the
  module path, not a manual base hunt). FREEZE: manifest + checkpoints are the frozen base.
