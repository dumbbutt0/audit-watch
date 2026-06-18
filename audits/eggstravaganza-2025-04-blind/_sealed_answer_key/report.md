# Eggstravaganza (CodeHawks 2025-04) — AWARDED FINDINGS (revealed post-blind-pass)

Counts confirmed from the results page: High=2, Medium=4, Low=4. Titles deduped from the public
submissions list (https://codehawks.cyfrin.io/c/2025-04-eggstravaganza/submissions); the orchestrator
stayed BLIND on titles until after the cold pass (contest was sourced by the randomness pattern in
EggHuntGame.sol, not by reading the answer key). The exact Medium awarded split is the best
reconstruction from the clustered public submissions.

## High Risk Findings

- H-01 | Weak / predictable on-chain randomness in `searchForEgg` — `random = keccak256(block.timestamp, block.prevrandao, msg.sender, eggCounter) % 100` gates the egg mint, so a caller (esp. via a wrapper contract that reverts on a miss) predicts/grinds the draw to mint egg NFTs at will. (Dominant submission cluster: "Insecure/Weak Randomness in searchForEgg", "On-Chain Randomness Exploit", "Random Number Manipulation".)

- H-02 | Missing access control / frontrun on `EggVault.depositEgg` — `depositEgg(tokenId, depositor)` is public and records the caller-supplied `depositor` after only checking the vault owns the NFT, so anyone can claim deposit rights over an egg NFT held by the vault (e.g. by frontrunning the real depositor) and `withdrawEgg` to steal it. (Submissions: "Anyone can steal EggNFTs by frontrunning depositEgg()", "Missing Access Control on EggVault.depositEgg", "Missing Authorization in depositEgg()".)

## Medium Risk Findings

- M-01 | `setEggNFT` / uninitialized EggVault NFT reference can corrupt game/custody state — the owner-set NFT reference can be (re)pointed or left uninitialized, breaking deposits/withdrawals. (Submissions: "Calling setEggNFT() will corrupt the entire game state", "Uninitialized EggVault NFT Reference".)
- M-02 | Owner can set `eggFindThreshold` to 0 (or 100) — privileged manipulation of find odds. (Submission: "Owner shouldn't be able to set the eggFindThreshold to 0".)
- M-03 | Reentrancy risk in `EggVault.withdrawEgg` / `depositEggToVault`. (Submissions: "Reentrancy Risk in EggVault.withdrawEgg", "Reentrancy Risk in depositEggToVault()".)
- M-04 | Unsafe NFT minting in `EggstravaganzaNFT.mintEgg` (`_mint` not `_safeMint`) / eggsFound counter not reset between games. (Submissions: "Unsafe NFT Minting", "Eggs found counter is not reset between games".)
