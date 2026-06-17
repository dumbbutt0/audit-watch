### [Low] Incorrect median gas price

### `medianOfArray` not correct for even list of elements

https://github.com/zeta-chain/node/blob/main/x/crosschain/keeper/keeper_gas_price.go#L194-L204

If the amount of values is even, we should divide the two elements on the middle by two in order to calculate the average between the two values which are located at the middle.

This function is only used for gas calculation, where the median gas is taken from a list of gas prices.

Meaning that the `MedianIndex` cannot really be calculated in the case of an even array, which is because in this case we need to calculate the average. So it may be more advisable to calculate the value directly rather than storing the index in the array.

Since the `OutboundTxGasPrice` of a CCTX is determined by this gas station, the gas will be under estimated and may lead to consensus disagreements if other clients are implemented in the future.

Most of the functions dealing with gas are also relying on this parameter, so it is quite important. For instance, any call to `GetMedianGasPriceInUint` which is the case for TSS migrations, CCTX transactions, and so on.

### [Low] Nil pointer dereference if the TSS was removed

In the function that is called in order for the validator to vote on an inbound tx, the non-existence of the current TSS is not checked and can result in a panic if the keys are not stored https://github.com/zeta-chain/node/blob/main/x/crosschain/keeper/keeper_cross_chain_tx_vote_outbound_tx.go#L138

The issue may occur in the case of a failed TSS migration, or in a manual removal of the TSS.
If there is a bug in the migration process and that the TSS is not existent anymore in the node memory, then a significant portion of the validators may not be able to vote because of an infinite loop since the panic is recovered because it’s behind the grpc client.

There is a very similar issue in the inbound side https://github.com/zeta-chain/node/blob/main/x/crosschain/keeper/keeper_cross_chain_tx_vote_inbound_tx.go#L74-L78 since the `tssPub` will stay empty if the tss was not found in memory, because it is not checked. This may lead to consensus failures.

### [Low] No duplicate check when updating the observer address

Some observer updates can be made through the UpdateObserver message.
The two reasons may either be that the current observer is tombstoned and want to migrate to a new address. The first one is that the observer is tombstoned, and the second one is an admin update and thus requires that the message originates from the admin.

The issue is that the newly added observer address is not checked for duplicates in the list of observers which may weaken the voting process since this is going to add observers which may not be removable. Note that observers cannot really be removed, but they can be “tombstoned” which will greatly remove their rights.

Fortunately, the logic of the ballot make it such that the first-seen observer in the list is going to ignore any later observer  with the `GetVoterIndex` function. Since Golang lists are deterministic, we should not be able to get another index from this function and be able to vote twice for instance.

But, this will still have an impact on ballots, since the voters amount is determined by the length of the voters list, which may contains these duplicates if the `NewObserverAddress` already exists.

In order to fix that, add something like:

```solidity
if k.IsObserverPresentInMappers(ctx, msg.NewObserverAddress, chain) {
		// return nil, errorsmod.Wrap(types.ErrNotAuthorized, fmt.Sprintf("Observer address is not authorized for chain : %s", chain.String()))
}
```

### [Low] Tombstoned observer can resurrect itself without restriction

When triggering the `UpdateObserver` function, the reason may either be a tombstoned observer, or an admin update. both of them are quite descriptive, but the weird part is that in order to get out of a tombstoned state, an observer can just update his own address with this message while being tombstoned is quite a restrictive behavior, since this state will not authorize the validator to execute some key operations such as voting on observed transactions or manipulate the block headers.

There should probably be some kind of consensus where people should agree to “un-tombstone” a specific observer if they deserve to, while the admin update can be triggered by the admin only which sounds like a more sane idea for the protocol.

The second issue is that if a tombstoned observer is updated, the tombstoned state of the old address is not cleaned and if this validator wants to retrieve his old address then they could but it would still be tombstoned.

### [Low] Strange logic for gas increases

When making a pending cctx go through, the `CheckAndUpdateCctxGasPrice` function is called in order to account for the gas increase to pay for the network usage and disincentivize heavy load.

https://github.com/zeta-chain/node/blob/main/x/crosschain/keeper/abci.go#L100-L102

There is a weird logic which doesn’t seem to stick with that idea:

```solidity
if newGasPrice.GT(limit) {
	return math.ZeroUint(), math.ZeroUint(), nil
}
```

If the `newGasPrice` is above the set limit, then we should just skip this cctx. That may be intended, but why don’t we return the increase in gas with `limit - currentGasPrice` so it’s capped in some way ? Later on, if the network agrees on that this limit is too low then they may lower it a bit.

### [Low] Unsafe Casting Can DoS The Chain

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/ab97a27b-8903-4eae-8e59-0c541f4685a0/5a83fcec-ed22-455a-a71c-ee1f8dbc19fa/Untitled.png)

A truncation on the `confirmedBlockNum` can cause a denial of service when the block is higher than 2**63. 

Because the value of `toBlock` is going to be **negative** the necessary confirmation to proceed will be never reach and will fail forever.

The current severity is classified as low because the likehood to arrived to the block 2**63 is not important.

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/ab97a27b-8903-4eae-8e59-0c541f4685a0/33c16808-b55b-4a2c-9d81-7be2b2fda44c/Untitled.png)

### [Low] Actual ballot threshold is slightly less than expected

The default param for the threshold for tx message voting is defined in `x/observer/types/params.go` https://github.com/zeta-chain/node/blob/develop/x/observer/types/params.go#L30 with a value of “0.66”. The issue is that it is 

### [Low] Forbidden increaseAllowance and decreaseAllowance

In `x/crosschain/keeper/evm_hooks.go`, in the function `PostTxProcessing`

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/ab97a27b-8903-4eae-8e59-0c541f4685a0/8fe3d6cb-3639-42ca-8bd8-4a585479ff2d/Untitled.png)

Those two methods are blacklisted. They are considered more safe than `approve` because they don’t allow race conditions. Protocols are still using it: https://www.codeslaw.app/search?chain=ethereum&q=.increaseAllowance&sort=deployment-desc

### [Low] ZRC20 tokens sent as fees to the ERC20Custody are locked

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/ab97a27b-8903-4eae-8e59-0c541f4685a0/112a7785-7ffc-468f-ab98-c9116a15b070/Untitled.png)

If the `zetaFee` is set to 0, there is no fee paid to the node operators.

### [Low] IsEVMChain returns `false` for Zetachain

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/ab97a27b-8903-4eae-8e59-0c541f4685a0/9ce74417-34be-4a04-b089-b0fff89c94db/Untitled.png)

The `ZetaChain` chain ID is not included in these, so the `IsEVMChain` will return `false` for `7000` which is the Chain ID of ZetaChain.

It may be good to create a new function that does

```go
func IsEVMOrZetaChain(chainID int64) bool {
	return chainID == 7000 || // ZetaChain
		IsEVMChain(chainID)
}
```

in order to prevent the following (low severity) issues:

`GetZetaAddress()` which will always return an empty address

Cannot debug `get-ballot-from-intx` for Zetachain

### [Low] The error handling on the Prometheus gauge is too strict

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/ab97a27b-8903-4eae-8e59-0c541f4685a0/56def952-ebfb-4d64-8576-b6097f299934/Untitled.png)

If the gauge is not present in the prometheus dashboard, then the function `startSendScheduler` is not going to scan the CCTX. This should just emit a log because there is no dependency on Prometheus, it is used as a visualizer which should not block the cctx pickup.

### [Low] Function could panic

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/ab97a27b-8903-4eae-8e59-0c541f4685a0/a05fba2e-83f4-4e34-8347-bb24cf540a32/Untitled.png)

`MustNewDecFromStr` is a function that converts a decimal number as a string into the `Dec` type.

`DurationFactorConstant` is known to be an irrational number and this function will panic if the input has more than 18 decimals, which is dictated by the `PRECISION` constant in the library.

### [Low] `DurationFactorConstant` is not correct according to docs

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/ab97a27b-8903-4eae-8e59-0c541f4685a0/6eb220db-051b-4bd2-9227-e8aa3315d40e/Untitled.png)

In the code comments, it is said that this constant is taken from the evaluation of `log(1 + 0.01 / 12)` but this is not correct.

In reality, `log(1 + (0.02 / 12)) = 0.00072322161`

### [Low] 100% of the validators must agree for a TSS migration

An astonishing amount of 100% of the validators must agree in order to initiate a migration of the TSS address.

This seems to be an highly unrealistic scenario, since any validator that would like to slow down the development of the chain could just deny any TSS migration. The issue is more impactful if the TSS address is highly desired, for instance in a panic environment such as if supposedly all the keys of the MPC are leaked.

### [Info] Code Not Reachable Due To Incorrect `nil` handling

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/ab97a27b-8903-4eae-8e59-0c541f4685a0/13e10d59-0b25-4bb0-8851-767be25cadf0/Untitled.png)

As the first `chain == nil` will **return** the second one will be useless and never used.
This one can be safely deleted to improve the code readibility. 

Also the code here has the same issue: 

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/ab97a27b-8903-4eae-8e59-0c541f4685a0/e47b5979-c9a6-424d-8115-7c591bd1e1c9/Untitled.png)

The if are the exact same making the code unreachable.

also there 

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/ab97a27b-8903-4eae-8e59-0c541f4685a0/76462ac2-cdab-46fc-ac25-2ad160bbc949/Untitled.png)

### [Info] Dangerous constant

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/ab97a27b-8903-4eae-8e59-0c541f4685a0/497e6357-4cfe-4083-b708-1f0c1072619c/Untitled.png)

Note that this constant is not used

### [Info] Hard-to-read code

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/ab97a27b-8903-4eae-8e59-0c541f4685a0/35f7e0f5-6232-4b7b-82d0-2ccd4cb0ff82/Untitled.png)

Use an `else` clause, because the cases are exhausted. If you really need the code to be forward-compatible, write an `else { panic("unreachable") }`

### [Info] backOff is not retrying every x2

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/ab97a27b-8903-4eae-8e59-0c541f4685a0/6e5bb410-32e9-41d2-8095-fc43292e465e/Untitled.png)

### [Info] Add debug help

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/ab97a27b-8903-4eae-8e59-0c541f4685a0/3b91f0db-0947-4717-a3d8-e341801d1f75/Untitled.png)

Add the `msg.ChainId` as a parameter in the error message to help in case of debugging issues.