# P215 — FUNNEL EFFECTIVENESS

The phase's core question: **can real candidates route through the actual funnel (not a side page)?** Answer: **yes.**

## Stages exercised end-to-end on a real audit workspace
audit_manager switch → coverage_manifest (201 in-scope items) → blind deep_trace → `findings_deep_trace.json` →
report_generator → `merged_findings.json` (1C/7H/4M) → /triage decisions → `triage_write.py` buckets →
`min_confirm_gate` (PASS 7/7) → `confirm_inventory`+`confirm_reachability`+`confirm_gate` (eval+submission, PASS) →
`pre_submission_gate --all` (12 PASS) → `final_submission_pack` (packages) → L3 readiness (flag on) → dry-run queue →
dashboard `_build_state` (read-only) → freeze → score. **No stage was bypassed; nothing was a P212-style side page.**

## Did the right candidates route?
- The 2 genuine in-scope Solidity findings (ZETA-04=H-13, ZETA-11=H-10) **did route** (into poc_required / submit) —
  the funnel surfaced them, but at Medium.
- The privileged/centralization item (ZETA-03) was correctly diverted to downgraded/Low.
- The by-design item (ZETA-09) was rejected with a disproof (no silent drop).

## Gaps the rehearsal exposed
1. **Scope:** discovery was Solidity-only; the contest is Go-node-heavy → ~40 findings unreachable. A real hunt must
   scope the off-chain node code. (Biggest recall driver.)
2. **confirm_gate ≠ privilege demotion:** `confirm_gate --mode submission` did not hard-fail privileged TSS Highs
   (classifier marked them `uncertain`, not `privileged_only`). Privilege calibration is enforced one layer later at L3.
   Defensible, but means confirm_gate alone is insufficient to demote privileged Highs.
3. **Dashboard depends on the Step-3 `populate_finding_metadata` substrate**, not just merged_findings + triage buckets;
   the funnel must run that step or the dashboard under-counts (found and fixed → 0 mismatches).
4. **DoS/availability under-rating** persists (H-13, H-10 → Medium): triage severity floor + missing harness effort, not
   an L3 fault.

## Safety (all held)
No external submission/route; `runtime_policy.json` untouched; canonical `submission_ready`/`routing_allowed` never
flipped; dashboard has no submit/promote-to-platform control; answer key opened only post-freeze; production hashes
byte-identical; quantamm restorable. **0 route/submit side effects.**

## Verdict
**The funnel works end-to-end and is safe.** Its limiting factors in this rehearsal were **scope coverage** and
**harness/severity calibration for DoS**, not routing mechanics.
