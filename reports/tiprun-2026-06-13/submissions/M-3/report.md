# M-3 (Medium, trust-dependent) — Liquidate / Deleverage have no on-chain maintenance-margin precondition

- **Target:** TipRun, perp profile. Commit `d5d4d2a…`.
- **Contracts:** `src/perp/transactions/LiquidateTransLib.sol` → `process`;
  `src/perp/transactions/DeleverageTransLib.sol` → `process`.
- **Severity:** Medium (operator-trust dependent; Low if the sequencer is fully trusted, higher if users are meant to
  be protected on-chain from having healthy positions seized).
- **PoC:** `poc/PoC_NoLiquidatablePrecondition.t.sol` (passing) · log `poc_output.log`.

## Root cause
`LiquidateTransLib.process` never checks that the targeted account is below maintenance margin before force-resizing
its position; it computes deltas, applies funding, and calls `position.updatePosition(...)` + executes the liquidator
order. There is no `require(account is unhealthy)`. `DeleverageTransLib.process` is weaker still: it only calls
`signerManager.checkSigner(...)` (i.e. "is a registered signer") for both parties — **no signature, no nonce, no
health precondition** — so the operator can force any account to be the deleverager or the deleveraged.

Both are gated by `onlyTxBatcher`, so exploitation requires a malicious/buggy operator. But the on-chain safety that
"only unhealthy accounts can be liquidated/deleveraged" is absent — the contract trusts the off-chain risk engine.

## Impact
A faulty or malicious sequencer can force-trade / seize positions of perfectly healthy, fully-collateralized accounts
at an operator-chosen price. Combined with F-1 (the margin check does not block value-reducing transitions on the
liquidated account), over-seizure is not blocked either.

## PoC (passing)
`forge test --match-contract PoC_NoLiquidatablePrecondition -vv` (from `../../harness/`):
- the target (cOwner) holds 100 collateral and a tiny long of 1 — proven **healthy** (`risk ≤ value·FXP`).
- a `TYPE_LIQUIDATE` transaction liquidates it anyway: the position is force-closed (`assets.length == 0`) and the
  forced trade settles against the target — no "not liquidatable" guard fires.

## Suggested fix
Require the target to be below maintenance margin before liquidation/deleverage (compute health on-chain and revert
otherwise), and bound the liquidation price to oracle ± a configured penalty. For deleverage, require a real signature
/ consent model or an explicit bankrupt-state precondition.

<!-- BEGIN classification-cvss -->

## Vulnerability classification & CVSS

- **Category (VRT):** Unsecure Design → Violation of Secure Design Principles (Liquidate/Deleverage have no on-chain maintenance-margin precondition; correctness relies entirely on the trusted off-chain batcher)
- **CWE (informative):** CWE-657 (Violation of Secure Design Principles); CWE-285 (Improper Authorization of the liquidation precondition)

| Aspect | CVSS v3.1 vector | Base score | Severity |
|---|---|---|---|
| Trusted-batcher precondition gap | `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N` | **4.9** | Medium |

> PR:H — exploitation requires the privileged batcher to submit a liquidation against a healthy account; this is a trust/centralisation finding.

> CVSS v3.1 base scores computed with the official formula (no temporal/environmental modifiers). For smart-contract findings the protocol/bounty severity may differ from the CVSS band; both are stated where they diverge.

<!-- END classification-cvss -->
