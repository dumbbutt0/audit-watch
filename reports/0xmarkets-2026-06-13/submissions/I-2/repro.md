# Reproduce — I-2 (code analysis; no runnable PoC)

Vulnerable source: `vulnerable/InsuranceFundUtils.sol` `attemptInjectPool` (~196-205). The off-sentinel is
`type(uint256).max`; the unset DataStore default is `0` = "inject on any drawdown". A fee-collecting market whose
`insuranceFundDrawdownTriggerFactor` isn't set to max auto-drains its reserve. Standalone PoC needs the full GMX build
(@openzeppelin-v4 + MarketUtils/DataStore deps). See `report.md`. Severity Low (config footgun).
