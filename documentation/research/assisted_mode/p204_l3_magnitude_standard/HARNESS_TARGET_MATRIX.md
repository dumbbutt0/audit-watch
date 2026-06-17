# P204 — harness target matrix (pre-registered)

| field | H-01 (positive) | M-03 (negative) | decent-06 (false-High) | decent-12 (false-High) |
|---|---|---|---|---|
| mechanism | DcntEth.setRouter public → arbitrary mint/burn | UTB.receiveFromBridge missing AC | UniSwapper.swapNoPath drain | DecentEthRouter redeem double-withdrawal |
| v1/v2 label | HIGH_CONFIRMED | HIGH_CONFIRMED (over-confirmed) | HIGH_CONFIRMED (unawarded) | HIGH_CONFIRMED (unawarded) |
| expected L3 | HIGH (material mint realized) | DEMOTE (no material theft) | DEMOTE / NEEDS_HARNESS | NEEDS_HARNESS (no source-valid path) |
| contracts | real DcntEth | real UTB + real UTBExecutor | real UniSwapper | real DecentEthRouter+DcntEth+WETH |
| mocks | OFTV2 base (ext dep) | solmate Owned, forge-std IERC20, honest swapper, MockERC20 | Owned, IERC20, IV3SwapRouter, MockERC20 | (not built — see below) |
| attacker setup | EOA, no role | EOA, no role; own funds only | EOA, own junk token | EOA |
| victim/protocol setup | legit deployer/owner; legit router set | victim approves UTB; UTB optional treasury | UniSwapper holds NO valuable token (honest) | LP via addLiquidityEth |
| tx sequence | setRouter(attacker); mint(attacker, 1e6 ether) | receiveFromBridge(...) two scenarios | swapNoPath(junk→valuable) | addLiquidity → redeemEth → removeLiquidity |
| measured invariant | balanceOf(attacker) & totalSupply delta | victim balance; UTB treasury; attacker P&L | attacker valuable-token gain; UniSwapper valuable balance | attacker net ETH vs deposited |
| pass (HIGH) cond | attacker balance += minted, no role | attacker profits / victim loses materially | attacker drains valuable token | attacker withdraws 2x deposit |
| fail (demote) cond | mint blocked w/o hijack | only revert / self-funded routing | transfer reverts (no residual) | attacker cannot obtain redeemable dcntEth |
| failure ⇒ | n/a (positive) | MEDIUM_OR_LOWER | DEMOTE; if needs unsourced residual → NEEDS_HARNESS | NEEDS_HARNESS (source obstacle) |

## decent-12 — why not a full harness (per L3 standard, documented obstacle)
`DecentEthRouter.addLiquidityEth()` mints dcntEth to **`address(this)` (the router)**, not to the depositor (the
depositor only gets a `balanceOf` LP credit via `userDepositing`). `redeemEth` requires the caller to **hold** and
`transferFrom` dcntEth. So **no source-valid flow gives the attacker redeemable dcntEth** — realizing the
double-withdrawal would require *artificially granting the attacker dcntEth* (arbitrary mock custody), which the L3
standard explicitly disallows. Per the standard → **NEEDS_HARNESS_FOR_SEVERITY** (not a built fabricated High).
