# GRPC server address does not allowed to set in current cosmos sdk version 

## Links to affected code

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/server/config/config.go#L339

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/server/flags/flags.go#L55

https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/server/start.go#L205C1-L206C1

## Impact

Current used cosmos sdk version hardcode the grpc server address to `"127.0.0.1:%s", port`, you can see the detail [here](https://github.com/cosmos/cosmos-sdk/pull/18254/files#diff-97289af2ab66016f168df6fccac70626d125f170e5cf0841fcdc8fa624999608L501), so `json-rpc.address` configuration inside `app.toml` is useless.

If one host want to start multiple nodes with the same port, it would be failed.



## Proof of Concept
1. start one full node with same port such as 2345.
2. start a new full node with same port, it would start failed.

## Tools Used

vscode

## Recommended Mitigation Steps

Upgrade the cosmos sdk version to new version such as 0.47.6.
