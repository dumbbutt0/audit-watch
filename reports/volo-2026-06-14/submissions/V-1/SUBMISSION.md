<!--
PLATFORM-PASTE-READY report for Volo finding V-1. Plain prose + standard code fences only — no
blockquote header, no viewer "Copy"/language-label artifacts. Paste each labelled section into the
matching HackenProof field. Facts validated; PoC passes. Copy from the RAW file, not a rendered preview.
-->

# Field: Target
https://github.com/Sui-Volo/volo-smart-contracts (volo-vault package, commit 1a9a36d) — Volo by NAVI Protocol, Sui/Move

# Field: Category
Business Logic Errors (asset mis-valuation / accounting)

# Field: Severity
Medium

## CVSS

CVSS v3.1: 5.9 (Medium) — `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N`

| Metric | Value | Rationale |
|---|---|---|
| Attack Vector (AV) | Network | Exploited on-chain via ordinary transactions; no local/physical access. |
| Attack Complexity (AC) | High | Requires a specific state window — the ZO pool's `acc_reward_per_share` must be stale (unsettled) while rewards have accrued; the attacker does not fully control when. |
| Privileges Required (PR) | None | Permissionless; any depositor, no operator/curator role. |
| User Interaction (UI) | None | Existing holders merely hold through the unsettled window; no victim action. |
| Scope (S) | Unchanged | Impact confined to the vault component. |
| Confidentiality (C) | None | No information disclosure. |
| Integrity (I) | High | The vault's NAV / share-price accounting is corrupted; value is transferred between holders. |
| Availability (A) | None | No denial of service. |

CVSS v4.0: Medium — `CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N`
(`AT:P` = Attack Requirements Present: the ZO pool must be in an unsettled-reward window. Use the official
FIRST CVSS 4.0 calculator for the exact numeric.)

# Field: Title
Vault undervalues ZO staking positions by reading a stale reward accumulator, causing stale NAV and enabling just-in-time reward capture

# Field: Vulnerability details

`volo_vault::zo_adaptor::get_zo_position_value` (the v1.1 adaptor that prices a ZO staking position held
by the vault) computes the position's pending-reward leg from the ZO pool's raw stored reward accumulator
without first settling it:

```move
let pending_reward_per_share =
    pool.pool_acc_reward_per_share() - credential.credential_v2_acc_reward_per_share();
let reward_amount =
    (((pending_reward_per_share as u256) * (credential.credential_v2_staked_amount() as u256))
        / (SCALE_FACTOR as u256)) as u128;
```

`zo_staking::pool::pool_acc_reward_per_share()` returns the raw stored `acc_reward_per_share`. That
accumulator is time-based: it only advances inside the ZO pool's private `refresh_pool`, which runs
exclusively on a state-changing interaction (deposit / withdraw / claim / add_reward / set_*). The
adaptor never triggers a refresh and there is no public settle function it could call, so it values the
position's rewards using an accumulator frozen at the moment the pool was last touched. Every reward unit
accrued since then is omitted from the position's value.

Because that value feeds the vault's NAV (`finish_update_asset_value`), the vault's total USD value — and
therefore its share price (NAV / total_shares) — is understated by the unsettled ZO rewards.

This is Medium because it is a permissionless mis-valuation that lets one user extract value from others
(no privileged role required), but the extractable amount is bounded by how stale the pool is
(elapsed_time × reward_rate × the vault's share of the pool), not an unconditional drain. NAVI's own prior
audit rated the identical class — "interest isn't compounded ... leading to a misestimation of the
position" (Certora M-02) — as Medium.

## Root cause and why it is a regression

The audited adaptors settle pending yield before valuing the position. The new (v1.1) ZO adaptor does not:

- `suilend_adaptor::update_suilend_position_value` calls `suilend_compound_interest(...)` to compound
  interest before reading the obligation value.
- `navi_adaptor::calculate_navi_position_value` uses `dynamic_calculator::calculate_current_index(...)`,
  which computes the time-accrued index on the fly.
- `zo_adaptor::get_zo_position_value` reads `pool_acc_reward_per_share()` directly — neither compounding
  nor computing the current accrual — reintroducing the exact mis-estimation class.

## Impact

The vault's share price is persistently understated by the unrealized ZO rewards. This is directly
exploitable as just-in-time reward capture (the same shape as unrealized-yield-not-in-NAV findings):

1. The vault holds a ZO position that has accrued rewards not yet reflected (pool not refreshed since the
   last touch). NAV, and thus share price, is understated.
2. An attacker deposits at the understated share price and receives more shares than fair, diluting
   existing holders.
3. The ZO pool is then settled by any normal interaction (the vault claiming/compounding rewards, or any
   third party's deposit/withdraw on that pool), and the next vault value-update reflects the now-higher
   reward accumulator. NAV jumps up.
4. The attacker withdraws, capturing a share of rewards that accrued before they joined — value taken from
   the depositors who held through the accrual period. Symmetrically, anyone who withdraws while the value
   is understated is underpaid.

## End-to-end share-price impact (executed)

This is proven end-to-end with a second runnable test that drives the **real** vault, the **real**
`zo_adaptor`, and a **real** `zo_staking` pool (no mocks) — see `poc/zzz_volo_zo_endtoend_poc.move`. The
code path it exercises:

- `volo_vault::zo_adaptor::update_zo_position_value` (sources/adaptors/zo_adaptor.move) values the
  vault-held ZO position via the stale `get_zo_position_value` and writes it with
  `vault.finish_update_asset_value(...)` (volo_vault.move:1367) into `assets_value[asset_type]`.
- The vault share price is `get_share_ratio = total_usd_value / total_shares` (volo_vault.move:1490), so an
  understated ZO value understates the share ratio that deposits price against.

The test **models the depositor's mint with the vault's own share-ratio math** (`get_share_ratio` /
`vault_utils::div_d` / `mul_d`) against the real adaptor + real pool — B's minted shares are added to
`total_shares` and B's deposited cash to NAV before B is re-valued, so the capture shown is the correct
**pro-rata** slice. (It does not call `user_entry::deposit`: the real `execute_deposit` requires the v1.1
single-vault-operator pairing that the repo's own test harness never sets up — the same gap that fails
several stock vault tests — so the in-test mint is modeled, not routed through the deposit entrypoint.)

Measured result (one stale hour, reward rate sized to ~2% of the position; SUI/USDC priced at $1):

```
stale   NAV / share ratio : 1_000_000_000   (1.0000)
settled NAV / share ratio : 1_021_600_000   (1.0216)
omitted reward leg        :    21_600_000   (2.16% of the position — what the adaptor failed to count)
B deposit (= stale NAV)   : 1_000_000_000   (shares minted at the STALE 1.0000 ratio)
B value after settle      : 1_010_800_000   (B's shares + deposit folded into the denominator/NAV)
B pro-rata gain           :    10_800_000   (1.08% of deposit = 50% of the omitted reward)
```

With B depositing an amount equal to the pre-existing stale NAV, B captures ~**half** the omitted reward
(1.08% instant gain); the captured fraction grows with deposit size, approaching the full omitted reward as
B dominates the vault (the test also computes a 10× deposit → ~91% of the leg). It is a **deterministic
accounting gain available to any unprivileged depositor once the stale-NAV state exists**, taken from the
pre-existing holders who accrued those rewards — bounded by `elapsed × reward_rate × pool_share` (how stale
the pool is), consistent with the Medium rating.

(Build note: this required resolving a pre-existing Pyth/Wormhole duplicate-dependency in the repo's
manifests so `volo-vault` compiles under `sui move test`; the standalone adaptor-level PoC below is
independent of that.)

## Proof of concept

The PoC stakes into a real `zo_staking` pool, lets one hour pass with no pool interaction, and then
computes the adaptor's exact reward formula (the lines above) using the same public getters the in-scope
adaptor calls. It shows the adaptor sees 0 pending reward while the true settled reward is 360,000. The
pool is settled by an unprivileged third party's ordinary `deposit_v2` (a `public` function that triggers
the private `refresh_pool`) — demonstrating that no special role is needed to move the accumulator the
adaptor should have read.

# Field: Validation steps

The PoC is a runnable Sui Move unit test. It is placed in the ZO staking package (which builds
standalone with only the Sui framework) and replicates `zo_adaptor::get_zo_position_value`'s reward leg
verbatim against the real ZO pool. From `volo-vault/local_dependencies/zo-staking-contract`:

```bash
sui move test zo_adaptor_staleness
```

Steps proven by the test:

1. Create a ZO pool, fund rewards, set reward_rate = 100/sec, and stake 1,000 (the deposit refreshes the
   pool, so the credential snapshots `acc_reward_per_share` as its baseline).
2. Advance the clock by 1 hour with no interaction on the pool.
3. Assert `pool_acc_reward_per_share()` is unchanged from the deposit-time value (the accumulator the
   adaptor reads is stale — it does not accrue on read).
4. Compute the adaptor's reward valuation now — it is 0 (an entire hour of accrual omitted).
5. Settle the pool with an unprivileged third party's `deposit_v2` (a `public` call that triggers the
   private `refresh_pool`); the accumulator increases. `refresh_pool` runs on the pre-existing total stake
   before the new stake is added, so the victim's settled reward is unchanged.
6. Recompute the adaptor's reward valuation — it is 360,000 (= 3600s × 100/sec × full pool share).
7. Conclude: the adaptor undervalued the position's reward leg by 360,000.

Captured output (passes):

```
Running Move unit tests
[ PASS    ] zo_staking::zzz_volo_zo_adaptor_staleness_poc::test_zo_adaptor_undervalues_pending_rewards_due_to_stale_accumulator
Test result: OK. Total tests: 1; passed: 1; failed: 0
```

## End-to-end vault share-accounting PoC

A second runnable test proves the share-accounting impact on the real vault. From `volo-vault/`:

```bash
sui move test zo_endtoend
```

Steps proven (`poc/zzz_volo_zo_endtoend_poc.move`): init the real vault + oracle; create a real ZO pool
(SUI/USDC); the operator stakes the vault's principal into ZO (real `CredentialV2`, held as a vault defi
asset); one hour passes with the pool untouched; the real `zo_adaptor::update_zo_position_value` records the
STALE NAV / share ratio (1.0000); a depositor B's mint is modeled at that depressed ratio using the vault's
own `div_d`/`mul_d`; an unprivileged third party settles the pool with `deposit_v2`; the adaptor re-values
and the ratio rises to 1.0216; with B's shares + deposit folded into the denominator/NAV, B's **pro-rata**
gain is 10,800,000 (1.08% of an equal deposit = 50% of the omitted reward; a 10× deposit captures ~91%).
Asserts: `v1 > v0`, `ratio_settled > ratio_stale`, `b_value_after > b_deposit`, and
`b_gain <= omitted_reward` (capture bounded by the leg). Passes (`Test result: OK. 1 passed`). The repo's
broader suite has pre-existing, unrelated failures from a v1.1 single-vault-operator dynamic-field setup gap
— none involve this finding, the adaptor, or the dependency fix.

## Suggested fix

Before reading `pool_acc_reward_per_share()`, settle the ZO pool's accumulator to the current time
(mirroring `suilend_adaptor`'s compound-first or `navi_adaptor`'s current-index approach). Since the ZO
pool exposes no public settle, either (a) have the ZO contract expose a public refresh / a view that
returns the time-accrued `acc_reward_per_share`, or (b) replicate `refresh_pool`'s accrual
(`elapsed × reward_rate / staked_amount`, capped at `end_time`) inside the adaptor before valuing, so the
position's pending rewards are valued as of `now`.

# Field: Attachments
- vulnerable/zo_adaptor.move                     (IN-SCOPE vulnerable source: get_zo_position_value, lines 47-52)
- poc/zzz_volo_zo_endtoend_poc.move              (executed END-TO-END PoC: real vault + zo_adaptor + ZO pool; pro-rata share capture, 1.08% on an equal deposit = 50% of the omitted reward)
- poc/zo_endtoend_output.log                     (captured passing run + decoded values)
- reference/suilend_adaptor.move                 (audited sibling — compounds interest BEFORE valuing; the correct pattern)
- reference/navi_adaptor.move                    (audited sibling — uses dynamic current-index; the correct pattern)
- reference/zo_staking_pool_excerpt.move         (OOS dependency excerpt: refresh_pool is private; pool_acc_reward_per_share() returns the raw stale accumulator)
- poc/zzz_volo_zo_adaptor_staleness_poc.move     (runnable Sui Move PoC; replicates get_zo_position_value's reward leg)
- poc_output.log                                 (captured passing run)
