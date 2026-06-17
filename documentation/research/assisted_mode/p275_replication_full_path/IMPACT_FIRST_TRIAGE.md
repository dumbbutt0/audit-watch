# P275 — IMPACT_FIRST_TRIAGE (Phase 5, frozen P269)

Frozen `impact_first_poc_triage.py` (`63c88d02d2c7eefa`) over the 5 coverage-handoff reps
(`outputs/triage_candidates.json`). Output `outputs/triage_decisions.json` (`05bb24e072f618af`). poc_budget = 4. Guard:
**0 violations**.

| id | class | impact_fit | heavy | outcome |
|---|---|---|---|---|
| `pool_mint` | SHARE | 13 | yes | **SELECT_FOR_PARTIAL_RUNTIME** |
| `npm_mint` | ACCESS | 11 | no | **SELECT_FOR_FULL_POC** |
| `swap_callback` | ORDER | 11 | no | **SELECT_FOR_FULL_POC** |
| `pool_burn` | SHARE | 5 | no | **DEFER_LOW_IMPACT** |
| `migrate` | STATE | 3 | no | **KEEP_AS_CONTROL** |

## Reading
- **3 PoC candidates across 3 distinct classes** (SHARE, ACCESS, ORDER). Heavy `pool_mint` → PARTIAL_RUNTIME (not
  de-scoped). `migrate` retained only as a low-impact control; `pool_burn` (2nd SHARE rep) deferred low-impact.
- Cross-class diversity from coverage survived impact ranking; no easy-proof drift (the easy `migrate`/`beacon` did
  not displace a high-impact candidate). Matches the P269 discipline.

Next: Phase 6 — class-specific completion on the 3 selected.
