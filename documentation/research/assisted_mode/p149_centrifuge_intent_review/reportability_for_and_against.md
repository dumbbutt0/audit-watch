# P149 — Reportability: For vs Against

## Strongest argument FOR reportability
**Functional ERC4626 break (the cleanest angle).** `withdraw(assets, receiver, owner)` / `redeem(shares, receiver,
owner)` are meant to let an owner send proceeds to **any** `receiver`. But `transferOut` (`UserEscrow.sol:43`)
requires `receiver == destination || allowance(destination, receiver) == type(uint256).max`. So a normal owner
withdrawing to a third-party `receiver` (a friend, a different wallet, a contract) **reverts** unless they first
granted that `receiver` an *infinite allowance on the currency token* — which is not a normal precondition. This
breaks standard ERC4626 to-receiver withdrawals (a DoS / spec-compliance defect). Secondarily, the documented
"additional protection … in case of compromized auth" is a **weak proxy**: an unrelated infinite approval
(common for routers/protocols) satisfies it, and it is never consumed (repeatable) — so the stated security goal
is only weakly achieved.

## Strongest argument AGAINST reportability
**No external-attacker path under intended operation.** Only the owner can initiate withdraw/redeem
(`LiquidityPool.sol:97-98,178,202`: `msg.sender == owner`; no operator delegation in this version), and the owner
chooses `receiver`. `transferOut` is ward-only (`UserEscrow.sol:36`). So an attacker cannot redirect a victim's
escrow without (a) being the owner, or (b) compromising a ward — and the allowance check is **explicitly**
documented (`UserEscrow.sol:39-42`) as defense-in-depth for the compromised-auth case, which is outside the normal
external-attacker threat model (wards are Root/governance-trusted). P147's runtime redirect modeled a privileged
ward, not an unauthorized attacker; the owner sending their own funds to a chosen receiver is intended ERC4626 —
no victim, no theft.

## Net
Both sides cite real source facts. The external-theft interpretation is **refuted by intent**; the functional /
defense-in-depth interpretation is **real but severity-ambiguous** → GRIEFING_OR_DESIGN_AMBIGUOUS, escalated to
human severity. `submission_ready=false`.
