# P279 — DERIVER_DESIGN

## Inputs (source-derived only)
Per candidate: award_class (router) + contract.function + the joined coverage-manifest item: `signature`, `visibility`,
`mutability`, `modifiers`, `external_calls`, `has_loop`, `in_tainted_sink`, `tags`, `source_span`.
**Forbidden inputs** (denylist + fail-closed if award-text present): award_title/award_body/ak_title/reveal/answer_key/
scoring/issue_id. No target-specific constants.

## Derived fields (each: value + confidence HIGH|MEDIUM|LOW + source_basis + unresolved_assumptions)
attacker_path · attacker_controlled_inputs · impact_delta · victim_gainer · terminality_or_amplification ·
transaction_sequence · invariant_expected · invariant_broken · poc_assertion · refutation_questions ·
poc_tier_recommendation · unresolved_assumptions. Class templates: ACCESS / ORDER+FRONT_RUN / DOS / ACCOUNTING /
MATH_SHARE / ORACLE / EXTERNAL / REWARDS (structural, keyed off manifest signals — never award text).

## Confidence model — ANOMALY-based (the FP-vs-READY discipline)
attacker_path is HIGH/MEDIUM **only when the class anomaly is MANIFEST-VISIBLE**:
- **auth-guarded** (modifier matches only*/role/auth/admin/govern/owner/...) ⇒ **LOW** for ALL classes (a guarded
  function is not a clean unauthorized entry; bypass is a CORE claim). [global override]
- ACCESS: HIGH = external+state-changing+no-auth+config/param tag; MEDIUM = external+state-changing+no-auth.
- DOS: HIGH = has_loop; MEDIUM otherwise.
- EXTERNAL: HIGH = external_calls; MEDIUM otherwise.
- ORDER/FRONT: MEDIUM only if signature/name has order/fill/cancel/swap/settle/quote.
- **ACCOUNTING / MATH_SHARE / ORACLE / REWARDS / STATE: LOW** — the anomaly is a value-flow/invariant fact NOT visible
  in the manifest; the unresolved assumption CARRIES the core exploitability claim (needs the next repair: value-flow
  derivation).
impact_delta: HIGH = state-changing + value-movement/external-call/accounting-tag; MEDIUM = state-changing; LOW =
view/pure. victim_gainer: MEDIUM = value-movement signal; else LOW. A field with no source_basis is never HIGH.

## READY gate (in poc_readiness_evidence_gate)
READY_FOR_POC_INTENT only if all required fields present (non-placeholder) AND attacker_path/impact_delta/victim_gainer
all ≥ MEDIUM AND poc_assertion present AND no LOW-confidence core. Else NEEDS_MORE_EVIDENCE / NEEDS_MORE_RUNTIME.
Never infers severity/reportability. Gate strictness from P278 preserved; the confidence check is additive.

## Fail-closed / FP-risk controls
fail-closed on malformed input or award-text leakage; advisory contract stamped on every package; placeholder detector
treats 'operator-to-derive'/empty as MISSING; auth-guard + value-flow-invisible classes blocked from READY.
