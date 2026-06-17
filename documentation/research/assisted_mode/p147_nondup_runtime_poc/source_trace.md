# P147 — Source Trace

File: `audits/centrifuge-2023-09-holdout/contracts/src/UserEscrow.sol` (solc 0.8.21, 51 lines).

## Escrow accounting
```solidity
/// @dev Map by token and destination
mapping(address => mapping(address => uint256)) destinations;

function transferIn(address token, address source, address destination, uint256 amount) external auth {
    destinations[token][destination] += amount;                       // funds escrowed FOR `destination`
    SafeTransferLib.safeTransferFrom(token, source, address(this), amount);
}
```

## The divergence (transferOut)
```solidity
function transferOut(address token, address destination, address receiver, uint256 amount) external auth {
    require(destinations[token][destination] >= amount, "UserEscrow/transfer-failed");
    require(
        receiver == destination
            || (ERC20Like(token).allowance(destination, receiver) == type(uint256).max),   // <-- weak proxy
        "UserEscrow/receiver-has-no-allowance"
    );
    destinations[token][destination] -= amount;                       // debits destination's escrow
    SafeTransferLib.safeTransfer(token, receiver, amount);            // <-- pays `receiver` (may != destination)
}
```

## Value/recipient provenance
- `validated_subject` / `quantity_source`: `destinations[token][destination]` — the balance escrowed **for**
  `destination`.
- `mutated_subject` / paid identity: `receiver` — the address actually paid.
- `divergence_point`: the `transfer(receiver, amount)` after a debit of `destination`'s escrow, gated only by
  `allowance(destination, receiver) == type(uint256).max`.
- The escrow **never reduces** that allowance, so a single max allowance (commonly granted to routers/protocols
  for unrelated reasons) authorizes **repeated** redirects of `destination`'s escrow to `receiver`.

⇒ Funds escrowed for `destination` can be paid to an unrelated `receiver` (validated subject ≠ paid subject).

## Trigger conditions
- `destinations[token][destination] >= amount` (escrow funded for destination).
- `receiver != destination` AND `allowance(destination, receiver) == type(uint256).max`.
- caller is a ward (`auth`) — the recognized concern is that this allowance proxy is too weak to "secure
  destination funds in case of compromised auth" (the NatSpec's own stated goal).

## Intent caveat
The NatSpec frames the `receiver != destination` path as "additional protection." So the runtime PoC proves the
**mechanism** (escrow redirectable to an unrelated max-allowance receiver, allowance never reduced); whether this
rises to a vulnerability vs intended flexibility is a **human severity/intent decision**.
