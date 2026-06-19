# Reproduce — N-2

From the persisted harness (out of /tmp):

```bash
cd reports/tiprun-2026-06-13/harness
forge test --match-contract PoC_CapabilityRegistryNoop -vv
```

PoC file: `poc/PoC_CapabilityRegistryNoop.t.sol` (also in `harness/test/`). Captured output: `poc_output.log`.

Expected: test passes. The base harness wires a real `CAP_MARGIN_CHECK` provider; the test reproduces the finding's
condition by clearing it (`unregisterPlugin(riskPlugin)` — never required by `registerPlugin`), then opens a short of
5000 against 1000 collateral. With the no-op fallback (`NullMarginCheck`) the insolvent position is accepted, and the
still-deployed Risk view reports the accepted account value as negative.

Scope: impact requires a deployment that should run the perp margin engine but has no `CAP_MARGIN_CHECK` provider; on
a spot/predict profile the fallback is intended (see `report.md` scope caveat).

Toolchain / lib setup: see `harness/SETUP.md`. No mainnet/testnet interaction — all assertions run on a local
Foundry EVM. Nothing is submitted by this package; human review + KYC + submission are the operator's responsibility.
