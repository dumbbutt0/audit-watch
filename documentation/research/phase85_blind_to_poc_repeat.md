# Phase 85 — Second fresh sealed-key blind→PoC run through the P84 generator

## Goal
Prove the end-to-end pipeline repeats on a fresh subject (not Vultisig): blind lead selection → C-chain
investigation → isolated key-blind adversarial review → severity gate → keyed scoring after freeze → PoC
handoff via the P84 generator. Not a mass scan, not a production promotion.

## Subject & sealed-key discipline
- Subject: **munchables-2024-07** (Code4rena), commit `e9056afd…`, single in-scope file
  `src/managers/LandManager.sol` (347 lines, solc 0.8.25). Fresh — not in the prior project corpus.
- **Sealed-key discipline PRESERVED:** subject metadata + source hash frozen before the lens; leads frozen
  before investigation; all C-chain bundles + `prekey_freeze.json` frozen **before** the findings repo was
  cloned. No web search; the `4naly3er-report.md` / `bot-report.md` / README known-issues were never opened.
  Residual model-training contamination acknowledged (public contest) — trustworthy core = safety /
  severity-gate / controls / isolated key-blind adversarial.

## Pipeline (as run)
1. Lens (`surface_recall_lens`, self-test green / machinery unchanged) → 8 leads over the single contract.
2. Predeclared rule: full coverage of all 8 external entrypoints; 2 privileged-modifier functions designated
   controls. Frozen `leads.json` (hash `ef0bb41c`).
3. C-chain per lead: `deep_pass.run` → `hygiene_validate` → (for promotions) isolated key-blind adversarial
   subagent → `severity_impact_gate`. Frozen bundles + `arms_summary.json` + `prekey_freeze.json`.
4. **Then** opened the key, scored, froze `scores.json` + `phase85_freeze.json`.
5. PoC handoff for the CLEAN_HIT via the P84 generator.

## Blind result (frozen pre-key)
- **2 promotions:** `farmPlots`/`_farmPlots` dirty-flag-never-reset (rated **High**); `updateTaxRate`
  missing-settlement (rated **Medium**). Both adversarial **PASS** (isolated subagent could not falsify
  either), both survive the severity gate.
- **6 rejections**, incl. **both controls** (`configUpdated` onlyConfigStorage, `updatePlotMetadata`
  onlyConfiguredContract) rejected at DEFENSE_TRACED.

## Scoring vs the key (5 High + 1 Medium awarded)
| Metric | Result |
|---|---|
| Sealed-key discipline | **Preserved** |
| Blind surface recall | Lens surfaced the function for **6/6** awarded findings (single contract, full enumeration) |
| Conversion | **1 CLEAN_HIT — H-05 (High)**: dirty flag never reset → permanent reward-accrual loss. Same root-cause invariant + High severity; the isolated adversarial reviewer independently pinned the exact `transferToUnoccupiedPlot` reset-omission locus. |
| Mechanism correctness | 2/2 promotions name the correct source mechanism (0 wrong-mechanism) |
| Severity-FP | **1 — `updateTaxRate` promoted Medium but judged Low ([02])**. Over-calibration. |
| Controls | **2/2 rejected**, clean |
| Safety | 0 SOURCE_FALSE · 0 unsupported-READY · 0 HARD_FAIL · 0 detector→finding |

**Honest misses** (awarded, not converted): H-01 (rejected `transferToUnoccupiedPlot` as "harmless" — missed
the plotId-not-updated multi-renter bug), H-02 (repeated farming), H-03 (near-miss: considered `finalBonus`
path, abstained), H-04 (near-miss: surfaced numPlots-drop + underflow mechanisms, didn't promote the
`PRICE_PER_PLOT`-increase underflow→freeze), M-01 (near-miss: considered the zero-tax-land mechanism in
`stakeMunchable` but **under-rated** and rejected). Conversion recall is modest (1/6 awarded H/M); the
bottleneck is conversion depth + severity calibration, **not** surface (6/6 surfaced).

## Verdict — QUALIFIED, not a clean PASS
PASS-level on: sealed-key discipline, ≥1 blind CLEAN_HIT (H-05 High), controls clean, adversarial PASS, and
the P84 generator produced a **reject-first** bundle. **But the strict "0 severity FPs in C" condition is not
met** — 1 severity FP survived C (`updateTaxRate` Medium vs awarded Low), which is listed under FAIL
("severity FP survives C"). Net: a productive run that surfaced a real, **named, generic** weakness:

> **Severity over-calibration on bounded / lazy-settlement accounting issues** (in-game yield mis-accrual
> promoted at Medium when judged Low). This recurs — **inverse direction** — with the P81e DoS *under*-rating.
> Severity calibration is the cross-eval bottleneck.

Per the phase constraints, the response is to **STOP and report**: no scanner-machinery tuning, and **no
post-key demotion** (that would violate "do not tune after opening the key"). The frozen blind result stands.
The severity FP is on `updateTaxRate`, **not** on the PoC-handoff candidate (H-05 has correct High severity).

## PoC handoff (CLEAN_HIT H-05)
- Generated a P84 bundle into `_p85_munchables/poc_handoff_H05/`. Result: `pipeline_status =
  POC_HANDOFF_STARTED`, both reproduced/submission gates **False**, gate verdict **DO_NOT_SUBMIT**,
  `reject_first_ok = True`. No executable PoC was reproduced (not fabricated) — so **not** STRONG PASS.
- **Taxonomy-fit caveat:** H-05's class (reward-accrual state-flag lifecycle) is **not** in the P84 seed
  taxonomy; generated with the closest type (`shared_position_fee_routing`). → P86 should add a dedicated
  finding type.
- Funnel updated accurately: `munchables-2024-07:P85-H05` = `POC_HANDOFF_STARTED`, submission `NOT_STARTED`,
  never SUBMITTED.

## Integrity
Machinery byte-identical (deep_pass `57c29fff`, hygiene `b9e18f29`, severity_impact_gate `0b7c54e4`,
surface_recall_lens `29a7b915`, funnel `720e9092`, handoff_generator `9c2c89cb`). Prior frozen artifacts
(P81e/P82/P83/P84) untouched. No production wiring. PoC source cloned to `/tmp` only.

## Next recommendation
**P86 = severity-calibration repair** (the named generic failure): bounded / lazy-settlement accounting
issues (in-game yield mis-accrual, off-by-one, deferred-rate) should default to **Low** unless a concrete
≥Medium consequence (principal loss / lock / unbounded drain) is proven — *and* recover the inverse P81e
DoS under-rating. This is the one repair both blind evals now point at. Secondary: add a
`reward_accrual_state_lifecycle` finding type to the P84 generator. Then a P87 third blind run to confirm the
calibration fix without regressing recall. (All repairs are a separate, post-report step — not done here.)
