## Logical judgment in observer abci

Line [28~34](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/abci.go#L28-L34) of the abci.go file determines totalObserverCount. The log output after that should look like it should be placed in an if condition.


### change
```go
	// #nosec G701 always in range
	if totalObserverCountCurrentBlock == int(lastBlockObserverCount.Count) {
		ctx.Logger().Error("LastBlockObserverCount does not match the number of observers found at current height", ctx.BlockHeight())
		for _, observer := range allObservers {
			ctx.Logger().Error("Observes for | ", observer.ObserverChain.ChainName, ":", observer.ObserverList)
		}
		return
	}
```