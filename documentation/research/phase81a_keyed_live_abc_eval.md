# Phase 81a — Keyed Live A/B/C Eval (Decent 2024-01)

**Result: LIVE-SAFETY PASS · HIT-ACCRUAL FAIL · 1 precision FP (D2).** This is the first *keyed* live measurement of the
P77/P78 verification workflow against a real answer key. The discipline stayed safe under live reasoning, but with my
frozen lead selection it did **not** find Decent's awarded bugs (**0 CLEAN_HIT / 0 STRONG_PARTIAL**) and over-promoted
one source-true-but-unawarded claim. **Readiness does NOT jump from this phase.** Research-only; promotes nothing.

## Objective
P80 proved the workflow survives live reasoning *safely* on Kelp but could not score hit-accrual (Kelp ships no in-repo
answer key). P81a re-runs the exact P80 protocol on **Decent 2024-01**, which ships a sealed Code4rena answer key
(`audits/decent-2024-01-holdout/_sealed_answer_key/report.md`: 4 High + 5 Medium awarded). Goal: measure live
**hit-accrual** (same-function + same-mechanism) and **false-negative recall** against the key.

## Honesty caveats (read first)
- **N=6 leads, one subject, live + non-deterministic** → a survival/quality signal, not statistical proof.
- The negative result is **not softened**: 0 CLEAN_HIT, 0 STRONG_PARTIAL. "I found something plausible" was **not**
  counted as a hit unless it matched the key by same-function + same-mechanism.
- **Hybrid-isolation leakage caveat** (same as P80): arms A/B are my own sequential frozen passes (A authored after I
  read source → not a perfectly cold baseline); only C's adversarial review was an isolated subagent (author≠judge).
- Freeze discipline: `_p81/leads.json` (`eea508c2`) frozen before investigation; all A/B/C bundles + D1/D2 adversarial
  reviews frozen **before** the sealed key was opened (`_p81/_freeze/phase81_freeze.json` attests this).

## The six frozen STATIC_LEADs (`_p81/leads.json`, `eea508c2`)
D1 `UTBFeeCollector.collectFees` (signature) · D2 `UniSwapper.swapNoPath` (access control) ·
D3 `UTBExecutor.execute` (value flow) · D4 `StargateBridgeAdapter.sgReceive` (cross-chain) ·
D5 `UTBFeeCollector.redeemFees` (access control) · D6 `UTB.bridgeAndExecute` (value flow).

## A/B/C decisions (frozen pre-key)
| lead | A baseline | B defense-first | C full (post-hygiene) |
|---|---|---|---|
| D1 collectFees | POC_REQUIRED | POC_REQUIRED | **NEEDS_CONTEXT** (hygiene: missing critical `state_consume_or_check`) |
| D2 swapNoPath | POC_REQUIRED | POC_REQUIRED | **POC_REQUIRED** (adversarial PASS, hygiene clean) |
| D3 execute | POC_REQUIRED | NEEDS_CONTEXT | NEEDS_CONTEXT |
| D4 sgReceive | POC_REQUIRED | NEEDS_CONTEXT | NEEDS_CONTEXT |
| D5 redeemFees | POC_REQUIRED | REJECTED | REJECTED |
| D6 bridgeAndExecute | POC_REQUIRED | NEEDS_CONTEXT | NEEDS_CONTEXT |

A over-promotes 6/6. C promotes only **D2**; hygiene **fail-closed D1** (my D1 ledger never classified the
signature-replay-critical `state_consume_or_check` defense), preventing a 2nd promotion. The isolated adversarial
subagent PASSed both D1 and D2 (recommend POC_REQUIRED) but flagged both as PoC-magnitude-dependent.

## The opened key (post-freeze): 9 awarded findings
H-01 `DcntEth.setRouter` no access control · H-02 missing min-gas LayerZero · H-03 `DecentBridgeExecutor.execute` fail →
funds to random address · H-04 dest router WETH reserves · M-01 `UniSwapper` permanent loss if swap data outdated ·
M-02 `DecentEthRouter.bridgeWithPayload` direct → no fees · **M-03 missing access control on `UTB.receiveFromBridge`
bypasses the fee/signature gate** · M-04 fixed fee calc loss · M-05 `DecentEthRouter` refund stuck in `DecentBridgeAdapter`.

## Strict per-lead scoring (vs key)
| lead | C decision | claimed mechanism | nearest awarded | category |
|---|---|---|---|---|
| D1 collectFees | NEEDS_CONTEXT | signature replay (missing nonce) | M-03 (gate **bypass**) | **ADJACENT** — right area, **wrong mechanism** (bypass, not replay); wrong fn (not receiveFromBridge); not promoted |
| D2 swapNoPath | POC_REQUIRED | missing `onlyUtb` | M-01 / M-03 | **FP** — source-true (public, no onlyUtb) but **not an awarded H/M** (transient/dust drain → Low/QA); over-promoted |
| D3 execute | NEEDS_CONTEXT | leftover native on success | H-03 / M-05 | **ADJACENT** — executor-refund family, wrong contract (UTBExecutor vs DecentBridgeExecutor) + sub-mechanism |
| D4 sgReceive | NEEDS_CONTEXT | cross-chain | M-03 (receiveFromBridge) | **ADJACENT/MISS** — ungated entry was receiveFromBridge, downstream; not led directly |
| D5 redeemFees | REJECTED | access control | none | **REJECT_CORRECT** — redeemFees IS onlyOwner; no awarded finding |
| D6 bridgeAndExecute | NEEDS_CONTEXT | fee binding | M-02 / M-04 | **ADJACENT** — fee theme, specific awarded mechanism not isolated; not promoted |

## Separated metrics (per the discipline)
**1. Safety:** PASS. C: 0 unsupported READY · 0 SOURCE_FALSE · 0 HARD_FAIL · 0 detector→finding. C rejected D5,
fail-closed D1/D3/D4/D6 (D1 via hygiene catching an incomplete ledger). A over-promoted 6/6 (incl D5, which is
onlyOwner). No STOP condition (no C SOURCE_FALSE / unsupported READY).

**2. Mechanism correctness:** Mixed. C's one promotion (D2) was the correct *mechanism class* (missing access control)
but on the *wrong function* relative to the awarded missing-AC bug (M-03 = `receiveFromBridge`, not `swapNoPath`). D1's
mechanism was wrong (replay vs the awarded gate-bypass). C had **0 WRONG_MECHANISM promotions** only because it
abstained on the mis-mechanism'd leads — safety, not mechanism mastery.

**3. Hit-accrual:** **FAIL — 0 CLEAN_HIT / 0 STRONG_PARTIAL** out of 9 awarded findings. No frozen lead matched an
awarded finding by same-function + same-mechanism. Closest were ADJACENT near-misses (D1/D2/D4 ↔ M-03; D3 ↔ H-03).

**4. Live-agent readiness:** PARTIAL → unchanged. Discipline ran live and fail-closed correctly (incl. hygiene catching
my own incomplete ledger), but produced zero real hits and one severity-level over-promotion. **Readiness does not jump.**

**5. Precision / severity failure:** **1 FP — D2 (`swapNoPath`).** This is the new failure mode P81a surfaces:
source-true (the function genuinely lacks `onlyUtb`) yet **not an awarded H/M** because its real impact is
transient/dust (Low/QA). The workflow promoted it to POC_REQUIRED — an over-promotion at the **severity/impact** level,
not a hallucination (so not a SOURCE_FALSE / not a STOP condition). The promotion-time pipeline has no severity/impact
gate to demote dust-impact-but-source-true claims.

## Pass / fail
- **Live-safety: PASS** (0 unsafe promotions; all C terminals source-backed; A→B→C unsafe strictly decreasing).
- **Hit-accrual: FAIL** (0 CLEAN_HIT / 0 STRONG_PARTIAL vs 9 awarded).
- **Precision: 1 FP** (D2 over-promotion at severity).
- **Readiness does NOT jump.**

## Bottleneck diagnosis
- **Primary: lead selection + mechanism naming.** The awarded surfaces were *reachable* but un-led or mis-named: M-03's
  `UTB.receiveFromBridge` and H-03's `DecentBridgeExecutor.execute` were never the subject of a lead, and D1 named the
  wrong mechanism (replay) for the right theme (fee/signature-gate bypass). High recall at the *review* layer is moot
  when the *lead* layer points at the wrong functions.
- **Secondary: severity/impact gating** (the lone D2 FP). One occurrence here vs five lead misses → primary > secondary
  on this subject.

## Recommended next
1. **P81b — lead-generation recall (first).** Fix the upstream that actually capped P81a: enumerate every public/external
   entry + every executor-refund / fee-gate / gate-bypass path so leads land on the awarded surfaces (e.g.
   `receiveFromBridge`, `DecentBridgeExecutor.execute`). Re-key against Decent and measure whether hit-accrual moves off
   zero. (Per the user's condition: lead misses (5) outnumber severity FPs (1) here, so recall comes before the gate.)
2. **P81c — severity/impact gate (second).** A promotion-time check that demotes source-true-but-dust-impact claims (D2)
   below POC_REQUIRED, closing the precision FP — to be prioritized ahead of P81b only if a later subject shows D2-style
   severity FPs recurring more often than lead misses.
- North star unchanged: high recall at the lead layer, near-zero false-positive promotion at the review layer.

## Integrity
`_p81/leads.json` (`eea508c2`) · `_p81/D{1..6}-*/{A,B,C}_bundle.json` + D1/D2 `adversarial_review.json` ·
`_p81/scores.json` · `_p81/_freeze/phase81_freeze.json` (key-opened-post-freeze attestation). Modules byte-identical to
P79/P80 (deep_pass `57c29fff` · hygiene `b9e18f29` · transitions `2c00069c` · lead_schema `3c57f04e` · abc_eval
`5e0d855d`); parked detectors (`f9ec0bff` / `2337edc2` / `e72b9994`) + value-flow (`aca9125a`) byte-identical. No new
detector logic, no module edits, no production wiring, no finality language. **Promotes nothing to production.**
