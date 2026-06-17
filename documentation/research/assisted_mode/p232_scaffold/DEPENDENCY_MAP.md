# P232 Dependency Map — dep → in-repo source (the Dependency-layer primitive)

The single most-repeated friction across all 8 harnesses (8/8) is dependency wiring, and the heaviest single
instance was QAMM-03 (2–6h, mostly Balancer-V3 remapping). P231 proved that the needed dependencies are almost
always **already present in the workspace** — the cost is *discovery + remapping*, not vendoring from scratch. This
manifest collapses that to a lookup. A scaffold `foundry.toml` generator consumes it.

| Dependency | In-repo source (proven in P231/P223) | Notes |
|---|---|---|
| forge-std | `pocs/foundry/lib/forge-std/src/` | global; used by every pocs harness |
| OpenZeppelin **5.x** | `pocs/p223/vendor/oz/` (5.0.2) | lending (Size) |
| OpenZeppelin **4.9.x** | yarn cache `…/.cache/yarn/v6/npm-@openzeppelin-contracts-4.9.6-…/node_modules/@openzeppelin/contracts` | **4.9 ≠ 5.x** (Ownable ctor + revert string "Ownable: caller is not the owner" vs custom error) — version matters for TF-17 |
| solmate (`Owned`) | `audits/dyad-2024-04-fresh/_src/lib/solmate/` or `audits/panoptic-2025-12-strict-eval/.../lib/solmate/` | cross-chain (Decent) |
| Aave v3 interfaces | `pocs/p223/vendor/aave/` (types-only) | lending |
| solady | `pocs/p223/vendor/solady/` | lending |
| Balancer-V3 full stack + @prb/math | the audit's **own** monorepo: `audits/quantamm-2024-12-eval/contracts/quantamm-monorepo/` (`pkg/*` + `node_modules/*`) | oracle (QuantAMM); remap absolute, `allow_paths`, solc 0.8.26 cancun, `ignored_error_codes=[2394,5574,3860]` |
| decent-bridge `IWETH` | `audits/decent-2024-01-holdout/contracts/lib/decent-bridge/` | cross-chain |

**Rule:** a target's own `node_modules` / `lib` / monorepo (shipped inside its `audits/<id>/` workspace) is the
first place to look — heavy frameworks (Balancer V3) compile fast when wired to the in-repo copy. Vendor from the
yarn cache only when the workspace lacks the dep (e.g. OZ 4.9 for TraitForge).
