# P291 — EVIDENCE_AUDIT

## Pools.deposit (Part A demotion) — CORRECT
Source: `function deposit(IERC20 token, uint256 amount) external nonReentrant { require(amount>DUST);
_userDeposits[msg.sender][token]+=amount; token.safeTransferFrom(...); }`. No low-level call / callback /
reentrancy-ordering (nonReentrant). `integration_deviation_evidence.deviation_present=False` → status
NEEDS_INTEGRATION_DEVIATION_EVIDENCE. The generic "crafted callback" hypothesis is blocked. No false READY. ✓

## EXTERNAL_INTEGRATION READY candidates — NONE
0 EXTERNAL_INTEGRATION candidates reached READY corpus-wide (the class-template path is closed). ✓

## _increaseUserShare (Part B) — SURFACED, but dedup-blocked before the lens
- Internal-locus surfacing real? Yes — `StakingRewards._increaseUserShare` is an internal share/index accounting
  function (writes user share + reward index) reached from a surfaced public liquidity entry; call path recorded;
  class-relevance high. ✓ (the P290 recall gap is fixed at the advisory layer).
- Reaches Lens 3? NO — P273 coverage router gives `COVERAGE_DEFER_DUPLICATE_CLASS` (SHARE_ROUNDING slot filled), dropping
  it before the validation queue. This is a SOURCE-BACKED, precise reason it doesn't reach the lens (not a silent miss).
  Honest status: surfacing repaired; queue admission is the next localized blocker (P273/P278).

## 10 internal-locus candidates (audited sample of 5 surfaced)
`_increaseUserShare`, `_dualZapInLiquidity`, `_withdrawLiquidityAndClaim` (salty), `_decrementWeightUntilFree`,
`updateTotalRebasingShares` (ECG): all real internal accounting/share/reward functions with state writes, reached from
surfaced public entries, class-relevant. No pure getters, no test/mock, no libraries-without-relevance. Bounded (≤3/entry).
No over-surfacing; advisory_only. ✓ No hallucinated call paths (each callee resolved to a manifest internal function).

## Regressions — CORRECT (no false READY, no over-demotion)
ECG H-04 stake READY (loss_on_stake, not EXTERNAL_INTEGRATION) · kelp H-01 getRsETHAmountToMint READY (D4.6) · blackhole
claim_many READY (sibling) · L2Governor.execute READY (state-machine). None affected by Part A (non-EXTERNAL) or Part B
(advisory-only). ✓

## Tally
Pools.deposit demoted ✓ · 0 generic EXTERNAL_INTEGRATION READY ✓ · 0 false READY introduced ✓ · 5 internal loci surfaced
(incl. the awarded `_increaseUserShare`) ✓ · 0 over-surfacing / hallucination ✓ · severe FP=0 ✓ · regressions stable ✓.
Residual: internal locus dedup-blocked before Lens 3 (P273/P278 — next phase).
