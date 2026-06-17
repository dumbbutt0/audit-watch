# Reproduce — I-1 (code analysis; no runnable PoC)

Vulnerable source: `vulnerable/InsuranceFundUtils.sol` (`attemptInjectPool`/`getDrawdownFraction`) +
`vulnerable/DecreasePositionCollateralUtils.sol` (call site ~line 557). Injection credits the live pool, so a JIT LP
depositing after a drawdown captures insurance compensation meant for drawdown-era LPs. Standalone PoC requires the
full GMX deposit/withdrawal + keeper machinery. See `report.md`. Severity Medium (design).
