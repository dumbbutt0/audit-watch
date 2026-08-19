# TI-004 — USDC blacklist/freeze DoS on payouts is per-iteration in batch loops (single bad address skipped, not whole-loop revert) but bricks an individual blacklisted owner's own funds permanently

- **Severity (recommended):** Low
- **Category (HackenProof VRT):** DoS with (Unexpected) revert
- **Triage status:** downgraded
- **Confidence:** High
- **ICE:** Impact=Low · Confidence=High · Exploitability=Conditional (requires a USDC blacklist event; batch DoS mitigated by keeper-curated owners[])
- **Location(s):** `src/CarthaVault.sol:565-598,280-337,371-416,421-467; src/CarthaParentVault.sol:684-704,625-659,713-725`
- **Vulnerable files (bundled in `sources/`):** `CarthaVault.sol`, `CarthaParentVault.sol`

## Description

Confirmed the batch withdrawal loops are resilient to a single blacklisted/frozen recipient: processQueuedWithdrawals (CarthaVault.sol:565-598) and processQueuedParentWithdrawals (CarthaParentVault.sol:684-704) iterate owners[] and the safeTransfer to a blacklisted owner reverts THAT iteration only via the natural top-level revert — WAIT: the safeTransfer is inside the loop body with NO try/catch, so a revert on owner[i]'s safeTransfer reverts the ENTIRE processQueued transaction, not just that iteration. The pre-transfer guards (pendingWithdrawal/exists/lock/cooldown/payout==0||payout>vaultBalance) only `continue` past INELIGIBLE owners; a blacklisted-but-eligible owner whose safeTransfer reverts will revert the whole keeper batch, denying all other queued owners in the same call. The keeper can work around it by excluding the blacklisted owner from the owners[] array (the batch is keeper-curated, not self-enumerating), so the DoS is bounded to: (a) the keeper must learn which address is blacklisted and exclude it, and (b) the blacklisted owner can never be paid through any push path (release/forceExit/processQueued all safeTransfer to the owner). This is the standard USDC-blacklist push-payment risk: the blacklisted user's OWN funds are stuck (their problem), and a naive keeper batch including them reverts for everyone until the keeper drops them. No pull-payment fallback exists. Medium-DoS pattern downgraded to Low because the batch is keeper-curated (the keeper controls owners[]) and the harm is to the blacklisted party's own funds.

## Impact

A blacklisted/frozen owner can never receive a payout (own funds stuck). A keeper batch that includes a blacklisted-but-eligible owner reverts entirely, blocking all other queued users in that call until the keeper excludes the bad address (operational DoS, recoverable by re-batching).

## Attack path (Intent / Technique / Evasion)

- **Intent:** Deny vault payouts (to a blacklisted user, and transitively to a batch) by exploiting USDC's blacklist + push-payment design.
- **Technique:** An owner is USDC-blacklisted (or USDC pauses); their safeTransfer in release/forceExit/processQueued reverts; in a batch this reverts the whole keeper call until the owner is dropped from owners[].
- **Evasion:** No try/catch around per-owner safeTransfer and no pull-payment fallback; the loop's continue checks only cover eligibility, not transfer failure.

## Reachability / follow-up

reachable: blacklisted owner in a batch / own withdrawal. no_privileged_keys: keeper curates list. state_before_after: iteration reverts / funds stuck. why_guards_fail: no try/catch; no pull pattern. scope_match: token-integration edge.

## Triage reasoning

USDC blacklist/freeze: the per-owner safeTransfer in processQueuedWithdrawals/processQueuedParentWithdrawals has no try/catch — a blacklisted-but-eligible owner reverts that batch iteration (mitigated since the loop is keeper-curated owners[] and is per-iteration). A blacklisted user's own funds are permanently stuck (no pull fallback). Low.
