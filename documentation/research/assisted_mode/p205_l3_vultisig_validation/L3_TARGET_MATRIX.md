# P205 — L3 target matrix (blind → awarded mapping, post-FREEZE-1 key open)

Key opened only after FREEZE 1 (`fa1afe1b`), read-only, to map blind mechanisms → awarded classes. Mapping kept
separate from harness code. **Authoritative awarded set** (`_sealed_answer_key/report.md`): 3 High / 3 Medium.

## Decisive scope finding
The vultisig C4 contest spans **two codebases**: `hardhat-vultisig/contracts/` (VULT token + `Whitelist.sol`) and
the foundry `src/` ILO launchpad (ILOPool/ILOManager/ILOWhitelist). **My bounded blind sample (v-01…v-08) covered
only `src/`.** Three awarded findings live in the hardhat codebase and were therefore out of the sampled
denominator.

| Awarded | title | locus | in my src/ sample? | blind mapping |
|---|---|---|---|---|
| **H-01** | Most users can't claim their Uniswap fee share | `ILOPool.claim` (src/) | ✅ | **v-02 HIGH — exact mechanism HIT** (first claimer absorbs fees) |
| **H-02** | Whitelisting can be bypassed by anyone | `hardhat-vultisig/.../Whitelist.sol::checkWhitelist` | ❌ (other codebase) | — (my v-07 targeted the *different* `src/base/ILOWhitelist.sol`) |
| **H-03** | Adversary prevents ILO launch via single-sided liquidity | `ILOPool`/`ILOManager` launch (src/) | ✅ | v-03 + v-06 PARTIAL HIT (launch DoS, different precise vector) |
| **M-01** | Vultisig should be burnable | VULT token (hardhat) | ❌ | — |
| **M-02** | `claim` lacks slippage controls on `pool.burn` amounts | `ILOPool.claim` (src/) | ✅ | v-02 area (slippage sub-mechanism, not isolated) |
| **M-03** | NFT transfer bypasses `maxCapPerUser` invariant | `ILOPool.buy` (src/) | ✅ | **v-01 HIGH — over-rated** (awarded Medium; blind rated the cap-bypass HIGH) |

## Control selection
- **Positive control (genuine awarded High to PRESERVE):** H-01 (`ILOPool.claim` fee loss) — blind HIT, genuine
  fund-loss High. *Harness feasibility: V3-entangled (live position fee growth).*
- **Negative control (over-rated → DEMOTE):** **M-03** cap-bypass (awarded **Medium**, blind v-01 **HIGH**) — the
  exact P204-M-03 analogue. *Harness feasibility: in `ILOPool.buy`, drivable without a live pool, but blocked by the
  ILOPool compile dependency web.*
- **Supplementary executed control:** **v-07** `src/base/ILOWhitelist.openToAll` access-bypass. **Honestly: this is
  by-design and NOT awarded H-02** (H-02 is the hardhat `Whitelist.sol`). It validates the L3 *demotion mechanism*
  (capability+admin-prereq+no-fund-movement → demote) executably, but not against a mapped awarded finding.

See `POSITIVE_CONTROL_POC.md` / `NEGATIVE_CONTROL_POC.md` for harness outcomes and the V3-dependency obstacle.
