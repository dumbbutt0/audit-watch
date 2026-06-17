# P241 — Predy (C4 2024-05) blind base candidates (pre-reveal)

Architecture: perps/derivatives (Uniswap-v3-based sqrt perps, vaults, liquidation, settlement). **Read bound:**
LiquidationLogic (partial) + the advisory hostile-token lens; the large trade/perp/settlement libraries NOT read —
base recall is a LOWER BOUND. Answer key (LOCAL `_sealed_answer_key/report.md`, 46460346…) NOT opened.

| ID | Title | Contract:fn | Sev | Conf | Source |
|---|---|---|---|---|---|
| PREDY-L1 | Liquidation/settlement pushes a pair token via SafeTransferLib with no containment; pairs are permissionlessly creatable so the token can be attacker-selected → a reverting/hostile token blocks liquidation/settlement (settlement-DoS / stuck position) | LiquidationLogic.liquidate (39) | High(lens)→needs review | Med | **hostile-token LENS** |
| PREDY-02 | (unread surface) sqrt-perp trade/settlement accounting + slippage (SlippageLib) + permissionless pair creation interactions — not read | Trade/Perp/Settlement libs | ? | Speculative | base (bounded) |

Advisory lenses on predy: Safe 0, **hostile 1 HIGH (PREDY-L1)**. This is the campaign's only non-zero advisory-lens
candidate. Harness BLOCKED_BY_BUILD.
