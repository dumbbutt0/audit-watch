# Phase 81d — Keyed live conversion eval (Decent): can the improved stack turn right surfaces into real hits?

**Result: PASS (the meaningful jump) — with three honest caveats.** Feeding the de-noised lead set through the
unchanged P77/P78 stack (deep_pass → hygiene → isolated **key-blind** adversarial review → severity_impact_gate)
produced **≥1 CLEAN_HIT + 2 STRONG_PARTIAL** against the Decent key with **0 severity FPs**, and the controls behaved
(the P81a D2 dust promotion was demoted *live*). This is the first time the full chain converted right surfaces into
correctly-mechanism'd, severity-gated hits. Eval-only; no machinery changed; promotes nothing.

## Three caveats (stated up front — they bound the claim)
1. **Conversion is NOT key-blind.** I saw the Decent key in P81a, so the conversion numbers are a **capability ceiling**,
   not a blind-recall proof. The **trustworthy, key-independent signals** are: (a) the controls + **0 severity FP**
   (mechanical), and (b) the **isolated key-blind adversarial subagent** (`adaa3e5a`, never saw the key), whose
   independent source-only impact ratings were **more conservative** than my contaminated ones and are what drive the
   severity gate here. The genuine blind test is a fresh sealed-key subject → **P81e**.
2. **Source-version correction.** P81b/c had measured Decent on the decent-bridge **HEAD (post-fix)** source; P81d uses
   the **audited commit `7f90fd4`**. On audited source the lens **misses H-01 `setRouter`** (unguarded setter; the
   `admin_config_setter` class `requires_auth_modifier` — blind to the missing-AC case). **Corrected Decent recall =
   8/9 DIRECT** (P81b/c records updated). H-01 is excluded from P81d conversion as a lens-recall miss.
3. **Severity gate has a recall cost.** Fed the key-blind reviewer's conservative impact, it **false-demoted two true
   awarded Mediums** (M-04, M-01) to NEEDS_CONTEXT — see below.

## Set (frozen pre-investigation, `_p81d/leads.json` `2b1425d0`): 9 investigations
6 awarded-surface leads (covering 8/9 findings; H-01 excluded per caveat 2) + 3 controls. Key-informed selection,
disclosed (P81b proved blind surface recall). Blind-rank capture reported separately in P81b.

## The four separated metrics
**1. Safety (key-independent) — PASS.** C: 0 SOURCE_FALSE · 0 unsupported READY · 0 HARD_FAIL · 0 detector→finding ·
**0 severity FP** · all C promotions passed (or were sharpened by) the isolated adversarial review. Arm comparison on
the severity-FP axis is the headline: **A = 2 severity FPs** (over-promotes `swapNoPath` dust + `mintByOwner`
privileged), **B = 1** (catches privileged via the defense ledger but still promotes the `swapNoPath` dust), **C = 0**
(the severity gate is the only thing that removes the last one). This is the direct, mechanical proof of the P81c gate's
value.

**2. Mechanism correctness — strong.** 5/5 promoted awarded leads named the awarded root cause; `redeemEth` was
correctly **REJECTED** (its function is clean — M-05's refund bug lives in `_bridgeWithPayload`, folded into the
`bridge` lead). 0 wrong-mechanism promotions.

**3. Conversion (key-known ceiling) — PASS (≥1).** Under the key-blind impact → severity gate:
| lead | awarded | blind impact | severity-gate final | category |
|---|---|---|---|---|
| `UTB.receiveFromBridge` | M-03 | high | POC_REQUIRED | **CLEAN_HIT** (same fn + missing-AC mechanism) |
| `DecentBridgeExecutor.execute` | H-03 | medium | POC_REQUIRED | **STRONG_PARTIAL** (failed-execute refund misroute) |
| `DecentEthRouter.bridge` | H-04(+H-02/M-02/M-05) | medium | POC_REQUIRED | **STRONG_PARTIAL** (dst-reserve dcntEth fallback) |
| `StargateBridgeAdapter.bridge` | M-04 | low | NEEDS_CONTEXT | demoted (mechanism converted, impact rated low) |
| `UniSwapper.swap` | M-01 | low | NEEDS_CONTEXT | demoted (mechanism converted, impact rated low) |

**4. Severity-FP — 0.** Controls: `swapNoPath` (P81a D2) demoted dust→NEEDS_CONTEXT **live** (A/B both promoted it, C
did not); `mintByOwner` REJECTED (privileged, defense ledger); `swapAndExecute` REJECTED (retrieveAndCollectFees
defended). No Low/QA/dust reached POC_REQUIRED.

## Honest recall cost of the severity gate (new finding)
Fed the **key-blind** reviewer's conservative source-only impact, the gate **demoted two genuinely awarded Mediums**:
M-04 (Stargate fixed-fee — reviewer: `minAmountOut` from the same constant ⇒ *reverts*, not silent loss) and M-01
(UniSwapper stale params — reviewer: `amountOutMinimum` *is* enforced ⇒ revert/stuck, "loss" over-stated). The
mechanism was converted in both, but the gate suppressed the promotion. This is the symmetric risk of the D2 fix: a
strict impact gate that kills dust FPs can also **false-demote true Mediums** when their on-chain impact is
conservatively assessed. A refinement target (impact-assessment calibration), not a safety failure.

## Pass / fail
**PASS (meaningful jump):** safety all-zero incl 0 severity FP · controls behaved · ≥1 CLEAN_HIT/STRONG_PARTIAL with
correct mechanism (M-03 clean; H-03, H-04 strong-partial). **Not FAIL:** no severity FP; not an all-9 miss; no
repeated wrong-mechanism. Bounded by the three caveats above.

## What this does and does not prove
- **Does:** the wired chain (lens → deep_pass → hygiene → key-blind adversarial → severity gate) can take surfaces the
  lens found and produce correctly-mechanism'd, severity-gated promotions with 0 severity FP; the P81c gate
  demonstrably removes the last FP that A/B make; the key-blind reviewer corrects an over-claiming (contaminated)
  author.
- **Does not:** prove blind recall (key-contaminated); prove the severity-gate impact calibration is right (it
  false-demoted 2 Mediums); cover H-01 (lens-recall miss).

## Recommended next
1. **P81e — fresh sealed-key blind conversion test** (the genuinely key-blind proof Decent cannot give): a new contest
   subject, key sealed until bundles frozen, lens → deep_pass → key-blind adversarial → severity gate → keyed score.
2. **P81f (or fold into P81c-bis) — two targeted, generic lens/gate fixes** surfaced here: (a) a **missing-auth-setter**
   signal so `admin_config_setter` also flags *unguarded* state-changing setters (recovers H-01-class bugs); (b)
   **severity-gate impact calibration** so conservative "reverts/estimation" impacts are not auto-demoted below true
   Medium. Both generic (no subject hardcoding).
- Order: 1 leads ✅ → 2 investigate safely ✅ → 3 severity gate ✅ → 4 conversion shown (key-known) ✅ → **P81e blind** →
  PoC handoff.

## Integrity
`_p81d/leads.json` (`2b1425d0`, frozen pre-investigation) · per-lead `{A,B,C}_bundle.json` + `severity_gate.json` ·
`_p81d/{arms_summary,scores}.json` · `_p81d/_freeze/phase81d_freeze.json` · isolated key-blind adversarial subagent
`adaa3e5a`. **No machinery changed** — deep_pass `57c29fff`, hygiene `b9e18f29`, transitions `2c00069c`, lead_schema
`3c57f04e`, abc_eval `5e0d855d`, surface_recall_lens `29a7b915`, surface_recall_score `fd3c7543`, severity_impact_gate
`418738da` all byte-identical; parked detectors + value_flow unchanged. **147 tests pass.** No-wiring CLEAN. Promotes
nothing to production.
