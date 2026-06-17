# Phase 89 — Fourth fresh sealed-key blind run (validate combined P86+P88 calibration)

## Goal
Confirm BOTH severity-calibration directions on a fresh subject: P86 (bounded/lazy without concrete consequence
must not survive as M/H) AND P88 (source-backed liveness / involuntary loss must not be under-rated or
false-demoted), holding the strict **0 severity-FP** bar. No post-key tuning.

## Subject & sealed-key discipline
- **phi-2024-08** (Code4rena), commit `2465e04364…`, **9 in-scope contracts** (~2854 lines). Fresh — not in
  the prior corpus.
- **Sealed-key PRESERVED:** metadata → leads → C-chain bundles → adversarial → severity-gate →
  `prekey_freeze.json` (`answer_key_opened=false`) all frozen **before** the findings repo was cloned. No web
  search; `4naly3er-report.md` / README never opened. Gate under test = P88 `193abf9f03f138c8`.

## Pipeline
Repaired lens → 67 leads over 9 contracts → predeclared frozen set **8 conversion + 3 controls** → C-chain
(`deep_pass` → `hygiene_validate` → isolated **key-blind adversarial** subagent → **P88 severity gate**) →
freeze → open key. Partial rule: **6 conversion leads investigated** (2 promoted, 2 rejected, +3 controls);
**4 conversion NOT_RUN** (signatureClaim / merkleClaim / depositBatch / claimFromFactory) — budget, excluded
from denominators.

## Blind result (frozen pre-key)
- **2 kept promotions** (both adversarial **PASS**, both Medium after the gate):
  - `Cred.batchSellShareCred` → public `_addCredIdPerAddress`/`_removeCredIdPerAddress` (L685/L695, no auth) →
    arbitrary cred-list corruption / sell-DoS. Concrete `unauthorized_execution`.
  - `Cred.batchBuyShareCred` → `buyShareCredFor` resets a victim's `lastTradeTimestamp` → third-party sell-lock
    DoS. **Involuntary** + `denial_of_asset_movement` (kept via the **P88 elevation**).
- 2 conversion rejected (claim/batchClaim wrappers), 3 controls rejected, 4 NOT_RUN.
- Safety: 0 SOURCE_FALSE / 0 unsupported-READY / 0 HARD_FAIL / 0 detector→finding.
- The adversarial layer **falsified my Claim-1 reward-distribution-DoS over-reach pre-freeze** (the corrupted
  arrays don't feed the distributor) and corrected it to the real sell-DoS/bookkeeping path.

## Scoring vs key (7 High + 8 Medium)
| Axis | Result |
|---|---|
| Sealed-key | preserved ✅ |
| Safety (4 axes) | 0 / 0 / 0 / 0 ✅ |
| **Severity FP after P88 gate** | **0** ✅ |
| Controls | 3/3 rejected ✅ |
| Conversion | **2 CLEAN_HITs** — **H-05** (public helpers, awarded **High**) + **M-07** (sell-lock DoS, awarded **Medium**) ✅ |
| False-demotion of a surfaced true M/H | **0** ✅ (both kept) |
| Under-ratings | **1** — H-05 rated Medium vs awarded High |
| P84 taxonomy | H-05 → `access_control_privileged`, M-07 → `validation_liveness_counter_scope` — both covered (no gap) |

**Both promotions matched the key verbatim:** H-05 names the exact two public functions (my adversarial
reviewer independently found the index-revert sell-DoS); M-07 is the exact `buyShareCredFor` lock-reset DoS at
the exact severity (Medium).

## Verdict — QUALIFIED PASS (strongest blind result so far)
Meets **every strict clean-PASS bullet** (sealed-key; 0 SOURCE_FALSE / unsupported-READY / HARD_FAIL /
detector→finding; **0 severity FP**; controls clean; **2 CLEAN_HITs**; no false-demotion of a surfaced true
M/H) **and** reaches **Strong-PASS mechanics** (P84 generator produced a reject-first `DO_NOT_SUBMIT`,
un-promotable bundle for H-05). **Qualified** by named non-blocking caveats below.

### Both calibration directions validated
- **P86 (over-rating) HELD:** 0 severity FP; no bounded/lazy issue survived as M/H; controls rejected.
- **P88 (under-rating) VALIDATED POSITIVE:** **M-07**, an *involuntary third-party* sell-DoS, was **KEPT** via
  the P88 elevation (involuntary + `denial_of_asset_movement`) and matched the awarded Medium — exactly the
  false-demotion class P88 was built to prevent. Pre-P88, a "looks self-inflicted/griefing" case like this
  risked demotion; P88 kept it correctly. No regression in either direction.

### Honest caveats (non-blocking)
- **H-05 under-rated Medium vs awarded High** — judgment-depth on access-control impact (the gate kept it at
  the asserted Medium; access-control corruption wasn't tagged with liveness/high markers). Same class as
  P87 H-01.
- **H-03 missed** — the real reward-distribution DoS is `shareBalance` EnumerableMap bloat (a *separate* High).
  My Claim-1 intuition pointed at reward-dist via the wrong arrays; the adversarial layer correctly falsified
  that path; I did not separately promote H-03.
- **Partial recall** — H-01 (signatureClaim replay) was in a NOT_RUN lead; H-02/H-04/H-06/H-07 + several M in
  unselected/uninvestigated surface.

Per constraints: **no machinery change during P89, no post-key tuning, no retroactive re-score.** The gate
stayed at the P88 hash `193abf9f`; all machinery byte-identical; prior frozen artifacts unmutated; 187 tests
pass; no-wiring CLEAN; PoC source cloned to `/tmp` only.

## PoC handoff
`Cred._addCredIdPerAddress` (H-05) → P84 `access_control_privileged` (good fit) → `_p89_phi/poc_handoff_H05/`:
`POC_HANDOFF_STARTED`, reproduced/submission gates **False**, verdict **DO_NOT_SUBMIT**, `reject_first_ok=True`.
No executable PoC reproduced (not fabricated). Funnel record `phi-2024-08:P89-H05` = `POC_HANDOFF_STARTED`,
submission `NOT_STARTED`, never SUBMITTED.

## Next recommendation
The calibration loop is now closed across four blind runs (over-rating fixed @P86 + validated @P87/P89;
under-rating fixed @P88 + validated-positive @P89). The recurring residual is **conversion depth + severity
under-labelling on kept findings** (H-05 here, H-01 in P87) and **lead-selection recall** (Highs landing in
NOT_RUN). Recommended next: a **recall/depth phase (P90)** — larger blind-N (raise the selected-lead cap so
fewer true Highs fall into NOT_RUN) and a deep-pass prompt that pushes the impact assessment to test the
*maximal* consequence (to curb the High→Medium under-labelling), measured against the existing frozen
corpora — **not** another calibration change to the gate (the gate is now validated in both directions).
