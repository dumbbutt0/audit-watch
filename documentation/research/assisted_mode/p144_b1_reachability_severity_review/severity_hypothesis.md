# P144 — Severity Hypothesis (provisional — NOT final)

## Hypothesis: **HIGH_POTENTIAL** (conditioned; gated by duplicate)

Rationale: the mis-valuation reaches the ERC4626 share price (`totalAssets`=`TVL`) consumed by deposit/redeem
across the whole connector set, giving a user-triggerable value-extraction path that harms the share pool. This
matches the local answer key's classification of H-03 as a primary High (oracle/valuation class). It is **not**
final severity — it is conditioned on a divergent ≥2-hop route being configured and on the end-to-end loss being
PoC'd, and it is gated by the duplicate/scope finding.

## Evidence map
| factor | status |
|---|---|
| value movement proven? | **path source-supported; end-to-end loss NOT PoC'd** (only oracle delta in P143) |
| user controlled? | mis-valuation: no (maintainer route). extraction: **yes** (any user deposit/redeem) |
| production reachable? | **design-supported, not config-demonstrated locally** (no on-disk ≥2-hop route) |
| bounded/unbounded? | unbounded in principle (scales with divergence × position size); **unquantified** |
| admin-only? | route config is maintainer-only; **no malicious admin needed** for the defect |
| trusted-role assumption? | depends only on the maintainer using the *intended* multi-hop feature |
| duplicate/scope? | **DUPLICATE_KNOWN_LOCALLY** — awarded noya H-03 (answer key) |

## Why not higher / lower
- Not Critical-claim: no unconditional, no-precondition fund loss demonstrated; requires a configured ≥2-hop
  divergent route and an unproven extraction path.
- Not Medium/Low: the consumer path is share-price/redemption (value-moving), not view-only — so it is not
  downgraded to informational.
- Final severity is a human decision after route-reachability confirmation + an end-to-end PoC + duplicate ruling.
