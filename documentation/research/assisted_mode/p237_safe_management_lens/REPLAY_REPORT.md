# P237 — Safe-management lens: reNFT replay report

> Research-only detector `safe_management_coverage` (un-wired). Replay on the frozen reNFT shadow workspace
> (`audits/renft-2024-01-shadow`). Recovery is mechanism-based (calldata offset value, selector-set difference),
> never answer-key string matching. Frozen P235 artifacts untouched.

## Replay setup
- Built the shadow `coverage_manifest.json` (22,345 items; 160 in-scope) via `build_coverage_manifest.py`.
- Ran `safe_management_coverage_audit.py` over the full manifest → `renft_replay_audit.json` (in this folder).
- Restored active audit to `size-credit-2024-06-blind`.

## Candidates produced (4 total — all on the real `Guard`, 0 elsewhere)
| Contract | Conf | Shape | Selector(s) | Maps to |
|---|---|---|---|---|
| Guard | HIGH | decode_offset_mismatch | disableModule (used 0x24, expected 0x44) | **H-04 (direct)** |
| Guard | HIGH | incomplete_selector_coverage | setFallbackHandler | **H-02 (direct)** |
| Guard | MED | incomplete_selector_coverage | execTransactionFromModule / multiSend / owner-mgmt | residual escape paths |
| Guard | MED | incomplete_selector_coverage | permit, increaseAllowance | **H-05 (partial — gasless-approval basis)** |

## Metrics
| Metric | Value |
|---|---|
| True recoveries (direct) | **2** — H-04 (decode offset), H-02 (setFallbackHandler) |
| Partial recoveries | **1** — H-05 (permit/increaseAllowance candidate + the setFallbackHandler candidate cover its fallback-removal + gasless-approval bases) |
| False positives | **0** — Stop/Factory (callers of Safe fns) and the test guards suppressed by the guard-entrypoint gate + in-scope/non-test filter |
| False negatives (in-family) | **0** within the Safe-management family |
| False negatives (out-of-family, by design) | H-01 (hostile-token), H-03 (create-time reentrancy), #387 (Seaport execution-invariant) — other families, out of scope |
| Candidate volume / noise | 4 candidates, all actionable; **0 noise** (un-wired → adds nothing to the production dashboard queue) |
| Dashboard ranking effect | none today (research-only/un-wired). If wired, the two HIGH defects (H-04, H-02) would surface at the top of a research queue |
| Precision (reNFT replay) | **4/4 = 100%** within-family on the anchor (single-anchor caveat) |

## Weighted recall — before vs after (Safe-management contribution)
Weighting High=3, Med=1; reNFT awarded ≈ 5×3 + ~14 = ~29.
- **Before P237 (P235 actual):** 1/5 Highs recovered (H-04, by hand) → recovered weight 3 → **~10–16% weighted**.
- **After P237 (this lens):** H-04 + H-02 direct + H-05 partial → recovered High-equivalent ≈ 3/5; recovered weight
  ≈ 3 + 3 + 1.5 ≈ **7.5/29 ≈ 26–36% weighted**; raw High recall **20% → ~60%**.
- Matches the P236 Scenario-A counterfactual (Safe-management lens: +2–3 Highs → ~31–36%).

## Before/after recall-gap assessment
| Safe-management family finding | Before P237 | After P237 |
|---|---|---|
| H-04 (disableModule offset) | hand-found only (RENFT-01) | **detector recovers directly (HIGH)** |
| H-02 (setFallbackHandler) | MISSED (partial via RENFT-04) | **detector recovers directly (HIGH)** |
| H-05 (fallback removal + permit) | MISSED | **detector recovers as partial (setFallbackHandler + permit/increaseAllowance)** |
The dominant P236 cluster is substantially closed. Out-of-family Highs (H-01 hostile-token, H-03 reentrancy, #387
Seaport) remain — by design, not this lens's scope.

## Would this have changed the P235 verdict?
Partially. P235 was **C — RECALL_GAPS_REMAIN** (1/5 Highs). With this lens, Safe-management recovery rises to ~3/5
Highs and weighted recall to ~26–36%, moving the result from **C toward B** (meaningful findings recovered). It does
**not** reach A — full contest competitiveness still needs the hostile-token and create-time-reentrancy families.

## Stop-and-report triggers — status
None fired after the precision fix. (Initial full-manifest run was noisy — Stop/Factory/test guards — which is the
"can't distinguish Safe-management risk from harmless selector presence" trigger; resolved by tightening
`is_safe_guard` to require a real guard transaction-check entrypoint + restricting to in-scope, non-test contracts.
The lens now distinguishes guards from callers cleanly.) Recovery is mechanism-based; no broad prompt rewrites;
forbidden files byte-identical; no dashboard/routing/severity change.

## Recommendation: **keep research-only (un-wired)** pending a validation campaign
The detector is clean on the anchor (0 FP, recovers H-04 + H-02 directly, H-05 partial) but is validated on a
**single anchor** → stability = PROMISING-BUT-NEEDS-REFINEMENT, not RESEARCH-STABLE. Do **not** wire yet. Next:
1. Run the 15–20 target validation campaign (other Safe-guard / module-guarded protocols) — wire only if 0
   high-confidence FP holds across the corpus.
2. **Hostile-token lens should be the next build** (P236's second cluster: H-01 + #64/#605 mediums; HIGH
   generalization) — pairs with this lens to lift reNFT toward B/A.
3. Re-run a second shadow contest (different architecture) to confirm the recall lift end-to-end before any live
   hunting.
