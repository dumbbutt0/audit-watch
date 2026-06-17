---
name: coverage-sweep
description: "Credit-free, skill-in-session cheap coverage sweep. Gives every low-attack-surface manifest item the deep specialists skipped a minimal, evidence-anchored review so no in-scope code reaches the review gate unexamined. Reasons over bundles from coverage_sweep_prepare.py and writes disposition decisions, then coverage_sweep_write.py validates+applies them. Activate when user says: /coverage-sweep, coverage sweep, sweep the long tail, clear remaining manifest items, close coverage gaps, or when the coverage gate blocks on unassigned items."
---

# Coverage Sweep (skill-in-session)

Closes the coverage long tail with **no API calls**. The deep specialists (/ite-audit) handle
high-surface items; this sweep makes every remaining in-scope manifest item examined/cleared/finding/
deferred — with evidence — so `coverage_completeness_gate.py` can pass honestly.

## When to use

After `/ite-audit` + `link_findings_to_manifest.py`, when the coverage gate still reports `unassigned`
in-scope items. Policy: `config/agent_policy.json → coverage_policy`. Reasoning spec: `prompts/coverage_sweep.md`.

## Procedure

1. **Prepare bundles (deterministic):**
   ```
   python scripts/coverage_sweep_prepare.py
   ```
   Writes `output/coverage_sweep/_bundles/<id>.json` (pending items grouped by file, lowest score
   first) + `_bundles/index.json`.

2. **Sweep each bundle (you, in-session).** Read `_bundles/index.json`, then each bundle. Apply
   `prompts/coverage_sweep.md` literally: for every item, read its source span (via Read) and decide
   `cleared | finding | needs_deep_pass | deferred_out_of_scope`.
   - `cleared` REQUIRES `evidence_span` (file:line you actually read) + one-line `reason` naming the
     guard/invariant/type-bound/no-attacker-path. **No clear without evidence — it will be rejected.**
   - **High-surface items (attack_surface_score >= 3) need a STRONG clear** with three extra fields or
     they are rejected: `attacker_reachability`, `guard_or_invariant`, `no_impact_reason`. If you can't
     supply all three confidently, emit `needs_deep_pass` (with `suggested_agent`) instead — never a
     shallow clear on a high-surface item.
   - A hardcoded address/constant is only `cleared` after you confirm its use is safe/admin-set;
     a mainnet address used on L2 (or similar) -> `needs_deep_pass`, never cleared.
   - **Dependency-based clears — a dependency is not a proof unless reviewed.** If you clear an item
     because another function/guard/estimator/oracle/math-rule/invariant/lifecycle-check protects it,
     name the dependency, give its `manifest_id`, give source evidence for it, and state whether the
     dependency is itself cleared/finding-linked/out-of-scope. If the dependency is unknown or
     unreviewed → `needs_deep_pass`, do NOT clear. Encode via `clear_depends_on`,
     `dependency_clearance_status`, `dependency_reason`, `dependency_evidence`, `downstream_guard_claim`,
     `downstream_guard_type`. Forbidden: "guarded downstream" / "bounded by MathGuard" / "the oracle
     prevents this" / "outputs pass through _guardQuantAMMWeights" when that guard is itself in-scope and
     unreviewed (the QuantAMM eval failure mode). `validate_dependency_clears.py` reports these;
     strict/full-audit mode routes them to `needs_deep_pass`.
   - **Structured capture (P178):** also record `dependency_name` (a REAL artifact — `validateBorrowCap`,
     `ensureNoNavOps`, `_guardQuantAMMWeights`; NOT a category word like guard/invariant/oracle/scope/
     downstream), `dependency_scope` (same_function|same_contract|cross_contract|out_of_scope|unknown),
     `dependency_status` (proven|unreviewed_dependency|missing), `proof_status` (valid|missing|not_applicable).
     A clear whose only "dependency" is a generic word is prose-only → advisory (never hard-routes).
   - **Reward-accounting clears need the checklist, not prose (Hybra reward-fn failure mode).** For
     reward/incentive/gauge/stake/claim/claimFees/notifyReward/emergencyWithdraw/receivePenaltyReward/createGauge
     items, prefer `needs_deep_pass` (`suggested_agent: reward_accounting_spec_review`); a `cleared` is valid ONLY
     with a `reward_accounting_checklist` object (11 fields: reward_index_update_order, totalsupply_sync_before_accrual,
     balance_snapshot_timing, transfer_side_effects, feeshares_before_after_rewards, fee_recipient_rewards,
     rewards_on_share_transfer, rewards_on_mint_burn, reward_debt_update_order, incentives_loop_bounds,
     totalsupply_includes_pending_feeshares), each answered concretely (yes/no/unknown · function · variable · file:line
     or "line unavailable" · conclusion · exploit direction). Any `unknown` ⇒ not cleared. Full contract:
     `prompts/coverage_sweep.md` / `prompts/deep_pass_packet.md`; `validate_spec_checklist_clears.py` routes prose/
     incomplete reward clears back.
   - Prefer honest `needs_deep_pass` (set `suggested_agent`) over a weak clear.
   - Don't let comments/NatSpec decide safety; verify against code.

3. **Emit decisions** to `data/coverage_sweep/_decisions.json` as
   `{"decisions": [{manifest_id, disposition, evidence_span, reason, [title, impact, severity,
   vuln_type, suggested_agent], [clear_depends_on, dependency_clearance_status, dependency_reason,
   dependency_evidence, downstream_guard_claim, downstream_guard_type], [reward_accounting_checklist]} ...]}`.

4. **Validate + apply (deterministic):**
   ```
   python scripts/coverage_sweep_write.py
   ```
   Applies dispositions, mints provisional `SWP-###` findings for `finding` items, and **rejects any
   clear lacking evidence/reason** (those items stay pending). Then re-run the coverage gate.

## Output

Report counts (cleared / finding / needs_deep_pass / deferred / rejected) and any items that stayed
pending. Then: `./run_pipeline.sh coverage-gate` to confirm the gate now passes (or see what remains).
