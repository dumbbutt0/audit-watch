# P212 Stage 1B — integrity checks (START == END)

## Production artifacts byte-identical START==END (none modified)
deep_trace.md `ef93a6c2` · min_confirm_gate.py `41dd3c96` · confirm_gate.py `4fadfc5f` ·
submission_readiness_review.py `7c4b563d` · dashboard.py `857d593a` · validate_p208_l3_readiness.py `7e148e18` ·
ledger `fc446040`. ✓

## Target / firewall
- Cloned target source tree `c2d9ecd1` — **unedited** (a byte-identical copy lives in `pocs/p212/realsrc/` for
  compilation only).
- Sealed answer key `targets/2024-05-sophon/_sealed/judging/` (267 files) present + **UNREAD**. No finding bodies/
  titles/judging opened.
- `AUDITWATCH_L3_READINESS` used in-process only; unset at END; not persisted to config; `api_free=true`.
- Active audit = quantamm (not switched). No submit/route/promote; canonical flags not flipped.

## Harnesses
- `pocs/p212/` Foundry (solc 0.8.25, OZ v5.0.2 remap): `forge test -vv` → **4 passed / 4** (`run_log.txt`).
- Real SophonFarming deployed unmodified; only external token deps mocked (MockERC20/MockStETH/MockWstETH); MockStETH
  models the documented stETH 1-wei share-rounding. Build artifacts (out/cache) trimmed.
- L3 records `output_research/l3_readiness/SOPH-0{1,2,3}.json` updated with measured results; overlay re-run.

## Outcome
SOPH-01/02 REFUTED (invalid); SOPH-03 confirmed MEDIUM (DoS). 0 High-submission-ready. `fabrication_rate=0` (every
verdict backed by a forge run log). `stage1b_metrics.json` valid JSON.

## Decision
`READY_FOR_SCORING` — answer key remains sealed; STAGE 2 awaits user approval.
