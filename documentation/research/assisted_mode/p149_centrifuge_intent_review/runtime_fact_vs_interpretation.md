# P149 — Established Runtime Fact vs Intent/Severity Interpretation

## Established (P147 runtime — treated as fact, NOT re-litigated)
- Real `UserEscrow.transferOut(token, destination, receiver, amount)` debits `destinations[token][destination]` and
  pays `receiver` when `receiver == destination || allowance(destination, receiver) == type(uint256).max`.
- With `destination`'s escrow funded and an infinite `receiver` allowance, the funds went to `receiver` (0xBEEF):
  1000e18, then 2000e18 on repeat; `destination` received 0. The allowance is never reduced (repeatable).
- This is a genuine validated-subject (`destinations[...][destination]`) ≠ paid-subject (`receiver`) divergence at
  the contract level.

## Interpretation (P149 — NOT established as reportable)
- **Caller model:** the only intended path into `transferOut` is owner-initiated `withdraw/redeem`
  (`withApproval(owner)`), where the **owner chooses `receiver`**. So under intended operation the "redirect" is
  the owner sending **their own** funds to a recipient they selected — no victim, no unauthorized redirect.
- **Threat model of the guard:** the allowance check is documented as defense-in-depth **"in case of compromized
  auth"** (a malicious/compromised ward). P147's harness called `transferOut` directly as a ward — i.e., it
  exercised exactly that privileged/compromised scenario, not an external attacker.
- **Therefore:** the P147 mechanism does not, by itself, demonstrate an external-attacker theft under intended
  operation. The **established fact** (mechanism executes) and the **interpretation** (is it a reportable
  vulnerability?) are different layers; only the former is settled.

## Residual, genuinely-ambiguous concerns (need human severity)
1. **Functional / ERC4626:** a legitimate `receiver != owner` withdrawal **reverts** unless the owner previously
   granted `receiver` an infinite *currency* allowance — breaking standard `withdraw(assets, receiver, owner)` to a
   third-party receiver (a DoS/compliance defect, severity TBD).
2. **Weak defense-in-depth:** the `allowance == max` proxy can be satisfied by unrelated infinite approvals and is
   never consumed, so the stated "protect destination funds under compromised auth" goal is only weakly met.
