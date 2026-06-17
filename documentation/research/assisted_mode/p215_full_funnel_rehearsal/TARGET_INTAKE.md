# P215 — TARGET INTAKE

| Field | Value |
|---|---|
| Contest name | ZetaChain |
| Platform | Code4rena (`2023-10-zetachain`) |
| Source path | `audits/zetachain-2023-10-holdout/contracts/contracts/` (`evm/`, `zevm/`) |
| Commit | `be8cdbf` ("Report for 2023-11-zetachain") |
| Answer-key path | `audits/zetachain-2023-10-holdout/_sealed_answer_key/report.md` |
| Seal status | **SEALED** (own `.git`; not opened; marker hash `5cf9c263d432`) |
| Build command | `forge build` (foundry; solc 0.8.7) — harnesses use the forge-std-free pattern in `pocs/p215/` |
| Test command | `forge test --match-contract <ZETA_xx>` |
| Dependency status | Self-contained source for core EVM/ZEVM; external deps = OpenZeppelin (ERC20/Ownable) + Uniswap/Trident/Pancake interfaces (mocked in harnesses, never re-implemented to manufacture a bug) |
| Contest severity rules | Code4rena: **High** = assets directly at risk / loss of funds; **Medium** = assets indirectly at risk or function/availability impacted; QA = Low/Non-critical. (Used for severity calibration scoring.) |

## In-scope (audited) contracts
**EVM:** `ERC20Custody.sol`, `Zeta.eth.sol`, `Zeta.non-eth.sol`, `ZetaConnector.base.sol`, `ZetaConnector.eth.sol`,
`ZetaConnector.non-eth.sol`, `tools/ZetaInteractor.sol`, `tools/ZetaTokenConsumer{UniV2,UniV3,Trident,PancakeV3}.strategy.sol`,
`tools/ImmutableCreate2Factory.sol`.
**ZEVM:** `SystemContract.sol`, `ZRC20.sol`, `WZETA.sol`, `ZetaConnectorZEVM.sol`, `Uniswap.sol`, `UniswapPeriphery.sol`.

## Out-of-scope (test helpers / interfaces — recorded so coverage isn't credited to them)
`evm/testing/*` (`AttackerContract`, `ERC20Mock`, `ZetaReceiverMock`, `ZetaInteractorMock`, `TestUniswapV3Contracts`),
`zevm/testing/SystemContractMock`, and all `interfaces/` (interface-only). NOTE: several pre-staged deep_pass bundles
point at test-helper surfaces (`AttackerContract.*`, `Victim.*`, `WETH9.*`, `*Mock.*`) — these are **out-of-scope** and
will be dispositioned as such during discovery, not promoted as candidates.

## Value surfaces for bounded discovery (≤5 deep-trace clusters)
1. **EVM custody** — `ERC20Custody` whitelist/deposit/withdraw/updateZetaFee (TSS-signed custody of bridged ERC20s).
2. **Cross-chain message validation** — `ZetaConnector.*` + `ZetaInteractor` (onReceive/onRevert, source-chain & sender allow-listing, replay).
3. **ZEVM gas/fee accounting** — `ZRC20` withdrawGasFee / transfer / protocol-fee, `SystemContract.setGasPrice`.
4. **AMM-consumer slippage/oracle** — `ZetaTokenConsumer{UniV2,UniV3,Trident,Pancake}` (min-out / deadline / price handling).
5. **Token supply conservation** — `WZETA` (legacy WETH-style deposit/withdraw) + `Zeta.*` mint/burn authority.
