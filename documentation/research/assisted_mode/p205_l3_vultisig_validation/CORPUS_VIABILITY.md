# P205 — corpus viability (vultisig-2024-06-holdout)

## Verdict: VIABLE for a two-sided test (with a feasibility caveat on the positive control)
- **3 High / 3 Medium** (count-only). PCS: 3/3 Highs contract-level + source-reachable; **2 qualifying** (permanent-
  loss permissionless) + 1 "other" (access/whitelist-bypass, non-qualifying).
- Two-sided test needs ≥1 genuine High + ≥1 Medium/false-High → available (qualifying High as positive; whitelist-
  bypass High and/or a Medium as negative). Not DATASET_TOO_THIN on counts.

## Domain & harness feasibility
vultisig = Uniswap-V3 ILO launchpad. ILOPool = ERC721 + V3-position; `claim`/`launch` touch a live V3 pool (the
likely loci of the qualifying permanent-loss Highs) → **positive-control harness is V3-entangled** (needs OZ v3.4 +
v3-core 0.7.6 + a faithful V3 pool/factory mock). `buy`/`claimRefund` are ERC20-tractable. The whitelist-bypass
High (negative control) is pure access-control.

## Caveat carried to scoring
If a faithful source-valid **positive-control** material-impact harness cannot be built within prototype scope
(V3 dependency web), that control is reported `HARNESS_INCONCLUSIVE` and the decision reflects it (per the plan's
fallback). The negative control (capability/access-bypass without material impact → demote) is expected tractable.
Bounded sample → out-of-sample signal, not full recall.
