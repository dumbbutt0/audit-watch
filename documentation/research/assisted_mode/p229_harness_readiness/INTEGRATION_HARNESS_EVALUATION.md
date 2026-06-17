# P229 — Integration Harness Readiness Evaluation

> **Type:** read-only assessment + architecture-only design. No code changes, no severity edits, no sync, no
> submit/route/promote. Every claim is cited to a harness `.t.sol` file, an L3 record, or a prior phase result.
> Active audit `size-credit-2024-06-blind`, post-P228.

## Goal

Determine whether **integration-tier harness generation** is the final major blocker to BUG_BOUNTY_READY. The
phase asks us to *assume* candidate generation, precision, and severity are mature and treat harness generation as
the primary unknown — but the final question demands the answer be **defended with evidence from completed phases
rather than assumptions**, so the premise is itself tested against P223/P228 evidence.

Focus: completed harnesses SC-01, SC-03, SC-04, SC-05, SC-08, ZETA-04/07/10/11; deferred SC-11, SC-12, ZETA-02.

---

## 1. Harness Taxonomy

Structural read of all 9 completed L3 harnesses (pocs/p215, p220, p223).

| Harness | Real @src instantiated | How state is reached | Mocks | Lifecycle? | Category |
|---|---|---|---|---|---|
| SC-03 (neg-APR) | 1 (YieldCurveLibrary) | none (pure fn) | 0 | single call | **isolated library** |
| SC-08 (cap bypass) | 1 (CapsLibrary) | 1 constructor field | 0 | single call | **isolated library** |
| SC-01 (ETH sweep) | 3 (Deposit, State, NonTransferrableToken) | constructor field assigns | 1 (MockWETH) | single action | **single-contract stateful** |
| SC-04 (compensate fee) | 4 (Compensate, State, NTToken, LoanLibrary) | ~25 hand-assigned fields + seeded positions | 2 (WETH, PriceFeed) | single action | **single-contract stateful** |
| SC-05 (scaled dust) | 1 (NonTransferrableScaledToken) | constructor (fixed index) | 2 (WETH, MockVariablePool) | single round-trip | **single-contract stateful** |
| ZETA-04 (pause bypass) | 1 (ZetaConnectorNonEth) | constructor roles + pause() | 1 (MintableZetaToken) | 2-step (pause→call) | **single-contract stateful** |
| ZETA-11 (Trident [0]) | 1 (ZetaTokenConsumerTrident) | constructor + mock factory | 2 (factory, router) | 2 paths | **single-contract stateful** |
| ZETA-07 (zero gas fee) | 1 (ZRC20) | FUNGIBLE-prank config + mint | 1 (MockSystem) | config→call | **single-contract stateful** |
| ZETA-10 (reentrancy) | 1 (ZetaTokenConsumerUniV3) + attacker | constructor + funding | 3 (token, WETH, router) | re-entrant multi-step | **multi-contract stateful** |

**Tally:** isolated function **0** · isolated library **2** · single-contract stateful **6** · multi-contract
stateful **1** · lifecycle-driven **0** · protocol-integration **0**.

**Missing: lifecycle-driven and protocol-integration** (and isolated-function, trivially). Decisive fact: **every
harness reaches state by constructor/field seeding and asserts on a single call's return/balance.** None executes
a multi-action protocol lifecycle (deposit→borrow→liquidate→claim); none asserts on intra-transaction event
ordering or an evolving index/price timeline.

---

## 2. Integration Gap Analysis (SC-11, SC-12)

The 9 harnesses prove point behaviors over *terminal* state. SC-11/SC-12 are **temporal** — the bug lives in the
sequence and timeline, not a single call. That is why every existing pattern fails on them.

| Gap | SC-11 (transient REPAID event) | SC-12 (sequential-index claim dust) |
|---|---|---|
| state reconstruction | MED — debt+credit positions, underwater borrower (SC-04 showed hand-seeding works but is heavy) | MED — debt + **multiple** credit positions |
| lifecycle reconstruction | **HIGH** — needs deposit→borrow→price-drop→liquidateWithReplacement; no lifecycle harness exists | **HIGH** — repay@idx0 then claim two credits @idx1<idx2 |
| dependency | MED — collateral token, price feed, lender/borrower (mocks exist) | **HIGH** — MockVariablePool is **fixed-index** (SC-05); needs a **mutable index** |
| event-ordering | **HIGH** — must capture that a `futureValue=0 UpdateDebtPosition` *precedes* the corrective event in one tx via `vm.recordLogs`; no harness asserts emission order | n/a |
| accounting timeline | LOW | **HIGH** — the bug *is* per-claim rounding drift as the index advances between claims |
| oracle timeline | MED — price must drop to make the position liquidatable | LOW |

**Effort (hand-built today):** SC-11 ≈ 8–12 h, SC-12 ≈ 10–14 h — driven by rebuilding lifecycle + timeline +
event-ordering plumbing from scratch each time. ZETA-02 is unrelated/light (2–4 h: copy ERC20Custody into p220
realsrc + ~20-line FoT mock; **harness-tooling gap, not architecture complexity**).

---

## 3. Reusable Harness Scaffold (architecture only — not implemented)

Target: cut lending integration-harness construction from 10–14 h to **1–2 h** by turning the 6 gaps into
reusable primitives. Lives at e.g. `pocs/lib/size/`; consumed by `forge` tests via remapping, reusing the p223
`realsrc/` + `vendor/` wiring already in `pocs/p223/foundry.toml`.

| # | Component | Closes |
|---|---|---|
| 1 | **`SizeHarness` base** — one real `State`; every action library (Deposit, Buy/SellCreditMarket, Repay, Liquidate, LiquidateWithReplacement, Claim, Compensate) exposed as thin externals over the *shared* state. Generalizes SC-04's "real libraries on one State". | state / lifecycle |
| 2 | **`StateFixture` builder** — fluent init of tokens/oracle/fee/risk config with sane defaults, ideally via the real `Initialize` library (state reached the *real* way, not 25 hand-assigned fields). | state reconstruction |
| 3 | **Lifecycle DSL** — `deposit/borrow/repay/liquidate/liquidateWithReplacement/claim(user, …)` helpers invoking the real libraries in sequence; a test reads as a script and state is reached by *executing* actions. | lifecycle reconstruction (the missing category) |
| 4 | **Mock kit** — `MockWETH`, `MockPriceFeed` with **scripted price steps**, `MockVariablePool` upgraded to a **mutable index timeline** (`setIndex`/`advanceIndex`). Reuses p223 mocks. | dependency + accounting + oracle timeline (unblocks SC-12) |
| 5 | **Assertion utils** — `expectEventOrder(...)` over `vm.recordLogs` (unblocks SC-11), credit/balance delta snapshotters, index-drift checker. | event-ordering |
| 6 | **Time/index controller** — advance `block.timestamp` and the pool index together. | accounting / oracle timeline |

**Build effort:** one focused phase (~1–2 days). After that, an integration harness is `StateFixture` + a few
DSL lines + assertions ≈ **1–2 h**.

**Caveat (carried into the verdict):** this scaffold is **lending-specific** — deposit/borrow/liquidate/claim
does nothing for NFT/oracle/router/cross-chain harnesses; an analogous scaffold is needed per architecture.

---

## 4. Counterfactual Readiness

Assume URL intake automated · build hardened · SC-11/SC-12/ZETA-02 harnessed · reusable lifecycle scaffold exists.
Recompute P228's **58/100**:

| P228 driver | Counterfactual effect |
|---|---|
| 2 BLOCKING stages (source, harness) | both removed → large lift |
| URL→L3 friction ~5 → with scaffold ~2 on lending | lift |
| FRAGILE evidence completion | unchanged |
| Architecture coverage: only Lending validated (1/6) | **unchanged — scaffold is lending-specific** |
| Cross-chain recall 0%, NFT/gaming unvalidated | **unchanged** |

**Recomputed score: ≈ 75/100. Verdict: still B — READY_WITH_OPERATOR_SUPERVISION (not A).** The counterfactual
fixes *conversion* (candidate → L3 proof) on lending but leaves *recall breadth* untouched. Aggressive hunting
across arbitrary live programs (NFT, oracle, router, cross-chain) still under-recalls and has no validated harness
scaffold. The variable that flips B→A is architecture-coverage breadth, **not** harness generation.

---

## Final Question — Is integration-tier harness generation NOW the dominant blocker to BUG_BOUNTY_READY?

### Answer: **NO.**

It is the largest *tooling* gap and the dominant blocker **within the validated lending vertical** — but
completed-phase evidence shows it is **not** the dominant blocker to BUG_BOUNTY_READY overall:

1. **Harnessing succeeded whenever a feasible, valuable candidate appeared.** 9 harnesses across 3 protocols
   (SC-01/04/05/08, ZETA-04/07/10/11). The only 3 deferred (SC-11/SC-12/ZETA-02) are **Medium, bounded** —
   proving them changes no severity decision and yields no High/Critical reportable. The harness gap sits behind
   low-value findings.
2. **The platform's actual failures were recall failures, not harness failures.** P223 (blind Size hunt) missed
   liquidation-math H-03/H-04 and oracle M-04 — the biggest named lever was a *liquidation-math lens* (recall).
   P228 measured cross-chain deterministic recall **0%** and NFT/gaming **unvalidated**. None are harness
   problems.
3. **Counterfactual proof.** Solving harness generation (+scaffold, +the 3 harnesses, +URL/build) moves the score
   58→~75 but leaves the verdict at **B**. A blocker whose complete removal does not flip the verdict is, by
   definition, not the dominant blocker. The verdict-flipping variable is **architecture-coverage recall**.

The premise "assume candidate generation is mature" does not survive contact with the evidence: candidate
generation is mature *on lending only*. Integration-tier harness generation is the right **next** phase (highest
single-step ROI; a precondition for validating any architecture) — but it is the dominant blocker for the lending
vertical, **not** for BUG_BOUNTY_READY as a whole.
