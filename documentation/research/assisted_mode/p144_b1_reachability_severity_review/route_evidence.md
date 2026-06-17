# P144 — Production-like Route Evidence (local repo only)

## Searched
- `updatePriceRoute` / `updateAssetPriceSource` / `priceRoutes` invocations across `*.sol/*.js/*.ts/*.json` in the
  noya clone.
- `test/` `deploy/` `script/` `fixture/` `config/` directories in the noya clone.
- docs mentioning route / multi-hop.

## Result: **no on-disk production/route configuration exists**
- The noya clone (`audits/noya-2024-04-eval/contracts/2024-04-noya/`) is **contracts-only** — no `test/`,
  `deploy/`, `script/`, or `fixture/` directories.
- The only references to `priceRoutes`/route setters are **in `NoyaValueOracle.sol` itself** (the definition) and
  in this pipeline's own research artifacts (`output/value_provenance_jobs/*`, `answer_key.md`) — **not**
  deployment/config evidence.
- Therefore there is **no local example of a configured ≥2-source route**, no asset/base/sources tuple, no
  connector-name wiring, and no demonstration that per-hop prices materially differ in production.

| asset | base | sources length | connectors | evidence path | per-hop prices differ? |
|---|---|---|---|---|---|
| — | — | — | — | none on disk | unknown |

## Implication
The mechanism's **production route reachability is not demonstrable from local artifacts**. It is *supported by
design* (the feature exists and is intended for multi-hop) but *not evidenced by a concrete local config*.
Confirming a live ≥2-source divergent route requires program context / on-chain deployment data not present here
(a human/program-context step). This is recorded honestly rather than assumed.
