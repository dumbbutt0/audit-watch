# N-4 (Low) — Settlement mints collateral at an unconstrained operator price (no oracle / signature / conservation)

- **Target:** TipRun contracts (off-chain-match / on-chain-settlement exchange), predict profile. Commit `d5d4d2a…`.
- **Contract:** `src/predict/transactions/SettlementTransLib.sol` → `process`, invoked via
  `src/predict/plugins/SettlementPlugin.sol`.
- **Severity:** Low (operator-trust-gated — no permissionless exploit; reported as a missing on-chain invariant /
  defense-in-depth gap).
- **PoC (passing):** `poc/PoC_SettlementUnconstrained.t.sol` · log `poc_output.log`.
- **Actor:** the settlement operator (the trusted batcher/back end that submits `Settlement` transactions).

## Root cause
`SettlementTransLib.process` force-settles a synthetic position by crediting collateral equal to
`syntheticBalance * settlementPrice`, where `settlementPrice` is a **raw operator input**:

```solidity
function process(Settlement memory self, IPositionManager position) public {
    require(self.accountId != 0, "SettlementTransLib: accountId is 0");
    require(self.settlementPrice >= 0 && self.settlementPrice <= type(int128).max,
            "SettlementTransLib: invalid settlement price");
    int256 syntheticBalance = position.getSyntheticBalance(self.accountId, self.syntheticAssetId);
    if (syntheticBalance == 0) { return; }
    int256 collateralDelta = syntheticBalance * self.settlementPrice;   // <-- price is operator-chosen
    int256 syntheticDelta  = -syntheticBalance;
    position.updatePositionInDict(self.accountId, collateralDelta, self.syntheticAssetId, syntheticDelta);
}
```

The only constraints on `settlementPrice` are `0 ≤ price ≤ int128.max`. There is:
- **no oracle binding** — the settlement price is not checked against `Oracle.getPrice` for the asset;
- **no signature / outcome binding** — nothing ties the price to a signed resolution outcome;
- **no aggregate conservation invariant** — for a YES/NO market, nothing checks that collateral credited to winners
  equals collateral burned from losers (or is backed by `LoadingZone` reserves).

So the operator can settle any position at any price, minting collateral that need not correspond to the market
outcome or to any reserve backing.

## Impact
Operator-mispriced or one-sided settlement mints collateral that is not offset by a matching burn and not backed by
`LoadingZone` reserves. That unbacked collateral becomes withdrawable, so a later `WITHDRAWAL` can drain other
users' deposited tokens. The amount is bounded only by operator honesty — there is no on-chain invariant that caps
or conserves settlement payouts. Because the path is gated by operator trust, there is **no permissionless exploit**;
this is a missing on-chain safety invariant (a single mis-set price or buggy settlement input has unbounded
accounting consequence), hence Low.

## PoC (passing)
From `../../harness/`:

```bash
forge test --match-contract PoC_SettlementUnconstrained -vv
```

`test_PoC_settlementMintsUnbackedCollateralAtOperatorPrice`: an account holds a synthetic position of 100; the oracle
price is 1. The operator settles at an **arbitrary price of 50** (unrelated to the oracle, with no signature/oracle
check). The synthetic is zeroed and collateral is credited by exactly `balance * operatorPrice = 5000` — unbacked,
later-withdrawable collateral created from an operator-chosen number. See `poc_output.log`.

## Suggested fix
- Bind `settlementPrice` to a signed resolution outcome and/or the oracle price for the asset (reject prices that
  don't match the resolved outcome).
- Enforce an aggregate conservation invariant per market (sum of credited collateral ≤ sum burned + available
  reserves), so settlement cannot mint net unbacked collateral.

## Submission caveats (honest — verify before submitting)
- **Trust model:** settlement is operator-driven; on a deployment where the operator is fully trusted and audited
  off-chain, programs may treat this as an accepted design (out of scope as "relies on trusted operator"). Submit as
  a missing-invariant / defense-in-depth finding and state the trust dependency explicitly.
- **Novelty:** verify against prior TipRun audits that the unconstrained settlement price is not already reported.

<!-- BEGIN classification-cvss -->

## Vulnerability classification & CVSS

- **Category (VRT):** Business Logic Errors — settlement payout not bound to oracle/outcome and no aggregate
  conservation invariant (operator-trust-gated).
- **CWE (informative):** CWE-20 (Improper Input Validation); CWE-840 (Business Logic Errors).

| Aspect | CVSS v3.1 vector | Base score | Severity |
|---|---|---|---|
| Unconstrained settlement price mints unbacked collateral | `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:L` | **4.2** | Medium (privileged) |

> Gated by operator trust (no permissionless exploit); reported as Low pending the program's treatment of trusted
> operator actions. Protocol/bounty severity may differ from the CVSS band.

<!-- END classification-cvss -->
