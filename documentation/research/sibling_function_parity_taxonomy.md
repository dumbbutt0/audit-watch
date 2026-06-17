# Taxonomy — `sibling_function_parity`

Seven parity categories. Each = a class of asymmetry between two **sibling** functions (functions that
reach the same state transition via name-stem kinship or shared call/state-write sets). For each: the
definition, the distinguishing signal the detector keys on, example sibling pairs, and the
suppression that keeps it FP-tight. Research-only; classifier returns the `parity_type` field set to
one of these `id`s.

## Sibling relation (precondition for every category)

Two functions A, B in the same contract are **siblings** iff:
- **Name-stem kinship:** shared stem after stripping a known variant affix —
  `claim`/`claim_many`, `deposit`/`depositFor`, `mint`/`mintTo`, `borrow`/`borrowFor`,
  `redeem`/`redeemFor`, `validateX`/`executeX`, `X`/`Xbatch`/`batchX`/`X_many`; **OR**
- **Behavioral kinship:** Jaccard(call-set A, call-set B) ≥ threshold **AND** ≥2 shared internal calls
  or shared state-write targets.
Both A and B must be non-view/non-pure and reach a mutating path. Sibling relation alone is **not** a
finding — an asymmetry (below) must also hold.

---

## 1. `validation_parity`

**Definition.** A performs a validation (require / internal validator call / threshold check) before a
shared state transition; B reaches the same transition without the equivalent validation.
**Signal.** A `require`/validator-call/threshold token present in A's body, absent in B's, where both
share the downstream mutating call/state-write.
**Examples.** `deposit`/`depositFor`, `mint`/`mintTo`, `borrow`/`borrowFor`, `validateSellCreditMarket`
vs the execute path (Size M-02).
**Suppress.** B forwards to A; B's missing check is provably enforced in a shared helper both call.

## 2. `cap_enforcement_parity`

**Definition.** One sibling checks a supply/borrow/mint cap or position limit; the sibling path does
not.
**Signal.** cap vocabulary (`cap`/`limit`/`ceiling`/`maxSupply`/`borrowCap`) in a guard in A, absent in
B, on a shared mint/borrow/supply state-write.
**Examples.** `mint` (cap-checked) vs `mintTo`/internal-mint; pool deposit vs depositFor.
**Suppress.** cap enforced in a shared `_beforeX` hook; B is admin-only seeding.

## 3. `access_control_parity`

**Definition.** One sibling carries an access modifier / `msg.sender` gate; the sibling reaching the
same effect lacks an equivalent restriction.
**Signal.** modifier-set(A) (from manifest `modifiers`) or `require(msg.sender == ...)` present, the
sibling's empty/weaker, on a shared privileged state-write. (Body-level; distinct from `semantic_guard`
which is an LLM modifier-only audit — here it is one *axis of a sibling diff*.)
**Examples.** `setX` (onlyOwner) vs `setXInternalExposed`; `withdraw`/`withdrawFor`.
**Suppress.** both admin; the unguarded sibling is `internal`/`private` and never externally reachable.

## 4. `state_transition_parity`

**Definition.** One sibling updates accounting state (checkpoint / debt / shares / balance / total);
the sibling partially updates or omits an update for the same logical transition.
**Signal.** a state-write target (`x -= ` / `x += ` / `checkpoint` / `_update*`) present in A, absent
in B, while both perform the value-moving call.
**Examples.** singular vs batch where the batch forgets `token_last_balance -=` per-item, or
`executeBuyCreditMarket` over-estimates vs sibling (Size M-12).
**Suppress.** the batch aggregates the same write once at the end (legitimate); the omitted write is to
a write-only event/log.

## 5. `recipient_parity`

**Definition.** One path validates/resolves the receiver/beneficiary/destination; the sibling skips it
and sends to a raw/unresolved address.
**Signal.** a recipient-resolution call (`getOriginalOwner`, owner-resolution branch, receiver
validation) present in A, absent in B, on a shared transfer/`deposit_for` recipient.
**Examples.** **blackhole M-04** `claim` (resolves `avm.getOriginalOwner`) vs `claim_many` (omits it).
**Suppress.** both use the same resolved recipient variable; difference is only the loop variable name.

## 6. `registry_parity`

**Definition.** One path registers/deregisters/updates a registry/position lifecycle entry; the sibling
omits the lifecycle step.
**Signal.** registry op (`positions[x] = ` add vs `delete positions[x]` / `remove*` / `*Holding*`)
present in A, absent in the inverse/sibling B.
**Examples.** open-position registers; close/transfer sibling forgets to deregister (NOYA-style
lifecycle, adjacent to the highest-value family in the eval).
**Suppress.** lifecycle handled by a shared modifier/hook; sibling is a pure read.

## 7. `pause_emergency_parity`

**Definition.** One sibling is `whenNotPaused` / has an emergency check; the sibling reaching the same
effect bypasses it.
**Signal.** `whenNotPaused`/`require(!paused)`/emergency-guard in A's modifiers/body, absent in B, on a
shared mutating path.
**Examples.** `withdraw` (whenNotPaused) vs `emergencyWithdraw` *that should still gate something*;
`deposit`/`depositFor`.
**Suppress.** `emergencyWithdraw` is *intentionally* pause-exempt by design (admin/owner-gated escape
hatch) — require an additional non-admin reachability signal before flagging.

---

## Confidence assignment (shared across categories)

- **high** — name-stem sibling **and** ≥2 shared calls **and** a single, clear missing controlled
  component on a shared mutating path (the anchor shape).
- **medium** — behavioral-kinship sibling (no name stem) with one missing controlled component.
- **low / needs_context** — weak kinship or the missing component is also plausibly relocated to a
  shared helper (one-level helper resolution unresolved).

Each emitted candidate records: `sibling_pair (A,B)` · `parity_type` (one id above) ·
`missing_component` · `confidence` · `evidence` (the asymmetric token + shared mutating path) ·
`signals` (shared calls, name-stem, suppression checks).
