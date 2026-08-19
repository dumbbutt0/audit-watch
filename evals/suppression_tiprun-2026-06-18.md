# Recall Lab — Real-Audit False-Suppression Report
_generated 2026-07-06T17:07:41Z_  ·  audit `tiprun-2026-06-18`

Eval-only. Does a precision filter recommend removing a finding this audit CONFIRMED? Oracle = the audit's own `submit.jsonl` / `state==ready` set. Measurement only — no pipeline change.

- Candidates: **48**  ·  confirmed oracle: **6 submit** / **6 ready**  ·  shared FP rules: **180**
- Loosen / make-reversible candidates (removed a confirmed keeper): **none**

| Filter | Step | Mode | Cut rate | Suppr (submit) | Suppr (ready) | Loosen? |
|---|---|---|---|---|---|---|
| ice_downgrade | 3.4 | non_removing | 0.000 | 0.000 | 0.000 | no |
| fp_pattern_check | 3.6 | recomputed | 0.000 | 0.000 | 0.000 | no |
| pre_submission_gates | 3.7 | logged | 0.042 | 0.000 | 0.000 | no |
| dedup_screen | 3.8 | non_removing | 0.000 | 0.000 | 0.000 | no |

> **Advisory — `ice_downgrade` (NOT suppression):** ICE capped 20 candidate(s) below the Medium floor (advisory severity guidance; the finding still advances): AC-001, AC-002, BSA-001, BSA-002, DOS-001, DOS-002, DT-01, DT-02, DT-03, LOG-001, LOG-002, LOG-003, ORC-001, ORC-002, PC-01, PC-02, SG-001, SG-003, TOK-001, TOK-002

> **Caveat — `fp_pattern_check`:** fp matcher never cleared the 0.6 review bar on any candidate (raw max similarity 0.256, thresholded top 0.0). 0/48 candidates carry vuln_type, but even matching vuln_types stay sub-threshold once keyword overlap is added. suppression=0 here means the rule set is DORMANT on these findings — not proven recall-safe.
