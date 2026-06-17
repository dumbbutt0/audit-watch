# Phase 87 — Third fresh sealed-key blind run (validate P86 calibration)

## Goal
Confirm the **P86 severity calibration** did not regress blind recall / mechanism conversion / true-Medium-High
retention, while preserving the strict **0-severity-FP** bar. Fresh subject, no post-key tuning.

## Subject & sealed-key discipline
- **traitforge-2024-07** (Code4rena), commit `72077d0a`, **6 in-scope contracts** (~1327 lines). Fresh — not
  in the prior corpus.
- **Sealed-key PRESERVED:** metadata → leads → all C-chain bundles → adversarial → severity-gate →
  `prekey_freeze.json` (`answer_key_opened=false`) were all frozen **before** the findings repo was cloned. No
  web search; `4naly3er-report.md` / README never opened. Severity gate under test = P86 `e7d298561d29e61c`.

## Pipeline (as run)
Repaired lens → 54 leads over 6 contracts → predeclared frozen set **8 conversion + 3 controls** → C-chain
(`deep_pass` → `hygiene_validate` → isolated **key-blind adversarial** subagent → **P86 severity gate**) →
freeze → open key → score.

## Blind result (frozen pre-key)
- **1 kept promotion:** `TraitForgeNft.mintWithBudget` — Medium, concrete `denial_of_asset_movement`,
  adversarial **PASS**. (Gate **kept** it ⇒ P86 did not over-demote a real liveness Medium.)
- **1 P86-demoted:** `EntityForging.forgeWithListed` (overpayment excess stuck) — my blind read = Low/bounded
  ⇒ gate demoted to NEEDS_CONTEXT.
- **9 rejected** (6 conversion by-design/footgun + 3 controls rejected at DEFENSE_TRACED).
- Safety: 0 SOURCE_FALSE · 0 unsupported-READY · 0 HARD_FAIL · 0 detector→finding.

## Scoring vs key (6 High + 19 Medium awarded)
| Axis | Result |
|---|---|
| Sealed-key discipline | **Preserved** |
| Investigation safety | 0 / 0 / 0 / 0 ✅ |
| **Severity FP after P86 gate** | **0** ✅ (the bar held) |
| Controls | **3/3 rejected**, clean ✅ |
| Conversion | **1 CLEAN_HIT — H-01** `mintWithBudget` (verbatim: global `_tokenIds` vs per-gen `maxTokensPerGen`, L215; budget-mint bricked after 10000) ✅ |
| Mechanism correctness | 2/2 promotions correct mechanism, 0 wrong-mechanism |
| **False demotions** | **2** ⚠ — see below |

**False demotions (both UNDER-rating direction):**
1. **`forgeWithListed` = M-18 (awarded Medium)** — I matched the mechanism but my blind impact read called it
   "self-inflicted/avoidable" (Low), so the P86 gate demoted it. M-18 is Medium because of an **involuntary**
   fee-reduction race (fee lowered between submit and execute → excess stuck) that I didn't consider. An
   impact-assessment depth miss exposed as a false demotion (the gate behaved per policy on a Low/no-concrete
   input).
2. **`mintWithBudget` = H-01 (awarded High)** — kept, but I + the isolated reviewer **under-rated** it Medium
   ("`mintToken` still works, no fund loss"); judges = High.

**Honest misses** (depth/selection): H-03 (NukeFund `devShare=msg.value/taxCut` wrong % when `taxCut` changed —
I dismissed as admin-footgun; awarded High), M-03 (DevFund claim-then-mint), M-10/M-16/M-17 (nuke
precision/slippage/`isApprovedForAll` — I rejected nuke as by-design), and the EntropyGenerator / generation-
internals highs (below the selected-lead cutoff). Surface recall over the full 25 H/M set is partial.

## Verdict — QUALIFIED PASS
Meets **every strict clean-PASS bullet** (0 SOURCE_FALSE / 0 unsupported-READY / 0 HARD_FAIL / **0 severity-FP
after the P86 gate** / controls 3/3 clean / ≥1 CLEAN_HIT = H-01) **and** reaches **Strong-PASS mechanics** (the
P84 generator produced a reject-first `DO_NOT_SUBMIT`, un-promotable bundle for the best candidate). **Qualified**
by two honest, non-critical calibration caveats — **both in the under-rating direction** (M-18 false-demoted;
H-01 severity under-rated).

### What this says about P86
- ✅ **No regression of the bar it targets:** 0 severity FP held; no new over-demotion of P86's class; the
  headline **true-High (`mintWithBudget`) was retained** as a kept promotion.
- ⚠ **The other direction is still open:** under-rating / false-demotion of liveness + involuntary-loss
  Mediums (the **P81e-class** problem) recurred twice. P86 was scoped to the over-rating direction, so this is
  *unaddressed*, not a *regression*.

Per constraints: **no machinery change during P87, no post-key tuning, no retroactive re-score.** The frozen
blind result stands.

## PoC handoff
`mintWithBudget` (CLEAN_HIT) → P84 generator → `_p87_traitforge/poc_handoff_H01/`: `POC_HANDOFF_STARTED`, both
reproduced/submission gates **False**, verdict **DO_NOT_SUBMIT**, `reject_first_ok=True`. No executable PoC
reproduced (not fabricated). **Taxonomy gap #2:** H-01's class (invalid-validation / counter-scope liveness)
has **no** fitting P84 type; bundle generated with the closest type only to exercise reject-first mechanics.
Funnel record `traitforge-2024-07:P87-H01` = `POC_HANDOFF_STARTED`, submission `NOT_STARTED`, never SUBMITTED.

## Integrity
Severity gate stayed at the P86 hash `e7d29856` (no P87 change); deep_pass `57c29fff` / hygiene `b9e18f29` /
surface_recall_lens `29a7b915` / funnel `720e9092` / handoff_generator `9c2c89cb` byte-identical. Prior frozen
artifacts (P81e/P82/P83/P84/P85/P86) unmutated. 174 tests pass. No-wiring grep CLEAN. PoC source cloned to
`/tmp` only.

## Next recommendation
**P88 = false-demotion / under-rating calibration (the *other* direction).** Two blind runs (P81e H-03, now
P87 H-01 + M-18) show the open gap is *under*-rating liveness/DoS and involuntary-loss Mediums. Add: (a) a
"liveness / denial-of-asset-movement" elevation so a proven permanent function-brick is not under-rated below
its awarded tier; (b) an involuntary-vs-self-inflicted distinction so a race-induced stuck-fund (M-18 class)
keeps as Medium; (c) a P84 "validation_liveness / counter_scope" finding type (taxonomy gap #2). Then a P89
fourth blind run to confirm both directions are calibrated without reintroducing severity FPs.
