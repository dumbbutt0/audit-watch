# P210 — recommendation

## Decision: `L3_DARK_WIRING_READY`

The P209 layered design is implemented behind the default-off flag `AUDITWATCH_L3_READINESS`, enforcing L3 only in the
human submission-readiness overlay + a read-only dashboard panel. Discovery, `deep_trace`, `min_confirm_gate`,
`confirm_gate`, `final_submission_pack`, routing, and canonical severity labels are unchanged (hash-verified).

## What was implemented
- `scripts/submission_readiness_review.py` (`b435a635`→`7c4b563d`): flag helper, `L3_DIR`, `_load_l3_record`, pure
  `l3_evaluate()` (imports the P208 `decide()`), new state `blocked_by_missing_l3_poc`, and flag-guarded hooks in
  `evaluate()` + `detail_overlay()`. Never flips `submission_ready`/`routing_allowed`.
- `scripts/dashboard.py` (`1eb4e278`→`857d593a`): flag-guarded read-only `l3` field per finding (absent flag-off).
- `tests/research/test_l3_readiness.py` (20 tests) + 2 human-override fixtures.

## Verification (all green)
- **Flag-off output-equivalent:** existing `test_submission_readiness.py` 14/14 unchanged; no `l3` key / no L3 blocker.
- **Flag-on correctness:** High+no-PoC → `blocked_by_missing_l3_poc`; High+PASS (decent & vultisig H-01) → clears;
  High+FAIL (M-03 ×2) → blocked; Medium → unaffected; malformed/None/garbage High → fail-closed; override+reason →
  allowed, override-no-reason → blocked.
- **Backtest/parity:** P208 backtest 10/10; `l3_evaluate` parity over all 10 fixtures.
- **No-submit guard:** advisory outputs only; L3 source region free of submit/route calls; canonical flags never flipped.
- **Hashes byte-identical START==END** for every out-of-scope gate/prompt/ledger; only the two intended files changed;
  `api_free=true` unchanged.

## Campaign status
The severity-calibration frontier is now realized as code: measured (P199) → principle (P204) → generalized on two
corpora (P205/P207) → dry-run policy (P208) → wiring design (P209) → **dark, default-off implementation (P210)**. The
L3 HIGH bar can be switched on per audit (`AUDITWATCH_L3_READINESS=1`) to require realized-impact PoC evidence for
High submission readiness, with zero impact when off.

## Next (NOT this phase; human decision)
Enable the flag in a real audit and add a cost model for L2/L3 harness authoring (auto-scaffold vs human-authored),
plus optional richer dashboard rendering. Wiring into the actual route-to-submit step remains out of scope (human
review stays mandatory). Deep-pass recall + oracle track remain separate.
