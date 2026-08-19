# Recall Lab — Corpus-Wide False-Suppression Sweep
_generated 2026-07-06T17:13:29Z_

Eval-only. Runs the real-audit suppression measure over every workspace with candidates. Measurement only — no pipeline change.

- Audits scanned: **63**  ·  with a confirmed oracle (submit>0): **12**  ·  total confirmed keepers: **73**
- **Any confirmed keeper suppressed anywhere? NO**
- fp_pattern_check ever fired on a real finding? NO (corpus raw max similarity 0.52; fires at >=0.6, rejects at >0.85)

| Filter | Corpus cut rate | audits w/ cut | audits w/ suppression | keepers suppressed |
|---|---|---|---|---|
| ice_downgrade | 0.0000 | 0 | 0 | 0 |
| fp_pattern_check | 0.0000 | 0 | 0 | 0 |
| pre_submission_gates | 0.0055 | 1 | 0 | 0 |
| dedup_screen | 0.0000 | 0 | 0 | 0 |

_No precision filter removed a confirmed keeper anywhere in the corpus._
