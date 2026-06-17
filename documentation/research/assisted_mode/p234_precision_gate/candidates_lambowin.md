# P234 blind candidate artifact — Lambowin (router/launchpad)

Subject: `audits/lambowin-2024-12-fresh` (vETH virtual-liquidity launchpad + swap router + Uniswap rebalance).
Blind Sonnet deep_trace pass (real recall instruments: deep_trace.md + logic/economic_attack/reentrancy/access_control/arithmetic/dos agents + griefing_dos/token_standard lenses). Report/output/answer-key files NOT opened. Tally: 12 — HIGH 5 · MED 4 · LOW 3 · NOISE 0.

| id | title | class | contract | conf | signal | impact / attacker |
|---|---|---|---|---|---|---|
| LAMBO-01 | cashIn mints `msg.value`(=0) not `amount` on ERC20 path → deposited ERC20 locked | accounting/invariant | VirtualToken | Confirmed | HIGH | High / conditional (non-native VirtualToken) |
| LAMBO-02 | rebalance decodes `amountOut` but passes `amountOutMin=0` to both V3 legs → MEV sandwich | economic | LamboRebalanceOnUniwap | Confirmed | HIGH | High / permissionless (MEV) |
| LAMBO-03 | owner fee `call` before swap; reverting owner DoSes all buys | dos/routing | LamboVEthRouter | High | HIGH | High / privileged |
| LAMBO-04 | 1-wei ETH retained per overpaying buy; no rescue | accounting/arith | LamboVEthRouter | Confirmed | MED | Low-Med / permissionless |
| LAMBO-05 | rebalance() permissionless (no onlyOwner) | access-control/dos | LamboRebalanceOnUniwap | Confirmed | MED | Med / permissionless |
| LAMBO-06 | swaps lack deadline; stale-reserve amountYOut | economic/routing | LamboVEthRouter | Confirmed | MED | Med / permissionless |
| LAMBO-07 | createLaunchPadAndInitialBuy initial buy minReturn=0 → MEV | economic | LamboVEthRouter | Confirmed | HIGH | High / permissionless (MEV) |
| LAMBO-08 | `value + _debt[from]` checked-add could panic at impossible debt | arith/dos | VirtualToken | Speculative | LOW | Low / conditional (impossible) |
| LAMBO-09 | sell-path owner fee `call` w/ require; reverting owner DoSes sells | dos/routing | LamboVEthRouter | High | HIGH | High / privileged |
| LAMBO-10 | rebalance `balanceAfter-balanceBefore` underflow panic under MEV loss → DoS | arith/economic | LamboRebalanceOnUniwap | High | HIGH | High / permissionless (MEV) |
| LAMBO-11 | LamboToken.initialize() public, no initializer modifier (impl initializable) | access-control | LamboToken | Confirmed | MED | Low-Med / permissionless |
| LAMBO-12 | no ETH/ERC20 rescue; dust accumulates | dos | LamboVEthRouter | Confirmed | LOW | Low / permissionless |
