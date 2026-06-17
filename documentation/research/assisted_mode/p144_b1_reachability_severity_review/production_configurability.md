# P144 — Production Configurability

## Q&A
- **Are multi-hop routes supported by the real contract?** Yes. `priceRoutes[asset][base]` is an `address[]` and
  `_getValue` loops over it; the entrypoint comment ("considering a specific number of sources",
  `NoyaValueOracle.sol:65`) shows multi-hop is intended.
- **Who can set them?** A maintainer, via `updatePriceRoute` / `updateAssetPriceSource` / `updateDefaultPriceSource`
  (`:61/:51/:37`), all `onlyMaintainer` (`:24-25`, `registry.hasRole(MAINTAINER_ROLE)`).
- **Is that role trusted/admin-only?** Yes — a protocol maintainer role.
- **Are routes expected to be set by maintainers?** Yes; that is the only way they are populated.
- **Are routes immutable after deployment?** No — mutable by the maintainer at any time.
- **User / admin / protocol controlled?** **Protocol/admin (maintainer) controlled.** Not user-controlled.
- **Can an attacker influence asset/base/sources?** No — no external/un-permissioned setter; arrays come only from
  `onlyMaintainer` writes.
- **Can an attacker select a route at call time?** No — the route is a `(asset, base)` mapping lookup inside
  `getValue`; the caller does not pass the sources array.
- **Malicious/compromised maintainer needed?** **No.** This is the key point: the bug fires under a *correctly
  intentioned* maintainer who configures a legitimate ≥2-hop route — the loop still mis-prices. So it is **not**
  merely a "trusted-admin misconfiguration" risk; it is a latent correctness defect in an intended feature.
- **Examples/configs/tests/docs showing ≥2-source routes locally?** **None on disk** (see route_evidence.md).

## Classification: **PROTOCOL_CONFIG_REACHABLE**
Multi-hop routes are a normal, intended, protocol-configured feature; the defect manifests whenever a ≥2-hop route
with differing per-hop oracle paths is configured. It is **not USER_REACHABLE** (no attacker control of routes),
and **stronger than TRUSTED_ADMIN_ONLY** (no malicious admin required — a correct configuration still mis-prices).

## Honest caveat
Reachability is **design-supported, not config-demonstrated locally**: the contract supports and is meant to use
≥2-hop routes, but no on-disk deployment/test exhibits a *live* ≥2-source route with materially different per-hop
prices. Whether production actually registers such a route (and for a material-value token) is the residual
human/program-context question.
