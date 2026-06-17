# P220 — Recommendation

**Decision: `ZETA_L3_PARTIAL`.** Three executed, source-valid L3 harnesses now back the ZETA-04/10/11 dashboard
cards with real PoC actual/expected/control/value-delta. One PASS (ZETA-04, Medium), one executed refutation
(ZETA-10), one wrong-mechanism DoS partial (ZETA-11). No candidate promoted to High on AI reasoning; every blocked
High carries a written blocker; all safety flags false; production untouched.

## What this closes
- The P219 "evidence GENERATION" follow-on for the three High-ceiling candidates is done: their PoC fields are now
  artifact-backed instead of `unknown`.
- The harness platform under `pocs/p220/` (real source + authentic OZ/Uniswap vendoring + minimal mocks) is reusable
  for the remaining Zeta candidates.

## Open items (human decision — NOT done here)
1. **Severity-floor calibration (recurring).** ZETA-04 (TSS-gated availability) and the DoS reading of ZETA-11 are
   calibrated Medium by `decide()` because their triggers aren't permissionless. The answer key rates ZETA-04 High.
   This is the same under-rating pattern measured in P212/P215. Options for a human: (a) review ZETA-04 for a
   `HUMAN_OVERRIDE` to High with written rationale; (b) consider whether the P214 DoS carve-out (or an analogous
   availability carve-out) should ever cover incident-response-control bypass — but only behind the existing
   default-off flag and after re-validation. Do not auto-upgrade.
2. **ZETA-10 residual.** The missing `nonReentrant` is a real low/code-quality observation even though theft is
   refuted; route as Low if the report wants completeness.
3. **ZETA-11 theft sub-claim.** Confirming or refuting it needs the *external* Trident factory's registration policy
   (out of scope here). If pursued, harness against the real factory's deployment, not a mock.
4. **Remaining candidates.** ZETA-01/05/06 stay `NEEDS_HARNESS`; ZETA-02/09/12 have no L3 record (PARTIAL). Build
   harnesses / author records if a fuller pass is wanted.

## Guardrails honored
Research-only; 0 route/submit/promote; production scripts + forbidden files + Zeta sources byte-identical
START==END; `api_free=true`; no fabricated evidence; answer-key text confined to `scoring_note`/`last_reviewer_note`.
