# P268 — DIAGNOSIS (Phase 12)

Fresh full-path run on a zero-exposure external contest (karak, 2024-07; 4H+5M; public findings; training-confound
disclosed), with the P267 selector inserted between B/C ranking and completion/PoC.

## Counts
- advisory candidates: **20** (guard PASS, 0 violations; recall-delta 15/20 = 75%).
- dashboard candidates displayed: 20 (standalone advisory-only).
- candidates triaged to PoC queue: **3** (C1 redeem, C2 mint, C-neg slashing), each a high-vs-easy B/C pair.
- **selector decisions: KEEP_BOTH ×2 (C1, C2), REFUTE_M1_FIRST ×1 (C-neg). KEEP_BOTH count = 2.**
- PoCs attempted: 3 · **PoCs passed: 3** (C2-M1 inflation confirmed; C1 roundtrip + C1-M2 revert characterized).
- exact awarded mechanisms: **0** · strong: **0** · family: **0**.
- not-awarded real issue: **1** (C2-M1 Vault first-depositor inflation — PoC-confirmed, not awarded).
- severe concluded/reportable FP: **0**.

## Did P267 fix the P266 drop? — YES (mechanically, on fresh data)
The raw pre-P267 path would have selected the easy rivals (C1-M2 approval-revert, C2-M2 dust-rounding) and dropped
the high-impact M1s. The selector returned **KEEP_BOTH** (anti-easy-PoC flag set on both), so **C2-M1 (inflation) was
carried into completion + PoC and confirmed a real victim loss**. The specific P266 failure mode —
*high-impact mechanism in top-2 dropped for an easier rival* — **did not recur**. The selector did its job.

## Why exact recovery was still 0 — the bottleneck moved UPSTREAM to TRIAGE
All 9 karak awards cluster in the **NativeVault / slashing / snapshot** subsystem. The recall harness **surfaced**
that subsystem (narrow `_startSnapshot`/withdrawal-credentials; recall-delta `validateSnapshotProofs`,
`SlasherLib.finalizeSlashing`/`cancelSlashing`) — locus recall worked. But **triage de-scoped it** (recorded
pre-reveal in `poc_queue.json` `skipped_high_ranked`: "needs beacon fixtures → heavy PoC harness") and routed the
self-contained **ERC20 Vault** subsystem to the selector instead. The selector can only choose among mechanisms
triage hands it; it cannot recover an award subsystem triage skipped. Separately, the one mechanism that WAS
confirmed (Vault first-depositor inflation) is a **real-but-not-awarded** issue.

## Per-stage localization
- Dashboard surface: ✅ advisory-only, safe.
- Discovery / locus recall: ✅ surfaced the award-dense NativeVault/slashing subsystem.
- **Triage (candidate-selection-for-PoC): ❌ the binding gap** — de-scoped the award subsystem for PoC-feasibility,
  chose the easier-to-harness ERC20 Vault.
- Ranking (B/C): ✅ surfaced M1 into top-2.
- **Selector (P267): ✅ worked** — preserved the high-impact M1 (KEEP_BOTH), fixed the P266 drop; correct REFUTE_FIRST
  on the gated control.
- Completion: ✅ machinery fine (COMPLETED_CHAIN on C2-M1).
- PoC harness: ✅ produced a confirming L3 PoC from an advisory candidate.
- Reportability gate: ✅ conservative; 0 severe concluded/reportable FP.

## Remaining bottleneck (exactly one): **TRIAGE**
The award-dense subsystem was surfaced by recall but **not selected at triage for PoC** (de-scoped on
PoC-feasibility). This is the P259 "selection-upstream" theme recurring at the **triage** stage: ranking is fixed
(P267), discovery/recall works, but *which surfaced subsystem gets routed into the expensive PoC path* is now binding.

## Comparison vs P263 / P265 / P266 mechanism precision
| phase | locus recall | exact recovery | note |
|---|---|---|---|
| P263 benddao | subsystem forced in | 0 exact (family PARTIAL) | recall win |
| P265 corpus | 72.7% recall-delta | 0 exact | shadow recall PASS |
| P266 phi | exact locus | 0 (awarded gen-but-misranked) | RANKING_GAP |
| **P268 karak** | surfaced award subsystem | **0 exact** | **RANKING fixed by P267; TRIAGE now binding** |
Exact recovery is still unproven — but the **specific gap P267 targeted is closed**, and the binding constraint has
moved one stage upstream (ranking → triage). No regression; the failure is newly-localized, not the same one.
