# P285 — INLINE_GUARD_GRANULARITY_DESIGN

## 1. P284 failure case
`claim_many` reached SIBLING_REFERENCE_FOUND/HIGH (missing `getOriginalOwner`), core dims upgraded, specific PoC
assertion — yet the gate returned INLINE_GUARD_REFUTED because the body contains `ownerOf(`. That token is
`address _nftOwner = IVotingEscrow(…).ownerOf(_tokenId)` — the **buggy recipient read** (the M-04 bug is using `ownerOf`
instead of `getOriginalOwner`), not an access guard. P281 D1's token-PRESENCE heuristic cannot tell the two apart.

## 2. The distinction
- **access guard** = controls whether the caller may proceed (gates execution).
- **ownership/value read** = computes who receives value / how much. Does not restrict the caller.
If D1 conflates them it suppresses recipient-parity, rewards, ownership, and batch/single sibling bugs.

## 3. Refinement: token-in-EXECUTION-GATE, not token-PRESENCE
On the comment-stripped body, compute **execution-gate spans**:
- `require(…)` / `assert(…)` argument span → STRONG.
- `if (cond)` when the following statement/braced block contains `revert`/`return` → STRONG (`break`/`continue` →
  MEDIUM). Handles single-line `if(c) revert;` and multi-line `if(c){ … revert …; }` (balanced-brace walk, bounded).
- `onlyX` modifier in the signature, and custom-error revert markers → STRONG.
A matched auth/ownership token is `EXECUTION_GUARD` iff one of its occurrences falls inside a gate span. Otherwise it is
classified by its statement: `RHS of =` → VALUE_READ / RECIPIENT_READ (recipient if the LHS/arg name carries
owner/recipient/to/beneficiary) · arg to transfer/claim/distribute/mint/send → RECIPIENT_READ/VALUE_READ · inside
`emit` → EVENT_READ · `return …` → RETURN_READ · arithmetic → ARITHMETIC_READ · else UNKNOWN_READ.

## 4. Context taxonomy (emitted per token)
`{token, context ∈ {EXECUTION_GUARD, VALUE_READ, RECIPIENT_READ, EVENT_READ, RETURN_READ, ARITHMETIC_READ,
UNKNOWN_READ}, guard_strength ∈ {STRONG, MEDIUM, LOW, NONE}, source_snippet, source_basis, reason}`.

## 5. Refined fields + gate
- `inline_guard_detected = any(EXECUTION_GUARD with strength STRONG|MEDIUM)`.
- `inline_guard_ambiguous = (no execution guard) and any(UNKNOWN_READ auth token)`.
- Gate precedence (unchanged) + one new fail-closed status: declaration-only → NEEDS_SOURCE_SPAN · execution guard →
  INLINE_GUARD_REFUTED · value-class no evidence → NEEDS_VALUE_FLOW · state-class no evidence → NEEDS_STATE_MACHINE ·
  **NEW** `inline_guard_ambiguous` and no deviation → `NEEDS_GUARD_CONTEXT` (held, never READY).
- A value/state candidate with a HIGH/MEDIUM invariant-delta deviation and only VALUE_READ/RECIPIENT_READ auth tokens is
  not blocked on D1 grounds (the `claim_many` lift path); it still must pass attacker/impact/victim + a specific PoC
  assertion (the P284 path).

## 6. Allowed-refutation vs non-refuting-read examples
- GUARD: `require(msg.sender == owner)` · `if (msg.sender != owner) revert` · `onlyOwner` · `assert(_isApprovedOrOwner(
  msg.sender, id))` · `require(isApprovedForAll[o][s])`.
- READ (not a guard): `address recipient = ownerOf(id)` · `token.transfer(ownerOf(id), amt)` · `emit Claimed(ownerOf(id))`
  · `return ownerOf(id)` · `if (msg.sender != owner) { allowance -= shares }` (ERC4626 allowance-spend, no revert).

## 7. Fail-closed rules
A true guard must be PRESERVED: any auth token inside require/assert/if-revert/modifier/custom-error → EXECUTION_GUARD.
An ambiguous auth READ that would otherwise reach READY → NEEDS_GUARD_CONTEXT (never silently lifted). Bypass is still an
explicit operator field, never inferred from source.

## 8. FP risk
The risk is MISSING a true guard (false unblock). Mitigated by: covering require/assert/if-revert/return/modifier/
custom-error; classifying by ALL occurrences (a token guarding in one place and reading in another counts as guard);
fail-closed NEEDS_GUARD_CONTEXT for ambiguity; and the audit confirming each reclassification. Liveness controls
(`whenNotPaused`) are intentionally not treated as access refutations (they don't restrict the caller).
