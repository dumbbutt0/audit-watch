# [M-XX] Liquidation engine allows unauthenticated liquidator impersonation and false liquidation attribution

## Summary

`execute_liquidation` in `k2-liquidation-engine` accepts a `liquidator: Address` parameter but
never calls `liquidator.require_auth()`. Any caller can supply an arbitrary address as the
liquidator, and the engine will execute the liquidation and permanently record that address as the
responsible liquidator — without the address ever authorizing the action.

In the current deployment the downstream `kinetic-router.liquidation_call` performs its own
`liquidator.require_auth()`, which prevents unauthorized token movement from the impersonated
address. The liquidation engine still violates the Soroban authorization model by accepting and
recording an address as actor without authenticating it, creating false attribution, fragile
integration assumptions, and a dependency on downstream router behavior the engine does not
control.

---

## Vulnerability Detail

**Location:** `contracts/2026-04-k2/contracts/liquidation-engine/src/contract.rs`, lines 49–97

```rust
pub fn execute_liquidation(
    env: Env,
    liquidator: Address,      // ← accepted but never authorized
    collateral_asset: Address,
    debt_asset: Address,
    user: Address,
    debt_to_cover: u128,
    _receive_a_token: bool,
) -> Result<LiquidationCall, KineticRouterError> {
    // No liquidator.require_auth() call anywhere in this function.

    validation::validate_liquidation_params(/*...*/)?;

    let liquidation_result = calculation::calculate_liquidation(/*...*/)?;

    let _: () =
        env.invoke_contract(&kinetic_router, &Symbol::new(&env, "liquidation_call"), args);
    //                                          ↑ liquidator is forwarded unchanged

    // On-chain record permanently attributes this liquidation to liquidator:
    let liquidation_call = LiquidationCall {
        liquidator,     // ← victim's address stored here without their consent
        // ...
    };
    storage::add_liquidation_record(&env, &liquidation_call);
    Ok(liquidation_call)
}
```

**Missing call — should be the first line of `execute_liquidation`:**
```rust
liquidator.require_auth();
```

**Root cause:** In Soroban's authorization model, any function that acts on behalf of an address
must call `address.require_auth()` before doing so. The engine omits this check entirely,
accepting any address as liquidator without verification.

---

## Impact

Any caller can invoke `liquidation-engine.execute_liquidation` with an arbitrary `liquidator`
address. Because the engine does not call `liquidator.require_auth()`, the liquidation record can
be falsely attributed to an address that did not authorize the action.

In the current deployment, the downstream router's `liquidation_call` performs its own
`liquidator.require_auth()` check, which prevents unauthorized token transfer from the
impersonated liquidator. However, the liquidation engine still violates the expected Soroban
authorization boundary by accepting and recording an address as actor without authenticating it.
This creates false attribution, integration risk, and a fragile dependency on downstream router
behavior.

If the engine is connected to a router path that does not independently authenticate the
liquidator, the missing check would allow unauthorized allowance consumption. In the current
router, that worst-case path is mitigated by the router's own `liquidator.require_auth()` check.

**Confirmed impacts in the current deployment:**

- **False liquidation attribution.** The stored `LiquidationCall` record permanently names an
  address as the liquidator without its consent. Any off-chain tool, analytics dashboard,
  compliance report, or future protocol feature reading liquidation history will show the victim
  as an active liquidator.

- **Griefing.** An attacker can flood a target address's liquidation history with fabricated
  records at low cost — no special permission or capital is required beyond a liquidatable
  position to target.

- **Integration fragility.** The engine's correctness depends on the downstream router always
  enforcing liquidator auth. This is not a designed invariant; it is defense-in-depth by
  coincidence. If the router is upgraded, replaced, or if the engine is integrated with a
  different protocol path, the missing check becomes immediately exploitable.

---

## Proof of Concept

Two tests in `pocs/k2/LG-001/src/integrated_test.rs` call the **real**
`LiquidationEngineContract` from the production k2-liquidation-engine crate.

**Run:**
```bash
cargo test --manifest-path pocs/k2/LG-001/Cargo.toml integrated_test 2>&1
```

**Output:**
```
test integrated_test::integrated::lg_001_execute_liquidation_missing_liquidator_require_auth ... ok
test integrated_test::integrated::lg_001_l3_attacker_impersonates_victim_liquidator ... ok
test result: ok. 2 passed; 0 failed
```

### Test 1 — L2: missing `require_auth` proof

**Function:** `lg_001_execute_liquidation_missing_liquidator_require_auth`

`env.mock_all_auths()` records every address for which `require_auth()` fires during the call.
After calling `execute_liquidation(&victim_liquidator, ...)`, victim is **absent** from
`env.auths()` — proving the engine never checked liquidator authorization.

```rust
let auths = env.auths();
let liquidator_auth_was_required = auths
    .iter()
    .any(|(signer, _)| *signer == victim_liquidator);

assert!(
    !liquidator_auth_was_required,
    "execute_liquidation never calls liquidator.require_auth()"
);
```

### Test 2 — L3: on-chain record falsification

**Function:** `lg_001_l3_attacker_impersonates_victim_liquidator`

Attacker calls `execute_liquidation(victim_address, ...)`. The stored `LiquidationCall` record
names victim as the liquidator and is queryable on-chain.

```rust
let record = client.execute_liquidation(
    &victim_liquidator,  // ← impersonated
    &collateral_asset,
    &debt_asset,
    &borrower,
    &(100 * WAD),
    &false,
);

assert_eq!(record.liquidator, victim_liquidator);

let stored = client.get_liquidation_record(&ids.get(0).unwrap());
assert_eq!(stored.unwrap().liquidator, victim_liquidator,
    "on-chain record attributes liquidation to victim without consent");
```

---

## Recommended Fix

**File:** `contracts/liquidation-engine/src/contract.rs`, first line of `execute_liquidation`

```rust
// Before (buggy):
pub fn execute_liquidation(
    env: Env,
    liquidator: Address,
    // ...
) -> Result<LiquidationCall, KineticRouterError> {
    let current_timestamp = get_current_timestamp(&env);
    // ...

// After (correct):
pub fn execute_liquidation(
    env: Env,
    liquidator: Address,
    // ...
) -> Result<LiquidationCall, KineticRouterError> {
    liquidator.require_auth();   // ← ADD THIS

    let current_timestamp = get_current_timestamp(&env);
    // ...
```

This is the standard Soroban pattern: any function that acts on behalf of an address must call
`address.require_auth()` as its first operation before any state mutation or cross-contract call.

---

## Severity Justification

**Medium** — the confirmed impact is attribution corruption and integration fragility, not direct
fund loss in the current deployment.

1. **Real bug, real impact.** The missing auth check is a verifiable violation of Soroban's
   security model. Any address can be falsely recorded as a liquidator with no authorization.

2. **Direct fund loss is mitigated in the current deployment.** The downstream router's own
   `liquidator.require_auth()` prevents token transfer from the impersonated address. This
   reduces the immediate severity from High to Medium.

3. **Integration risk warrants a fix.** The engine cannot rely on all current and future router
   deployments enforcing this guard. The one-line fix makes the engine safe independently of
   downstream behavior.

4. **Griefing is permissionless.** Record falsification requires no capital or privilege — only a
   liquidatable position to target.

---

## References

- **Bug location:** `contracts/2026-04-k2/contracts/liquidation-engine/src/contract.rs:49–97`
- **Downstream guard (current mitigation):** `contracts/2026-04-k2/contracts/kinetic-router/src/liquidation.rs:111`
- **PoC:** `pocs/k2/LG-001/src/integrated_test.rs`
- **Run:** `cargo test --manifest-path pocs/k2/LG-001/Cargo.toml integrated_test 2>&1`
