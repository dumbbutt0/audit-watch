# P205 — failure cases & honest limitations

1. **Bounded sample missed half the awarded set.** The vultisig C4 contest spans two codebases; my coverage
   manifest sampled only the foundry `src/` ILO contracts, so awarded H-02 (hardhat `Whitelist.sol`) and M-01 (VULT
   token) were never in the blind denominator. This is a coverage gap in *this phase's sampling*, not a recall claim.

2. **The executed negative control does not map to an awarded finding.** v-07 demotes the *by-design*
   `src/base/ILOWhitelist.openToAll`, not the awarded H-02 `Whitelist.sol::checkWhitelist`. It validates the L3
   demotion *mechanism* executably, but a critic can fairly say no *awarded* over-rated finding was demoted by an
   executed harness here. The clean awarded negative control (M-03 cap-bypass, awarded Medium / blind HIGH) was
   identified but blocked by the compile obstacle below.

3. **Positive control HARNESS_INCONCLUSIVE.** All src/ awarded findings are in ILOPool/ILOManager, which need
   solc-0.7.6-compatible OZ 3.4.x + Uniswap v3-core + v3-periphery — none vendored locally (all local OZ/v3 are
   `^0.8.0`+). Assembling the 0.7.6 V3 web exceeded bounded prototype scope (pre-registered risk). So the L3
   HIGH-confirmation side was not re-demonstrated on vultisig (it was on decent in P204).

4. **Severity over-skew reproduced, not corrected.** The blind stack rated 7/8 src/ surfaces ≥HIGH including
   over-rating the awarded-Medium M-03 to HIGH — confirming the P199 frontier on a 3rd architecture. P205 measures
   this; it does not change deep_trace (production untouched, by design).

5. **Orchestrator was answer-aware at scoring (post-freeze).** Mitigated by: blind subagents fresh+key-blind;
   FREEZE 1 before any key open; L3 standard pre-written; harness verdicts are objective EVM executions or documented
   compile obstacles (fabrication_rate=0). Contamination caveat carried from PCS as in P204.

6. **Bounded sample = generalization signal, not full recall.**
