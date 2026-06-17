# P147 — Runtime Model

## Actors
- `source` (0x5005) — funds the escrow.
- `destination` (0xDDDD) — the address funds are escrowed **for** (entitled subject).
- `receiver` (0xBEEF) — an unrelated third party; only link to destination = a max ERC20 allowance.

## Setup
- `MockERC20` reward token (`balanceOf`/`allowance`/`approve`/`transfer`/`transferFrom`; respects allowance,
  treats `type(uint).max` as non-decrementing).
- `AMT = 1000e18`. `source` mints + approves the escrow; `escrow.transferIn(token, source, destination, AMT)`
  escrows AMT for `destination`.
- `destination` grants `receiver` an infinite allowance (`approve(receiver, type(uint).max)`) — modeling an
  unrelated approval (e.g. a router).

## Scenarios
| test | call | expected |
|---|---|---|
| vulnerable | real `escrow.transferOut(token, destination, receiver, AMT)` | pays **receiver** AMT; destination gets 0 |
| corrected ref | `CorrectedUserEscrow.transferOut(...,receiver,...)` (guard `receiver==destination`) | **reverts** (no redirect) |
| control | real `escrow.transferOut(token, destination, destination, AMT)` | pays **destination** (correct) |
| repeat | two escrows, two `transferOut(...,receiver,...)` | receiver gets `2·AMT` (allowance never reduced) |

## Observed (forge logs)
- vulnerable: `paid_subject_receiver = 0xBEEF`, `redirected_amount = 1000e18`, destination balance 0.
- corrected: revert `Corrected/receiver-must-be-destination`.
- control: destination = 1000e18, receiver = 0.
- repeat: receiver = 2000e18.

## Reading
Same inputs, real contract pays an unrelated `receiver`; the corrected reference refuses; the control (receiver ==
destination) matches — isolating the divergence to the `receiver != destination` + `allowance == max` path.
