# DOS-002 — A matured parent LP cannot withdraw while child funds are GM-deployed (no permissionless exit; `_availableFromChildren` ignores deployed value)

| | |
|---|---|
| **Severity** | **Medium** (matured user funds unwithdrawable for an unbounded time; liveness/censorship gated entirely on keeper recall) |
| **Category (HackenProof VRT)** | DoS with (Unexpected) revert |
| **Target** | Cartha Vaults (`cartha-vaults-main`, commit `4c51f2a8915f438976b57134d646b55199a11318`) |
| **Contracts** | `src/CarthaParentVault.sol` (`_availableFromChildren` 431-442, `_prepareSharePayout` 456-470, `releaseFromParent` 625-659, `processQueuedParentWithdrawals` 684-704), `src/CarthaVault.sol` (`deployToPool`/`recallFromPool` 476-531) |
| **Trigger** | Normal operation: the keeper has deployed child idle USDC into the 0xM pool (the core yield feature), and a matured LP's claim exceeds the remaining idle liquidity. No attacker required. |
| **PoC** | `poc/PoC_MaturedExitDoS_DOS002.t.sol` (passing — `poc/run_output.txt`) |

## Not a duplicate of DOS-001

DOS-001 is a *revert* in the pricing path (`totalAssets()` reverts when a child's GM read fails). DOS-002 is the opposite: pricing works fine, `totalAssets()` returns the full value — but the value is **not liquid**, because the payout path can only draw on idle USDC. Different root cause (a liquidity/availability gap vs an unguarded external revert), different fix.

## Summary

A parent withdrawal is satisfied from parent idle USDC plus `_availableFromChildren()`. But `_availableFromChildren()` counts **only each child's idle USDC balance** — it does **not** count the child's GM-deployed value:

```solidity
// src/CarthaParentVault.sol:431-442
function _availableFromChildren() internal view returns (uint256 available) {
    ...
    uint256 childIdle = IERC20(asset()).balanceOf(vault);   // <-- idle USDC only; GM value uncounted
    available += (parentShares * childIdle) / childSupply;
}
```

So once the `KEEPER_BOT` has deployed child idle USDC into the 0xM pool (`deployToPool`), a parent LP whose lock **and** cooldown have **both** expired still cannot withdraw the GM-backed portion:

```solidity
// _prepareSharePayout, CarthaParentVault.sol:456-470
uint256 needed = shareValue > idleUsdc ? shareValue - idleUsdc : 0;
if (needed > 0) {
    if (_availableFromChildren() + 10 < needed) return (0, false);   // <-- insufficient
    _withdrawFromChildren(needed);
}
```

`releaseFromParent` then reverts `InsufficientVaultBalance` (`647`), and the keeper batch path `processQueuedParentWithdrawals` silently `continue`s on `!sufficient` (`699`), settling nothing. There is **no permissionless force-recall and no emergency exit** — `deployToPool`/`recallFromPool` are `KEEPER_BOT`-only — so the matured user's funds are reachable only after a trusted keeper performs an async, multi-tx `recallFromPool`. The value is fully present in `totalAssets()`; it is simply not withdrawable.

## Impact

A matured LP (lock + cooldown both expired — i.e. the protocol's own conditions for withdrawal are satisfied) cannot withdraw the GM-deployed portion of their principal. A stalled, offline, or adversarial keeper can block matured withdrawals for an **unbounded** time, with no permissionless escape hatch. No value is destroyed (an honest keeper restores access), which bounds this to **Medium** — but it breaks the core availability promise that matured funds are withdrawable, and it is borne by every LP whenever liquidity is deployed.

## Step-by-step (from the PoC)

1. Incumbent LP locks **$1,000,000** → $500k to each child.
2. Keeper deploys **all** of child B's idle USDC into the 0xM pool → child B holds $500k of GM and **zero** idle USDC (no deploy-ratio cap is configured).
3. `parent.totalAssets() == $1,000,000` — the value is all still there.
4. Lock **and** cooldown both expire — the position is fully matured.
5. `releaseFromParent(1_000_000e6)` **reverts** `InsufficientVaultBalance` — only child A's $500k idle is "available"; child B's $500k is GM-deployed and uncounted.
6. `requestReleaseFromParent()` + `processQueuedParentWithdrawals([incumbent])` settles **$0** (the keeper batch `continue`s); the LP still holds all parent shares.
7. The LP **cannot self-recall**: `childB.recallFromPool(...)` reverts (`onlyRole(KEEPER_BOT)`).
8. **Control:** the keeper calls `recallFromPool` + the 0xM keeper executes the withdrawal → child B's idle USDC is restored → `releaseFromParent(1_000_000e6)` now **succeeds**, paying the LP the full $1,000,000. The funds were gated solely on keeper liveness.

```
parent totalAssets() (value present) : 1000000000000
full release reverted (matured LP cannot exit)
queued withdrawal settled $0 (keeper batch also bricks)
LP cannot self-recall (recallFromPool is KEEPER_BOT-only)
after keeper recall, LP exits in full : 1000000000000
```

## Recommended fix

Give matured users a path to their funds that does not depend on keeper liveness:
- A **permissionless recall**/emergency-exit that lets a matured LP trigger `recallFromPool` (or queue a withdrawal the keeper is obligated to service within a bounded window), and/or
- count the recallable GM value in the exit accounting so a matured exit can initiate the recall itself, and/or
- pay matured exits in kind (transfer the pro-rata GM/child shares) when idle USDC is insufficient, so the user is never trapped behind keeper action.

## Re-verification note

Re-verified end-to-end with the project's own Foundry harness (parent + 2 children via `CarthaVaultFactory`, real `depositAndLockSpread` / `deployToPool` / `recallFromPool` flows). The PoC asserts the full chain: value present → matured full exit reverts → keeper batch settles $0 → LP cannot self-recall → keeper recall restores liquidity → full exit succeeds. Test passes (`poc/run_output.txt`). Self-contained — no external dependencies (`forge test --match-path "test/poc/PoC_MaturedExitDoS_DOS002.t.sol" -vv`).
