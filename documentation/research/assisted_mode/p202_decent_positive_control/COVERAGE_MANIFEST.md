# P202 — coverage manifest + pre-registered blind sample (decent-2024-01)

Source-only, read-only. In-scope = `src/` + `lib/decent-bridge/src/`
(`audits/decent-2024-01-holdout/contracts`). Cross-chain bridge swap/execute protocol. Awarded (PCS count-only):
**4 High / 5 Medium**. Sample chosen for **comprehensive category coverage** (mitigates orchestrator selection bias).

## Severity-relevant surface inventory (from source)
- **UTB (entry)**: `swapAndExecute`, `bridgeAndExecute`, `callBridge`, `receiveFromBridge`, `performSwap`,
  `approveAndCheckIfNative`, setters (`setExecutor/setWrapped/setFeeCollector`, `registerBridge/registerSwapper`).
- **Executor**: `UTBExecutor.execute` (×2 overloads, refund/stuck-funds), `DecentBridgeExecutor.execute/_executeWeth/_executeEth`.
- **Fees/signature**: `UTBFeeCollector.collectFees/redeemFees/splitSignature/setSigner`.
- **Swap/token**: `UniSwapper.swap/swapExactIn/swapExactOut/swapNoPath/_sendToRecipient/_receiveAndWrapIfNeeded`.
- **Adapters/message**: `StargateBridgeAdapter.bridge/callBridge/sgReceive/registerRemoteBridgeAdapter`,
  `DecentBridgeAdapter.bridge/receiveFromBridge`.
- **Router/bridge token**: `DecentEthRouter.bridge/_bridgeWithPayload/onOFTReceived/redeemEth/redeemWeth/
  add-removeLiquidity`, `DcntEth.mint/burn/setRouter/mintByOwner`.
- **Access-control primitives**: `UTBOwned`, `BaseAdapter`, `Operable`, `Roles`.

## Pre-registered blind sample (14 surfaces) — frozen BEFORE the blind run
| id | file(s) · function(s) | required category |
|---|---|---|
| decent-01 | UTB.sol · swapAndExecute / _swapAndExecute | swap+execute entry |
| decent-02 | UTB.sol · bridgeAndExecute / callBridge | bridge initiation |
| decent-03 | UTB.sol · receiveFromBridge | bridge completion / message validation |
| decent-04 | UTBExecutor.sol · execute (×2) | executor / refund / stuck-funds |
| decent-05 | UTBFeeCollector.sol · collectFees / redeemFees / splitSignature | fee handling / signature-auth |
| decent-06 | UniSwapper.sol · swap / swapExactIn / swapExactOut / _sendToRecipient | swap / token transfer |
| decent-07 | StargateBridgeAdapter.sol · bridge / callBridge / sgReceive | adapter / message validation |
| decent-08 | DecentBridgeAdapter.sol · bridge / receiveFromBridge | adapter / completion |
| decent-09 | DcntEth.sol · mint / burn / setRouter / mintByOwner | token mint-burn access-control |
| decent-10 | DecentEthRouter.sol · bridge / _bridgeWithPayload | bridge initiation (router) |
| decent-11 | DecentEthRouter.sol · onOFTReceived | bridge completion / message validation |
| decent-12 | DecentEthRouter.sol · redeem/removeLiquidity | stuck-funds / liquidity value-flow |
| decent-13 | DecentBridgeExecutor.sol · execute / _executeWeth / _executeEth | executor / stuck-funds |
| decent-14 | UTBOwned + BaseAdapter + Operable + Roles | access-control path |

Category coverage: bridge initiation (02,10) · bridge completion (03,08,11) · refund (04) · executor (04,13) ·
adapter (07,08) · swap (01,06) · fee (05) · access-control (09,14) · stuck-funds (04,12,13) · message validation
(03,07,11) · token transfer (06,09). All 11 required categories covered. Bounded sample → out-of-sample signal.
