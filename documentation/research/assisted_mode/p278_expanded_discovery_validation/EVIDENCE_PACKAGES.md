# P278 — EVIDENCE_PACKAGES

Per validation-queue candidate, an evidence package is auto-extracted from the harness mechanism body
(`expanded_validation_queue.py`). 23 required fields; any field empty OR equal to an `"operator-to-derive"`
placeholder is recorded MISSING. Outputs: `outputs/<contest>/evidence_packages.json`.

## Auto-extraction (the honest completeness signal)
The harness populates only `mechanism_summary` / `source_backed_trigger` (→ root_cause/source_refs) /
`falsification_question`. The exploitability fields — `attacker_action`, `affected_state_assets_permissions`,
`expected_value_delta`, `victim_gainer_hypothesis`, `terminality_hypothesis`, `assumptions` — are literal
**`operator-to-derive`** placeholders, and `tx_sequence` / `invariant_*` / `refutation_result` / `poc_assertion` have
**no harness source at all**. So every auto-extracted package is MISSING the attacker/delta/victim/terminality/
tx/assertion dimensions. This is the **completion-stage evidence gap** — the binding constraint on PoC-readiness.

## Hand-authored corpus sample (`outputs/hand_sample_packages.json`)
Two source-grounded packages from `audits/revert-lend-2024-03-strict-eval` src (read read-only) with all 10 readiness
dimensions filled, demonstrating the standard is reachable (not vacuous):
1. **V3Vault.transform** (EXTERNAL_INTEGRATION) — whitelisted transformer gets NFT approval + arbitrary `data` call;
   bounded only by end-of-call owner-unchanged + `_requireLoanIsHealthy`. Complete attacker path / control point /
   delta / victim / refutation / PoC assertion.
2. **V3Vault share-rounding** (SHARE_ROUNDING_PRECISION) — opposed rounding (debt `Rounding.Up` vs share-credit down)
   round-trip; complete tx-sequence + PoC assertion + refutation-to-attempt.
These are **validation hypotheses** (evidence complete enough to attempt a PoC), labeled SUPERVISED_EVAL — **not**
confirmed findings, no severity/reportability.
