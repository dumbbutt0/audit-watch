# P263 — TARGET_SCREEN (content-safe; existence-only)
Requirement: PUBLIC-findings (scorable) EVM subtle-accounting contest, unused by P253–P262 (scorability > freshness).
| candidate | type | source public | FINDINGS public (git ls-remote refs) | decision |
|---|---|---|---|---|
| **2024-07-benddao** | C4 Solidity lending (borrow/leverage, ERC20+NFT collateral, cross/isolate liquidation, Supply/BorrowIndex, share/redemption, restaking yield; 42 contracts) | YES | **YES (scorable)** | **SELECT** |
| 2024-08-wildcat | credit/lending | YES | YES | reject (protocol-family overlap w/ used wildcat-2023-10) |
| 2024-10-superposition | AMM | YES | YES | reject (Rust/Stylus — toolchain mismatch) |
| 2025-11-merkl / 2025-11-brix-money | rewards / staking | YES | **NO (judging)** | reject (not scorable) |
| 2024-03-revert-lend | lending | YES | YES | reject (contaminated p177/p189/p191) |
DISCLOSED: benddao 2024-07 < Jan-2026 training cutoff ⇒ training-confound (well-known; some awards may be in
training) — accepted per operator guidance (scorability > freshness). No award content fetched pre-reveal.
