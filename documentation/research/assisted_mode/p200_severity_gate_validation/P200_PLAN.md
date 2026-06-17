# P200 — Blind fresh-corpus validation of the P199 severity-gate discriminator

## Goal
Test the P199 reject-first severity gate **out-of-sample** on a fresh sealed corpus (`badger-2024-06-holdout`,
eBTC). P199 derived and validated the gate on the *same* dataset it was built from (n=30, 6 corpora). P200 asks the
honest precondition for any production severity change: **does the discriminator reduce Medium/Low over-HIGH without
demoting genuine Highs, on a corpus it has never seen?**

## Out-of-sample property (the whole point)
A **double freeze**, both *before* the answer key is read:
1. **Freeze 1** — blind threat-ceiling verdicts (Sonnet on production `deep_trace.md` + verbatim source).
2. **Freeze 2** — the P199 gate applied **offline** by the orchestrator to the frozen outputs, *still answer-key
   blind* (graded from each output's own evidence + source only).
3. **Then** open the seal and score original-vs-calibrated.

The gate never saw badger's key → genuine out-of-sample. The gate is applied **offline / read-only only**; it is
**not** implemented in production (no `deep_trace.md`/checker/router/detector/severity-label edit).

## Sequence
1. Integrity precheck (`INTEGRITY_PRECHECK.md`).
2. Controlled MINIMAL viability unseal — count-only severity headers (`CONTROLLED_UNSEAL.md`, `CORPUS_VIABILITY.md`).
3. Read-only source-grounded coverage manifest + pre-registered bounded sample (`COVERAGE_MANIFEST.md`).
4. Blind Sonnet run, FREEZE 1 (`BLIND_THREAT_CEILING_RESULTS.md`, `blind_prompts/`, `raw_outputs/`).
5. Offline P199 gate, FREEZE 2 (`OFFLINE_SEVERITY_CALIBRATION.json`).
6. Controlled answer-key scoring (post-freeze).
7. Metrics (`metrics.json`, `CALIBRATED_SCORECARD.md`, `ORIGINAL_VS_CALIBRATED.md`).
8. Failure cases (`FAILURE_CASES.md`).
9. Recommendation + decision (`P200_RECOMMENDATION.md`).
10. Integrity re-check, memory.

## Decision space
`SEVERITY_GATE_VALIDATED_OUT_OF_SAMPLE` · `SEVERITY_GATE_PARTIAL` · `SEVERITY_GATE_FAILED_FALSE_DEMOTIONS` ·
`DATASET_TOO_THIN` · `INVALID_RUN`.

## Guardrails
Read-only/offline; production hashes byte-identical START==END; seal opened only as documented; blind firewall
(prompts token-scanned pre-run, outputs verbatim, scorer post-freeze, no backfill); `fabrication_rate=0`; Sonnet
blind model (same-vendor caveat recorded); bounded sample = out-of-sample *signal* not full recall.
