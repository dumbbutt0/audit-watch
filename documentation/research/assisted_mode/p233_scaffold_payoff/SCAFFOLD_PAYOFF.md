# P233 — Scaffold Payoff: SC-11 & SC-12 converted to full L3

> **Type:** execution + measurement. Built a minimal Size lifecycle Fixture on the P232 scaffold and converted the
> two P227-deferred integration candidates through the REAL action-library lifecycle (not direct state mutation).
> No production/detector/severity/dashboard/routing edits; real source copied byte-identically into `pocs/`;
> external-only mocks; answer keys never opened.

## Results

| Candidate | l3_status | forge | `decide()` | proof |
|---|---|---|---|---|
| **SC-11** (LiquidateWithReplacement transient REPAID event) | **PASS** | 2/2 | medium | Real lifecycle deposit→open loan→price-drop→liquidateWithReplacement; `vm.recordLogs` proves `UpdateDebtPosition(futureValue=0, original borrower)` fires **before** the corrective `UpdateDebtPosition(futureValue=1000e18, replacement borrower)`. Control asserts the buggy zero-intermediate exists. |
| **SC-12** (Claim sequential-index rounding) | **PASS** | 1/1 | medium | Real lifecycle deposit→open loan→repay@RAY→`advanceIndex` 1.5·RAY→claim. Split (two K claims) pays the lender **3 wei less** than the single 2K claim (whole=3000e18+3, split=3000e18). |
| GATE A (one real loan opens) | **PASS** | 1/1 | — | The make-or-break milestone: deposit + market action create a real DebtPosition + CreditPosition. |

Total: **4/4 forge tests pass** in `pocs/p233/size`. L3 records: `output_research/l3_readiness/SC-11.json`,
`output_research/l3_readiness/SC-12.json` (both PASS, research_only, not routed).

## Part 5 — Effort & scaffold-payoff analysis

| | SC-11 | SC-12 |
|---|---|---|
| Original estimate (P229/P231, hand-built) | 8–12 h | 10–14 h |
| Actual P233 marginal effort *after* the Fixture | small — 1 fix iteration (add the underwater price drop) | small — 1 fix iteration (fund the borrower with borrowAToken, not underlying) |

**The cost moved, exactly as P232 predicted.** The heavy work was the **one-time Size Fixture** (`init` config +
faithful Aave pool/aToken mock + the prank/funding driver helpers + real `Initialize` wiring ≈ 270 lines). Once the
Fixture compiled and GATE A passed (one real loan opens), each bug was a short test plus one debugging iteration.

**Scaffold components reused (P232):**
- `HarnessBase` — `vm.recordLogs`/event-order pattern (SC-11) + actor/`bal()` helpers.
- `MutableIndexPool` — the SC-12 index timeline: `MockAavePool extends MutableIndexPool`, so `advanceIndex` drove
  idx0→idxNow (the fixed-index pool was the original SC-12 blocker).
- `DEPENDENCY_MAP` — dep wiring was a lookup, not discovery (OZ5/Aave/solady copied from `pocs/p223/vendor`,
  forge-std from the global lib).
- **Fixture + Driver seam** — `SizeFixture` is the per-protocol Fixture; `raw*` entrypoints + Driver verbs
  (`deposit/openLoan/repay/claim/liquidateWithReplacement/setPrice/advanceIndex`) drive the real action libraries.

**Manual code still required:** the Size Fixture itself — the irreducible per-protocol piece (deploy/wire/seed real
contracts + a faithful Aave mock). This is amortized: SC-11, SC-12 (and re-expressions of SC-01/04/05/08) all share it.

**Was P232's 1–2h target realistic?** **Per bug: YES** — after the Fixture, each candidate was well under 2 h.
**The one-time Fixture: NO** — it is the multi-hour front-loaded cost P232 explicitly called the per-protocol piece.
So the accurate statement is "1–2 h *per bug after* a one-time per-protocol Fixture," which P232 stated and P233 confirms.

**Evidence quality: IMPROVED.**
- vs the deferred state: SC-11/SC-12 went from `L1_STATIC_TRACE`/`NEEDS_HARNESS` (no runtime proof) to full
  `L3_REAL_CONTRACT_POC` with controls.
- vs prior lending harnesses: SC-01/04 were "single-contract stateful" (hand-assigned State in the constructor).
  P233 is the **first true lifecycle-driven / protocol-integration harness** — state is reached by *executing* real
  actions (Initialize→deposit→market loan→repay/liquidate→claim), filling the two taxonomy categories P229 flagged
  as missing. No fabricated positions; real events; real rounding.

## Severity note (honest)
Both bugs are genuinely **low**: SC-11 is an event-ordering/indexer-integrity issue (on-chain end state correct);
SC-12 is wei-scale rounding dust (3 wei, SC-05 family). `decide()` classifies both **medium** (capped — no clean
attacker beneficiary). The value of P233 is the **scaffold thesis validation**, not the bugs' severity.

## Remaining limitations
- The Fixture uses faithful external-only mocks (Aave pool/aToken, price feed) rather than a forked mainnet Aave;
  sufficient for these bugs (index + token plumbing), but a forked-pool variant would be needed for Aave-specific
  edge cases.
- SC-12's 3-wei delta blends the claim floor with the borrowAToken scaled-transfer rounding (both real, on the real
  path); isolating the pure claim sub-additivity to exactly 1 wei would need index values chosen to null the
  transfer rounding — not worth it for a precision-class finding.
- Live-target **precision** (candidate→confirmed hit-rate on live programs) remains the one unmeasured readiness axis.

## Recommendation: **Targeted precision gate** (then live hunting)
Capability (P230 recall), conversion (P231), efficiency (P232 scaffold), and now the integration tier (P233) are all
proven. The only readiness axis never measured is **precision on live targets** — P230 sealed keys (quality not
hit-rate), and P231/P232/P233 measured conversion/efficiency, not false-positive rate against ground truth. The
highest-ROI next phase is a **targeted precision gate**: measure candidate→confirmed precision (and FP rate) on a
small live/holdout set, then proceed to aggressive live hunting. Building "one more scaffold phase" is not warranted
— the scaffold already converted both deferred integration bugs.
