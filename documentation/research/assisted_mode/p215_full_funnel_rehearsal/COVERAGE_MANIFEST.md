# P215 — COVERAGE MANIFEST (source-only denominator)

Source: `output/coverage_manifest.json` (schema v1, pre-staged blind; `7850867f…`). Reused as-is (not regenerated, to
preserve the blind upstream). **273 total items; 201 in-scope.** Kinds: 214 functions, 28 immutables, 18 constructors,
8 constants, 5 addresses.

## In-scope surface families (the denominator the funnel must account for)
| Family | Where | Manifest signal |
|---|---|---|
| External entry points | `ERC20Custody.{deposit,withdraw,whitelist,unwhitelist}`, `ZetaConnector*.{send,onReceive,onRevert}`, `ZRC20.{deposit,withdraw,transfer}` | function + `cross_chain` (18) + `permissions` (18) |
| Deposits / withdrawals / redemptions | `ERC20Custody.deposit/withdraw`, `WZETA.deposit/withdraw`, `ZRC20.deposit/withdraw`, `Zeta.*` mint/burn | `token` (101), `mint_redeem` surfaces |
| Accounting state transitions | `ZRC20` supply/balance, fee accounting, `ZetaTokenConsumer*` swap accounting | `accounting` (35) |
| Asset custody paths | `ERC20Custody` (TSS custody of bridged ERC20), `WZETA`, AMM consumers holding ZETA | `token`, `accounting` |
| Access-control boundaries | `onlyTSS`/`onlyTSSUpdater`/`Ownable` on custody+connector; `ZetaInteractor` sender allow-list | `permissions` (18) |
| Oracle / price dependencies | `SystemContract.setGasPrice`, `ZetaTokenConsumer*` price/min-out paths | `oracle` (23) |
| Signature / message validation | `ZetaConnector`/`ZetaInteractor` cross-chain message origin + replay | `cross_chain` (18) |
| Callbacks / hooks / external calls | `onZetaMessage`/`onZetaRevert`, AMM router calls, `zContract` calls | `external_calls` field |
| Upgrade / admin paths | TSS-updater rotation, `updateZetaFee`, `updateProtocolFlatFee`, `setGasPrice` | `permissions`, `config` (144) |
| Invariant families | (a) custody balance ≥ accounted deposits; (b) cross-chain msg authenticity (only TSS/allow-listed sender); (c) ZRC20 supply conservation across deposit/withdraw/burn; (d) AMM-consumer slippage protection; (e) fee monotonicity | derived |

## In-scope items by contract (top)
ZRC20 27 · ZetaTokenConsumerPancakeV3 13 · ZetaTokenConsumerUniV3 13 · SystemContract 13 · ERC20Custody 12 ·
ZetaTokenConsumerTrident 12 · ZetaConnectorBase 10 · ZetaTokenConsumerUniV2 10 · ZetaInteractor 7 ·
ZetaConnectorNonEth 6 · ZetaConnectorZEVM 5 · ZetaConnectorEth 5 · ZetaNonEth 5 · WZETA 2 · …

## Note on test-helper surfaces in the manifest
The blind manifest marks some **test helpers** in-scope (`AttackerContract` 9, `SystemContractMock` 7,
`ZetaInteractorMock` 3, `WETH9` 12, `Victim` 2, `ERC20Mock` 1). Per `TARGET_INTAKE.md` these are **out-of-scope for
finding credit** and are dispositioned as such in discovery — they are not promoted as candidates.
