# P215 — FAILURE CASES & EDGE BEHAVIORS

## Tooling friction (non-fatal, recorded)
1. **`final_submission_pack.py` blocked** until `pre_submission_gate.py --all` produced `data/triage/gate_results.jsonl`
   (Step 3.7). Expected ordering; ran the gate, then the packager succeeded.
2. **Dashboard server launch flaky** in-harness (consistent with prior phases) — verified read-only routes by importing
   `dashboard.py` and calling `_build_state()` / handlers directly. 0 stray processes left.
3. **Dashboard under-counted (0)** until the Step-3 `populate_finding_metadata` substrate (`data/findings/<id>.json`)
   was written; after running it, funnel counts matched the artifacts.

## Calibration failure cases (the substantive ones)
4. **Under-rated H-13 (pause-DoS) → Medium.** Found the exact mechanism (ZETA-04) but the triage severity floor + no
   executed harness kept it Medium. The P214 carve-out doesn't fire (admin-prereq pause + no harness).
5. **Wrong mechanism on H-10 (Trident).** Right contract/function/impact (ZETA-11) but identified pool-array validation
   instead of the wrong-router-method root cause → PARTIAL, under-rated.
6. **Scope blindness.** Solidity-only discovery missed the entire Go-node surface (~40 findings, most Highs).

## Things that worked (no failure)
- 0 false-Highs; 0 route/submit side effects; production hashes byte-identical; answer key sealed until post-freeze;
  no canonical flag flipped; dry-run queue carried 0 Highs-without-L3-PASS; no silent drops (ZETA-09 disproof recorded).

## No abort conditions triggered
None of the HUNT_ABORTED_* conditions occurred (no external route, no runtime_policy edit, key sealed until freeze,
quantamm restored, no submit/promote control, no High in queue without L3 PASS, no High package missing L3 evidence).
