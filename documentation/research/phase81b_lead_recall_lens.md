# Phase 81b — Lead-Generation Recall: a surface-first lead lens

> **CORRECTION (added during P81d, audited-source re-verification).** P81b/c originally measured Decent recall on the
> decent-bridge **HEAD (post-fix)** submodule, where `DcntEth.setRouter` had `onlyAdmin` and so matched
> `admin_config_setter`. On the correct **audited 2024-01 commit (`7f90fd4`)** `setRouter` is **unguarded** and the
> lens **does not lead on it** (it matches no class — `admin_config_setter` `requires_auth_modifier`, the inverse of a
> missing-AC bug). **Corrected Decent recall = 8/9 DIRECT** (H-01 `setRouter` → ADJ: the DcntEth contract is flagged
> but not the unguarded setter). The other 8 surfaces are version-robust. NOYA is unaffected. The artifacts in
> `_p81b/decent/` now reflect the audited source. See P81d for the named lens flaw (missing-auth-setter gap).

**Result: LEAD-RECALL PASS (corrected: Decent 8/9 DIRECT, was 9/9 on fixed source).** On Decent (full 11-contract scope, the keyed P81a subject) the new surface-first lens
covers **9/9 awarded findings DIRECT (100%)**, including the two functions P81a missed — `UTB.receiveFromBridge` and
`DecentBridgeExecutor.execute`. On a held-out second protocol (NOYA 2024-04) the **unchanged frozen lens** covers
**8/8 surface-relevant awarded bugs DIRECT** — so the design **generalizes, it is not Decent-overfit**. The lens also
exposed a real precision wart (over-broad `bridge_receive` tagging) and the mechanism-naming layer remains the weaker
link — both honest, actionable. Research-only, un-wired, promotes nothing.

## Why this phase (what P81a proved)
P81a separated two questions: the workflow now *avoids bad promotions live* (safety good) but *did not generate leads on
the surfaces where awarded bugs live* (0 CLEAN_HIT / 0 STRONG_PARTIAL). Two corrections sharpened it:
- P81a's leads were **pattern-biased** — they picked likely bug shapes, not security-relevant surfaces.
- **Scope:** the Decent clone held only the 8-contract UTB subset; **6 of 9 awarded findings live in the un-cloned
  `decent-bridge` package** (DcntEth / DecentBridgeExecutor / DecentEthRouter). Most P81a "MISSes" were *out of
  acquired scope*, not pure lead failures. P81b acquired the full scope (per the official `scope.txt`) first.

## What was built (surface-first, recall-biased — NOT a bug detector)
- `scripts/investigation/surface_recall_lens.py` (+ `config/surface_recall_lens.json`) — enumerates every in-scope
  public/external function (+ `receive`/`fallback`) and classifies it into 8 **generic** security-surface classes
  (`bridge_receive`, `external_executor`, `admin_config_setter`, `fee_path`, `refund_path`, `value_exit`,
  `calldata_forward`, `auth_boundary`). Emits a STATIC_LEAD per surface **even when the mechanism is uncertain**, via
  `lead_schema.normalize_lead`. Precision is the downstream P77/P78 job, never the lens's.
- `scripts/investigation/surface_recall_score.py` — scores the four pipeline stages **separately** (the P81b rubric):
  lead-recall (DIRECT / ADJ / MISS) · mechanism-naming (scored **only on DIRECT** hits — honest) · investigation
  outcome (stretch) · promotion safety / severity-FP (stretch). The awarded map is an **eval-only** scorer input,
  never read by the lens.
- Reuse only: `sibling_function_parity_taxonomy.{strip_comments,extract_features}`, `lead_schema.normalize_lead`. No
  edits to deep_pass / hygiene / transitions / lead_schema / abc_eval / parked detectors / value_flow (byte-identical).

## Decent (train, full scope) — the four separated metrics
| metric | result |
|---|---|
| **1. Lead recall** | **9/9 DIRECT (100%)**, 0 ADJ, 0 MISS. 66 leads over 11 contracts. |
| **2. Mechanism naming** | **9/9** surface-class ∩ awarded-mechanism-class. |
| **3. Investigation outcome** | STRETCH — deferred (see below). |
| **4. Promotion safety / severity-FP** | STRETCH — deferred. |

All 9 awarded surfaces hit directly: H-01 `DcntEth.setRouter`, H-02/H-04 `DecentEthRouter.bridge`, H-03
`DecentBridgeExecutor.execute`, M-02 `DecentEthRouter.bridgeWithPayload`, M-03 `UTB.receiveFromBridge`, M-04
`StargateBridgeAdapter.bridge`, M-01 `UniSwapper.swap`, M-05 `DecentEthRouter.redeemEth`. Both required functions
present. **PASS condition (≥6/9 incl `receiveFromBridge` + `DecentBridgeExecutor.execute`): met decisively.**

## NOYA 2024-04 (held-out, frozen lens, unchanged) — overfit check
Raw: 18/19 covered (15 DIRECT). But the honest split (lens target vs out-of-scope math) matters:
| subset | covered | DIRECT | mechanism MATCH | reading |
|---|---|---|---|---|
| **surface-relevant** (access / value-movement / registry — the lens's target) | **8/8** | **8/8** | 7/8 | **generalizes — not Decent-overfit** |
| non-surface (TVL/oracle **view** math — out of lens scope) | 10/11 | 7/11 | **0** | **spurious `bridge_receive` tags** (matched on `abi.decode`/bytes), inconsistent (SNX `_getPositionTVL` not led) — noise, not real recall |

**Honest reading:** the surface-first approach recalls value-movement / access / registry surfaces on a completely
different protocol (8/8), confirming it is **not anchored to Decent** — the recurring Phase 12/13 overfit failure did
**not** occur. The raw 94.7% *overstates* recall: the view-math "coverage" is a precision artifact, not genuine
surface recall. Two NOYA awarded-map contract-name typos (`Dolomite`→`DolomiteConnector`, `Registry`→
`PositionRegistry`) were corrected against source after scoring; the frozen lens output was unchanged.

## Honest findings / limitations
1. **Mechanism naming is the weaker layer** (Decent 9/9 but NOYA surface-relevant 7/8, overall 7/19) — consistent with
   P81a's secondary bottleneck. Surface classes are a *coarse* mechanism proxy; precise mechanism naming is still the
   deep-pass's job.
2. **`bridge_receive` over-tags** accounting/view code via the `abi.decode`/bytes-param signal → noise on
   accounting-heavy protocols. Tighten to require the trusted-caller *shape* (external + bytes payload + `only*`/
   relayer gate), not `abi.decode` alone. (Lens stays frozen for this phase; this is a P81c refinement.)
3. **Recall-biased by design:** 66 Decent / 231 NOYA leads is a wide net — intended. Precision is downstream
   (P77/P78 + the planned P81c severity gate); the lens must not pre-filter the surfaces.
4. **Stretch not run:** whether the *improved* lead set now yields a live CLEAN_HIT/STRONG_PARTIAL through P77/P78 is
   the P81a question and deserves a full keyed live A/B/C re-run — deferred rather than rushed. P81b's claim is
   strictly **lead-recall improvement**, per the user's pass framing.

## Pass / fail
- **Lead-recall: PASS** — Decent 9/9 DIRECT incl both named functions; no answer-key hardcoding (generic-config test);
  holdout generalizes (NOYA 8/8 surface-relevant). 
- **Mechanism naming: partial** (strong on Decent, weaker cross-protocol) — flagged.
- **Precision wart:** `bridge_receive` over-broad — flagged for P81c.
- **Stretch (live hit-accrual): not attempted this phase.**

## Recommended next
1. **P81c — `bridge_receive` precision tighten + severity/impact gate.** Tighten the one noisy class (trusted-caller
   shape, not `abi.decode`), then add the promotion-time severity/impact gate that P81a's D2 FP motivated. Re-freeze.
2. **P81d — keyed live A/B/C re-run on Decent** with the improved lead set fed through P77/P78, to test whether better
   lead recall converts to a live CLEAN_HIT/STRONG_PARTIAL with 0 added severity FP (the genuine end-to-end question).
- Order unchanged: 1 generate relevant leads ✅ (this phase) → 2 investigate safely ✅ (P77/P78) → 3 severity gate →
  4 PoC → 5 submission.

## Integrity
`scripts/investigation/surface_recall_lens.py` + `config/surface_recall_lens.json` + `surface_recall_score.py` +
`_p81b/{decent,noya}/{leads,awarded_map,recall_score}.json` + `_p81b/_freeze/{lens_freeze,phase81b_freeze}.json` +
`tests/investigation/test_surface_recall_{lens,score}.py`. Lens frozen before the holdout run; post-run docstring-only
edit reproduced byte-identical leads (decent `6dad519f`, noya `c5861bdc`). Protected modules byte-identical (deep_pass
`57c29fff` · hygiene `b9e18f29` · transitions `2c00069c` · lead_schema `3c57f04e` · abc_eval `5e0d855d`; parked
detectors + value_flow unchanged). **137 tests pass** (investigation 42 + signature_replay 22 + access_control 51 +
candidates 22). No-wiring CLEAN. No production wiring; no finality language. **Promotes nothing to production.**
