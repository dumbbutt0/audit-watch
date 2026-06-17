# P144 — Decision

## Decision: **ADVANCE_TO_HUMAN_REVIEW_FINDING** — scope gate **DUPLICATE_KNOWN_LOCALLY**

Both rubric conditions for advancing are met from source:
- **Value-impact path is source-supported:** oracle output → connector/AccountingManager TVL → `totalAssets()`
  (ERC4626 share price) → `previewDeposit`/`previewRedeem` ⇒ user-triggerable value movement
  (consumer_impact_analysis.md).
- **Production reachability is source-supported (by design):** multi-hop `priceRoutes` are an intended, maintainer-
  configured feature that mis-prices on any ≥2-hop divergent route; no malicious admin required
  (production_configurability.md → **PROTOCOL_CONFIG_REACHABLE**).

So B1 **advances to human review**. Two hard caveats keep it short of submission:
1. **DUPLICATE_KNOWN_LOCALLY** — it is the awarded noya **H-03** (answer key) ⇒ route as confirmation of a known
   finding, **not** a novel submission.
2. **Reachability is design-supported, not config-demonstrated** (no on-disk ≥2-hop route) and the **end-to-end
   economic loss is not PoC'd** (P143 proves only the oracle delta). The human must confirm a live divergent route
   + quantify loss before any severity is finalized.

### Why not the other labels
- Not RUNTIME_CONFIRMED_BUT_REACHABILITY_UNPROVEN: reachability *is* source-supported (intended feature); only a
  *live config instance* is unproven — captured as a caveat, not a blocker.
- Not RUNTIME_CONFIRMED_BUT_IMPACT_UNPROVEN: the value path is clearly source-supported (4626 share price); only
  the end-to-end magnitude is unproven — caveat.
- Not TRUSTED_ADMIN_CONFIG_ONLY: no malicious/compromised admin is needed — a *correct* multi-hop config still
  mis-prices.
- Not VIEW_ONLY_OR_NO_VALUE_MOVEMENT: consumers move value (deposit/redeem).
- Not DUPLICATE_OR_SCOPE_BLOCKED as the *technical* verdict, but the duplicate fact is recorded as the **governing
  submission gate** — net effect: advance to human review, do not submit.
- Not KILLED_BY_SOURCE_CONTEXT: source supports, not contradicts, the defect.
- Not NEEDS_MORE_CONTEXT: enough source evidence to advance; residual items are explicit human steps.

## Status separation (unchanged)
`prompt_decision=finding` · `runtime_status=runtime_confirmed` (mechanism evidence only) ·
`review_status=advance_to_human_review` · `scope=DUPLICATE_KNOWN_LOCALLY` · **`submission_ready=false`** ·
`advisory_only=true` · `requires_human_review=true` · `requires_poc_review=true`. Runtime confirmation strengthens
the advisory; it does not authorize submission.

## Human to-do before any submission decision
1. Confirm a production ≥2-hop `priceRoute` exists on a material-value token with divergent per-hop oracles.
2. End-to-end PoC: configured route → TVL skew → deposit/redeem share delta → net loss > gas (bounded).
3. Duplicate ruling (it is the known H-03) + final severity.
