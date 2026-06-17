When decoding a `BlockNumber`, some invalid inputs will not return an error.

[Here](https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/node/rpc/types/block.go#L102), `case.ToUint64` cannot return an error. If there is a decoding issue, `blckNum` will be zero.

```go
blckNum, err := hexutil.DecodeUint64(input)
if errors.Is(err, hexutil.ErrMissingPrefix) {
	blckNum = cast.ToUint64(input)
} else if err != nil {
	return err
}
```

You can add the following test case to [the test cases here](https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/node/rpc/types/block_test.go#L14) to check it.

```go
{
  "JSON input with invalid block number",
  []byte("{\"blockNumber\": \"aaaaaaa\"}"),
  func() {
  },
  false,
},
```