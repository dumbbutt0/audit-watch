# Recall Lab — Real-Audit False-Suppression Report
_generated 2026-07-06T17:07:41Z_  ·  audit `cronos-vvs-2026-06-20`

Eval-only. Does a precision filter recommend removing a finding this audit CONFIRMED? Oracle = the audit's own `submit.jsonl` / `state==ready` set. Measurement only — no pipeline change.

- Candidates: **11**  ·  confirmed oracle: **0 submit** / **0 ready**  ·  shared FP rules: **180**
- Loosen / make-reversible candidates (removed a confirmed keeper): **none**

| Filter | Step | Mode | Cut rate | Suppr (submit) | Suppr (ready) | Loosen? |
|---|---|---|---|---|---|---|
| ice_downgrade | 3.4 | non_removing | 0.000 | — | — | no |
| fp_pattern_check | 3.6 | recomputed | 0.000 | — | — | no |
| pre_submission_gates | 3.7 | logged | 0.000 | — | — | no |
| dedup_screen | 3.8 | non_removing | 0.000 | — | — | no |

> **Advisory — `ice_downgrade` (NOT suppression):** ICE capped 3 candidate(s) below the Medium floor (advisory severity guidance; the finding still advances): DT-001, ECO-001, TI-001

> **Caveat — `fp_pattern_check`:** fp matcher never cleared the 0.6 review bar on any candidate (raw max similarity 0.447, thresholded top 0.0). 11/11 candidates carry vuln_type, but even matching vuln_types stay sub-threshold once keyword overlap is added. suppression=0 here means the rule set is DORMANT on these findings — not proven recall-safe.
