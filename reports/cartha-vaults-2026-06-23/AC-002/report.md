# AC-002 — CarthaParentVault.executeForceExit applies an uncapped penaltyBps from the FORCE_EXITER, not bound to any merkle proof

- **Severity (recommended):** Low
- **Category (HackenProof VRT):** Improper Access Control
- **Triage status:** submit
- **Confidence:** High
- **ICE:** Impact=Victim's locked principal is confiscated (up to ~100%); the retained penalty inflates the parent's residual assets for everyone else. · Confidence=- · Exploitability=-
- **Location(s):** `/home/dummy/clones/cartha-vaults-main/src/CarthaParentVault.sol:713`
- **Vulnerable files (bundled in `sources/`):** `CarthaParentVault.sol`

## Description

CarthaParentVault.executeForceExit(owner, penaltyBps) is gated by Roles.FORCE_EXITER and applies the penalty with NO upper bound at the parent: `if (penaltyBps > 0) payout -= (payout * penaltyBps) / BASIS_POINTS;` (line 721). The parent trusts the caller (the satellite) to cap penaltyBps and to have verified the merkle proof; the parent itself enforces neither a cap nor a proof. Today the only FORCE_EXITER is the CarthaForceExit satellite, which passes 0 (eviction) or UNDERPERFORMER_PENALTY_BPS = 500 (5%) after verifying (owner, category) against its roots. But the authority model is: ANY address holding Roles.FORCE_EXITER can call executeForceExit(victim, arbitraryPenalty<=10000) directly on the parent with no merkle proof and seize up to 100% of the victim's locked payout (penalty stays in the parent vault, diluting attacker's own future redemption only marginally vs. the victim's loss). penaltyBps > 10000 simply reverts (underflow), so the practical attacker range is 1..10000. This confirms deep-analysis DT-005, generalized: the parent's force-exit penalty is unconstrained and unbound to the eviction reason. The child CarthaVault hardcodes its penalty path (forceExitUnderperformer uses $.performancePenalty which is ADMIN-capped to MAX_PENALTY_BPS=2000), so the unbounded penalty is parent-specific. Defense-in-depth fix: clamp penaltyBps to a MAX in executeForceExit even though the satellite is trusted.

## Impact

A FORCE_EXITER (a satellite that is upgraded/compromised, or any extra address ever granted the role) can force-exit any locked parent position and confiscate up to 100% of its payout with no merkle binding; the parent has no cap to backstop a misbehaving satellite.

## Attack path (Intent / Technique / Evasion)

- **Intent:** Holding (or compromising) Roles.FORCE_EXITER, force-exit an arbitrary locker on the parent and confiscate up to 100% of their locked payout, bypassing the satellite's merkle list entirely.
- **Technique:** Call CarthaParentVault.executeForceExit(victim, 9999) directly. onlyRole(FORCE_EXITER) passes; lockPos.exists check passes; _prepareSharePayout computes the victim's full share value; line 721 subtracts 99.99% as 'penalty'; _settleFullExit deletes the position, burns the victim's shares, and sends them only the 0.01% residual.
- **Evasion:** The design intends the satellite (CarthaForceExit) to (a) verify (owner, category) merkle membership and (b) pass only 0 or 500 bps. The parent re-implements neither check and applies penaltyBps verbatim with no cap (BASIS_POINTS is the divisor, not a ceiling). The trust is fully delegated to the caller, with no parent-side backstop.

## Reachability / follow-up

reachable: FORCE_EXITER calls executeForceExit(user, ~9999). no_privileged_keys: NO — requires FORCE_EXITER. state_before_after: user payout reduced to ~0. why_guards_fail: no penalty ceiling. scope_match: privileged hardening.

## Triage reasoning

CarthaParentVault.executeForceExit applies payout*penaltyBps/10000 with no upper cap (BASIS_POINTS is the divisor, not a ceiling; >10000 just underflow-reverts) and no merkle binding at the parent. Any FORCE_EXITER could confiscate up to ~100% of a matured user's payout. Today only the CarthaForceExit satellite holds FORCE_EXITER and passes 0/500, so trust-bounded. Merges DT-005 (same uncapped-penalty finding). Fix: clamp penaltyBps <= MAX_PENALTY_BPS in executeForceExit.
