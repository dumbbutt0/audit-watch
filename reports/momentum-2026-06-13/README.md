# Momentum mmt-v3-core (Sui Move CLMM) — audit deliverables (2026-06-13)
Real HackenProof hunt, the ORIGINAL gated target (source via user's private-repo zip), local-only, nothing submitted.
mmt_v3 CLMM, published-at 0xcf60a40f…c3c1d1. HONEST NEGATIVE — post-Cetus integer-mate CLMM (turbos-class quality).
Cetus-class checked_shlw re-confirmed CLEAN (mask 1<<192). All value-critical surfaces (math/swap/tick-cross/flash/
position-fee/liquidity) re-derived from source = sound; rounding pool-favoring; flash hot-potato+repay enforced.
Repo suite: sui move test 364/364 PASS. See FINDINGS.md.

## Reproduce
unzip the repo, cd clmm, `ln -sf move.toml Move.toml`, `sui client switch --env mainnet`, `sui move test`.
