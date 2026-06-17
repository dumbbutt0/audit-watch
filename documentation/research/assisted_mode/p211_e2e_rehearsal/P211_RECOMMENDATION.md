# P211 — recommendation

## Decision: `E2E_REHEARSAL_READY_FOR_REAL_HUNT`

The dark-wired L3 readiness gate was rehearsed end-to-end with `AUDITWATCH_L3_READINESS=1` on a known corpus
(decent-2024-01-holdout) through the real wired functions, with zero submit/route/promote side effects and the active
quantamm eval untouched.

## Results
- **Flag-off baseline clean:** no `l3` fields, no `blocked_by_missing_l3_poc`, no dashboard panel — output-equivalent
  to pre-P210.
- **Flag-on correct:** DEC-H-01 (L3 PASS) → High readiness cleared; DEC-M-03 (L3 FAIL) as High → blocked; DEC-M-03 as
  Medium → unaffected; DEC-STATIC (no record) as High → fail-closed blocked.
- **Readiness write path:** `record_review` blocked the L3-failing High and, for the L3-PASS High, saved an advisory
  `ready_for_submission_package` row with `routing_allowed:false` and `submission_ready` never set — the canonical-flag
  invariant holds with the gate enabled.
- **Human override:** with written reason → allowed + visible; without reason → blocked.
- **Dashboard:** L3 panel present only flag-on, read-only, no controls.
- **Package:** the High package carries full L3 evidence (status/poc_path/poc_command/actual/control) and shows no
  auto-submit.
- **Answer key:** genuine High (H-01) preserved, over-rated Medium (M-03) demoted, 0 false positives; L3-blocker
  correctness 3/3.
- **Integrity:** all production prompt/gate/ledger hashes byte-identical START==END; only the two P210 files exist
  (unchanged in P211); `api_free=true`; active audit not switched; flag never persisted; rehearsal ledger rows removed.

## Campaign status
The L3 HIGH bar now runs correctly through the real pipeline surface under the flag. The full arc is realized:
measured (P199) → principle (P204) → generalized on two corpora (P205/P207) → dry-run policy (P208) → wiring design
(P209) → dark default-off implementation (P210) → **end-to-end rehearsal validated (P211)**.

## Next (human decision; NOT this phase)
1. Enable `AUDITWATCH_L3_READINESS=1` on a real hunt (per-candidate L3 records at `output_research/l3_readiness/`).
2. Wire the L3 fields into `final_submission_pack.py` rendering (so packages emit L3 natively).
3. Cost model for L2/L3 harness authoring (auto-scaffold vs human).
4. Decide whether to extend the q6 severity vocabulary to include "Critical".
Deep-pass recall + oracle track remain separate. Route-to-submit stays out of scope; human review mandatory.
