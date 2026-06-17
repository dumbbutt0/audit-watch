# P152 — Decision

## Decision: **RUNTIME_REFUTED** (conversion_outcome = `runtime_refuted`)

A real-contract Foundry harness exercised the production `ERC20MultiVotes` (Credit Guild) delegate/transfer logic
(inherited unmodified). The canonical "delegated votes retained/inflated after transferring tokens away" suspicion
was **refuted**: the real guarded `transfer` (`_decrementVotesUntilFree`) decremented the delegatee's votes
1000e18 → 0, while an unguarded vulnerable reference retained 1000e18 and a no-transfer control stayed stable.
Distinct mechanism class (governance vote-accounting); fully unprivileged surface (reachability answered);
`duplicate_unknown`; `submission_ready=false`.

### Required output fields
candidate_id=H4-ecg-multivotes-accounting · audit=ecg-2023-12-holdout · architecture_class=governance/credit-guild
· mechanism_class=governance_vote_accounting_on_transfer · surface_function=transfer/transferFrom/
_decrementVotesUntilFree/getVotes · candidate_origin=P152 holdout scan · selection_reason=distinct class +
unprivileged + crisp + deploy-light + conversion-learning · rejected=pooltogether(heavy)/munchables(large)/
kelp(oracle) · deploy_complexity=moderate · harness_cost=low · real_contract_used=yes · production_source_changed=no
· corrected_reference_used=yes · control_case_used=yes · runtime_status=runtime_refuted · runtime_delta=getVotes
1000e18→0 (real) vs retains 1000e18 (ref) · reachability_verdict=unprivileged-but-mechanism-absent ·
severity_class=no_security_impact_shown · duplicate_status=duplicate_unknown · routing_allowed=false ·
submission_ready=false · conversion_outcome=runtime_refuted · primary_blocker_if_not_reportable=
mechanism_absent_guard_present · human_review_required=false.

### conversion object
`{mechanism_confirmed:false, attacker_reachable:true, severity_bearing:false, novelty_clear:false,
reportable:false, outcome:"runtime_refuted", blocker:null}`.

## Acceptance criteria
- Not merely another `runtime_confirmed` — a distinct-class **refutation**. ✓
- Explains non-conversion: the `_decrementVotesUntilFree` guard structurally prevents retention. ✓
- Reachability answered (unprivileged surface; mechanism absent). ✓; blocker explicit. ✓
- All P151 integrity checks preserved. ✓

## Panel + funnel
Panel after P152: `{rows: 15, runtime_only: 4, by_status: {runtime_confirmed: 4, runtime_refuted: 2, not_run: 9}}`
across 6 architectures; conversion schema on all 4 runtime-only rows. Across the 4 non-duplicate candidates,
**zero** reached `reportable_candidate_needs_human_review` — each stopped at its honest boundary
(needs_context / refuted / privileged-only / refuted). `submission_ready=false`.

## Next recommended phase (P153)
A cross-architecture conversion-quality summary (now that the panel spans 6 architectures with confirmed / refuted
/ privileged-only / needs-context outcomes and the conversion schema), or a fourth non-duplicate holdout
deliberately chosen to maximize the chance of a *reachable, value-bearing* candidate (to test whether the funnel
can reach `reportable_candidate_needs_human_review` honestly).
