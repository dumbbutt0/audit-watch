# Phase 81e — Fresh sealed-key BLIND conversion eval (Vultisig 2024-06)

**Result: PASS — the first genuinely repo-key-blind conversion.** On a fresh subject never used in the corpus, with
the answer key sealed until every bundle was frozen, the repaired stack (lens+P81f → deep_pass → hygiene → isolated
key-blind adversarial → severity gate) produced **1 CLEAN_HIT (H-01)** with **0 severity FPs**, controls all clean, and
the adversarial layer correctly **killed a blind over-claim** before it could promote. Eval-only; no machinery changed;
promotes nothing.

## Blindness (the honest scope of "blind")
**Repo-key-blind + web-blind:** the `2024-06-vultisig-findings` repo, `bot-report.md`, and `4naly3er-report.md` were
not opened, and no web search was done, until **after** all 12 leads, A/B/C bundles, adversarial reviews, hygiene and
severity-gate outputs, and the pre-key freeze (`_p81e/_freeze/prekey_freeze.json`, leads `44db9418`, 54 artifacts) were
complete. **Residual:** for any public contest, the findings may be diffusely in model-training data — unquantifiable,
but this subject was *not studied in-project* (unlike Decent in P81a/d), so P81e is **substantially more blind than
P81d**. The training-independent signals (safety, severity-gate mechanics, controls, the key-blind adversarial subagent)
are the trustworthy core.

## Subject + version (resolved before lead generation)
Vultisig 2024-06 (Code4rena), commit `befb1b11702a26ad0018308ef6e82b73683fe1d6`. In-scope = the 21 files in the repo
`scope.txt` (token/whitelist/TWAP-oracle + an ILO launchpad: vesting/refund/liquidity/multicall/payments). Submodules
(forge-std/OZ/v3-core) are standard libs, out of scope — no in-scope version ambiguity.

## Fixed blind selection rule (committed pre-investigation)
Top **12** scoped-contract leads by `surface_score` (desc, ties by candidate_id). Role expectation is **surface-derived**
(onlyOwner setter/callback → control; permissionless value/refund/claim → conversion), never key-derived. P80 partial
rule applied (≥6 fully; all 12 completed).

## The six separated metrics (scored after opening the key: 3 High + 3 Medium)
**1. Blind lead recall.** Selected blind set covered **4/6** awarded surfaces (H-01 `claim`, H-02 `Whitelist`, H-03
`launch`, M-02 `claim`); the lens **surfaced 5/6** (ILOPool.`buy` for M-03 was lens-surfaced at rank 19, below the
top-12 cutoff); **M-01** ("Vultisig should be burnable" = a *missing* function) is **unsurfaceable** by a
function-enumeration lens.

**2. Safety (key-independent) — PASS.** C: 0 SOURCE_FALSE · 0 unsupported READY · 0 HARD_FAIL · 0 detector→finding ·
**0 severity FP**; every C promotion adversarially reviewed.

**3. Mechanism correctness.** 1 correct-mechanism promotion (`claim` → H-01); **0 wrong-mechanism promotions** — my
blind `launch` hypothesis (sandwich value-skim) was **wrong**, but the isolated adversarial reviewer **falsified it**
(the exact-price guard `ILOManager.launch:190` removes the manipulable band) → demoted, never promoted. The adversarial
layer prevented a wrong-mechanism promotion on a blind author error.

**4. Conversion — PASS (≥1).** **H-01 `ILOPool.claim` = CLEAN_HIT**: same function, same mechanism (the single shared
Uniswap position + `collect(max)` routes non-claiming users' fees to `feeTaker`, breaking later claims), same High
impact. Independently confirmed by the key-blind adversarial subagent ("most users won't be able to claim their
fees… high"). This matches awarded **H-01** verbatim in root cause.

**5. Severity-gate behavior.** Prevented the `launch` wrong-mechanism promotion (adversarial FAIL + low impact). **One
honest false-demote:** awarded **H-03** (permissionless launch DoS via single-sided liquidity) — the key-blind reviewer
*identified the price-manipulation DoS mechanism* but rated it "transient griefing (low)", so the gate demoted it
(judge rated it High). This is the **inverse** of P81d's M-04/M-01: there the gate over-demoted true Mediums; here the
*blind impact assessment* under-rated a real DoS. Refinement signal (DoS/grief severity calibration), not a safety
failure.

**6. Controls — clean.** All **5 privileged `onlyOwner` setters REJECTED** by B/C (arm A over-promoted all 5 = 5 FPs;
B/C = 0); `Multicall.multicall` and `Whitelist.receive` → NEEDS_CONTEXT (honest abstain). No control became a promoted
severity finding.

## Pass / fail
**PASS:** C has 0 severity FP; no SOURCE_FALSE / unsupported READY / HARD_FAIL; controls not promoted; ≥1 CLEAN_HIT
(H-01) after opening the sealed key. No answer-key leakage before freeze; source/version unambiguous.

## Honest misses (no overclaim)
- **H-02** (whitelist bypass): right surface led (`Whitelist.receive`) but C **abstained** (NEEDS_CONTEXT) — a blind
  reasoning miss, not a lens miss.
- **H-03** (launch DoS): right surface + mechanism *identified* by adversarial, but **under-severity-demoted**.
- **M-03** (buy NFT-transfer cap bypass): lens-surfaced (`ILOPool.buy`, rank 19) but below the top-12 blind cutoff.
- **M-01** (missing burn function): **unsurfaceable** — a missing-function class the function-enumeration lens cannot
  reach (a distinct future lens, not this one).

## What this proves / does not
- **Proves:** on a fresh, repo-key-blind subject the repaired stack converts ≥1 real awarded High to a CLEAN_HIT with
  correct mechanism and **0 severity FP**, the controls hold, and the key-blind adversarial layer catches a blind
  author over-claim. This is the genuine signal P81d (key-contaminated) could not give.
- **Does not:** eliminate model-training contamination; prove broad recall (4/6 selected, 1 converted); fix the H-03
  DoS severity under-call or the missing-function (M-01) / cutoff (M-03) recall gaps.

## Readiness for PoC handoff
P81e clears the bar it was set: safety-clean + ≥1 genuine blind CLEAN_HIT + 0 severity FP. The repaired stack is **ready
for PoC-handoff testing** on confirmed promotions (the H-01 claim finding is the natural first PoC candidate). Residual
refinements (DoS severity calibration; missing-function & deeper-N recall) are improvements, not blockers.

## Integrity
`_p81e/{subject_metadata,all_leads,leads,arms_summary,scores}.json` · per-lead `{A,B,C}_bundle.json` +
`severity_gate.json` (+ `adversarial_review.json` for the 2 promotions) · `_p81e/_freeze/{prekey_freeze,
phase81e_freeze}.json` · isolated key-blind adversarial subagent `a7140b25`. **No machinery changed** — deep_pass
`57c29fff`, hygiene `b9e18f29`, transitions `2c00069c`, lead_schema `3c57f04e`, abc_eval `5e0d855d`, surface_recall_lens
`29a7b915`, surface_recall_score `fd3c7543`, severity_impact_gate `0b7c54e4` (P81f) all byte-identical; parked detectors
+ value_flow unchanged. Investigation suite green. No-wiring CLEAN. Promotes nothing.

## Recommended next
- **PoC handoff pilot** on the H-01 `claim` promotion (the L3-standard local PoC) — the first time a blind-converted
  finding enters the PoC builder.
- Optional refinements (non-blocking): DoS/griefing severity calibration (recover H-03-class), a missing-function lens
  (M-01-class), and a larger blind-N or score-floor sweep (recover M-03-class).
