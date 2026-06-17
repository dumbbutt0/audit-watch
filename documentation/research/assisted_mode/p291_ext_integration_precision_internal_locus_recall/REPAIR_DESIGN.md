# P291 — REPAIR_DESIGN

## P290 root causes (verified in source)
- **A** — EXTERNAL_INTEGRATION false READY: `completion_evidence_deriver.derive()` assigns EXTERNAL_INTEGRATION
  `attacker_path` MEDIUM/HIGH from the CLASS LABEL alone (HIGH if `external_calls`, else MEDIUM) + impact template HIGH.
  The gate, since EXTERNAL_INTEGRATION is neither a value nor state class, lifts via the main P279 readiness path with NO
  source-backed deviation. `Pools.deposit` (nonReentrant + plain `safeTransferFrom`, no callback) reached READY and was
  PoC-refuted.
- **B** — reward-index lens starved: the blind candidate set = `recall_first_harness.run` → `recall_first_shape_sweep.
  sweep` → `_to_advisory`; internal functions are not surfaced as candidates, so internal awarded loci
  (`StakingRewards._increaseUserShare`) never reach the queue/lenses.

## Part A — EXTERNAL_INTEGRATION READY precision
`integration_deviation_evidence.deviation_present` is True ONLY with a concrete, source-backed basis:
- **AUTO-detected (unambiguous, on the comment-stripped body)**: low-level external call (`.call(`, `.call{`,
  `delegatecall`) / callback-interface invocation; reentrancy-ordering = a low-level external call with NO
  `nonReentrant`/reentrancy guard. These are signals `Pools.deposit` lacks.
- **EXPLICIT operator/source evidence** (`integration_deviation_evidence` provided with `deviation_present:true` +
  basis): for the structural bases that are NOT safely auto-inferable (fee-on-transfer/rebasing accounting gap, adapter/
  bridge result-without-validation, CREATE2/callback-sender, cross-contract sibling parity). "READY if evidence complete"
  = the operator/source supplied the deviation, never auto-guessed.
**Forbidden as deviation** (fail-closed): class label · generic "crafted callback" text · mere `safeTransferFrom`/
`transferFrom`/external call/token transfer · external visibility · naming-only callback/router/adapter ·
`nonReentrant`-protected ordinary transfer · invariant_delta NO_REFERENCE.
**Why fee-on-transfer is NOT auto-detected**: structurally identical to `Pools.deposit` (credit input `amount` + pull via
`transferFrom`, no before/after balance measure). Auto-flagging it would re-introduce the exact P290 false READY (salty
whitelists only fee-less tokens by design). So fee-on-transfer requires explicit evidence.
**Gate**: precedence block `elif cls == "EXTERNAL_INTEGRATION" and not _integration_deviation(pkg):
NEEDS_INTEGRATION_DEVIATION_EVIDENCE` (new status, fail-closed). `Pools.deposit` → NEEDS_INTEGRATION_DEVIATION_EVIDENCE.

## Part B — internal accounting/reward locus recall
Post-sweep pass in `recall_first_harness.run()`: for each surfaced public/external candidate, read its body
(`source_span_guard_extractor.extract_body`, read-only), resolve internal callees by name vs the manifest (same-contract
or unique; fail-closed on ambiguous/external/dynamic), and surface a callee as an `internal_locus` advisory candidate iff
ALL: reached from a public/external candidate · has source span · not test/mock · not a trivial getter · class-relevant
by signal terms (share/index/reward(s)/accumulator/checkpoint/epoch/debt/collateral/loss/slash/stake/unstake/deposit/
withdraw/mint/burn/supply/balance/accounting/update/increase/decrease) · performs a state mutation (write).
**Caps (config)**: ≤3 internal expansions per public entry · ≤15 internal-locus candidates per contest · ranked by
class-relevant term count + state writes · no pure libraries unless reached+class-relevant · no constructor/init-only
unless reward-index/init-relevant · `advisory_only:true` (no READY unless the evidence gate later proves it).

## FP / noise controls
A is fail-closed (auto-detect only unambiguous low-level/callback/reentrancy-ordering; everything else needs explicit
evidence). B is advisory-only + hard caps + class-relevance + fail-closed callee resolution. Regression isolation: the
kelp/blackhole/L2Governor/ECG-H04 regressions are re-checked by running deriver+gate on the FROZEN P278/run
evidence_packages (the harness edit cannot perturb them); the internal-locus surfacing is demoed by re-running the harness.

## Not production authority
All outputs advisory/research/blind-eval only; no severity/submission/confirmed; reused detectors imported read-only.
