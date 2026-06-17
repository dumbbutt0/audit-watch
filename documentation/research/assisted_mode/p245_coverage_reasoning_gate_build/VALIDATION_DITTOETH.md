# P245 — Second Validation: DittoETH (diamond/facet generalization)

**Validation only — no gate changes.** Confirms the default-off coverage + reasoning-depth gate built in
P245 generalizes from NextGen's flat-contract layout to the P241 **diamond/facet** failure mode. Ran
against the **real dittoeth manifest** (`audits/dittoeth-2024-03-holdout/output/coverage_manifest.json`)
loaded into a tmp workspace via `get_audit_root` redirect — **zero writes to any audit; active audit
`size-credit-2024-06-blind` never switched.** Raw data: `_validation_dittoeth_data.json`,
`_triage_dittoeth_data.json`.

## Metrics
| Metric | Value |
|---|---|
| Total manifest items | 711 |
| In-scope items | 104 |
| Critical items (in-scope) | 49 |
| READ_FULL required (= critical in-scope) | 49 |
| Blocked items (Arm B, enforced) | 44 |
| False blocks (diamond infra / interfaces) | **0** |
| Awarded in-scope finding loci forced into coverage | redemption-dispute (proposeRedemption / disputeRedemption / claimRedemption), liquidation (`liquidate`, `_fullorPartialLiquidation`), orders (`createBid`, `createLimitShort`), oracle libs (LibOracle, UniswapOracleLibrary) |
| `coverage_enforced_recall_gain` (estimate) | see below |
| Operator burden | 49 critical / 104 in-scope = 47% (lower than NextGen's 75%) |

## Q1 — Does enforce_read_completeness block triage on unread critical facets/selectors? **YES**
Arm B (`--enforce-read-completeness`) → **BLOCK (rc 1)**: 44 of 49 critical in-scope items blocked (only
the one "already-read" facet, BridgeRouterFacet's 5, pass as READ_FULL). Blocked by file:

| File | Blocked | File | Blocked |
|---|---|---|---|
| PrimaryLiquidationFacet.sol | 8 | RedemptionFacet.sol | 4 |
| LibOracle.sol | 8 | BidOrdersFacet.sol | 3 |
| LibOrders.sol | 8 | UniswapOracleLibrary.sol | 3 |
| ExitShortFacet.sol | 6 | LibSRUtil.sol | 2 |
| | | ShortOrdersFacet.sol / LibBridgeRouter.sol | 1 / 1 |

## Q2 — Does the critical-item predicate correctly identify diamond/facet surfaces? **YES**
`read_completeness_utils.is_critical` flags facet entrypoints via the existing field-based predicate
(state-mutating public/external, privileged, oracle/token/liquidation tags). Forced in-scope facet loci:
- RedemptionFacet: `proposeRedemption`, `disputeRedemption`, `claimRedemption`, `claimRemainingCollateral`
- PrimaryLiquidationFacet: `liquidate`, `_performForcedBid`, `_fullorPartialLiquidation`, `_liquidationFeeHandler`, …
- ExitShortFacet: `exitShort`, `exitShortWallet`, `exitShortErcEscrowed`
- BidOrdersFacet: `createBid`, `createForcedBid`; ShortOrdersFacet: `createLimitShort`

The predicate also fires on **out-of-scope** facets (ShortRecordFacet `increaseCollateral`/`combineShorts`,
OrdersFacet `cancelShort`) — i.e. it *recognizes* the facet surface; scope (below) is what gates them out.
No diamond-specific tuning was required.

## Q3 — Are the P241 missed finding loci inside the forced-read set? **YES for in-scope; scope-bounded otherwise**
The dittoeth P241 award themes were short-record management, linked-list/order corruption, and
**redemption-proposal disputes**. Of these, the redemption-dispute area maps to **RedemptionFacet, which is
in-scope and fully forced** (proposeRedemption/disputeRedemption/claimRedemption all blocked until
READ_FULL). Order/liquidation surfaces (BidOrders, ShortOrders, PrimaryLiquidation, LibOrders) are
in-scope and forced. The **short-record** theme maps to ShortRecordFacet, which is **out of scope per the
contest `scope.txt`** (see the caveat) — so the gate correctly does not force it. This is consistent with
P243's documented dittoeth attribution caveat (theme-level, >10 MB report).

### Scope-reach caveat (important, and NOT a gate bug)
The manifest faithfully follows `audits/dittoeth-2024-03-holdout/contracts/scope.txt`. In-scope facets =
{BidOrders, BridgeRouter, ExitShort, PrimaryLiquidation, Redemption, ShortOrders}; ShortRecordFacet,
OrdersFacet, SecondaryLiquidationFacet, Vault/Yield/View/Owner facets are `not listed in scope.txt`. The
coverage gate enforces over **in-scope** items, so its reach is **bounded by scope correctness** — a
property of the scope layer (`scope.txt` + `build_coverage_manifest.py`), not of the gate. The gate forces
every awarded *in-scope* facet locus; it cannot (and should not) force surface the contest excluded.

## Q4 — False blocks on non-critical wrappers/interfaces? **NONE**
`false_blocks_on_diamond_infra_or_interfaces = []`. DiamondLoupeFacet, DiamondEtherscanFacet,
DiamondCutFacet, and interface files contribute **0 critical items** (view getters / non-mutating), so the
diamond plumbing is never blocked. The non-critical advisory-warn count was 0. This is the key diamond
precision result: the gate targets real facet logic, not the proxy/loupe scaffolding.

## Q5 — Does the reasoning-depth gate preserve sensitive rejected candidates? **YES**
`triage_write.main()` (flag on) over dittoeth-flavored rejections:
- DT-101 — RedemptionFacet.disputeRedemption dispute-window abuse, **no depth record** → **rerouted to
  human_review_queue (needs_depth)**, area "diamond facets" detected, all 6 fields flagged missing,
  candidate preserved (not silently rejected).
- DT-102 — LibOracle staleness, **complete depth record** → stays rejected (allowed).
- QA-101 — gas (non-sensitive) → unaffected.

## Q6 — Does default-off preserve existing workflow? **YES**
Arm A (flag off) → **PASS (rc 0)**, `enforced:false`; identical to the pre-gate behavior on a
fully-dispositioned manifest. (Confirmed broadly by the 17 pre-existing coverage tests staying green in the
build phase.)

## coverage_enforced_recall_gain (estimate, answer-key/theme-anchored; read ≠ detect)
Under the frozen P241 system the in-scope facets were not read in full → recall gain on them was
structurally **0**. The gate forces all 44 unread in-scope critical items, which makes the **redemption-
dispute** award area (RedemptionFacet) and the liquidation/order/oracle surfaces reachable for the
specialist. As with NextGen, the gate forces the *reading* (necessary precondition); realized detection is
bounded by the ~60% full-read recovery anchor from P243. Item-level, the redemption-dispute cluster (4
loci) + liquidation/oracle surfaces are the high-value fraction of the 44 forced reads; the remainder is
supporting facet/lib surface. The honest signal: **the awarded in-scope loci are 100% inside the forced
set, and were 0% read under the frozen system.**

## Verdict

# A — GENERALIZES_TO_DIAMOND_FACETS

The critical predicate identifies diamond/facet surfaces with no diamond-specific tuning; enforcement blocks
the unread in-scope facet entrypoints (including the P241 redemption-dispute loci) with **0 false blocks on
diamond infra/interfaces**; the reasoning-depth gate preserves sensitive facet rejections; and default-off
preserves the workflow. The one caveat — coverage reach is bounded by `scope.txt` — is correct behavior of
a separate (scope) subsystem, not a gate limitation, and matches P243's documented dittoeth scope/report
caveat. No gate change was required; no stop-condition triggered.
