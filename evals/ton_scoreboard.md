# TON / FunC recall scoreboard (SEEDED — unmeasured)

> No scored TON contest has been adjudicated yet, so **recall is UNMEASURED**. The `ton-*` mechanism
> classes are SEEDED from the public TON DEX/jetton audit corpus (STON.fi/TONCO/Swap Coffee/PixelSwap/
> FIVA TrailOfBits & Quantstamp reviews) and never count toward Solidity recall. `eval_scoreboard.py`
> `build_language('ton')` overwrites this with real numbers once an `adjudication.json` carries
> `language=ton` records (run the recall lab on a TON answer key).

**Seeded mechanism classes:** 18  |  **Adjudicated TON projects:** 0

## Available recall corpus (KB answer keys, not yet adjudicated)

| Protocol | Findings |
|---|---:|
| STON.fi TON AMM DEX V2 Review | 5 |
| TONCO CLAMM DEX v1.6 | 23 |
| Swap Coffee TON DEX | 7 |
| PixelSwap DEX | 24 |
| FIVA Yield Tokenization Protocol | 14 |

## Seeded ton-* classes

| class | agent section | status |
|---|---|---|
| `ton-jetton-sender-spoof` | ton_sender_auth.md#1 | seeded |
| `ton-recipient-substitution` | ton_sender_auth.md#3 | seeded |
| `ton-pool-lock-bypass` | ton_sender_auth.md#5 | seeded |
| `ton-async-state-desync` | ton_message_flow.md#1 | seeded |
| `ton-lp-account-race` | ton_message_flow.md#2 | seeded |
| `ton-message-replay-reorder` | ton_message_flow.md#5 | seeded |
| `ton-bounce-ignored` | ton_bounce_handling.md#1 | seeded |
| `ton-bounce-no-rollback` | ton_bounce_handling.md#2 | seeded |
| `ton-bounce-rate-desync` | ton_bounce_handling.md#5 | seeded |
| `ton-reserve-mode-drain` | ton_carry_value.md#2 | seeded |
| `ton-gas-stranding` | ton_carry_value.md#1 | seeded |
| `ton-value-check-missing` | ton_carry_value.md#4 | seeded |
| `ton-multihop-cell-misparse` | ton_cell_parsing.md#1 | seeded |
| `ton-slice-trailing-data` | ton_cell_parsing.md#2 | seeded |
| `ton-cell-depth-dos` | ton_cell_parsing.md#4 | seeded |
| `ton-math-overflow` | ton_arithmetic.md#1 | seeded |
| `ton-rounding-direction` | ton_arithmetic.md#2 | seeded |
| `ton-convergence` | ton_arithmetic.md#3 | seeded |
