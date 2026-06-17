[L-1] Validating initializationCode Length and Eliminating Redundant Code
Validating the length of initializationCode is essential, and the computation of targetDeploymentAddress is unnecessary at this stage; it can be checked after a successful deployment or just remove it. The following is the final code with all optimization:
```solidity
File: repos/protocol-contracts/evm/tools/ImmutableCreate2Factory.sol
 function safeCreate2Internal(
        bytes32 salt,
        bytes memory initializationCode
    ) internal returns (address deploymentAddress) {
        require(initializationCode.length != 0, "Bytecode length is zero");
        // using inline assembly: load data and length of data, then call CREATE2.
        assembly {
            deploymentAddress := create2(
                callvalue, // wei sent with current call
                // Actual code starts after skipping the first 32 bytes
                add(initializationCode, 0x20),
                mload(initializationCode), // Load the size of code contained in the first 32 bytes
                salt // Salt from function arguments
            )
        }
        require(deploymentAddress != address(0), "Failed on deploy");
        // ensure that a contract hasn't been previously deployed to target address.
        // this require also unnecessary
        require(!_deployed[deploymentAddress], "Contract deployed");
        // record the deployment of the contract to prevent redeploys.
        _deployed[deploymentAddress] = true;
    }

```
For the above code require: 
```require(!_deployed[deploymentAddress], "Contract deployed"); ```
is also unnecessary, as it will revert when deploying to the same address. I suggest removing it too.

[L-2] WZETA transferFrom does not follow spec
There are two conditions that do not adhere to the specifications.
1. If the message sender is the source of a transferFrom call, the sender’s allowance will not
be considered, and the transfer will initiate immediately. This breaks invariants expected of
transferFrom.
Traditionally, the transferFrom method moves tokens from one account to another,
provided the source account has approved the sender to send such an amount using the
ERC20 method approve. However, the transferFrom function in WETH9’s ERC20 token
does not require approval if the sender is the source of the account.

2. If the message sender is not the source of a transferFrom call, and the allowance is set to the maximum value of uint256, the sender's allowance will not be subtracted. Consequently, the transfer will be initiated immediately. This violation of the expected invariants of transferFrom can lead to issues.

```solidity
File: repos/protocol-contracts/contracts/zevm/WZETA.sol
 function transferFrom(address src, address dst, uint wad) public returns (bool) {
        require(balanceOf[src] >= wad);

        if (src != msg.sender && allowance[src][msg.sender] != uint(-1)) {
            require(allowance[src][msg.sender] >= wad);
            allowance[src][msg.sender] -= wad;
        }

        balanceOf[src] -= wad;
        balanceOf[dst] += wad;

        Transfer(src, dst, wad);

        return true;
    }

```
Exploit Scenario
Alice sends a transaction that invokes transferFrom with her own address as the source
address, assuming it will fail if no approval was set beforehand. Instead, the transfer
succeeds, and Alice’s funds are lost.

Recommendation
Short term, document this contract’s non-standard behavior and verify that all code
interfacing with it does not break due to this behavior.

Long term, use Echidna to review the ERC20 specification and verify your contracts meet
the standard. When interfacing with external ERC20 tokens, be wary of popular tokens that
do not properly implement the standard (e.g., many tokens do not include return values for
approve, transfer, transferFrom, etc.).

[L-3] Compile error in macos
go version: go1.20.4 darwin/arm64
os: macos

https://github.com/code-423n4/2023-11-zetachain/tree/main/repos/node

run go mod tidy in this repo, the following is err:

go: github.com/zeta-chain/keystone/keys@v0.0.0-20231105174229-903bc9405da2 requires
        github.com/tendermint/tendermint@v0.34.12 requires
        github.com/moby/buildkit@v0.10.4 requires
        github.com/tonistiigi/go-actions-cache@v0.0.0-20220404170428-0bdeb6e1eac7 requires
        github.com/moby/buildkit@v0.8.1 requires
        github.com/containerd/stargz-snapshotter@v0.0.0-20201027054423-3a04e4c2c116 requires
        github.com/Microsoft/hcsshim/test@v0.0.0-20200826032352-301c83a30e7c requires
        github.com/docker/distribution@v0.0.0-20190905152932-14b96e55d84c requires
        github.com/mitchellh/osext@v0.0.0-20151018003038-5e2d6d41470f: invalid version: git ls-remote -q origin in /Users/xx/xx/xx/mod/cache/vcs/94ed57c5b21c953d93b47487113db43a5c9b69fd990329ec70dc77348c4dd443: exit status 128:
        remote: Repository not found.
        fatal: repository 'https://github.com/mitchellh/osext/' not found
When I build Zeta for the first time, this error occurs. If it's not the first time build it, this error may not appear because the cache already has the 'osext' repo.

[L-4] Enhancing Flexibility for ChainName
The ChainName enum can be made flexible by structuring it as an array. It should allow for dynamic addition and removal of chains, a functionality that can be granted to administrators. This design is particularly important for EVM chains, anticipating the potential addition of more supported chains in case of future forks.
```solidity
File: repos/node/proto/common/common.proto
 enum ChainName {
  option (gogoproto.goproto_enum_stringer) = true;
  empty = 0;

  eth_mainnet = 1;
  zeta_mainnet = 2;
  btc_mainnet = 3;
  polygon_mainnet = 4;
  bsc_mainnet = 5;
  //  Testnet
  goerli_testnet = 6;
  mumbai_testnet = 7;
  ganache_testnet = 8;
  baobab_testnet = 9;
  bsc_testnet = 10;
  zeta_testnet = 11;
  btc_testnet = 12;
  //  LocalNet
  //  zeta_localnet = 13;
  goerli_localnet = 14;
  btc_regtest = 15;
  // Athens
  //  zeta_athensnet=15;
}

```

[L-5] Caution: Managing the Order of Writes and Reads in KV Database
For KV databases, the order of reads and writes is often inconsistent. When dealing with scenarios that require strong ordering for serialization and deserialization, it is necessary to use additional storage to establish the order. Please carefully examine whether this situation exists, especially for the storage of critical data such as ballots, observers, and more. It is particularly important to document this when providing access to external interfaces or third-party usage.
