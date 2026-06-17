## redundant code
The module observer has [SetKeygen in line 36](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/abci.go#L36) of beginBlocker.
The same code in [AddObserver](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/keeper/msg_server_add_observer.go#L40) can be removed.