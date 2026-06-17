# Assisted-Mode Pilot — P97 M-11 (SecondSwap maxSellPercent)

**Status:** RESEARCH-ONLY. First assisted-mode pilot, proving the P98 pivot. Date: 2026-06-03.
**Subject:** code4rena 2024-12-secondswap @ `6693d9e4`. **Decision: `VALIDATED_FOR_POC_HANDOFF`.**

## Premise
P97's autonomous run **false-rejected** M-11: it traced a sybil "buy-and-resell" framing and concluded the cap
"conserves." P98 repositioned the tool to take the invariant as **human input**. This pilot supplies the correct
invariant and re-derives the mechanism **from in-scope source only** (no answer-key wording).

## Human-supplied invariant
> A vesting/listing holder must not be able to bypass or exceed the intended `maxSellPercent` restriction through
> sale/listing/claim state transitions, schedule inheritance, or accounting paths. Any sellability cap should be
> enforced against the correct holder, schedule, and claim state, and should not be bypassable by ordering or
> state mutation.

## Source-derived mechanism (the break)
The cap is enforced in `VestingManager.listVesting` (`SecondSwap_VestingManager.sol:121-140`):
`require(sold <= bought + maxSellPercent*(currentAlloc+sold-bought)/BASE)`. Two source facts break it:
1. `completePurchase` credits `allocations[buyer][vesting].bought += amount` **unconditionally**
   (`SecondSwap_VestingManager.sol:161-164`).
2. `Marketplace._validatePurchase` has **no buyer≠seller check** (`SecondSwap_Marketplace.sol:387-404`; only
   `require(msg.sender != _referral)`), so a holder can buy their **own** public listing.

**Counterexample (single holder, no sybil):** H lists `p·A` → H self-buys it → `bought += p·A`, which is added at
100% to `sellLimit` while `(currentAlloc+sold-bought)` stays `= A`, so `sellLimit` grows to `2p·A`. Repeating k
self-buy cycles (cost = marketplace fees only; H pays itself the principal back as seller) lifts
`sellLimit = (k+1)·p·A`, letting H eventually sell its **entire** original locked allocation to an external buyer
— bypassing the `maxSellPercent` cap. The cap is enforced against an **inflatable `bought` counter**, not the
original schedule.

## Pipeline result (bundle in `bundle/`)
| Stage | Component | Result |
|---|---|---|
| INPUT | intake schema | accepted (`candidate_invariant` present) |
| TRIAGE | `localized_depth_trace` | `REJECT`? no → **trace complete, concrete_outcome PASS** (cap bypassed) |
| STRESS | `adversarial_ordering_check` | **`PASS_CANDIDATE`** — counterexample breaks the relied-upon invariant (7 orderings recorded) |
| VERIFY | `maximal_consequence` → `severity_impact_gate` (193abf9f) → `hygiene` | consequence medium (no escalation); gate **kept Medium, no FP**; hygiene OK |
| **DECISION** | `validate_candidate_invariant.py` | **`VALIDATED_FOR_POC_HANDOFF`** |
| REPRODUCE | `handoff_generator` (`validation_liveness_counter_scope`) | reject-first scaffold in `handoff/` — `DO_NOT_SUBMIT`, PoC = TODO placeholders, funnel_record PoC/submission `NOT_STARTED` |
| TRACK | `funnel.py` | record `source=assisted`, `supplied_by=human`, `candidate_invariant_present=true`, `assisted_validation_status=VALIDATED_FOR_POC_HANDOFF`, **never SUBMITTED** |

## Pass-condition check (ASSISTED PASS)
- ✅ intake accepted · ✅ invariant traced against source · ✅ wrong-invariant drift avoided (the P97
  conservation framing was re-examined; the real `bought`-inflation path was derived from source) · ✅ reached
  `VALIDATED_FOR_POC_HANDOFF` · ✅ severity gate kept Medium with **no FP** · ✅ funnel shows assisted status,
  not submitted.
- ✅ frozen P97 artifacts untouched; P97 score not rewritten; not claimed as autonomous; no answer-key wording
  used as proof; nothing submitted; severity gate / lens / scanner machinery unchanged.

## Reproduction (executable PoC — added after validation)
The `VALIDATED_FOR_POC_HANDOFF` candidate was then **reproduced executably** against the real in-scope contracts
(`/tmp/p97-secondswap`, `SecondSwap_Marketplace.sol` sha256(first14) `80573b863544a3` = P97 frozen). Foundry PoC:
`M11SelfPurchasePoC.t.sol` (+ `poc_run_output.txt`, `bug_chain.md`).
- **Vulnerable** `forge test --match-test test_M11_SelfPurchaseInflatesBoughtAndBypassesMaxSellPercent -vv` →
  **PASS**: self-purchase allowed (no `buyer != seller` check) → `bought` credited → cumulative `sold` reaches
  the **full allocation A = 5× the 20% cap**; a distinct `externalBuyer` receives real vested tokens for fee cost.
- **Minimal patch** (`require(msg.sender != listing.seller, "SS_Marketplace: no self purchase");` in
  `_validatePurchase`) → `forge test --match-test test_M11_Patch_SelfPurchaseReverts -vv` → **PASS**:
  self-purchase reverts, third-party purchase still works. Source then **restored** + hash re-verified
  (`80573b863544a3`).
- Funnel `ASSISTED-M11` advanced to `POC_REPRODUCED` (reject-first gate satisfied), **submission `NOT_STARTED`**.

## Honest caveats
- This is **not** a blind discovery — the human supplied the invariant. The pilot proves the *validation/handoff*
  path works when the correct invariant is given (exactly the step P97 showed the autonomous stack cannot do).
- The PoC is a self-contained **local fixture** (no fork); no in-scope contract was modified except the
  temporary one-line patch, which was reverted and hash-verified. The repo's own suite is hardhat/TS, so there is
  no in-repo "unrelated tests" run.
- Severity remains **Medium** (cap bypass for fee cost), not escalated; nothing submitted.
- The `PASS_CANDIDATE` rests on a **reasoned source trace**, not an executed test. The handoff scaffold requires
  a human to write the Foundry PoC (L1–L3) before any submission; it is `DO_NOT_SUBMIT` until then.
- Severity is **Medium** (a sell-restriction bypass for fee cost), deliberately not escalated to a fund-loss
  High — the gate kept it Medium with no consequence-tag inflation.
- The handoff PoC scaffold uses the closest existing seed type (`validation_liveness_counter_scope`); its generic
  template hint is not M-11-specific, but the title/summary/source refs are.
