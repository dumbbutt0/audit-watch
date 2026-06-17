# P288 — DIAGNOSIS

## Target: ecg-2023-12-holdout (Ethereum Credit Guild, C4 2023-12) · awarded H/M = 29 (4H/25M)
Fresh, never scored (`submit_count=0`/`poc_count=0`); chosen by content-light H/M screen only.

## Funnel (blind, pre-reveal)
- advisory candidates: 23 · validation queue: 8 (5 classes) · READY: **0** · PoC-supported: **0**.
- High-contract recall: **4/4**; exact High-function recall: **2/4** (onBid, stake) surfaced+queued.
- STRONG/EXACT awarded mechanism recoveries: **0**. SAME_AREA_WRONG_MECHANISM: 1 (H-03 onBid). SUBSYSTEM_ONLY_RECALL: 4
  (H-01, H-02, H-04, M-02). severe concluded/reportable FP: **0**. false positives: 0. non-awarded TP: 0.

## First-failed stage
**EVIDENCE_DERIVATION** for the exact-awarded loci: 6/8 candidates (incl. H-04 stake) are
`value_flow_present_but_no_anomaly` + invariant_delta `NO_REFERENCE`; H-03 onBid was INLINE_GUARD_REFUTED (access-guard
read, wrong for a bad-debt-cascade bug). NO candidate matched the D4.6 oracle-normalization lens (ECG is not
oracle-centric) — the lens that carried kelp in P287.

## Comparison to P274 / P286 / P287
- P274 (blind, gondi): 2 EXACT awarded recoveries (hand-run).
- P286 (supervised): READY → PoC-supported 2/2.
- P287 (fresh blind, kelp): 1 STRONG awarded recovery (H-01 oracle staleness) READY+PoC, FP=0 → verdict A.
- **P288 (fresh blind, ECG): 0 READY, 0 recovery, FP=0 → verdict D.** Strong *locus* recall (2/4 exact High functions
  surfaced+queued) but the evidence-derivation layer derived no mechanism for ECG's awarded bug classes
  (slash-on-prior-loss, reward-theft-via-transfer, bad-debt-cascade, gauge-reward-index).

## Headline conclusion
**Generalization is LENS-BOUNDED, not universal.** P287 replicated the full path because kelp's awarded High matched a
built lens (D4.6 oracle-normalization). P288 shows that when a fresh target's awarded mechanisms match NO current lens,
the stack still *surfaces* the right loci (decent recall) but produces 0 READY — the binding constraint is
EVIDENCE_DERIVATION, not recall/coverage/selection/gate-strictness. The READY gate stayed correctly fail-closed (0 false
READY).

## Final bottleneck (exactly one): **F — EVIDENCE_DERIVATION_GAP**
The exact-awarded loci were surfaced and queued; they failed to reach READY because no evidence lens models their
mechanism. Next repair targets (each a candidate lens): (1) **loss/slash-on-stake coupling** (position staked into a
unit that already realized a loss — H-04); (2) **bad-debt / loss contagion across coupled positions** (auction cascade —
H-03); (3) **reward-accounting index/initialization** (userGaugeProfitIndex — H-01); (4) **share-transfer reward theft**
(rebase distributor transfer — H-02).
