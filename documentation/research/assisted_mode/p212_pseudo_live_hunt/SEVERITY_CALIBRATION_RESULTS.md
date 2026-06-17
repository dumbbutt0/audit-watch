# P212 Stage 2 — severity calibration results

| finding | my calibrated | official | delta |
|---|---|---|---|
| SOPH-03 / 003-H (stETH depositStEth DoS) | Medium | **High** | **UNDER (-1)** |

- exact: 0 · over-rated: 0 · **under-rated: 1** · unscored (missed): 4.
- The single confirmed finding was under-rated. Root cause of the miscalibration: the L3 demotion rule
  *"DoS/griefing → Medium unless L3 proves permanent material loss/insolvency"* treated a **permanent DoS of a core
  deposit path** as Medium. Sherlock explicitly judged it High ("can cause asset loss or deposit DoS … should be
  classified as high risk"; escalation accepted → upgraded to High).
- **Direction note:** the whole P199-P211 campaign targeted *over*-rating; the first live test exposed the opposite
  failure — *under*-rating a genuine High by a too-blunt DoS→Medium floor.
