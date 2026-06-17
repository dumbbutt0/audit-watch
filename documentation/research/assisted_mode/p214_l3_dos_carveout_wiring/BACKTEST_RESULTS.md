# P214 — backtest results

- **Flag-off equivalence:** P208 backtest 10/10 unchanged; `decide()` on the updated SOPH-03 record → medium with NO
  carve-out keys → byte-equivalent to pre-P214.
- **Flag-on fix:** SOPH-03 medium → **High** (`dos_carveout_applied=true`); **0 new false-Highs**.
- **Negative controls (flag-on) stay < High:** decent M-03 / vultisig M-03 / decent-06 (medium), decent-12 /
  munchables-DoS / static-no-PoC / precision (needs_harness), source-refuted (invalid) — verified by the P213 set
  (still 10/10) and the new tests' guards.
- **Schema compatibility:** records with and without carve-out fields both validate.
- **No-submit side effects:** none; canonical `submission_ready`/`routing_allowed` never set; active audit unchanged.
