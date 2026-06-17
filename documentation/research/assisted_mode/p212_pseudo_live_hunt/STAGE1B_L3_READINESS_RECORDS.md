# P212 Stage 1B — L3 readiness records (updated, overlay re-run)

Records at `output_research/l3_readiness/SOPH-0{1,2,3}.json`, updated with measured harness results; overlay re-run
with `AUDITWATCH_L3_READINESS=1`.

| candidate | l3_status | poc_tier | high_promotion_allowed | calibrated | meaning |
|---|---|---|---|---|---|
| SOPH-01 | FAIL | L3_REAL_CONTRACT_POC | **false** | invalid | conservation holds → hypothesis refuted |
| SOPH-02 | FAIL | L3_REAL_CONTRACT_POC | **false** | invalid | view==settled (delta 0) → refuted |
| SOPH-03 | FAIL (for High) | L3_REAL_CONTRACT_POC | **false** | **medium** | confirmed executable DoS → Medium, not High |

**Net:** 0 High-submission-ready (unchanged); the two over-claimed Highs are now executably **refuted** (invalid), and
SOPH-03 is a harness-**confirmed Medium**. The harness layer separated real (1) from over-claimed (2).
