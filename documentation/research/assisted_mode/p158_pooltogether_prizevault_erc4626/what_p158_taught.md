# P158 — What this taught the campaign

- **The H5 lesson changed selection — correctly.** I deliberately picked a **no-keeper, unprivileged,
  direct-value** ERC4626 path (`deposit`/`withdraw`/`redeem`) instead of another operator-gated mechanism.
  That is the right direction.
- **But "no keeper" ≠ "high ceiling."** The pre-screen flagged that PrizeVault's obvious rate-mismatch only
  bites in a **lossy state** (environmental, not attacker-forced) — a *different* ceiling cap than H5's
  keeper cadence, but a cap nonetheless. Severity-ceiling pre-screening before harnessing paid off.
- **Cheap source refutation beats an expensive harness.** Reading `_depositAndMint` revealed the
  `LossyDeposit` guard + debt-aware withdraw/redeem previews — the hypothesis is a **static false positive**.
  Found in minutes, no harness needed.
- **Deploy-light is a real selection constraint.** The real `PrizeVault` imports concrete `TwabController` +
  `PrizePool` (un-vendored, heavy) → `deploy_too_heavy`. "Few source files" (5) hid a heavy external
  dependency graph. **Check the import graph, not the file count, during selection.**
- **Two campaign learnings in one candidate:** *what refutes* (guarded) and *what was too expensive*
  (un-vendored deps). A clean stop is a successful measurement.

## Selection rule to carry into P159
Add to the pre-screen: **"are the contract's heavy deps vendored / is it deploy-light to *compile*, not just
few files?"** Prefer self-contained contracts (own ERC20, few external concrete-type imports). Spectra and
basin both have moderate-heavy deploy graphs too; P159 should hunt for a **self-contained, vendored-deps,
no-keeper, direct-value** target (e.g., a standalone AMM/vault/token with its own accounting and an
attacker-forced delta that doesn't need an environmental precondition).
