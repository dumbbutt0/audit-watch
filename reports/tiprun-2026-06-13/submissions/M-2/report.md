# M-2 (Medium) — Oracle has no read-side staleness check and the monotonic-update guard is commented out

- **Target:** TipRun. Commit `d5d4d2a…`.
- **Contract:** `src/core/oracle/Oracle.sol` → `updatePrice` (monotonic guard commented out, ~lines 46-54) and
  `getPrice` (no max-age). Consumed by `src/core/risk/Risk.sol::getAssetValueAndRisk`.
- **Severity:** Medium / Low.
- **PoC:** `poc/PoC_OracleStaleness.t.sol` (passing) · log `poc_output.log`.

## Root cause
`Oracle.updatePrice` has its `timestamp > current` monotonic guard **commented out** (a `TODO`), and `Oracle.getPrice`
returns `exist = (timestamp > 0)` with **no freshness/max-age check**. `Risk.getAssetValueAndRisk` treats any stored
price as valid forever. Ingestion (`OraclePriceTickTransLib`) enforces signer-quorum + median + a ≤1-day bound, but
once stored, a price is used in all margin/liquidation math indefinitely, and a (recently-signed, ≤1-day-old) price
can be re-applied **out of order** because the monotonic guard is gone.

## Impact
Under operator delay/failure, reorg, or a deliberately reordered tick, margin and liquidation decisions run on stale
or rolled-back prices. There is no on-chain guarantee that the price used for a solvency decision is recent.

## PoC (passing)
`forge test --match-contract PoC_OracleStaleness -vv` (from `../../harness/`):
- set price 100 @ a recent timestamp; then `updatePrice` with an **older** timestamp and price 1 → accepted (no
  monotonic guard); `getPrice` now returns the rolled-back 1 and `getCurrentTimestamp` regressed.
- warp 10 years forward; `getPrice` still reports `exist=true` for the ancient price (no staleness rejection).

## Suggested fix
Restore the monotonic timestamp guard in `updatePrice` and enforce a max-age in `getPrice` (or in `Risk` before
using the price), reverting / flagging stale prices used for margin or liquidation.

<!-- BEGIN classification-cvss -->

## Vulnerability classification & CVSS

- **Category (VRT):** Insufficient Cryptography / Insecure Design → Business Logic Errors (oracle price consumed with no read-side staleness check; monotonic-update guard disabled)
- **Secondary category:** Sensitive Data / data-authenticity: Insufficient Verification of Data Authenticity
- **CWE (informative):** CWE-345 (Insufficient Verification of Data Authenticity); CWE-672 (Operation on a Resource after Expiration/Release)

| Aspect | CVSS v3.1 vector | Base score | Severity |
|---|---|---|---|
| Stale-price acceptance | `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L` | **4.8** | Medium |

> Impact realises only while the feed is stale (AC:H).

> CVSS v3.1 base scores computed with the official formula (no temporal/environmental modifiers). For smart-contract findings the protocol/bounty severity may differ from the CVSS band; both are stated where they diverge.

<!-- END classification-cvss -->
