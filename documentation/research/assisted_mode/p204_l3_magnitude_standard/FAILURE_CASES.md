# P204 — failure cases & limitations

## No false demotions, no false Highs in the harnessed set
- H-01 confirmed HIGH via executed material mint; no genuine High demoted; M-03 / decent-06 demoted only after an
  executed harness showed no material value movement; decent-12 routed to NEEDS_HARNESS on a documented source
  obstacle. So L3 produced **0 false-High and 0 false-demotion** on the four harnessed/analysed targets.

## Honest limitations of this prototype
1. **decent-12 not executed.** Its demotion rests on a source argument (addLiquidityEth mints dcntEth to the router,
   not the depositor) rather than a run. The argument is concrete and source-cited, but a full DcntEth+WETH+router
   liquidity harness was not built (prototype scope). Recorded as NEEDS_HARNESS, not a confirmed negative.
2. **External-dep mocks.** DcntEth's `OFTV2` base and UTB's `solmate Owned`/`IV3SwapRouter`/`IERC20` are mocked.
   The mocks reproduce only the inherited ERC20/Ownable/router-interface surface; the **vulnerable logic is the real
   decent code**. A different (faithful) base could in principle change behavior, but the mocked surfaces are
   standard and the vulnerable paths do not depend on the omitted cross-chain machinery.
3. **Honest-custody modeling is a judgment.** "Source-valid custody" for M-03 assumes UTB does not hold user funds at
   the `receiveFromBridge` call point — consistent with the source flow (`performSwap` pulls from msg.sender) and
   with the C4 Medium rating, but a deployment that parks funds in UTB would change the verdict. The harness makes
   this assumption explicit and tests the strongest realistic theft attempts against it.
4. **Single corpus.** L3 is validated only on decent here; generalization to other corpora is unproven (follow-on).
5. **H-02/H-03/H-04** were not harnessed (recall-misses — the blind layer never produced their exact mechanism), so
   L3 says nothing new about them; they remain NEEDS_HARNESS. This is a deep-pass recall gap, not an L3 gap.

## Orchestrator-awareness note
The orchestrator is answer-aware (knows H-01=High, M-03=Medium). The L3 results are **objective executions** (the EVM
decides whether value moves), and the harness setups are source-justified and pre-registered in
`HARNESS_TARGET_MATRIX.md`, which bounds the risk of building harnesses biased toward the known answer. The custody
assumptions are stated explicitly for audit.
