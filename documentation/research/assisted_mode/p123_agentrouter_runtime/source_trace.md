# P123 — Source trace: AgentRouter.buy (iq-ai-2025-01)

Subject: `src/AgentRouter.sol` (solc 0.8.25). Read-only; framing only — runtime decides.

## buy (thin router, permissionless)
`buy(address _agentToken, uint256 _amountIn, uint256 _minAmountOut, address _recipient) public returns (uint256 _amountOut)`
(the 3-arg overload forwards with `_recipient = msg.sender`).
- `agent = factory.tokenAgent(_agentToken); if (agent == 0) revert AgentNotFound();`
- `liquidityManager = LiquidityManager(factory.agentManager(agent)); bootstrapPool = liquidityManager.bootstrapPool();`
- **bootstrap path** (`!bootstrapPool.killed()`):
  `currencyToken.safeTransferFrom(msg.sender, address(this), _amountIn);`
  `currencyToken.forceApprove(address(bootstrapPool), _amountIn);`
  `_amountOut = bootstrapPool.buy(_amountIn, _recipient);`
- **Fraxswap path** (`killed`):
  `fraxswapPair = IFraxswapPair(fraxswapFactory.getPair(currency, _agentToken));`
  `fraxswapPair.sync(); _amountOut = fraxswapPair.getAmountOut(_amountIn, currency);`
  `currencyToken.safeTransferFrom(msg.sender, address(fraxswapPair), _amountIn);`
  `fraxswapPair.swap(0, _amountOut, _recipient, "")` (or reversed by `token0()`).
- final: `if (_amountOut < _minAmountOut) revert InsufficientAmountOut();`

`fraxswapFactory` is a **hardcoded constant** `0xE30521fe7f3bEB6Ad556887b50739d6C7CA667E6`.

## Observations (router level)
- The router pulls **exactly `_amountIn`** from the caller and forwards it (to the pool via approve+`buy`, or directly
  to the Fraxswap pair). It holds no standing state; agent tokens are delivered straight to `_recipient`.
- Guards: non-existent agent → `AgentNotFound`; slippage → `InsufficientAmountOut`.
- `_recipient` is arbitrary (buy-for-another) — the caller still pays; not a privilege.
- **Pricing is delegated**: `bootstrapPool.buy` (bonding curve) and Fraxswap (`getAmountOut` on synced reserves +
  `swap` k-check) determine `_amountOut`. The router does not compute price.

## Cross-contract scope limit (honest)
The interesting economic questions live in the COLLABORATORS, not the router:
- `BootstrapPool` curve math / fee / `killed` transition.
- Fraxswap `sync` (donation skim), reserve manipulation, fee tier (the IQ-M-01 `moveLiquidity` pair-adoption area).
A mocked-collaborator harness cannot honestly settle those → recorded as NEEDS_CONTEXT. The harness decisively answers
the **router's own** safety (guards, exact-pull, no skim/retention/over-issue, slippage) on both branches.

## Framed runtime question (→ harness)
Is the router itself safe — does `buy` deliver agent tokens only for the full `_amountIn` paid, enforce
`_minAmountOut`, reject non-existent agents, and retain nothing — with pricing delegated to the pool? → answered by
the harness.
