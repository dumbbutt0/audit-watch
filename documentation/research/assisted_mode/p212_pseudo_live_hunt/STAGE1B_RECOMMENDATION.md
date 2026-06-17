# P212 Stage 1B — recommendation

## Decision: `READY_FOR_SCORING`

Built and ran executable Foundry harnesses (solc 0.8.25, OZ v5, real cloned SophonFarming, only external deps mocked)
for the top-3 permissionless candidates. The sealed Sherlock report remains **unopened**; production byte-identical;
no submit/route/promote.

## Harness outcomes (4/4 tests pass)
- **SOPH-01 — REFUTED.** After a full-deposit `withdraw`, `amount == boostAmount` → conservation **holds**. The
  "withdraw omits boostAmount → conservation break" hypothesis is a false positive; the residual is the paid boost
  weight (persists by design). L3 FAIL/invalid. (Residual Low/Info: boosters keep accruing after withdrawing deposit.)
- **SOPH-02 — REFUTED.** `pendingPoints` view == post-`updatePool` settled (delta 0 for both users) → the
  `*1e18 … /1e36` scaling cancels correctly. The "1e18 over-report" hypothesis is a false positive. L3 FAIL/invalid.
- **SOPH-03 — CONFIRMED MEDIUM.** With realistic stETH 1-wei share-rounding, `depositStEth` **reverts** (wrap pulls the
  full `_amount` while the contract received `_amount-1`); honest-stETH control succeeds. Executable, permissionless,
  source-valid → **DoS of stETH deposits (Medium, not High).** L3 FAIL-for-High → calibrated Medium.

## Net
**0 High-submission-ready** (unchanged). The harness layer did exactly its job — it **executably refuted 2 of 3
over-claimed Highs** and **confirmed 1 real Medium** (SOPH-03), giving one human-reviewable package. This is the value
proposition of the L3 standard on a live target: it stops over-rated points-accounting "Highs" from being presented as
submission-ready, and converts hand-wavy leads into measured verdicts.

## Why READY_FOR_SCORING
≥1 candidate (SOPH-03) is human-reviewable as a Medium with an executed PoC; no candidate is recommended High (so the
"High requires L3 PASS/override" rule is vacuously satisfied); the answer key is sealed; production hashes unchanged;
JSON valid. The remaining over-claimed candidates are honestly retired as refuted.

## What STAGE 2 will check (after user "ready for scoring")
- Does the official Sherlock report contain the SOPH-03 stETH-wrap DoS (HIT/PARTIAL/ADJACENT)?
- Were SOPH-01/02 correctly **non-findings** (true negatives) or did the harness miss something (the report will tell)?
- L3 effectiveness: did refuting the 2 over-claimed Highs + capping SOPH-03 at Medium match the official severities,
  i.e. did the gate prevent severity overstatement without dropping a real High?

## Guardrails honored
Only SOPH-01/02/03 harnessed; sealed report unopened (267 files); harnesses under `pocs/p212/` (real source via
byte-identical `realsrc/` copy `c2d9ecd1`; original `targets/` unedited); no production-source edit; L3 records updated
+ overlay re-run; production hashes byte-identical START==END; `api_free=true`; active audit untouched; JSON valid;
fabrication 0.
