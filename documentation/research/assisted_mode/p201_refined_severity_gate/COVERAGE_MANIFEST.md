# P201 — coverage manifest + pre-registered blind sample (zetachain-2023-10)

Source-grounded, read-only. zetachain omnichain bridge, 18 core `.sol` / 2444 LOC
(`audits/zetachain-2023-10-holdout/contracts/contracts`). Awarded (count-only): **14 High / 34 Medium**.

## Severity-relevant surface inventory (from source)
- **EVM custody / TSS**: `ERC20Custody.{deposit,withdraw(onlyTSS),updateTSSAddress(onlyTSSUpdater),whitelist}`.
- **EVM connector (lock / mint-burn / message)**: `ZetaConnector.base.{updateTssAddress,pause}`,
  `ZetaConnector.eth.{send,onReceive,onRevert}`, `ZetaConnector.non-eth.{send,onReceive,setMaxSupply,mint}`.
- **EVM cross-chain auth**: `ZetaInteractor.{isValidMessageCall,isValidRevertCall,setInteractorByChainId}`.
- **EVM gas/value swap**: `ZetaTokenConsumerUniV2.{getZetaFromEth,getEthFromZeta,getZetaFromToken,getTokenFromZeta}`.
- **zEVM token**: `ZRC20.{deposit(onlySystem),withdraw,withdrawGasFee,burn,transferFrom,updateSystemContractAddress,updateGasLimit}`.
- **zEVM system**: `SystemContract.{depositAndCall,onCrossChainCall,setGasPrice,setGasCoinZRC20,updateSystemContractAddress}`.
- **zEVM connector / wrapped**: `ZetaConnectorZEVM.{send,withdraw}`, `WZETA.{deposit,withdraw,transferFrom}`.

## Pre-registered blind sample (18 surfaces) — frozen BEFORE any blind run
Chosen for gate-class spread (A theft/value-flow · D DoS · E auth · C precision · F multi-mechanism). Each traced
blind by one Sonnet subagent on production `deep_trace.md` + verbatim source; no finding details supplied.

| id | file | function(s) under trace | gate classes targeted |
|---|---|---|---|
| zeta-01 | evm/ERC20Custody.sol | `deposit` | A accounting / value-in |
| zeta-02 | evm/ERC20Custody.sol | `withdraw` (onlyTSS) | A theft / E auth |
| zeta-03 | evm/ERC20Custody.sol | `updateTSSAddress` / `updateTSSAddressUpdater` / `whitelist` | E auth/privileged transition |
| zeta-04 | evm/ZetaConnector.base.sol | `updateTssAddress` / `pause` / `unpause` | E auth / D DoS |
| zeta-05 | evm/ZetaConnector.eth.sol | `send` / `onReceive` / `onRevert` | A value-flow / E message-auth / F multi |
| zeta-06 | evm/ZetaConnector.non-eth.sol | `send` / `onReceive` / `onRevert` | A mint-burn supply / E / F multi |
| zeta-07 | evm/ZetaConnector.non-eth.sol | `setMaxSupply` / mint path | A supply-cap / C precision |
| zeta-08 | evm/tools/ZetaInteractor.sol | `isValidMessageCall` / `isValidRevertCall` / `setInteractorByChainId` | E cross-chain caller verification |
| zeta-09 | zevm/ZRC20.sol | `deposit` (onlySystem) | A value-in / E auth |
| zeta-10 | zevm/ZRC20.sol | `withdraw` / `withdrawGasFee` | A value-flow / C gas-fee precision / F multi |
| zeta-11 | zevm/ZRC20.sol | `updateSystemContractAddress` / `updateGasLimit` (onlyFungible) | E auth/privileged |
| zeta-12 | zevm/ZRC20.sol | `burn` / `transferFrom` / `approve` | A token accounting |
| zeta-13 | zevm/SystemContract.sol | `depositAndCall` / `onCrossChainCall` | A cross-chain value-flow / E |
| zeta-14 | zevm/SystemContract.sol | `setGasPrice` / `setGasCoinZRC20` / `updateSystemContractAddress` | E auth/privileged |
| zeta-15 | zevm/ZetaConnectorZEVM.sol | `send` / `withdraw` | A zevm value-flow |
| zeta-16 | zevm/WZETA.sol | `deposit` / `withdraw` / `transferFrom` | A wrapped-token value-flow |
| zeta-17 | evm/tools/ZetaTokenConsumerUniV2.strategy.sol | `getZetaFromEth` / `getEthFromZeta` | C swap precision / D slippage |
| zeta-18 | evm/Zeta.non-eth.sol | mint/burn (connector-gated) | A cross-chain supply / E |

Class spread: A ≈ 11 · E ≈ 9 · D ≈ 3 · C ≈ 4 · F (multi-mechanism) ≥ 4 · **B oracle = 0 (carved out)**. Bounded
sample → out-of-sample **signal**, not full recall.
