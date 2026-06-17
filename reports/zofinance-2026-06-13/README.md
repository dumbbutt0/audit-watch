# ZO Finance (Sui Move perps) — audit deliverables (2026-06-13)

Real HackenProof hunt (zofinance/zo-contracts-public @ec48af4), local-only, nothing submitted.
GMX-style pool-counterparty perpetuals on Sui. CORE AUDITED → honest negative (no permissionless bug in the
signed-math / PnL / per-side-funding / liquidation / decrease-settlement core). NOT a full pass: build is blocked
(empty [addresses] + old framework rev mainnet-v1.38.3) and bounty is PAUSED, so source-level only; market.move +
pool.move LP-conservation layer not exhausted. See FINDINGS.md.
