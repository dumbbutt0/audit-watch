<!--
PLATFORM-PASTE-READY report for Haedal haWAL finding V-1. Plain prose + standard code fences only — no
blockquote header, no viewer "Copy"/language-label artifacts. Paste each labelled section into the matching
field. This is an ANALYSIS-ONLY finding (code path / source comparison; no fund loss, no runnable PoC) —
the Validation steps describe the code; no fabricated test output. Copy from the RAW file, not a rendered
preview.

NOTE: source supplied as a dropped zip (hawal-bug-bounty-main); confirm the official program/Target before
submitting.
-->

# Field: Target
Haedal haWAL (Walrus liquid staking, Sui Move) — hawal-bug-bounty-main, sources/walstaking.move
(supplied as an archive; confirm the official submission Target/URL before submitting)

# Field: Category
Business Logic Errors (missing input validation / validator-curation bypass)

# Field: Severity
Low

# Field: Title
haWAL request_stake_coin omits the active-validator check the audited haSUI enforces, letting a user route stake to any Walrus validator outside Haedal's curated set

# Field: Vulnerability details

When a user stakes with an explicitly chosen validator, `walstaking::request_stake_coin` stakes directly to
that validator without verifying it belongs to Haedal's curated `active_validators` set:

```move
// hawal walstaking.move :: request_stake_coin
if (validator == object::id_from_address(@0x0)) {
    let auto_validator = get_min_total_validator(staking);          // auto-select (active set only)
    stake_to_validator(coin::into_balance(input), staking, wal_staking, auto_validator, ctx);
} else {
    // user selects a validator -> staked DIRECTLY, no active-set membership check
    stake_to_validator(coin::into_balance(input), staking, wal_staking, validator, ctx);
};
```

`stake_to_validator` then registers that arbitrary validator into the protocol's own bookkeeping
(`staking.pools` and `staking.validators`) the first time it is seen.

The audited sibling protocol (haSUI), built on the same Haedal framework, does NOT do this. It validates the
user-chosen validator against the active set and falls back to a vault buffer if the validator is not active:

```move
// hasui staking.move :: request_stake_coin (audited by MoveBit; OtterSec ongoing)
let active_validators = sui_system::active_validator_addresses(wrapper);
if (validator == @0x0 || !is_active_validator(validator, &active_validators)) {
    vault::deposit(&mut staking.sui_vault, coin::into_balance(input)); // safe fallback
} else {
    save_user_selected_staking(staking, input, validator);
}
```

So haWAL dropped a validation guard that exists in its audited counterpart — a defense-in-depth regression
introduced by the Walrus port.

This is Low because it is not a fund-loss bug and its blast radius is bounded (see below); it is a
validator-curation bypass plus minor reward under-accounting, with no path to theft or to harming other
users' funds.

## Why the impact is limited (escalation paths checked)

- The chosen validator must be a real Walrus validator, otherwise `staking::stake_with_pool` reverts. A user
  cannot inject a fake/garbage validator — only a real one outside Haedal's curated `active_validators`.
- Other users are not affected: auto-selected stakes (`validator == 0x0`) go through `get_min_total_validator`,
  which iterates ONLY `staking.active_validators`. An injected non-active validator therefore cannot capture
  other users' auto-staked WAL.
- Reward accounting stays conservative: rewards from a non-active validator may not be credited by the robot's
  per-validator `update_validator_rewards`, so they are under-counted in `total_rewards`; on withdrawal the
  real rewards return and the surplus accrues to the protocol vault — it does not dilute or steal from other
  holders.
- Validator-list growth is bounded by the size of the Walrus validator committee, so the `staking.validators`
  loops (instant unstake / claim) grow by at most a bounded amount.

## Impact

A user can cause the protocol to stake with, and register, a validator Haedal never vetted (e.g. a
high-commission or poorly-performing node), bypassing the operator's `active_validators` curation. The
practical effects are: stake placed with an unapproved validator, that validator's rewards under-counted in
protocol accounting, and a bounded increase in the `staking.validators` set iterated by the unstake/claim
loops. No fund loss; no cross-user fund impact.

## Suggested fix

Mirror the audited haSUI behavior: before staking to a user-chosen validator, verify it is in
`staking.active_validators` (e.g. `vector::contains(&staking.active_validators, &validator)`); if it is not,
either revert or fall back to a vault buffer / auto-selection, exactly as haSUI deposits to `sui_vault` when
the chosen validator is not active.

# Field: Validation steps

Proof type: code analysis + cross-protocol source comparison (no runnable PoC — there is no fund loss to
demonstrate; the issue is a missing validation present in the audited sibling). Established directly from
source:

1. `hawal/sources/walstaking.move::request_stake_coin` — for a non-zero `validator` argument, calls
   `stake_to_validator(..., validator, ...)` with no check that `validator` is in `staking.active_validators`.
2. `stake_to_validator` registers any previously-unseen validator into `staking.pools` and pushes it to
   `staking.validators`.
3. `hasui/sources/staking.move::request_stake_coin` (the audited sibling) guards the same path with
   `!is_active_validator(validator, &active_validators)` and falls back to the vault — confirming the haWAL
   port dropped the guard.
4. `hawal/sources/walstaking.move::get_min_total_validator` iterates only `staking.active_validators`,
   confirming auto-stakes (and thus other users) are not affected — bounding the blast radius to the caller's
   own stake.

# Field: Attachments
- vulnerable/walstaking_request_stake_coin.move   (haWAL request_stake_coin + stake_to_validator — missing check)
- reference/hasui_request_stake_coin.move          (audited haSUI — the active-validator check + vault fallback)
- reference/hawal_get_min_total_validator.move     (auto-select iterates active set only — bounds blast radius)
