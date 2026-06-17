# P260 — MODULE_SPEC
## CLI
python scripts/research/locus_shape_prioritizer.py --manifest <p> --accounting <p> --state-transition <p>
  [--base-candidates <p>] [--with-source] --out <json> [--top-n N] [--quiet]

## Pipeline
1. Load in-scope function/initializer/constructor items; drop low-signal loci (no checkpoint hit AND attack_surface<3).
2. locus_priority_score = Σ weight·dimension over: checkpoint_hit_strength, accounting_state_surface_density,
   asset_share_debt_reward_vars, lifecycle_criticality, external_call_callback, cross_contract_identity,
   first_depositor_donation_shareprice, liquidation_solvency, redemption_withdrawal_migration,
   queue_auction_statemachine, base_candidate_incompleteness, downstream_exploitability, attack_surface_score,
   risk_score. **Rule: BASE_COMPLETED_CHAIN gets a penalty so skipped high-risk checkpoint-hit loci outrank
   completed base candidates** (the P259 fix).
3. Shape routing: signals → applicable templates T1–T8 (marker→template map).
4. Per template emit an interrogative mechanism hypothesis (template_id, mechanism_summary, source_backed_trigger,
   attacker_action, affected_state, value_delta, victim/gainer, terminality, amplification, comparand_hint,
   assumptions, falsification_question, ranking_features_for_profile_B, ranking_features_for_profile_C). Operator-
   to-derive fields are explicit (module does not conclude).
5. top_2_mechanisms (by solvency/share-price-first ordering) + downstream_recommended_action ∈ {APPLY_RANKING,
   APPLY_COMPLETION, REFUTE_FIRST, LOW_PRIORITY, NEEDS_MANUAL_REVIEW}.
6. Sort by score; bound to top-N (default 15) to avoid noise flooding.

## Output per locus
locus_id, contract, function, source_path, source_span, base_signal, checkpoint_signal, why_prioritized,
locus_priority_score, priority_dimensions, applied_shape_templates, generated_mechanism_hypotheses, top_2_mechanisms,
bc_ranking_handoff (profile_B_inputs / profile_C_inputs), falsification_questions, downstream_recommended_action.

## Shape templates
T1 external-dependency-availability · T2 redemption/withdrawal-state-coupling · T3 reentrancy-through-accounting-
boundary · T4 migration/conversion-residue · T5 state-machine-liveness/terminality · T6 cross-transaction-drift ·
T7 liquidation/solvency-boundary · T8 share-price/donation/inflation-boundary.

## B/C handoff
Module does NOT decide severity/reportability; it prepares Profile B (messy-reconciliation) + Profile C (runner-up
challenge) ranking inputs + feeds five-operation completion.
