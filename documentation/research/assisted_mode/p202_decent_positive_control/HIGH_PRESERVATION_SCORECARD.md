# P202 — High-preservation scorecard (decent-2024-01)

The axis P200/P201 could never test: does the refined gate **confirm genuine contract-level Highs**? Calibration
authored by a **fresh firewall subagent** (FREEZE 2 `90cf2a4f`); awarded key opened only after both freezes.

## Awarded Highs (4) → blind mechanism match → calibrated label
| awarded High | blind surface | match quality | calibrated label | outcome |
|---|---|---|---|---|
| **H-01** Anyone can set DcntEth Router → mint/burn | decent-09 | **strong/exact** | **HIGH_CONFIRMED** | ✅ **genuine High confirmed** |
| H-02 Missing min-gas (LayerZero) → dest exec fails | decent-10 | partial (gas/LZ) | NEEDS_HARNESS | ◑ not demoted; routed to harness |
| H-03 DecentBridgeExecutor.execute fail → funds to random addr | decent-13 | same-surface, diff mechanism | NEEDS_HARNESS | ◑ recall-miss on exact mechanism; not demoted |
| H-04 Destination lacks WETH reserves → user loses tx | decent-11 | partial (reserve fallback) | NEEDS_HARNESS | ◑ not demoted; routed to harness |

## Headline
- ✅ **The High-confirmation path works.** The gate, applied by a fresh uncontaminated subagent, **confirmed a
  genuine permissionless-theft High (H-01)** — the first positive confirmation in the campaign (P201 had 0
  HIGH_CONFIRMED / 0 matched contract-Highs).
- ✅ **Zero genuine Highs demoted to Medium/None.** H-02/H-03/H-04 (partial / same-surface / recall-miss matches)
  were routed to **NEEDS_HARNESS**, not Medium — the acceptable "needs a test to settle severity" middle, not a
  false demotion.
- **Caveat:** only **1 of 4** awarded Highs (H-01) was matched by mechanism *strongly enough to confirm*; the other
  3 are partial/recall-miss matches (deep-pass recall limitation), so they could not be confirmed-or-refuted on
  mechanism — they were correctly held at NEEDS_HARNESS rather than demoted.
- (`metrics.json` loosely credits decent-12 as an H-04 confirm; conservatively decent-12's HIGH_CONFIRMED is on an
  **unawarded** double-withdrawal mechanism, not H-04 — see FAILURE_CASES. The clean confirmed genuine-High is H-01.)

## Verdict on this axis
**High preservation: PASS (demonstrated).** No genuine contract-High was demoted; one was positively confirmed.
This is the first out-of-sample evidence that the refined gate can preserve/confirm genuine Highs.
