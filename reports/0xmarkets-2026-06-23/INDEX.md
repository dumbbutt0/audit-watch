# Submission Packs — 0xmarkets

13 findings total (12 real + 1 merged/rejected/info). Each folder has `report.md` + `sources/` (full vulnerable files).

## Real findings (recommended for submission) (12)

| ID | Severity | Category (VRT) | Title | Vulnerable files | Status |
|---|---|---|---|---|---|
| [INS-001](INS-001/report.md) | High | Business Logic Errors | Drawdown trigger is computed on USD pool value (price-driven), so the  | InsuranceFundUtils.sol, MarketUtils.sol, DecreasePositionCollateralUtils.sol |  |
| [CFG-001](CFG-001/report.md) | Medium | Violation of Secure Design Principles | ConfigValidatorUtils drops canonical GMX range bounds (LIQUIDATION_FEE | ConfigValidatorUtils.sol, ConfigAllowedKeys.sol |  |
| [CFG-002](CFG-002/report.md) | Medium | Business Logic Errors | Config.setPythLazerFeed writes the Pyth Lazer feed config to the WRONG | Config.sol, Timelock.sol, ConfigAllowedKeys.sol, PythLazerFeedProvider.sol |  |
| [POS-001](POS-001/report.md) | Medium | Business Logic Errors | Leverage ladder is enforced per-position, not per-account: notional-ba | Position.sol, MarketUtils.sol, LeverageLadderUtils.sol, PositionUtils.sol |  |
| [PYO-001](PYO-001/report.md) | Medium | Business Logic Errors | PythHermesFeedProvider performs NO signature or staleness verification | PythHermesFeedProvider.sol |  |
| [CFG-003](CFG-003/report.md) | Low | DoS with (Unexpected) revert | Config.setBaselineSwap is permanently bricked by a double nonReentrant | Config.sol |  |
| [INS-002](INS-002/report.md) | Low | Business Logic Errors | topUp() (documented governance treasury-seeding path) is unreachable d | InsuranceFundUtils.sol, InsuranceFundUtilsTest.sol |  |
| [INS-003](INS-003/report.md) | Low | Business Logic Errors | Unset insuranceFundDrawdownTriggerFactor defaults to 0 ('inject on any | InsuranceFundUtils.sol |  |
| [INS-004](INS-004/report.md) | Low | Business Logic Errors | LP can capture insurance-fund injections by providing liquidity into a | LiquidationHandler.sol, AdlHandler.sol, OrderHandler.sol, InsuranceFundUtils.sol |  |
| [PYO-002](PYO-002/report.md) | Low | Business Logic Errors | Config.setPythLazerFeed writes Lazer feed config to the WRONG DataStor | Config.sol, PythLazerFeedProvider.sol |  |
| [PYO-003](PYO-003/report.md) | Low | Business Logic Errors | PythHermesFeedProvider expo->multiplier conversion uses fully keeper-s | PythHermesFeedProvider.sol |  |
| [PYO-004](PYO-004/report.md) | Low | Business Logic Errors | Pyth confidence band has no minimum-spread floor: spreadFactor=0 colla | PythLazerFeedProvider.sol |  |

## Informational (1)

| ID | Severity | Category (VRT) | Title | Vulnerable files | Status |
|---|---|---|---|---|---|
| [CFG-004](CFG-004/report.md) | Info | Business Logic Errors | LIMITED_CONFIG_KEEPER path is dead code: onlyKeeper admits the role bu | Config.sol |  |

