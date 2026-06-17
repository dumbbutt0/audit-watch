# Phase 97 — Final sealed-key decision run (SecondSwap 2024-12)

**Status:** RESEARCH-ONLY. Eighth fresh sealed-key blind run. **Decision run, not a repair phase.**
**Date:** 2026-06-03. **Subject:** code4rena 2024-12-secondswap @ `6693d9e4` (7 in-scope contracts, 1823 lines).
**Answer key:** 3 High + 20 Medium (code4rena.com/reports/2024-12-secondswap), opened **only after** all
artifacts + `prekey_freeze.json` (`answer_key_opened=false`) were frozen.

## Headline
**NEGATIVE result — does not meet clean PASS. The explicit STOP condition is met → pivot.**

- ✅ **1 genuine CLEAN_HIT:** F1 → **M-14 "Incorrect Referral Fee Calculations"** (Medium). `_handleTransfers`
  computes `referralFeeCost` but never transfers it to `_referral`, and `feeCollectorTotal` doesn't subtract it
  (the would-be referral reward is silently absorbed by `feeCollector`; `referralFeeCollector` is unused). An
  isolated **key-blind adversarial review** confirmed it Medium and correctly flagged it as protocol-surplus,
  not user fund loss.
- ✅ **Safety stack held:** 0 SOURCE_FALSE · 0 unsupported-READY · 0 HARD_FAIL · 0 detector→finding · controls
  3/3 rejected (+~10 other onlyAdmin setters) · NOT_RUN = 0 · **0 adversarial-ordering false escalations**.
- ❌ **1 probable severity FP:** F2 (Whitelist.`whitelistAddress` permissionless self-registration) was promoted
  Medium/POC_REQUIRED but matches no awarded finding. The contract has **no curated-add function at all**, so
  open self-registration up to a seller-set cap is almost certainly **by design** — the "private-not-private"
  reading is a probable over-claim. Trips the strict 0-FP bar.
- ❌ **Three completed-but-wrong false-rejects of true HIGHs** (the decisive result):
  - **H-01** (listing order affects claimable) — I localized the exact mechanism (the VestingManager holds one
    aggregated vesting whose `stepsClaimed` is set by the **first** lister and is stale for later listers;
    buyers inherit `manager.stepsClaimed`) and concluded **REJECT** because **token-sum conserves**. Wrong: the
    bug breaks **per-buyer claim-schedule correctness**, not token-sum.
  - **H-02** (sell+repurchase premature unlock) — I traced the sybil sell/repurchase ordering only for the
    `maxSellPercent` cap and concluded "no bypass"; I missed that repurchase **resets** the buyer's
    `stepsClaimed` to the manager's stale value.
  - **H-03** (incorrect `releaseRate`) — my **F4**: I localized the exact formula
    (`releaseRate = totalAmount / numOfSteps`, ignoring `stepsClaimed`) but rated it **bounded/Low** (the
    final-step branch trues up). Judges rated it **High**.
  - plus **M-11** (`maxSellPercent` bypass) — explicitly traced and rejected as "conserves".

## Why P96 did not help (the core finding)
P96's `adversarial_ordering_check` behaved **exactly as specified**: on the mechanism underlying H-01/H-02/M-11
it returned `REJECT_CONFIRMED` after 6 orderings, with **0 false escalations**; on F4/H-03 it returned
`REJECT_CONFIRMED` after 5. But it confirmed the **wrong** rejects — because I supplied the
`relied_upon_invariant` **"token sum is conserved"** (which *is* preserved) and orderings that probe *that*
invariant. The check faithfully verified the invariant it was given; the invariant was simply the wrong one.

> **The capability bottleneck is one level upstream of every advisory gate: selecting the correct invariant and
> discovering the breaking ordering. A forced adversarial-ordering enumeration is defeated by enumerating
> against a true-but-irrelevant invariant.**

This is the P95 ceiling, now confirmed deeper. P92/P94 proved a trace can be *done* but *wrong*. P96 proved an
adversarial-ordering enumeration can be *complete* but aimed at the *wrong invariant* — and still rubber-stamp a
wrong REJECT.

## Contributing factor: lens-recall gap
The surface lens scored the **economic core** (`spotPurchase`/`listVesting`/`completePurchase`) at **1** (only
`auth_boundary` matched; `value_exit`/`fee_path` not tagged on the transfer body) and over-scored admin/fee
setters at **5**. So top-16 ∪ per-contract-floor selected mostly setters; the bug-bearing functions were reached
only **transitively** during C-chain tracing. Same P81b/P91 bias, more severe here. (The false-rejects happened
on the transitively-reached mechanisms — so deeper selection alone would not have fixed correctness.)

## Decision (per the pre-registered rule)
P97 has completed-but-wrong REJECTs of true Highs **and** a severity FP → the explicit stop condition is met.

**Recommendation: STOP pursuing fully autonomous blind discovery.** Formally reposition Audit-Watch as a
**high-discipline assisted audit triage / validation / PoC-handoff / submission-readiness system** — the role in
which it is demonstrably strong:

- **0 severity-FP severity calibration across 8 sealed-key runs** (P86/P88 gate frozen `193abf9f`);
- clean privileged-control rejection and **reject-first discipline** (no fabricated passes);
- the **P81e → P82** end-to-end blind-hit → executable Foundry PoC handoff (Vultisig H-01);
- well-formed abstains, 0 detector→finding, 0 SOURCE_FALSE across the depth-equipped runs;
- and here, a clean **Medium CLEAN_HIT** plus a correctly-scoped key-blind adversarial review.

What it is **not**, on hardened/well-engineered code: a reliable autonomous discoverer of the *correct
invariant* for subtle accounting/lifecycle Highs. Five consecutive depth-/ordering-equipped blind runs (P91,
P93, P95, Kleidi, P97) produced 1 Medium conversion and repeated completed-but-wrong rejects on Highs.

## Ceiling note (honest)
Across P81e–P97 the platform's **safety, calibration, and handoff** properties are real and repeatable. Its
**autonomous blind-conversion** ceiling is a **reasoning-correctness** limit — invariant selection and
adversarial-ordering *discovery* — that no advisory gate (depth-trace, completion gate, maximal-consequence,
adversarial-ordering) has moved. The honest, evidence-backed position is to deploy it as an **assistant to a
human auditor** (triage, validation, calibration, PoC scaffolding, submission-readiness), not as a standalone
discoverer.

## Constraints honored
No machinery change · no post-key tuning · no retroactive re-score of prior phases · no frozen-artifact mutation
· no submission written · no production wiring · dashboard/funnel not set to SUBMITTED. `severity_impact_gate`
`193abf9f`, `localized_depth_trace` `86f944e5`, `maximal_consequence_check` `5a5aa996`, `surface_recall_lens`
`29a7b915`, `hygiene_validate` `b9e18f29`, and the P96 `adversarial_ordering_check` all unchanged this phase.

## Deliverables (`documentation/research/_p97_secondswap/`)
`subject_metadata.json` · `leads.json` (inclusion_source) · `machinery_outputs.json` (depth-trace +
adversarial-ordering + maximal-consequence + severity) · `hygiene_outputs.json` · `adversarial_review.json` ·
`arms_summary.json` (per-lead dispositions) · `prekey_freeze.json` (sealed) · `scores.json` (post-key).
