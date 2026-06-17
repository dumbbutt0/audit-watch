## 1. keeper's ProcessLogs silents errors from ProcessZRC20WithdrawalEvent / ParseZetaSentEvent

Not all errors are logged within ParseZRC20WithdrawalEvent / ParseZetaSentEvent so if any of those fails,
we have no visibility on the fail reason because returned err is never accessed.

in x/crosschain/keeper/evm_hooks.go:94
```go
	for _, log := range logs {
		eventWithdrawal, err := k.ParseZRC20WithdrawalEvent(ctx, *log)
		if err == nil {
			if err := k.ProcessZRC20WithdrawalEvent(ctx, eventWithdrawal, emittingContract, txOrigin); err != nil {
				return err
			}
		}
		eZeta, err := ParseZetaSentEvent(*log, connectorZEVMAddr)
		if err == nil {
			if err := k.ProcessZetaSentEvent(ctx, eZeta, emittingContract, txOrigin); err != nil {
				return err
			}
		}
	}
```

## 2. EVMChainClient's IsSendOutTxProcessed silents errors from ParseZetaReceived / ParseZetaReverted

Errors are not logged within ParseZetaReverted / ParseZetaReceived so if any of those fails,
we have no visibility on the fail reason because returned err is never accessed.

```go
    revertedLog, err := connector.ZetaConnectorNonEthFilterer.ParseZetaReverted(*vLog) 
	if err == nil {
        logger.Info().Msgf("Found (revertTx) sendHash %s on chain %s txhash %s", sendHash, ob.chain.String(), vLog.TxHash.Hex())
    // err != nil is never handled
```

```go
	receivedLog, err := connector.ZetaConnectorNonEthFilterer.ParseZetaReceived(*vLog)
	if err == nil {
        logger.Info().Msgf("Found (outTx) sendHash %s on chain %s txhash %s", sendHash, ob.chain.String(), vLog.TxHash.Hex())
    // err != nil is never handled
```

## 3. Error from PostGasPrice is overwritten by GetBlockHeight error value in WatchGasPrice()

Following happens twice in evm client, bitcoin client is fine.
When `PostGasPrice` and `GetBlockHeight` fails the underlying `PostGasPrice` fail reason is purged thus it's nil.

```go
			err = ob.PostGasPrice()
			if err != nil {
				height, err := ob.zetaClient.GetBlockHeight()
				if err != nil {
					ob.logger.WatchGasPrice.Error().Err(err).Msg("GetBlockHeight error")
				} else {
					// @remark: here the err is nil, not the error from ob.PostGasPrice() as expected.
					ob.logger.WatchGasPrice.Error().Err(err).Msgf("PostGasPrice error at zeta block : %d  ", height)
				}
			}
```

## 4. Logging error and returning it to caller is a bad practice.

Logging an error is a way of handling it. Another way of handling error is returning it to caller so that it can decide 
what to do.
When error is logged and propagated to caller a person reviewing the logs might be confused seeing errors that had no 
negative impact on the system because were handled gracefully in other place.

## 5. Check if value is greater than math.MaxInt64 / math.Uint64 is ineffective

The codebase has multiple checks like:
```go
	if block >= math.MaxInt64 {
		panic("lastBlockScanned is too large")
	}
```

This is ineffective since the value overflow and it's not possible to satisfy `int64 > int64 + 1`.

## 6. Potential insecure access of prometheus counter 

While "rpc_getBlockByNumber_count" is always available as it's set during zetaclient initialization, it's a good practice to be consistent with accessing it.
There is one use case where counter is accessed not in else block during error check:

```go
	counter, err := ob.GetPromCounter("rpc_getBlockByNumber_count")
	if err != nil {
		ob.logger.ExternalChainWatcher.Error().Err(err).Msg("GetPromCounter:")
	}
	counter.Inc() // potential panic when "rpc_getBlockByNumber_count" would be not available.
```
