# P206 — corpus ranking

Ranked on: positive-control High quality · negative-control availability · harness simplicity · source reachability ·
dependency readiness · architecture diversity · firewall cleanliness.

| rank | corpus | pos-control High | neg-control | harness | deps | firewall | label |
|---|---|---|---|---|---|---|---|
| 1 | **munchables-2024-05** | **none** (2 Highs = permissionless DoS/griefing, no value transfer = demote-class) | strong (2 demote-Highs + 4 Mediums) | trivial (94 files compile, solc 0.8.25, OZ v5 local) | minor (OZ v5 local; @api3 isolated to rng/) | orchestrator contaminated re mechanisms by run-2 prose (caveat) | **`FALLBACK`** (negative-side only; NOT a positive control) |
| 2 | pooltogether-2024-03 | weak (1 High = `trusted_prereq` permanent-loss; excluded as main positive per criteria) | strong (5 Mediums) | light (6 files, OZ-only, 0.8.24) | minor (OZ local) | clean | **`FALLBACK`** (no permissionless positive High) |
| — | badger-2024-06 | — | — | — | — | — | `REJECT_TOO_THIN` (0 High) |
| — | kleidi-2024-10 | — | — | — | — | — | `REJECT_TOO_THIN` (0 High) |
| — | decent-2024-01 | (used) | — | — | — | — | `REJECT_ALREADY_USED` (P202/P204 — positive control already executed here) |
| — | vultisig-2024-06 | **yes** (H-01 claim-fee-loss = permissionless material; mapped in P205) | yes (M-03 cap-bypass) | **heavy** (solc 0.7.6 + OZ-3.4 + v3-core/v3-periphery; no local compatible deps) | major | clean (mapped post-freeze in P205) | `REJECT_ALREADY_USED` as *fresh* corpus, but the **only identified source of a positive-control High** |
| — | zetachain / centrifuge / predy | — | — | — | — | — | `REJECT_ALREADY_USED` |

## Key result
No firewall-clean (sealed, unused) **lightweight** corpus supplies an L3 **positive-control High** (permissionless +
material theft/permanent-loss/insolvency/privileged-control, non-trusted, non-RNG). The two eligible lightweight
corpora are rich in **negative** controls but have only demote-class or trusted-prereq Highs. The only identified
corpus with a mapped permissionless material High remains **Vultisig** — heavy deps, already partially done in P205.
