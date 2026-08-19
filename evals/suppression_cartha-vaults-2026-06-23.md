# Recall Lab — Real-Audit False-Suppression Report
_generated 2026-07-06T20:07:49Z_  ·  audit `cartha-vaults-2026-06-23`

Eval-only. Does a precision filter recommend removing a finding this audit CONFIRMED? Oracle = the audit's own `submit.jsonl` / `state==ready` set. Measurement only — no pipeline change.

- Candidates: **32**  ·  confirmed oracle: **8 submit** / **6 ready**  ·  shared FP rules: **180**
- Loosen / make-reversible candidates (removed a confirmed keeper): **none**

| Filter | Step | Mode | Cut rate | Suppr (submit) | Suppr (ready) | Loosen? |
|---|---|---|---|---|---|---|
| ice_downgrade | 3.4 | non_removing | 0.000 | 0.000 | 0.000 | no |
| fp_pattern_check | 3.6 | recomputed | 0.000 | 0.000 | 0.000 | no |
| pre_submission_gates | 3.7 | logged | 0.000 | 0.000 | 0.000 | no |
| dedup_screen | 3.8 | non_removing | 0.000 | 0.000 | 0.000 | no |

> **Advisory — `ice_downgrade` (NOT suppression):** ICE capped 12 candidate(s) below the Medium floor (advisory severity guidance; the finding still advances): AC-001, AR-001, CARTHA-SEAM-001, DOS-001, DOS-002, DOS-003, DT-001, DT-003, DT-004, EA-001, OR-001, TI-005

> **Caveat — `fp_pattern_check`:** fp matcher never cleared the 0.6 review bar on any candidate (raw max similarity 0.445, thresholded top 0.0). 9/32 candidates carry vuln_type, but even matching vuln_types stay sub-threshold once keyword overlap is added. suppression=0 here means the rule set is DORMANT on these findings — not proven recall-safe.
