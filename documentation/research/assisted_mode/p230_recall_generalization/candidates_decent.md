# P230 measurement artifact — Decent UTB (Cross-chain) blind candidate set

Subject: `audits/decent-2024-01-holdout` (cross-chain swap+bridge settlement router). Keys SEALED (not opened).
Method: blind Sonnet deep_trace pass driven by `prompts/deep_trace.md` + `agents/{cross_chain,access_control,logic,economic_attack,dos,reentrancy}.md` + `config/{cross_chain_constants,migration_flow_patterns}.json`.
Tally: 17 candidates — HIGH 8 · MED 8 · LOW 1 · NOISE 0.

| id | title | bug class | contract | conf | signal |
|---|---|---|---|---|---|
| DEC-01 | UTB.receiveFromBridge fully unguarded public — arbitrary payload execution | access-control | UTB | Confirmed | HIGH |
| DEC-02 | sgReceive ignores all src-chain validation fields (srcChainId/srcAddress/nonce) | access-control/routing | StargateBridgeAdapter | High | HIGH |
| DEC-03 | fee signature omits block.chainid → cross-chain fee-signature replay | access-control/invariant | UTBFeeCollector | Confirmed | HIGH |
| DEC-04 | ERC20 approval to paymentOperator not cleared on failed call → drain | accounting/logic | UTBExecutor | High | HIGH |
| DEC-05 | native msg.value overpayment not refunded → ETH locked (no sweep) | accounting/economic | UTB | Confirmed | MED |
| DEC-06 | UniSwapper swapNoPath/ExactIn/ExactOut public, bypass onlyUtb → residual drain | access-control | UniSwapper | Confirmed | HIGH |
| DEC-07 | callBridge forwards raw msg.value; getValue dead code; Stargate underpay grief | economic/accounting | StargateBridgeAdapter | Medium | MED |
| DEC-08 | gasIsEth native path under-funds router (amt2Bridge vs msg.value) | accounting/invariant | DecentBridgeAdapter | Medium | MED |
| DEC-09 | collectFees ecrecover no zero-address check; address(0) signer bypass window | access-control | UTBFeeCollector | High | HIGH |
| DEC-10 | native refund unchecked low-level call → permanently locked ETH | dos/accounting | UTBExecutor | Confirmed | HIGH |
| DEC-11 | fee collected before bridge; no atomicity → fee lost on bridge revert | accounting/economic | UTB | Medium | MED |
| DEC-12 | swapExactOut refund to attacker-controlled payload refund address | routing/economic | UniSwapper | Medium | MED |
| DEC-13 | sgReceive ignores _token/amountLD → bridged-vs-execution amount mismatch | accounting/cross-chain | StargateBridgeAdapter | High | HIGH |
| DEC-14 | receiveFromBridge onlyExecutor depends on correct bridgeExecutor config | access-control | DecentBridgeAdapter/BaseAdapter | Medium | LOW |
| DEC-15 | performSwap msg.value check on original value, not post-fee balance | accounting | UTB | Medium | MED |
| DEC-16 | fee signature omits address(this) → same-chain multi-deployment replay | access-control/routing | UTBFeeCollector | Medium | MED |
| DEC-17 | swapNoPath EXACT_OUT tokenOut==0 delivers WETH but UTB expects native | logic/accounting | UniSwapper | Medium | MED |
