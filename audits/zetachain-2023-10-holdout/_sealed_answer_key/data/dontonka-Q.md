### **[[ 1 ]]** 
`evm_signer::TryProcessOutTx` `err` variable doesn't need to be declared [here](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_signer.go#L330), as it will be created [here](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_signer.go#L357) and is not used before that. So the [following code](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_signer.go#L351-L354) is also useless. So I suggest to remove those.
```diff
	var to ethcommon.Address
-	var err error
	var toChain *common.Chain
	if send.CctxStatus.Status == types.CctxStatus_PendingRevert {
		to = ethcommon.HexToAddress(send.InboundTxParams.Sender)
		toChain = common.GetChainFromChainID(send.InboundTxParams.SenderChainId)
		if toChain == nil {
			logger.Error().Msgf("Unknown chain: %d", send.InboundTxParams.SenderChainId)
			return
		}
		logger.Info().Msgf("Abort: reverting inbound")
	} else if send.CctxStatus.Status == types.CctxStatus_PendingOutbound {
		to = ethcommon.HexToAddress(send.GetCurrentOutTxParam().Receiver)
		toChain = common.GetChainFromChainID(send.GetCurrentOutTxParam().ReceiverChainId)
		if toChain == nil {
			logger.Error().Msgf("Unknown chain: %d", send.GetCurrentOutTxParam().ReceiverChainId)
			return
		}
	} else {
		logger.Info().Msgf("Transaction doesn't need to be processed status: %d", send.CctxStatus.Status)
		return
	}
-	if err != nil {
-		logger.Error().Err(err).Msg("ParseChain fail; skip")
-		return
-	}

	// Early return if the cctx is already processed
	included, confirmed, err := evmClient.IsSendOutTxProcessed(send.Index, send.GetCurrentOutTxParam().OutboundTxTssNonce, send.GetCurrentOutTxParam().CoinType, logger)
	if err != nil {
		logger.Error().Err(err).Msg("IsSendOutTxProcessed failed")
	}
```
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_signer.go#L351-L354


### **[[ 2 ]]** 
`evm_signer::TryProcessOutTx` does allow to send out CCTX tx to address(0), which would effectivelly cause a funds loss. This is low as self-reck. I would recommend to add the following conditions.

```diff
	if send.CctxStatus.Status == types.CctxStatus_PendingRevert {
		to = ethcommon.HexToAddress(send.InboundTxParams.Sender)
		toChain = common.GetChainFromChainID(send.InboundTxParams.SenderChainId)
		if toChain == nil {
			logger.Error().Msgf("Unknown chain: %d", send.InboundTxParams.SenderChainId)
			return
		}
+		if to == (ethcommon.Address{}) {
+			logger.Error().Msgf("Invalid receiver %s", send.InboundTxParams.Sender)
+			return
+		}
		logger.Info().Msgf("Abort: reverting inbound")
	} else if send.CctxStatus.Status == types.CctxStatus_PendingOutbound {
		to = ethcommon.HexToAddress(send.GetCurrentOutTxParam().Receiver)
		toChain = common.GetChainFromChainID(send.GetCurrentOutTxParam().ReceiverChainId)
		if toChain == nil {
			logger.Error().Msgf("Unknown chain: %d", send.GetCurrentOutTxParam().ReceiverChainId)
			return
		}
+		if to == (ethcommon.Address{}) {
+			logger.Error().Msgf("Invalid receiver %s", send.GetCurrentOutTxParam().Receiver)
+			return
+		}
	} else {
		logger.Info().Msgf("Transaction doesn't need to be processed status: %d", send.CctxStatus.Status)
		return
	}
```

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_signer.go#L332-L349


### **[[ 3 ]]** 
`SystemContract.sol` could have some minor refactor introducing a `modifier` as follow to aliviate and make the code cleaner, and use it on all the `external` functions and the contructor as they are all gated with the `same condition` below.
```diff
+    /**
+     * @dev Only Fungible address allowed modifier.
+     */
+     modifier onlyFungibble() {
+        if (msg.sender != FUNGIBLE_MODULE_ADDRESS) revert CallerIsNotFungibleModule();
+        _;
+    }
```

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/SystemContract.sol#L51


### **[[ 4 ]]** 
`ERC20Custody.sol` has the following useless code in `pause` function which I suggest to remove. Since the function is guarded by `onlyTSS` the modifier, which ensure `msg.sender == TSSAddress` before going even further into the function, this means `TSSAddress` can never be `address(0)`, which make this code totally useless. 
```diff
    function pause() external onlyTSS {
        if (paused) {
            revert IsPaused();
        }
-       if (TSSAddress == address(0)) {
-           revert ZeroAddress();
-       }
        paused = true;
        emit Paused(msg.sender);
    }
```
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L122-L124


### **[[ 5 ]]** 
`ERC20Custody.sol` has a `divergence` in the implementation regarding fees, consider the following:
- `zeta` which represent the Zeta token contract on the chain is `immutable`, so can't be changed after contract contruction.
- `zetaFee` is not immutable and can be updated at any point in time by `updateZetaFee`.

The `deposit` function along with the `constructor` are causing this divergence, as constructor allow zeta to be address(0) at construction, which deposit account for in the following code, but then if `zetaFee` are modified later on (Zeta wants to start charging fees on ERC20 deposits), those fees will never be able to be charged in case zeta was passed as address(0) at constrution.

So I would recommend the following changes to mitigate this. While we are here, I would also suggest to add a validation for `zetaMaxFee` in the constructor since it's immutable too.

```diff
    constructor(address TSSAddress_, address TSSAddressUpdater_, uint256 zetaFee_, uint256 zetaMaxFee_, IERC20 zeta_) {
        TSSAddress = TSSAddress_;
        TSSAddressUpdater = TSSAddressUpdater_;
        zetaFee = zetaFee_;
+       if (zeta == address(0)) revert ZeroAddress();
        zeta = zeta_;
        zetaMaxFee = zetaMaxFee_;
    }

    function deposit(
        bytes calldata recipient,
        IERC20 asset,
        uint256 amount,
        bytes calldata message
    ) external nonReentrant {
        if (paused) {
            revert IsPaused();
        }
        if (!whitelisted[asset]) {
            revert NotWhitelisted();
        }
-       if (zetaFee != 0 && address(zeta) != address(0)) {
+       if (zetaFee != 0) {
            zeta.safeTransferFrom(msg.sender, TSSAddress, zetaFee);
        }
        uint256 oldBalance = asset.balanceOf(address(this));
        asset.safeTransferFrom(msg.sender, address(this), amount);
        // In case if there is a fee on a token transfer, we might not receive a full exepected amount
        // and we need to correctly process that, o we subtract an old balance from a new balance, which should be an actual received amount.
        emit Deposited(recipient, asset, asset.balanceOf(address(this)) - oldBalance, message);
    }
```
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L177


### **[[ 6 ]]** 
`evm_signer` is hardcoding the `gaslimit` at `21000` in multiples places (see links below). We have seen in previous EVM forks changing the gas cost of some key opcode, for example the SSTORE opcode. This can happen again in the future and if it does happen that this hardcoded gas limit is not enought anymore for the target chain, it will lead to CCTX not working as expected and failures on the network. Finally, since this value need to be working for all the EVM-supported chain, the gas costs can be different to a level that this hardcoded value will not satisfy all the chains.

I would recommend to fetch this value at least from a configuration file, and have it per EVM chain, such that it is flexible enought to adapt to the future not requiring to recompile a new binary.

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_signer.go#L210
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_signer.go#L237
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_signer.go#L286


### **[[ 7 ]]** 
`evm_signer::SignCancelTx` is unused code, would suggest to remove the function.

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_signer.go#L209-L228

### **[[ 8 ]]** 
gRPC endpoint `ConvertGasToZeta` is `unsafe` which allow to `panic this endpoint` very easely by providing a gas price that can't be converted in Integer. Fortunatelly, there is a `recovery`, so the program doesn't crash, which is why this is only submitted as a `Low`, otherwise that would be probably a High as you could DoS `zetacored` at will. 

This is confirmed throught directly reaching the public endpoint as follow:
```
REQUEST
curl -X 'GET' -H 'accept: application/json' 'https://zetachain-athens.blockpi.network/lcd/v1/public/zeta-chain/crosschain/convertGasToZeta?chainId=97&gasLimit=100_000_'

RESPONSE
{"code":13,"details":[],"message":"cannot convert \"100_000_\" to big.Int"}
```

While a more normal error would be as follow (for unknow chain)
```
REQUEST
curl -X 'GET' -H 'accept: application/json' 'https://zetachain-athens.blockpi.network/lcd/v1/public/zeta-chain/crosschain/convertGasToZeta?chainId=1&gasLimit=100_000'

RESPONSE
{"code":2,"details":[],"message":"codespace observer code 1102: chain not supported"}
```

I also added this unit test, which also confirm the issue and the a panic is occuring internally but recovered, as the error message match the panic.

```
// zeta_conversion_rate_test.go
package keeper

import (
	"github.com/stretchr/testify/require"
	"github.com/zeta-chain/zetacore/x/crosschain/types"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestConvertGasToZeta(t *testing.T) {
	keeper, ctx := setupKeeper(t)
	chainID := int64(1)
	gasLimitTest := "100_000_"
	keeper.SetGasPrice(ctx, types.GasPrice{
		ChainId:     chainID,
		MedianIndex: 0,
		Prices:      []uint64{2},
	})

	req := &types.QueryConvertGasToZetaRequest{chainID, gasLimitTest}

	fc, err := keeper.ConvertGasToZeta(ctx, req)
	require.Nil(t, err)
	assert.Nil(t, fc)
}

```

```
=== RUN   TestConvertGasToZeta
--- FAIL: TestConvertGasToZeta (0.02s)
panic: cannot convert "100_000_" to big.Int [recovered]
	panic: cannot convert "100_000_" to big.Int

goroutine 78 [running]:
testing.tRunner.func1.2({0x1601920, 0xc000c61d40})
	/usr/local/go/src/testing/testing.go:1526 +0x24e
testing.tRunner.func1()
	/usr/local/go/src/testing/testing.go:1529 +0x39f
panic({0x1601920, 0xc000c61d40})
	/usr/local/go/src/runtime/panic.go:884 +0x213
cosmossdk.io/math.NewUintFromString(...)
	/mnt/c/IX/GitProjects/go/pkg/mod/cosmossdk.io/math@v1.0.0-rc.0/uint.go:46
github.com/zeta-chain/zetacore/x/crosschain/keeper.Keeper.ConvertGasToZeta({{0x1cb6db8, 0xc000c61d10}, {0x1c985b0, 0xc000c61c10}, {0x1c985d8, 0xc000c61c20}, {0x1c99e38, 0xc000be0bb0}, {{0x1cb2a20, 0xc000c61d00}, ...}, ...}, ...)
	/mnt/c/IX/GitProjects/platform-tools/ETH_course/C4/2023-11-zetachain/repos/node/x/crosschain/keeper/zeta_conversion_rate.go:27 +0x85b
github.com/zeta-chain/zetacore/x/crosschain/keeper.TestConvertGasToZeta(0xc000ef8340?)
	/mnt/c/IX/GitProjects/platform-tools/ETH_course/C4/2023-11-zetachain/repos/node/x/crosschain/keeper/zeta_conversion_rate_test.go:23 +0x2ca
testing.tRunner(0xc000ef8340, 0x1af4e20)
	/usr/local/go/src/testing/testing.go:1576 +0x10b
created by testing.(*T).Run
	/usr/local/go/src/testing/testing.go:1629 +0x3ea
```

Even if this error is recovered, I would recommend the team to introduce a validation `ConvertGasToZeta` function such that the program return proper error, and not a panicked error, which doesn't give proper information about the error.

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/zeta_conversion_rate.go#L27

### **[[ 9 ]]** 
`updateTssAndConnectorAddresses` from `ZetaNonEth.sol` is allowing TSS and Updater adresses to be updated to the **same address**, which defeat the purpose of `renounceTssAddressUpdater`. I would recommend to add the followind condition to protect against this.

```diff
    function updateTssAndConnectorAddresses(address tssAddress_, address connectorAddress_) external {
        if (msg.sender != tssAddressUpdater && msg.sender != tssAddress) revert CallerIsNotTssOrUpdater(msg.sender);
        if (tssAddress_ == address(0) || connectorAddress_ == address(0)) revert InvalidAddress();
+       if (tssAddress_ == connectorAddress_) revert InvalidAddress();

        tssAddress = tssAddress_;
        connectorAddress = connectorAddress_;

        emit TSSAddressUpdated(msg.sender, tssAddress_);
        emit ConnectorAddressUpdated(msg.sender, connectorAddress_);
    }
```

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L40-L49

### **[[ 10 ]]** 
`EVMChainClient::observeInTX` is consuming events from EVM external chains. It will consume `ZetaSent` and `Deposited` logs plus check `Native asset` being sent directly to the TSS address. While Deposited and Native asset are communicated to Zetacore using `PostSendEVMGasLimit`, somehow `ZetaSent` isn't, which seems wrong, so I would recommended to update this.

```diff
      ...
		// Pull out arguments from logs
		for logs.Next() {
			msg, err := ob.GetInboundVoteMsgForZetaSentEvent(logs.Event)
			if err != nil {
				ob.logger.ExternalChainWatcher.Error().Err(err).Msg("error getting inbound vote msg")
				continue
			}

-	                zetaHash, err := ob.zetaClient.PostSend(PostSendNonEVMGasLimit, &msg)
+	                zetaHash, err := ob.zetaClient.PostSend(PostSendEVMGasLimit, &msg)
			if err != nil {
				ob.logger.ExternalChainWatcher.Error().Err(err).Msg("error posting to zeta core")
				return
			}
			ob.logger.ExternalChainWatcher.Info().Msgf("ZetaSent event detected and reported: PostSend zeta tx: %s", zetaHash)
		}

      ...
```

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_client.go#L856
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_client.go#L898
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_client.go#L977

### **[[ 11 ]]** 
`FetchZetaZetaNonEthTokenContract` naming seems wrong, would recommend to rename is `FetchZetaNonEthTokenContract`.

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_client.go#L261-L263

### **[[ 12 ]]** 
`ERC20Custody::whitelist` allow any address to be whitelisted, the only verification that is made (inside Observer before calling ERC20Custody contract) is that it's not address(0). But this open the room for operational mistake like whitelisting ZETA token itself. Doing so would cause potential problems, as now the user would be able to pass throught ERC20Custody to send ZETA, which is not expected, and could cause multiples sides effect.
- Supply [not properly calculated](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/zeta_supply_checker.go#L216-L218) in ZetaSupplyChecker.
- By-passing [security check](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/utils.go#L153-L156) that are present only when processing ZetaSent log, but not Deposited log.

I would recommend todo the following verification in the contract (or do it in the Observer)

```diff
    function whitelist(IERC20 asset) external onlyTSS {
+       if (address(asset) == address(zeta)) revert InvalidAsset();

        whitelisted[asset] = true;
        emit Whitelisted(asset);
    }
```


### **[[ 13 ]]** 

The following protection code in `fungible\keeper\evm_hooks.go` is totally redundant as if you trace back where hooks are called (with `PostTxProcessing`) in **ethermint@v0.22.0::state_transition.go** you can see that `receipt` parameter even if passed as a pointer can `never be nil`. Otherwise in case you are paranoid and like redundant code and would like to keep it somehow, then add the same protection at least in `crosschain\keeper\evm_hooks.go` so that is consistent accross the protocol.

```diff
func (k Keeper) CheckPausedZRC20(ctx sdk.Context, receipt *ethtypes.Receipt) error {
-	if receipt == nil {
-		return nil
-	}

	// get non-duplicated list of all addresses that emitted logs
	var addresses []ethcommon.Address
```

**ETHERMINT**
```
	if !res.Failed() {
		receipt.Status = ethtypes.ReceiptStatusSuccessful
		// Only call hooks if tx executed successfully.
		if err = k.PostTxProcessing(tmpCtx, msg, receipt); err != nil {
			// If hooks return error, revert the whole tx.
			res.VmError = types.ErrPostTxProcessing.Error()
			k.Logger(ctx).Error("tx post processing failed", "error", err)
                        ...
```

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/fungible/keeper/evm_hooks.go#L31-L33


### **[[ 14 ]]** 
When `PostTxProcessing` I would recommend to use the same protection in `fungible` and `crosschain` when you iterage over logs. Right now crosschain is lacking the nil check (which might be redundant, I didn't check). Moreover, I would `highly recommend` to check the `Removed` field as indicated by the documention and ignore those. 

```
	// The Removed field is true if this log was reverted due to a chain reorganisation.
	// You must pay attention to this field if you receive logs through a filter query.
	Removed bool `json:"removed"`
```

```
        ...

	for _, log := range logs {
+		if log == nil || log.Removed {
+			continue
+		}

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

        ...
```

### **[[ 15 ]]** 
`ProcessZetaSentEvent` lacks any validation for the `DestinationAddress` which could translate in funds loss if sent to invalid address or address(0). I would recommend to use the same logic as in `ProcessZRC20WithdrawalEvent` which is better implementated, which validate the destination address is not empty and valid.

```diff
func (k Keeper) ProcessZetaSentEvent(ctx sdk.Context, event *connectorzevm.ZetaConnectorZEVMZetaSent, emittingContract ethcommon.Address, txOrigin string) error {
	if !k.zetaObserverKeeper.IsInboundEnabled(ctx) {
		return types.ErrNotEnoughPermissions
	}

        ...

	if receiverChain.IsExternalChain() && coreParams.ZetaTokenContractAddress == "" {
		return types.ErrUnableToSendCoinType
	}
-	toAddr := "0x" + hex.EncodeToString(event.DestinationAddress)
+	toAddr, err := receiverChain.EncodeAddress(event.DestinationAddress)
+	if err != nil {
+		return fmt.Errorf("cannot encode address %s: %s", event.DestinationAddress, err.Error())
+	}
+
	senderChain := common.ZetaChain()
	amount := math.NewUintFromBigInt(event.ZetaValueAndGas)

        ...

```


https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/evm_hooks.go#L209


### **[[ 16 ]]** 
I would recommend to following change to not be `sending 0 amount value` accross Zetachain protocol which can happen if the amount of value sent is exactly the same as fees, granted that should be rare, which is why this is a Low severity. `PayGasInZetaAndUpdateCctx`, `PayGasNativeAndUpdateCctx` and `PayGasInERC20AndUpdateCctx` should use `GTE` instead of `GT`.

```diff
	// subtract the withdraw fee from the input amount
-	if outTxGasFee.GT(inputAmount) {
+	if outTxGasFee.GTE(inputAmount) {
		return cosmoserrors.Wrap(types.ErrNotEnoughGas, fmt.Sprintf("outTxGasFee(%s) more than available gas for tx (%s) | Identifiers : %s ",
			outTxGasFee,
			inputAmount,
			cctx.LogIdentifierForCCTX()),
		)
	}
	ctx.Logger().Info("Subtracting amount from inbound tx", "amount", inputAmount.String(), "fee", outTxGasFee.String())
	newAmount := inputAmount.Sub(outTxGasFee)
```

```diff
	// reduce the amount of the outbound tx
-	if feeInZeta.GT(zetaBurnt) {
+	if feeInZeta.GTE(zetaBurnt) {
		return cosmoserrors.Wrap(types.ErrNotEnoughZetaBurnt, fmt.Sprintf("feeInZeta(%s) more than zetaBurnt (%s) | Identifiers : %s ",
			feeInZeta,
			zetaBurnt,
			cctx.LogIdentifierForCCTX()),
		)
	}
```

```diff
	// subtract the withdraw fee from the input amount
-	if math.NewUintFromBigInt(feeInZRC20).GT(inputAmount) {
+	if math.NewUintFromBigInt(feeInZRC20).GTE(inputAmount) {
		return cosmoserrors.Wrap(types.ErrNotEnoughGas, fmt.Sprintf("feeInZRC20(%s) more than available gas for tx (%s) | Identifiers : %s ",
			feeInZRC20,
			inputAmount,
			cctx.LogIdentifierForCCTX()),
		)
	}
	newAmount := inputAmount.Sub(math.NewUintFromBigInt(feeInZRC20))
```

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/gas_payment.go#L109
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/gas_payment.go#L171
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/gas_payment.go#L299



### **[[ 17 ]]** 
I would recommend to verify the receiver chain is supported in `ProcessZRC20WithdrawalEvent`. I understand that the condition is mostly redundant in the moment as that would require `foreignCoin.ForeignChainId` to be invalid somehow (which seem impossible by [updating](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/keeper/msg_server_update_core_params.go#L22-L24)), but just to be safe, it would be more explicit and safer when refactoring the code.

```diff
func (k Keeper) ProcessZRC20WithdrawalEvent(ctx sdk.Context, event *zrc20.ZRC20Withdrawal, emittingContract ethcommon.Address, txOrigin string) error {
	if !k.zetaObserverKeeper.IsInboundEnabled(ctx) {
		return types.ErrNotEnoughPermissions
	}
	ctx.Logger().Info("ZRC20 withdrawal to %s amount %d\n", hex.EncodeToString(event.To), event.Value)
	tss, found := k.GetTSS(ctx)
	if !found {
		return errorsmod.Wrap(types.ErrCannotFindTSSKeys, "ProcessZRC20WithdrawalEvent: cannot be processed without TSS keys")
	}
	foreignCoin, found := k.fungibleKeeper.GetForeignCoins(ctx, event.Raw.Address.Hex())
	if !found {
		return fmt.Errorf("cannot find foreign coin with emittingContract address %s", event.Raw.Address.Hex())
	}

	receiverChain := k.zetaObserverKeeper.GetParams(ctx).GetChainFromChainID(foreignCoin.ForeignChainId)
+	if receiverChain == nil {
+		return zetaObserverTypes.ErrSupportedChains
+	}
	senderChain := common.ZetaChain()
	toAddr, err := receiverChain.EncodeAddress(event.To)
```

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/evm_hooks.go#L126
 
### **[[ 18 ]]** 
There seems to be a divergence in the implementation regarding `DisableInboundOnly` and `IsOutboundEnabled`, which seems to indicate this is a bug.

[DisableInboundOnly](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/keeper/crosschain_flags.go#L54): in case crosschain flag is not found in the store, we fallback setting `IsOutboundEnabled` to true, which is permissive.
[IsOutboundEnabled](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/keeper/crosschain_flags.go#L40): in case crosschain flag is not found in the store, we fallback returning false, which is restrictive.

The proper behavior seems to be with `IsOutboundEnabled`, so `DisableInboundOnly` should probably be aligned.

```diff
func (k Keeper) DisableInboundOnly(ctx sdk.Context) {
-	flags, found := k.GetCrosschainFlags(ctx)
+	flags, _ := k.GetCrosschainFlags(ctx)
-	if !found {
-		flags.IsOutboundEnabled = true
-	}
	flags.IsInboundEnabled = false
	k.SetCrosschainFlags(ctx, flags)
}

func (k Keeper) IsOutboundEnabled(ctx sdk.Context) (found bool) {
	flags, found := k.GetCrosschainFlags(ctx)
	if !found {
		return false
	}
	return flags.IsOutboundEnabled
}
```

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/keeper/crosschain_flags.go#L40
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/keeper/crosschain_flags.go#L54

### **[[ 19 ]]** 
`CleanAddressList`, `UpdateObserverList` and `GetAllObserverMappersForAddress` should add a `break` in their loop.

```diff
func CleanAddressList(addresslist []string, address string) []string {
	index := -1
	for i, addr := range addresslist {
		if addr == address {
			index = i
+                       break
		}
	}
	if index != -1 {
		addresslist = RemoveIndex(addresslist, index)
	}
	return addresslist
}
```

```diff
func UpdateObserverList(list []string, oldObserverAddresss, newObserverAddress string) {
	for i, observer := range list {
		if observer == oldObserverAddresss {
			list[i] = newObserverAddress
+                       break
		}
	}
}
```

```diff
func (k Keeper) GetAllObserverMappersForAddress(ctx sdk.Context, address string) (mappers []*types.ObserverMapper) {
	store := prefix.NewStore(ctx.KVStore(k.storeKey), types.KeyPrefix(types.ObserverMapperKey))
	iterator := sdk.KVStorePrefixIterator(store, []byte{})
	defer iterator.Close()
	for ; iterator.Valid(); iterator.Next() {
		var val types.ObserverMapper
		k.cdc.MustUnmarshal(iterator.Value(), &val)
		addToList := false
		for _, addr := range val.ObserverList {
			if addr == address {
				addToList = true
+                               break
			}
		}
		if addToList {
			mappers = append(mappers, &val)
		}
	}
	return
}
```

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/keeper/hooks.go#L138-L149
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/keeper/msg_server_update_observer.go#L94-L100
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/keeper/observer_mapper.go#L66-L84


### **[[ 20 ]]** 
`GetInboundVoteMsgForZetaSentEvent` should use the variable instead of the doing the computation twice.

```diff
func (ob *EVMChainClient) GetInboundVoteMsgForZetaSentEvent(event *zetaconnector.ZetaConnectorNonEthZetaSent) (types.MsgVoteOnObservedInboundTx, error) {
	ob.logger.ExternalChainWatcher.Info().Msgf("TxBlockNumber %d Transaction Hash: %s Message : %s", event.Raw.BlockNumber, event.Raw.TxHash, event.Message)
	destChain := common.GetChainFromChainID(event.DestinationChainId.Int64())
	if destChain == nil {
		ob.logger.ExternalChainWatcher.Warn().Msgf("chain id not supported  %d", event.DestinationChainId.Int64())
		return types.MsgVoteOnObservedInboundTx{}, fmt.Errorf("chain id not supported  %d", event.DestinationChainId.Int64())
	}
	destAddr := clienttypes.BytesToEthHex(event.DestinationAddress)
	if *destChain != common.ZetaChain() {
		cfgDest, found := ob.cfg.GetEVMConfig(destChain.ChainId)
		if !found {
			return types.MsgVoteOnObservedInboundTx{}, fmt.Errorf("chain id not present in EVMChainConfigs  %d", event.DestinationChainId.Int64())
		}
		if strings.EqualFold(destAddr, cfgDest.ZetaTokenContractAddress) {
			ob.logger.ExternalChainWatcher.Warn().Msgf("potential attack attempt: %s destination address is ZETA token contract address %s", destChain, destAddr)
			return types.MsgVoteOnObservedInboundTx{}, fmt.Errorf("potential attack attempt: %s destination address is ZETA token contract address %s", destChain, destAddr)
		}
	}
	return *GetInBoundVoteMessage(
		event.ZetaTxSenderAddress.Hex(),
		ob.chain.ChainId,
		event.SourceTxOriginAddress.Hex(),
-		clienttypes.BytesToEthHex(event.DestinationAddress),
+               destAddr,
		destChain.ChainId,
		sdkmath.NewUintFromBigInt(event.ZetaValueAndGas),
		base64.StdEncoding.EncodeToString(event.Message),
		event.Raw.TxHash.Hex(),
		event.Raw.BlockNumber,
		event.DestinationGasLimit.Uint64(),
		common.CoinType_Zeta,
		"",
		ob.zetaClient.GetKeys().GetOperatorAddress().String(),
		event.Raw.Index,
	), nil
}
```
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/utils.go#L162


### **[[ 21 ]]** 
There is a `missing nil` check in `AddBlockHeader` handler which will cause the `zetacored` to panic, but seems to recover or at least I was not able to generate a crash, which is why I submit this only as `Low`.

While Observers that broadcast those AddBlockHeader message are being [verified](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/types/messages_add_block_header.go#L55), such that an unknown chain is not possible, there is always the risk of a `malicious Observer` (or `malicious user` that have access to the node machine which could use the CLI to broadcast) to broadcast a `malicious AddBlockHeader message` which would include an `unknown chain` and trigger this panic.

I would recommend to add the missing nil check.

```diff
// AddBlockHeader handles adding a block header to the store, through majority voting of observers
func (k msgServer) AddBlockHeader(goCtx context.Context, msg *types.MsgAddBlockHeader) (*types.MsgAddBlockHeaderResponse, error) {
	ctx := sdk.UnwrapSDKContext(goCtx)

	// check authorization for this chain
	chain := common.GetChainFromChainID(msg.ChainId)
+	if chain == nil {
+		return nil, types.ErrSupportedChains
+	}	
	if ok := k.IsAuthorized(ctx, msg.Creator, chain); !ok {
		return nil, types.ErrNotAuthorizedPolicy
	}


```
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/keeper/msg_server_add_block_header.go#L18-L21


### **[[ 22 ]]** 
`MsgCreateTSSVoter::ValidateBasic` is lacking validations, for example `TssPubkey` and `KeyGenZetaHeight` are not validated at all, and neither [inside the handler itself](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/msg_tss_voter.go#L29). While I understand this message is restricted to validator, I think you should add more validations as follow.

I would also recommend to go over all the `ValidateBasic` functions, the implementation is not consistent overall, like not all the message fields are validated inside their corresponding `ValidateBasic`, some lacking more then others.

```diff
func (msg *MsgCreateTSSVoter) ValidateBasic() error {
	_, err := sdk.AccAddressFromBech32(msg.Creator)
	if err != nil {
		return sdkerrors.Wrapf(sdkerrors.ErrInvalidAddress, "invalid creator address (%s)", err)
	}
+
+	_, err = cosmos.GetPubKeyFromBech32(cosmos.Bech32PubKeyTypeAccPub, msg.TssPubkey)
+	if err != nil {
+		return errorsmod.Wrapf(sdkerrors.ErrInvalidPubKey, "invalid tss pubkey (%s)", err)
+	}

	return nil
}
```

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/types/message_tss_voter.go#L43-L49
