# P266 — DIAGNOSIS (Phase 9)

First full production-path run on a scored contest (phi-2024-08; 7H+8M; public findings; training-confound +
shallow non-answer-key prior-exposure disclosed). Route exercised end-to-end:
`shadow advisory candidate → standalone advisory dashboard → triage → B/C ranking → five-op completion → isolated
foundry PoC → sealed reveal → strict pre-reveal gate`.

## Production-path counts
- advisory candidates emitted: **18** (guard PASS, 0 violations, recall-delta 13/18 = 72%).
- dashboard candidates displayed: 18 (standalone advisory-only feed + page; 0 authority controls).
- candidates triaged to PoC queue: **3** (C1 narrow primary, C2 recall-delta primary, C-neg negative control).
- PoCs attempted: 3 · **PoCs passing: 3** (2 mechanism PoCs + 1 negative control), all with L1/L2/L3 evidence.
- exact awarded mechanisms recovered: **0** · family-level (generated-but-misranked): **1** (H-03) ·
  same-area-wrong-mechanism: **2** (C1, C2) · severe concluded/reportable FP: **0**.
- operator burden: ~10 min/candidate triage + ~20 min/PoC harness (after the one-time lib-bootstrap).

## MECHANISM_RECOVERY (the primary criterion)
| bucket | count | detail |
|---|---|---|
| exact mechanisms recovered | **0** | — |
| strong mechanism matches | **0** | — |
| family-level matches | 1 | **H-03** curator-enumeration gas-DoS — generated as m1c |
| subsystem-only recalls | ✓ | distribute + Cred curator-share subsystem (H-03/H-05/M-07 area) |
| same-area wrong mechanisms | 2 | C1 royalty→caller; C2 JIT spot-share capture (both real, non-awarded) |
| generated-but-misranked | 1 | m1c (H-03 family) reached **Profile B top-2** but was **not ranked/selected #1** |
| selected-but-not-completed | 0 | C2 selected + PARTIAL-completed; C1 COMPLETED |
| completed-but-PoC-failed | 0 | all 3 PoCs passed |
| PoC-supported | 2 (+1 benign) | C1, C2 PoC-supported but non-awarded; C-neg PoC-supported benign |

## Where the path failed (per-stage localization)
- **Dashboard surface:** ✅ works. Advisory-only, safe, no authority leakage.
- **Discovery / locus recall:** ✅ works. Surfaced the **exact** awarded locus `distribute` (H-03) and the Cred
  curator-share subsystem (H-05/M-07 area). Consistent with the P259→P265 "locus recall works" result.
- **Mechanism enumeration:** ✅ partially — the awarded H-03 gas-DoS family **was generated** (m1c).
- **Ranking / selection:** ❌ **the binding failure.** m1c (H-03 family) reached Profile-B top-2 but a non-awarded
  mechanism (m1a royalty-to-caller) was ranked #1 and routed to PoC. A **PoC-feasibility triage bias** (pick the
  easy-to-PoC value flow over the harder gas-DoS) compounded the mis-rank.
- **Completion:** ✅ machinery works (COMPLETED_CHAIN / PARTIAL_CHAIN produced) — but aimed at the wrong mechanism.
- **PoC harness:** ✅ works (3 runnable L3 PoCs from advisory candidates; negative control correctly benign).
- **Reportability gate:** ✅ works and was appropriately conservative (C1 only CONDITIONAL, C2 held, C-neg benign);
  **0 severe concluded/reportable FP**, no leakage.
- **Triage scope:** the claim/art/factory Highs (H-01/H-02/H-04/H-06/H-07) were de-scoped to focus the first run on
  the reward subsystem; H-01's locus was surfaced (narrow#0) but triage-skipped.

## Comparison vs P263 / P265 mechanism precision
| phase | locus recall | mechanism precision | note |
|---|---|---|---|
| P263 (benddao) | yield subsystem forced in | **family-level PARTIAL** (H-08), 0 exact | recall win; mechanism partial |
| P265 (13-corpus) | 72.7% recall-delta | **0 exact** across trial | shadow recall PASS; exact unproven |
| **P266 (phi, full path + PoC)** | **exact locus** (`distribute`=H-03) | **0 exact / 0 strong**; awarded family **generated-but-misranked** | PoC layer works; **ranking/selection** is now the proven bottleneck |
**Conclusion:** mechanism precision did **not** improve beyond P263/P265. The full path adds a working dashboard +
PoC layer and a clean safety record, but the awarded mechanism, though *discovered and enumerated*, was lost at
**ranking/selection** — the exact P256/P257 ranking gap, now reproduced through the entire production path.

## Bottleneck (exactly one): **C — RANKING_GAP**
The awarded mechanism (H-03) was surfaced (locus) AND enumerated (Profile-B top-2) but ranked/selected #2; a
non-awarded mechanism was completed and PoC'd instead. Not a discovery gap (locus + family found), not a PoC-harness
gap (PoCs ran), not a gate gap (gate was correctly conservative, 0 FP). Contributing: a PoC-feasibility triage bias.
