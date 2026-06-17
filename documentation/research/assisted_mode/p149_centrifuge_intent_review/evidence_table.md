# P149 — Evidence Table

| # | Evidence | Source location | Supports | Weakens | Notes |
|---|---|---|---|---|---|
| 1 | `withApproval(owner)` = `require(msg.sender == owner)` | `LiquidityPool.sol:97-98` | INTENDED / against-reportability | — | Only the owner can call withdraw/redeem; no operator/share-allowance delegation in this version |
| 2 | `withdraw(assets, receiver, owner)` / `redeem(shares, receiver, owner)` both `withApproval(owner)` | `LiquidityPool.sol:176-178, 200-202` | INTENDED (ERC4626 owner-directed) | — | `receiver` is the owner's chosen recipient |
| 3 | `userEscrow.transferOut(lPool.asset(), user, receiver, currencyAmount)` | `InvestmentManager.sol:545` | INTENDED | — | `user`=owner, `receiver`=owner's ERC4626 recipient; reachable only via owner-initiated withdraw/redeem |
| 4 | `function transferOut(...) external auth` (ward-only) | `UserEscrow.sol:36` | against-reportability | — | External actors cannot call it; only InvestmentManager (a ward) can |
| 5 | NatSpec: "additional protection to secure destination funds **in case of compromized auth**" | `UserEscrow.sol:39-42` | against (defense-in-depth framing) | for (admits the guard is only a weak mitigation) | The allowance check is explicitly secondary, not primary authz |
| 6 | `receiver == destination \|\| allowance(destination, receiver) == type(uint256).max` | `UserEscrow.sol:43` | — | for-reportability | Legitimate `receiver != owner` withdrawals revert unless owner pre-approved infinite *currency* allowance (ERC4626 break) |
| 7 | Allowance is never reduced (by design) | `UserEscrow.sol:41` (NatSpec) | INTENDED (deliberate proxy) | for (weak/repeatable proxy) | Unrelated infinite approvals satisfy the check repeatedly |
| 8 | `transferIn(currency, escrow, recipient, amount)` escrows for `recipient` | `InvestmentManager.sol:272` | context | — | `destination` = the owner the payout is escrowed for |
| 9 | No local tests/docs/scripts for transferOut | holdout is contracts-only | NEEDS-CONTEXT (severity only) | — | Intent of the caller path is still classifiable from source; only severity needs program context |

## Net reading
Rows 1–5, 8 establish that the redirect is **owner-directed and ward-gated** (no external-attacker path under
intended operation). Rows 6–7 establish a **real residual defect** (functional ERC4626 revert + weak compromised-
auth proxy). ⇒ GRIEFING_OR_DESIGN_AMBIGUOUS.
