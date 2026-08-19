# Recall Lab — False-Suppression (Two-Budget) Report
_generated 2026-07-06T17:05:50Z_

Eval-only. Measurement of precision filters' recall cost; does not affect the real-world dashboard or pipeline behavior.

- Sets: `holdout`  ·  projects scored: **15**  ·  shared FP rules: **180**

## Top line
- Combined cut rate (measured filters): **0.0**
- Combined false-suppression rate: **0.0**  (0/102 known-valid caught findings removed)
- Loosen / make-reversible candidates (suppression_rate > 0): **none**
- Unmeasured in eval path: ice_downgrade, pre_submission_gates

## Per-filter

| Filter | Step | Mode | Cut rate | Suppression rate | n_suppressed | Loosen? |
|---|---|---|---|---|---|---|
| ice_downgrade | 3.4 | unmeasured_in_eval | — | — | 0 | no |
| fp_pattern_check | 3.6 | recomputed | 0.000 | 0.000 | 0 | no |
| pre_submission_gates | 3.7 | unmeasured_in_eval | — | — | 0 | no |
| dedup_screen | 3.8 | non_removing | 0.000 | 0.000 | 0 | no |

> **Caveat — `fp_pattern_check`:** STRUCTURALLY INERT on eval candidates: the FP matcher keys on vuln_type / _source_agent / description-keyword overlap, but 80/80 candidates carry no vuln_type and max similarity across all candidates is 0.0 (below the 0.6 review bar). suppression_rate=0 here means the filter never fired on this candidate shape — NOT that the rules are proven recall-safe. Re-run on real-world audits (rich merged_findings) for a true FP suppression signal.

_No filter removed a known-valid (awarded, caught) finding on the measured set._

## Measurement modes
- `recomputed` — filter decision reproduced faithfully over eval candidates (pure fn of finding+rules).
- `logged` — joined a per-finding disposition sidecar the project actually wrote.
- `non_removing` — filter never hard-removes (max action = human_review); cut_rate 0 by design.
- `unmeasured_in_eval` — evidence-gated (needs PoC/judge/defense sidecars the blind pass omits) and not run in the recall path; reported as null, not faked as 0.
