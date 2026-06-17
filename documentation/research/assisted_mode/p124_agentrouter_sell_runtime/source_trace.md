# P124 — Source trace: AgentRouter.sell (iq-ai-2025-01)

Subject: `src/AgentRouter.sol` (solc 0.8.25). Read-only; framing only — runtime decides. Symmetric mirror of `buy`
(P123).

## sell (thin router, permissionless)
`sell(address _agentToken, uint256 _amountIn, uint256 _minAmountOut, address _recipient) public returns (uint256 _amountOut)`
(the 3-arg overload forwards with `_recipient = msg.sender`).
- `agent = factory.tokenAgent(_agentToken); if (agent == 0) revert AgentNotFound();`
- `liquidityManager = LiquidityManager(factory.agentManager(agent)); bootstrapPool = liquidityManager.bootstrapPool();`
- **bootstrap path** (`!bootstrapPool.killed()`):
  `IERC20(_agentToken).safeTransferFrom(msg.sender, address(this), _amountIn);`
  `IERC20(_agentToken).forceApprove(address(bootstrapPool), _amountIn);`
  `_amountOut = bootstrapPool.sell(_amountIn, _recipient);`   // returns currency
- **Fraxswap path** (`killed`):
  `fraxswapPair = IFraxswapPair(fraxswapFactory.getPair(currency, _agentToken));`
  `fraxswapPair.sync(); _amountOut = fraxswapPair.getAmountOut(_amountIn, _agentToken);`
  `IERC20(_agentToken).safeTransferFrom(msg.sender, address(fraxswapPair), _amountIn);`
  `fraxswapPair.swap(...)` (direction by `token0()`) → currency to `_recipient`.
- final: `if (_amountOut < _minAmountOut) revert InsufficientAmountOut();`

`fraxswapFactory` is the hardcoded constant `0xE30521fe7f3bEB6Ad556887b50739d6C7CA667E6`.

## Observations (router level)
- The router pulls **exactly `_amountIn`** of the AGENT token from the caller and forwards it (approve + `sell`, or
  direct transfer to the pair). It holds no standing state; currency output is delivered straight to `_recipient`.
- Guards: non-existent agent → `AgentNotFound`; slippage → `InsufficientAmountOut`.
- `_recipient` is arbitrary (sell-for-another) — the caller still surrenders the agent tokens; not a privilege.
- **Pricing is delegated** to `BootstrapPool.sell` (bonding curve) / Fraxswap (`getAmountOut`/`swap`).

## Cross-contract scope limit (honest)
The economic questions live in the COLLABORATORS, not the router: `BootstrapPool` curve/fee/`killed` transition;
Fraxswap `sync` (donation skim)/reserves/fee (the IQ-M-01 `moveLiquidity` pair-adoption area). A mocked-collaborator
harness cannot honestly settle those → NEEDS_CONTEXT. The harness decisively answers the **router's own** safety.

## Framed runtime question (→ harness)
Is the router itself safe — does `sell` return currency only for the full `_amountIn` of agent tokens surrendered,
enforce `_minAmountOut`, reject non-existent agents, and retain nothing — with pricing delegated to the pool? →
answered by the harness.
