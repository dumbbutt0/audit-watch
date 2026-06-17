# Phase 95 — Seventh fresh sealed-key blind run (higher-density; P91 + v3.1 depth-completion)

## Goal
On a deliberately **higher-density** subject, test whether the P92/P94 depth-trace system improves conversion
while holding the calibrated 0 severity FP (gate frozen `193abf9f`).

## Subject & sealed-key discipline
- **wildcat-2024-08** (Code4rena), commit `7c5d8389…`, **18 in-scope contracts** (~6683 lines; hooks-based
  lending market). Fresh; high-density (1 High + 8 Medium awarded).
- **Sealed-key PRESERVED:** metadata → leads → C-chain bundles → depth-trace outputs → severity outputs →
  `prekey_freeze.json` (`answer_key_opened=false`) all frozen before the findings clone. No web search.

## Pipeline
P91 selection: lens → 81 leads → top-16 ∪ per-contract floor + 3 controls = 27 (floor added 10). C-chain with
v3.1 (completion gate). **11 traced-REJECT** (accounting/value-exit — closeMarket, collectFees, borrow,
rescueTokens, executeWithdrawal, withdrawableProtocolFees, …) with the **P94 completion gate satisfied**
(in-scope `MarketState`/withdrawal-batch reads resolved). **7 controls** rejected. **9 NOT_RUN** — honestly
excluded (deep hooks `AccessControl`/`FixedTermLoan` `on*`, `HooksFactory.deploy*`, sentinel/escrow exceeded
budget on a 6683-line subject; marked NOT_RUN rather than fake-REJECTed, respecting the P94 rule against
incomplete-trace REJECTs).

## C-chain result (frozen pre-key)
- **0 promotions.** 18 REJECTED (11 v3.1-traced + 7 control), 9 NOT_RUN. Safety 0/0/0/0. **0 depth-trace false
  escalations. 0 severity FP.**

## Scoring vs key (1 High + 8 Medium)
| Axis | Result |
|---|---|
| Sealed-key · Safety (4 axes) | preserved · 0/0/0/0 ✅ |
| Severity FP after gate | **0** ✅ |
| Controls | 7/7 rejected ✅ |
| Depth-trace false escalations | **0** ✅ |
| **Conversion** | **0 CLEAN_HIT / 0 STRONG_PARTIAL** ❌ |
| **False-reject of a surfaced true M/H** | **2** ❌ |

- **H-01 (High, over-withdrawal):** the bug is in `executeWithdrawal`'s pro-rata
  `mulDiv(batch.normalizedAmountPaid, status.scaledAmount, batch.scaledTotalAmount)` **when the market is
  closed** (withdrawals execute before all requests are batched + small-request rounding) → invariant
  `sum ≤ normalizedAmountPaid` breaks → last user fails. I **traced `executeWithdrawal` with v3.1 (in-scope
  read resolved) and concluded REJECT** ("pro-rata correct; accounting consistent") — a **confident-but-wrong
  completed trace**, a **FALSE-REJECT of a true High** (missed the closed-market early-execution boundary).
- **M-05 (Medium, role-provider expiry bypass):** I **localized `grantRole`/`_grantRole`** (the
  `newExpiry>oldExpiry || caller==lastProvider` replacement rule) and **classified it a CONTROL**
  ("trusted-provider") → false-clear; the awarded finding is exactly that rule being bypassable
  provider-vs-provider.
- **M-02/M-04/M-07** (FixedTermLoanHooks / role-provider): **NOT_RUN** (honest budget misses). **M-03**
  (repay-fee inconsistency), **M-01/M-06** (close-market lifecycle, traced-REJECTed), **M-08** (`onQueueWithdrawal`,
  below-cutoff): misses.

## Verdict — SAFETY-ONLY PASS *by the letter*, but a NEGATIVE result
Safety + 0 severity-FP + controls clean + 0 depth-trace false escalations hold with conversion 0 (the
SAFETY-ONLY bucket), **but the clean-PASS bullet "no material false-demotion of a surfaced true M/H" is
violated** — H-01 was traced-REJECTed and M-05 false-cleared. This is the most concerning result across all
seven blind runs.

### The critical, honest conclusion about P92/P94
The depth-trace system **improved process rigor and safety** — across four depth-equipped runs it forced
traces, resolved in-scope reads, produced only well-formed abstains, and held **0 false escalations / 0
severity FP**. But it has **not improved conversion** (four consecutive 0-conversion blind runs), and here it
produced a **completed-but-wrong REJECT of a true High**. **The P94 completion gate guarantees a trace is
*done*, not that it is *correct*.** The bottleneck is now unambiguously **blind reasoning correctness /
boundary-case discovery on well-engineered code** — the trace correctly read the in-scope `executeWithdrawal`
math but failed to *imagine the closed-market ordering* that breaks the invariant. That is a model-capability
limit which neither the selection policy, the (validated) severity gate, nor the depth-completion discipline
addresses.

Per constraints: no machinery change (gate frozen `193abf9f`; `localized_depth_trace` unchanged), no post-key
tuning, no retroactive re-score. No promotion → no P84 bundle, no funnel record.

## Next recommendation
The verifier/safety scaffolding is mature and validated; the open problem is **conversion correctness**, which
the discipline layers cannot manufacture. Honest options for P96:
1. **Boundary/adversarial-scenario enumeration aid** — a checklist that, for a localized invariant
   (e.g. "sum of pro-rata withdrawals ≤ batch paid"), forces enumerating *state orderings that could break it*
   (market closed, partial batch, first/last actor, rounding accumulation) before a REJECT — targeting the
   H-01-class "trace read the math but missed the ordering." Regression-anchor it on H-01 + M-05.
2. **Stop treating `grantRole`-style provider functions as controls when the finding is provider-vs-provider**
   — refine the control-classification so a permissioned function with an *inter-principal* trust boundary
   (provider can affect another provider's grant) is investigated, not auto-rejected (targets M-05).
3. Accept the demonstrated ceiling and **report it plainly**: the platform is a strong *safety/rigor* harness
   (0 sev-FP, reject-first, reproducible-handoff) whose blind *conversion* on hardened code is capability-bound;
   value is in disciplined triage + handoff of human-or-tool-surfaced candidates, not autonomous blind discovery.
