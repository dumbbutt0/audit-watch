# P271 — LIMITATIONS

1. **CALIBRATION, not fresh recovery.** P271 used the post-reveal Wise H-03/H-04 mechanisms to build/calibrate the
   scaffold + checklist. It does NOT claim blind recovery. The real test is P272 (fresh full-path rerun with the
   checklist available, dimensions/mechanisms derived blind pre-reveal).

2. **No full Tier-A runtime built.** A complete deposit→borrow→price-drop→liquidate→bad-debt runtime on the live
   WiseLending stack was not constructed. The calibration showed it was *not needed* for these two specific
   mechanisms (localized accounting asymmetries), but mechanisms that genuinely require cross-contract state
   evolution (interest accrual + oracle drift driving the health factor over time) would still need Tier A. The
   "reusable scaffold" is therefore the **project template + two PoC patterns + the completion checklist**, not a
   one-click full lending simulator.

3. **H-04 is Tier C (faithful reproduction), not the deployed private function.** The exact branch-ordering + real
   cashout formula are transcribed from source; the conversion helper is modeled 1:1. The proven fact (ordering bug
   → over-extraction by `removePct × userShares`) is faithful, but it does not execute the deployed
   `WiseCore._calculateReceiveAmount` (which needs the full stack). One notch below H-03's Tier B.

4. **H-03 harness uses dummy ctor deps.** The bad-debt path touches storage only, so dummy addresses + a 1-fn
   PositionNFTs mock are faithful for THIS path — but the harness is not a fully-wired FeeManager (other FeeManager
   functions would need real deps).

5. **Checklist is calibrated on 2 cases (n=2).** The SET-vs-INCREMENT and guard-ordering items generalized cleanly
   from H-03/H-04, but the checklist's breadth (share conversion, oracle, rounding, etc.) is informed by general
   lending knowledge, not all validated against awarded cases here. It is a hypothesis to be exercised in P272.

6. **No production authority / no severity / advisory only.** Nothing here concludes a finding or sets severity;
   the PoCs prove mechanisms on a (now-revealed) contest for calibration, not for submission.
