# P143 — Limitations

1. **Mechanism proven, impact not.** The PoC proves the *value discrepancy* in the real `getValue` at runtime. It
   does **not** establish severity or economic loss in the live protocol — that depends on which production routes
   have ≥2 sources with materially different per-hop oracles and what downstream accounting consumes the
   mis-value. Severity is a human decision.
2. **Routes configured in-test.** The route and per-hop oracles are set via the real `onlyMaintainer` setters
   behind a stub registry. The PoC therefore shows the function *can* mis-value such a route; it does not by itself
   prove a production deployment *does* register a divergent ≥2-source route (a scope/reachability question for
   human review).
3. **Mock oracles.** Per-pair prices come from a deterministic `TablePriceOracle` (real `INoyaValueOracle`
   interface) rather than live Chainlink/AMM connectors; chosen to make the arithmetic explainable. Real
   connectors would change magnitudes, not the mechanism.
4. **Corrected reference is a control.** The corrected output (6e18) comes from a copy of the loop with one line
   fixed (`asset`→`quotingToken`), not from a patched production contract — used only for comparison.
5. **Stub registry.** `hasRole→true` bypasses access control to let the real setters run; the valuation read path
   never reads the registry, so this does not affect the result.
6. **Build deps fetched from network** (forge-std, OZ v5.0.2) — re-runnable via the documented clone commands.
7. **Not a submission.** Runtime-confirmed strengthens advisory evidence only; duplicate/scope/severity checks +
   human review remain mandatory before any submission.
