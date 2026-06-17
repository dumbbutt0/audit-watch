# Contracts are not deployed to all chains that supposed to be

## Links to affected code

[https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/README.md?plain=1#L131](https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/README.md?plain=1#L131)
[https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/deploy/SystemDeploy.s.sol#L22-L26](https://github.com/code-423n4/2024-10-kleidi/blob/ab89bcb443249e1524496b694ddb19e298dca799/src/deploy/SystemDeploy.s.sol#L22-L26)

## Impact

Contracts are not deployed to all chains that supposed to be

## Proof of Concept

Accroding to contest README, the chains the protocol will be deployed on are Arbitrum, Ethereum, Optimism, and Base. But in SystemDeploy.s.sol, it only deploys on Ethereum mainnet, Base mainnet, Base Sepolia Testnet, and Optimism Sepolia Testnet.

```solidity
contract SystemDeploy is MultisigProposal {
    bytes32 public salt =
        0x0000000000000000000000000000000000000000000000000000000000003afe;

    constructor() {
        uint256[] memory chainIds = new uint256[](4);
@>      chainIds[0] = 1; // Ethereum mainnet 
@>      chainIds[1] = 8453; // Base mainnet
@>      chainIds[2] = 84532; // Base Sepolia Testnet
@>      chainIds[3] = 11155420; // OP Sepolia Testnet
        addresses = new Addresses("./addresses", chainIds);
    }
```

## Tools Used

Manual Review

## Recommended Mitigation Steps

Add Arbitrum mainnet and Optimism mainnet at `chainIds` so that it can deploy at all chains.