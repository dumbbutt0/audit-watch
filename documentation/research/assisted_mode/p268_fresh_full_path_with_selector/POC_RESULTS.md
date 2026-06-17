# P268 — POC_RESULTS (Phase 9)

Isolated foundry project `pocs/p268/karak/`. Karak `src` copied read-only to `karak_src/` (contest tree unmodified);
deps cloned pinned (forge-std v1.9.6 · solady v0.0.228 · OZ + OZ-upgradeable v5.0.2); solc 0.8.25, via-IR (NativeVault
needs it). Vault initialized via `LibClone.clone` (bypasses the impl's `_disableInitializers`).

```
cd pocs/p268/karak && forge test -vv
```

## Results — 3/3 pass (built after the mechanism claims were frozen in the queue/selector docs)
| test | mechanism | result | observed | supports claim? |
|---|---|---|---|---|
| `test_C2_first_depositor_inflation_zeros_victim` | C2-M1 inflation | **PASS** | victim deposit 5000e18 → **0 shares**, 0 redeemable; victim's assets join the pool unrecoverable | **YES — exploit confirmed** |
| `test_C1_redeem_roundtrip_and_permissionless_finish` | C1-M1 finishRedeem | PASS | quiet-path redeem returns ~1000e18; permissionless finisher (attacker) gains **0** (assets → beneficiary) | refutes C1-M1 as a standalone bug (by-design) |
| `test_C1_startRedeem_requires_self_approval` | C1-M2 | PASS | `startRedeem` reverts without `allowance[staker][vault]` | confirms the low-impact UX rival |

## L1/L2/L3 (C2-M1, the recovery)
- **L1** attacker EOA: `deposit(1 wei)` then donate; no privilege.
- **L2** named state asserted: `victimShares == 0`, `convertToAssets(0) == 0`, `vault balance ≥ donation+victim`.
- **L3** outcome: a 5000e18 victim deposit yields **0 shares** → unconditional victim loss; root cause = Karak's
  Vault does not override solady `_decimalsOffset()` (offset 0 → only +1 virtual-share protection).

## Honest characterization
- **C2-M1 is a real, PoC-supported victim-loss** (first-depositor / deposit-rounds-to-zero inflation). **Attacker
  profit is PARTIAL**: solady's +1 virtual share absorbs ~half the donated value, so it is victim-loss/griefing with
  capped attacker profit, not a clean drain. Severity framing (Med vs High) is left to human review; the **loss is
  unconditional**.
- **C1-M1 did NOT yield a standalone exploit** (quiet path safe; permissionless finish pays the beneficiary; slashing
  during the queue is intended per NatSpec) → by-design.
- Mocks/assumptions: MockToken (solady ERC20); Vault via clone (production uses BeaconProxy — equivalent init path).
  No contest/production source edited.

## Freeze hashes (sha256[:16])
`P268_Vault.t.sol` `ed7fb79345dfa0be` · `p268_poc_queue.json` `7e26d0cbeefc9a4a` · `p268_selector_input.json`
`769322906b5f1857` · `p268_selector_decisions.json` `68497ab2ad0362cd`. No answer key consulted up to here.
