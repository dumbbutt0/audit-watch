## `Digest` Functions Are Not Guaranteed to Be Deterministic and Can Lead to Collisions

Most of the messages' `Digest` functions, used to uniquely identify a message, make use of the protobuf message's String method before hashing. In the generated protobuf code, this is defined as:

```go
func (m *MsgUpdateObserver) String() string { return proto.CompactTextString(m) }
```

This is not guaranteed to deterministic! I'm reporting this as low because I did not have the time to look deeeper into this or look for a way to exploit it in the codebase. It is dangerous to make critical operations that require determinism depend on this.

But, besides protobuf itself not guaranteeing this to be deterministic accross versions/binaries and the fact this is generated code not tightly controlled by the project, this can come to be a self-made footgun as it is now.

For example, suppose there are two different messages with different privilege restrictions to access them:

```go
package main

import (
        fmt "fmt"

        "github.com/golang/protobuf/proto"
)

// Everyone can send this
type PublicMsg struct {
        Creator string `protobuf:"bytes,1,opt,name=creator,proto3" json:"creator,omitempty"`
        Message string `protobuf:"bytes,2,opt,name=vote,json=vote,proto3" json:"vote,omitempty"`
        Command string `protobuf:"bytes,3,opt,name=cmd,json=cmd,proto3" json:"cmd,omitempty"`
}

// Proto interface requirement
func (*PublicMsg) ProtoMessage()    {}
func (m *PublicMsg) String() string { return proto.CompactTextString(m) }
func (m *PublicMsg) Reset()         { *m = PublicMsg{} }

// Only admins can vote on this
type AdminCmd struct {
        Creator string `protobuf:"bytes,1,opt,name=creator,proto3" json:"creator,omitempty"`
        Command string `protobuf:"bytes,2,opt,name=cmd,json=cmd,proto3" json:"cmd,omitempty"`
}

// Proto interface requirement
func (*AdminCmd) ProtoMessage()    {}
func (m *AdminCmd) String() string { return proto.CompactTextString(m) }
func (m *AdminCmd) Reset()         { *m = AdminCmd{} }

func main() {
        pubMsg := &PublicMsg{
                Creator: "address",
                // Omit Message, default value is used.
                Command: "AllBasesAreBelongToUs",
        }

        adminCmd := &AdminCmd{
                Creator: "address",
                Command: "AllBasesAreBelongToUs",
        }

        fmt.Println(pubMsg.String())
        fmt.Println(adminCmd.String())
        fmt.Println("Both are equal:", pubMsg.String() == adminCmd.String())
}
```

Running the code above will produce the following:

```
creator:"address" cmd:"AllBasesAreBelongToUs" 
creator:"address" cmd:"AllBasesAreBelongToUs" 
Both are equal: true
```

In this codebase, ballots unique indices are generated with the `Digest` function. For(and non-determinism?)example:

```go
index := msg.Digest()
```

And, as you can see, the generated `String` method ignores `omitempty` fields. Just by omitting or using the default value for a field causes a collision in the `String` results for these different messages. In a scenario similar to how ZetaChain uses this method, a public user message with some optional commands coud be crafted to have the same hash digest as an admin command. It could also be a collision with required fields with the same name, etc. This is not to say that not using `omitempty` or different field names makes it a good idea. I'm showing a very obvious example to illustrate the concept, but it is not hard to imagine how more complex implementations could be made vulnerable.

This is a very dangerous pattern if used how it is being used. The `String` method should just be used for showing non-critical data to users, and nothing else. A tightly deterministic solution versioned in the codebase (not generated code) must be implemented for a critical operation like this.

## Policy Type Group 2 Can Use Old TSS Pubkeys

With the current logic, `Group2` Admins can choose to use old, "revoked" TSS Pubkeys. It just loops through all TSS keys, looking for a TSS Pubkey that matches `msg.TssPubkey`, and simply uses it if found. This This may be dangerous and cause problems if a mistake happens.

* https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/msg_tss_voter.go#L117C1-L130C2
```go
func (k msgServer) UpdateTssAddress(goCtx context.Context, msg *types.MsgUpdateTssAddress) (*types.MsgUpdateTssAddressResponse, error) {
    // ... SNIP ...
    tss, ok := k.CheckIfTssPubkeyHasBeenGenerated(ctx, msg.TssPubkey)
	if !ok {
		return nil, errorsmod.Wrap(types.ErrUnableToUpdateTss, "tss pubkey has not been generated")
	}
	k.SetTssAndUpdateNonce(ctx, tss)
```

Consider implementing some sort of tracking method for "revoked" or inutilised keys so there can be a check here.

## Bitcoin Static PoW Check

`CheckProofOfWork` is passed a static `PowLimit` parameter. That static `PowLimit` is the maximum allowed PoW, it is, the easiest value allowed. This does not really checks if the Proof-of-Work is valid in the current state:

* https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/common/headers.go#L161C1-L164C3
```go
	err = blockchain.CheckProofOfWork(liteBlock, chainParams.PowLimit)
	if err != nil {
		return fmt.Errorf("proof-of-work verification failed (%s)", err)
	}
```

## Too Few Confirmations for Critical Operations

Critical operations depends on too few confirmations. For example:

* https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/types/core_params_mainnet.go#L16C1-L54C6
```go
				ConfirmationCount:           14,
				// ... SNIP ...
				ConfirmationCount:           2,
```

These confirmation counts may be fine for user clients or less critical software. But for a project like ZetaChain, where value will move accross a diverse set of connected chains, moving these values in a terminal way with only these confirmation counts is highly risky. I recommend a serious research to decide what these values should be for the acceptable risk of the project, but definetely not values this low.

## Bitcoin Client Useless Resource Spent on Block Loop

For each transaction in a block the `bitcoin_client` prints all `vout`s for every transactions without requiring any testing or debug flags, always. This is not recommended for production as will waste lots of resources and delay the client:

* https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/bitcoin_client.go#L357C1-L365C4
```go
		// print some debug information
		if len(res.Block.Tx) > 1 {
			for idx, tx := range res.Block.Tx {
				ob.logger.WatchInTx.Debug().Msgf("BTC InTX |  %d: %s\n", idx, tx.Txid)
				for vidx, vout := range tx.Vout {
					ob.logger.WatchInTx.Debug().Msgf("vout %d \n value: %v\n scriptPubKey: %v\n", vidx, vout.Value, vout.ScriptPubKey.Hex)
				}
			}
		}
```

## Bitcoin Client is Vulnerable to Leaf-Node Weakness

The Bitcoin Client implemented in `bitcoin_client.go`, that is a fork of Summa bitcoin-spv is vulnerable to Leaf-Node Weakness. You can read more about this [here](https://bitslog.com/2018/06/09/leaf-node-weakness-in-bitcoin-merkle-tree-design/) and [here](https://bitcoin.stackexchange.com/questions/76121/how-is-the-leaf-node-weakness-in-merkle-trees-exploitable). This is basically a way to fooling SPV verification to interpret maliciously crafted transactions as inner nodes. I think this attack is too costly to the possible gains of exploiting how the SPV verification is being used here. But beware about using this code for critical operations as the mostly used SPV implementations and chain projects that neeed this kind of verification (e.g., RootStock, Blockstream Elements sidechain) are implementing mitigations to this vulnerability.

Some of these mitigations include:##
* Forbidding 64-bytes transactions, as these are non-standard and will probably only be crafted to perform such attack;
* Be strict about the merkle proof size, according to number of transactions and the consequent tree depth.

`bitcoin_client.go`:
* https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/common/bitcoin/bitcoin_spv.go

## nosec G701

The code is full of comments like this:

```go
// #nosec G701 always in range
```

There are safer patterns than casting integers hoping the expectations are met. This not how critical software should be deal with this. There are ways to safely cast different number types with defensive patterns.

My recommendation is that these patterns are researched and the ones that best meet the software needs are applied, so these `#nosec` comments can be removed from the codebase.

## Unchecked `nil`

The Message Server's function `AddBlockHeader` does not check for the possible `nil` return from `common.GetChainFromChainID(msg.ChainId)` and tries to dereference it, causing a `panic`.

* https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/keeper/msg_server_add_block_header.go#L18C1-L21C3
```go
	chain := common.GetChainFromChainID(msg.ChainId)
	if ok := k.IsAuthorized(ctx, msg.Creator, chain); !ok {
		return nil, types.ErrNotAuthorizedPolicy
	}
```

The call to `isAuthorized`, before any authorization is possible, sends `chain` to `GetObserverMapperIndex`.

* https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/oobserver/keeper/observer_mapper.go#L45
```go
	index := GetObserverMapperIndex(chain)
```

`GetObserverMapperIndex` then tries to dereference it, causing a `panic`:

* https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/keeper/observer_mapper.go#L15C1-L17C2
```go
func GetObserverMapperIndex(chain *common.Chain) string {
	return fmt.Sprintf("%d", chain.ChainId)
}
```

This is reported as a low because the `panic` is handled by the default recovery middleware, but this is not good to depend or spend resources on this.

As you may have noticed, this is similar to what was found in the June 30, 2023 Zellic's report, although it was then spotted in other parts of the project. So this should be encoded and enforced by some sort of Variant Analysis tool or similar in order to further avoid new occurrences of this same vulnerable pattern.

## Same Default Address for Both Admin Groups

Both admin groups, thave have very different security models and privileges, have the same default address:

* https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/types/params.go#L37-L48
```go
func DefaultAdminPolicy() []*Admin_Policy {
	return []*Admin_Policy{
		{
			PolicyType: Policy_Type_group1,
			Address:    GroupID1Address,
		},
		{
			PolicyType: Policy_Type_group2,
			Address:    GroupID1Address,
		},
	}
}
```

This is reported as a low because it seems to be intended and can be changed with a genesis state file. Nevertheless, I think that is insecure and a good road to end up with these equal addresses in some nodes' production environment due to some error along the way. Consider forcing the user to have it configured and loaded from this configuration instead of using repeated fixed values.

As a side note, for some reason, the smoketests `genesis.json` uses the same address for both admin groups.

```bash
# cd into 2023-11-zetachain/repos/node
$ make start-smoketest && sleep 60 && docker exec -it zetacore0 zetacored query observer params
# `sleep 60` is used just to wait a bit for the node to be ready to answer the query
# ... SNIP...
params:
  admin_policy:
  - address: zeta1srsq755t654agc0grpxj4y3w0znktrpr9tcdgk
    policy_type: group1
  - address: zeta1srsq755t654agc0grpxj4y3w0znktrpr9tcdgk
    policy_type: group2
# ... SNIP ...
```

These are tests, but I think it is worth pointing since this can lead to a bad practice that will eventually result in a dangerous mistake.

## `x/crosschain/keeper/keeper_gas_price.go`'s `GasPriceVoter` Repeated If Condition

Unnecessarily repeated if condition:

* https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_gas_price.go#L129C1-L137C3
```c++
	if chain == nil {
		return nil, observertypes.ErrSupportedChains
	}
	// ... SNIP ...
	if chain == nil {
		return nil, sdkerrors.Wrap(types.ErrUnsupportedChain, fmt.Sprintf("ChainID : %d ", msg.ChainId))
	}
```
