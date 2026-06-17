# P212 Stage 2 — integrity checks

## Answer key
- Opened ONLY after explicit user "ready for scoring". Judging repo `_sealed/judging/` read for scoring; sophon is a
  completed contest — **no submission was or could be made**.
- Blind candidates were frozen BEFORE unseal (raw_outputs FREEZE `c14b2421`; CANDIDATE_REGISTER + L3 records) →
  scoring is honest/post-hoc; no backfilling of candidates after seeing the key.

## Production unchanged START==END (Stage 2 made NO code changes)
deep_trace.md `ef93a6c2` · validate_deep_pass_mechanisms.py `5d2a97f9` · eval_locus_resolver.py `3b0b2c02` ·
min_confirm_gate.py `41dd3c96` · confirm_gate.py `4fadfc5f` · submission_readiness_review.py `7c4b563d` ·
validate_p208_l3_readiness.py `7e148e18`. (dashboard.py `dbed5174` = the earlier /p212-page task, not Stage 2.)
Active audit = quantamm (unchanged). No submit/route/promote. `fabrication_rate=0` (every score cites the official
issue folder + the frozen candidate).

## Result
HIT 1 (003-H, the only High) / FALSE_POSITIVE 0 / recall 1/5; the confirmed finding was severity **under-rated**
(Medium vs official High). Decision: `SEVERITY_GATE_REGRESSION`.
