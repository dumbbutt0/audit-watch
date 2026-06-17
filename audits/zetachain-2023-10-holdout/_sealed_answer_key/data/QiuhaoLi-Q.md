## Observer's AddBlockHeader can trigger nil panic for GetChainFromChainID

## Links to affected code

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/keeper/msg_server_add_block_header.go#L19

## -- Vulnerability details

## Impact

Anyone can trigger a nil reference panic by sending `MsgAddBlockHeader` message with invalid `msg.ChainId`.

## Proof of Concept
When `MsgAddBlockHeader` messages are handled in x/observer/keeper/msg_server_add_block_header.go:AddBlockHeader, we don't check if the value returned from `common.GetChainFromChainID(msg.ChainId)` is not `nil`, and then pass it to `IsAuthorized`:

```solidity
// AddBlockHeader handles adding a block header to the store, through majority voting of observers
func (k msgServer) AddBlockHeader(goCtx context.Context, msg *types.MsgAddBlockHeader) (*types.MsgAddBlockHeaderResponse, error) {
	ctx := sdk.UnwrapSDKContext(goCtx)

	// check authorization for this chain
	chain := common.GetChainFromChainID(msg.ChainId)
	if ok := k.IsAuthorized(ctx, msg.Creator, chain); !ok {  // <===
		return nil, types.ErrNotAuthorizedPolicy
	}
```

And in `IsAuthorized` --> `GetObserverMapper` --> `GetObserverMapperIndex`, chain is referenced directly:

```solidity
func GetObserverMapperIndex(chain *common.Chain) string {
	return fmt.Sprintf("%d", chain.ChainId)
}
```

Since the reference happens before any checks in `AddBlockHeader`, anyone can trigger a panic by sending invalid msg.chainId. For example, we add a chainId = 0 to TestMsgServer_AddBlockHeader:

```solidity

// x/observer/keeper/msg_server_add_block_header_test.go

func TestMsgServer_AddBlockHeader(t *testing.T) {
	header, err := sample.EthHeader()
	assert.NoError(t, err)
	observerChain := common.GoerliChain()
	observerAddress := sample.AccAddress()
	// Add tests for btc headers : https://github.com/zeta-chain/node/issues/1336
	tt := []struct {
		name                  string
		msg                   *types.MsgAddBlockHeader
		IsEthTypeChainEnabled bool
		IsBtcTypeChainEnabled bool
		wantErr               require.ErrorAssertionFunc
	}{
		{
			name: "success submit eth header",
			msg: &types.MsgAddBlockHeader{
				Creator:   observerAddress,
				ChainId:   common.GoerliChain().ChainId,
				BlockHash: sample.Bytes(),
				Height:    1,
				Header:    common.NewEthereumHeader(header),
			},
			IsEthTypeChainEnabled: true,
			IsBtcTypeChainEnabled: true,
			wantErr:               require.NoError,
		},
		{
			name: "submit eth header with wrong ChainId",
			msg: &types.MsgAddBlockHeader{
				Creator:   observerAddress,
				ChainId:   0,               // <===
				BlockHash: sample.Bytes(),
				Height:    1,
				Header:    common.NewEthereumHeader(header),
			},
			IsEthTypeChainEnabled: true,
			IsBtcTypeChainEnabled: true,
			wantErr:               require.NoError,
		},
		{
```

Test Output:

```bash
qiuhao@pc:~/web3/zeta-chain/node/x/observer/keeper$ go test -tags TESTNET -run TestMsgServer_AddBlockHeader
--- FAIL: TestMsgServer_AddBlockHeader (3.15s)
    --- FAIL: TestMsgServer_AddBlockHeader/submit_eth_header_with_wrong_ChainId (0.00s)
panic: runtime error: invalid memory address or nil pointer dereference [recovered]
        panic: runtime error: invalid memory address or nil pointer dereference
[signal SIGSEGV: segmentation violation code=0x1 addr=0x8 pc=0x12cfa37]

goroutine 138 [running]:
testing.tRunner.func1.2({0x1551cc0, 0x268eed0})
        /usr/local/go/src/testing/testing.go:1526 +0x24e
testing.tRunner.func1()
        /usr/local/go/src/testing/testing.go:1529 +0x39f
panic({0x1551cc0, 0x268eed0})
        /usr/local/go/src/runtime/panic.go:884 +0x213
github.com/zeta-chain/zetacore/x/observer/keeper.GetObserverMapperIndex(...)
        /home/qiuhao/web3/zeta-chain/node/x/observer/keeper/observer_mapper.go:20
github.com/zeta-chain/zetacore/x/observer/keeper.Keeper.GetObserverMapper({{0x1b8edc0, 0xc0018d9060}, {0x1b75630, 0xc000dd37b0}, {0x1b75658, 0xc000dd37c0}, {{0x1b8edc0, 0xc0018d9060}, 0xc000128da0, {0x1b75630, ...}, ...}, ...}, ...)
        /home/qiuhao/web3/zeta-chain/node/x/observer/keeper/observer_mapper.go:49 +0x57
github.com/zeta-chain/zetacore/x/observer/keeper.Keeper.IsAuthorized({{0x1b8edc0, 0xc0018d9060}, {0x1b75630, 0xc000dd37b0}, {0x1b75658, 0xc000dd37c0}, {{0x1b8edc0, 0xc0018d9060}, 0xc000128da0, {0x1b75630, ...}, ...}, ...}, ...)
        /home/qiuhao/web3/zeta-chain/node/x/observer/keeper/keeper_utils.go:36 +0x9e
github.com/zeta-chain/zetacore/x/observer/keeper.msgServer.AddBlockHeader({{{0x1b8edc0, 0xc0018d9060}, {0x1b75630, 0xc000dd37b0}, {0x1b75658, 0xc000dd37c0}, {{0x1b8edc0, 0xc0018d9060}, 0xc000128da0, {0x1b75630, ...}, ...}, ...}}, ...)
        /home/qiuhao/web3/zeta-chain/node/x/observer/keeper/msg_server_add_block_header.go:20 +0x105
github.com/zeta-chain/zetacore/x/observer/keeper_test.TestMsgServer_AddBlockHeader.func3(0xc0005bad00?)
        /home/qiuhao/web3/zeta-chain/node/x/observer/keeper/msg_server_add_block_header_test.go:105 +0x42d
testing.tRunner(0xc0005bad00, 0xc0018f34a0)
        /usr/local/go/src/testing/testing.go:1576 +0x10b
created by testing.(*T).Run
        /usr/local/go/src/testing/testing.go:1629 +0x3ea
exit status 2
FAIL    github.com/zeta-chain/zetacore/x/observer/keeper        3.174s

```

## Tools Used
Manual Review.

## Recommended Mitigation Steps
Add a `nil` check:

```diff
diff --git a/x/observer/keeper/msg_server_add_block_header.go b/x/observer/keeper/msg_server_add_block_header.go
index 83f8c97d..fe7d9548 100644
--- a/x/observer/keeper/msg_server_add_block_header.go
+++ b/x/observer/keeper/msg_server_add_block_header.go
@@ -17,6 +17,9 @@ func (k msgServer) AddBlockHeader(goCtx context.Context, msg *types.MsgAddBlockH
 
        // check authorization for this chain
        chain := common.GetChainFromChainID(msg.ChainId)
+       if chain == nil {
+               return nil, fmt.Errorf("chain id (%d) invalid", msg.ChainId)
+       }
        if ok := k.IsAuthorized(ctx, msg.Creator, chain); !ok {
                return nil, types.ErrNotAuthorizedPolicy
        }
```
