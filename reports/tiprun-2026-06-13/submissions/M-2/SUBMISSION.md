<!--
PLATFORM-PASTE-READY version of the M-2 report. Plain prose + standard code fences only — no blockquote
header, no viewer "Copy"/language-label artifacts. Paste each labelled section into the matching HackenProof
field. Facts are identical to report.md (validated, PoC passing). Copy from the RAW file, not a rendered
preview, to avoid pulling in a viewer's "Copy" button text.
-->

# Field: Target
https://github.com/hackenproof-public/tiprun-contracts

# Field: Category
Business Logic Errors

# Field: Severity
Medium

# Field: Title
Oracle prices never expire and can be rolled back, so margin and liquidation can run on stale prices

# Field: Vulnerability details

`Oracle.updatePrice` has its monotonic-timestamp guard commented out, and `Oracle.getPrice` returns a price
with no freshness/max-age check. `Risk.getAssetValueAndRisk` treats any stored price as valid forever. As a
result, under operator delay, a reorg, or a deliberately reordered tick, margin and liquidation decisions can
run on stale or rolled-back prices, with no on-chain guarantee that the price used for a solvency decision is
recent.

## Impact

This is Medium because solvency-critical math (margin checks, liquidations) can execute against a price that
is arbitrarily old or has been moved backwards in time, with no privileged role required to reach the stale
state — but realizing loss depends on the feed actually being stale/reordered, so it is conditional rather
than an unconditional drain.

Concretely: once a price is stored it is used in all margin/liquidation math indefinitely, and a
recently-signed (<= 1-day-old) price can be re-applied out of order because the monotonic guard is gone.
Ingestion (`OraclePriceTickTransLib`) still enforces signer-quorum + median + a <= 1-day bound, but nothing on
the read side enforces recency or monotonicity.

## Root cause

`Oracle.updatePrice` has its `timestamp > current` monotonic guard commented out (a `TODO`), and
`Oracle.getPrice` returns `exist = (timestamp > 0)` with no freshness/max-age check. `Risk.getAssetValueAndRisk`
treats any stored price as valid.

## Suggested fix

Restore the monotonic timestamp guard in `updatePrice` and enforce a max-age in `getPrice` (or in `Risk`
before using the price), reverting or flagging stale prices used for margin or liquidation.

# Field: Validation steps

The PoC runs against the project's own contracts in a local Foundry harness; it passes. From the harness root:

```bash
forge test --match-contract PoC_OracleStaleness -vv
```

Steps proven: set price 100 at a recent timestamp; then call `updatePrice` with an older timestamp and price 1
— it is accepted (no monotonic guard), and `getPrice` now returns the rolled-back 1 while `getCurrentTimestamp`
has regressed. Warp 10 years forward; `getPrice` still reports `exist = true` for the ancient price (no
staleness rejection).

Captured output (passes):

```
[PASS] test_PoC_priceCanBeRolledBackAndIsNeverStale()
  rolled-back price (FXP): 4294967296
  age of price at read (days): 5
Suite result: ok. 3 passed; 0 failed; 0 skipped
```

# Field: Attachments
- PoC_OracleStaleness.t.sol
- poc_output.log   (captured passing run)
