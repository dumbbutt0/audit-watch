# Reproduce — N-2

From the persisted harness (out of /tmp):

```bash
cd reports/tiprun-2026-06-13/harness
forge test --match-contract PoC_CapabilityRegistryNoop -vv
```

PoC file: `poc/PoC_CapabilityRegistryNoop.t.sol` (also in `harness/test/`). Captured output: `poc_output.log`.

Expected: three tests pass, all via the real user path.
- `test_PoC_tradePluginDoesNotRequireMarginCapability`: the TYPE_TRADE plugin declares zero required capabilities, so
  it registers with no `CAP_MARGIN_CHECK` provider.
- `test_sameUserTradeRevertsWhenRiskProviderRegistered` (negative control): with the real Risk provider wired, a
  normal user-signed trade relayed through the txBatcher reverts `"PM: risk inc"`.
- `test_PoC_userTradeAcceptedWhenPerpMarginProviderMissing`: with the provider absent (deployment state set up via an
  owner call — NOT the attack action), the identical user trade is accepted, leaving the account far below
  maintenance margin (`risk > value*FXP`).

Scope: impact requires a deployment that reaches the missing-`CAP_MARGIN_CHECK` state while trading is live. HIGH if
that state is in-scope reachable (deploy/upgrade window or a perp profile that omits the provider); MEDIUM as a
fail-open design defect; OUT OF SCOPE if only owner misconfiguration reaches it (see `report.md` reachability section).

Toolchain / lib setup: see `harness/SETUP.md`. No mainnet/testnet interaction — all assertions run on a local
Foundry EVM. Nothing is submitted by this package; human review + KYC + submission are the operator's responsibility.
