# P275 — RANKING_AND_COMPLETION (Phase 6)

B/C + five-op completion (STS/AAS/TSE/IDC/CCIT) on the 3 triage-selected mechanisms, each in its routed class, with
class-specific checklists. **All BLIND** (Katana-V3 source only; no answer key). Honest caveat up front: Katana V3 is
largely a vanilla Uniswap-V3 fork; the bug surface is concentrated in the *custom* additions (governance authorization,
the `tx.origin` quoting gate, fee/flash config, beacon upgrade). My blind analysis found custom **deviations** but
could not establish a high-confidence exact exploit for most — recorded faithfully below.

---

## M1 — `npm_mint` → routed ACCESS_CONTROL (governance authorization subsystem)
**Loci:** `NonfungiblePositionManager.mint` → `AuthorizationLib.checkPair` → `KatanaGovernance.isAuthorized`; and the
sibling custom gate `KatanaV3Pool.swap` `if (tx.origin != address(0)) require(msg.sender == governance.getRouter())`.
**Class-specific (access) checklist:**
- caller authority: pool.swap restricted to `governance.getRouter()`; mint to `positionManager`; both custom.
- the **exact deviation**: `pool.swap` authorization is gated on `tx.origin != address(0)` — an **authorization
  decision driven by `tx.origin`**. Intent: let off-chain quoters (`eth_call`, `tx.origin == 0`) simulate swaps
  without the router restriction.
- whitelist model: `_isAuthorized` = `whitelistUntil` window then public; `_isSkipped` = `allowedAll || owner ||
  isAllowedActor`.
**Exact hypothesis (STRONG-candidate, exploitability-LIMITED):** the `tx.origin`-based gate is a non-standard
authorization pattern. **On-chain exploitability is limited** — in a state-changing tx `tx.origin` is the originating
EOA (never 0), so the router restriction is always enforced; the bypass only manifests under `tx.origin == 0`
(simulation), which does not persist state. I could **not** find an on-chain path that sets `tx.origin == 0`.
**Completion:** STS ✓ · AAS partial (no on-chain attacker path to `tx.origin==0`) · TSE ✓ (gate reachable) · IDC
partial · CCIT partial. **Status: COMPLETE on the deviation; PARTIAL/UNCONFIRMED on exploitability.**

## M2 — `swap_callback` → routed ORDER_VALIDATION (router)
**Locus:** `V3SwapRouter.katanaV3SwapCallback` + `_swap` (`governance.isAuthorized(tokens, msg.sender)` + callback
`computePoolAddress(...) == msg.sender`).
**Class-specific (order) checklist:** callback caller validation = `computePoolAddress == msg.sender` (standard,
correct); token whitelist enforced at the router on the user; slippage via `maxAmountInCached`.
**Exact hypothesis:** none cleanly derivable blind — callback validation matches canonical Uniswap; whitelist check
present. **Status: PARTIAL — control-flow only, NEEDS_MORE_RUNTIME. Not advanced to PoC.**

## M3 — `pool_mint` → routed SHARE_ROUNDING_PRECISION (pool math)
**Locus:** `KatanaV3Pool.mint` / `_modifyPosition` (concentrated-liquidity math).
**Class-specific (math) checklist:** mint restricted to `positionManager`; amounts via `_modifyPosition`; balance
deltas checked (`balance0Before.add(amount0) <= balance0()`). This is vanilla Uniswap V3 math.
**Exact hypothesis:** none — matches canonical Uni V3 conservation. Serves as a **negative control** (conservation
expected to hold). **Status: BENIGN-expected; control PoC only.**

---

## PoC plan (Phase 7+)
| mech | class | tier | plan |
|---|---|---|---|
| M1 pool.swap `tx.origin` gate | ACCESS | C (faithful reproduction) | prove the exact gate logic: enforced when `tx.origin!=0` (revert for non-router), skipped when `tx.origin==0` |
| M3 mint/burn conservation | SHARE | C (negative control) | faithful conservation reproduction — expected to hold (isolates that pool math is not the bug) |
| M2 swap_callback | ORDER | — | NEEDS_MORE_RUNTIME (no exact hypothesis) |

**Honest note:** these PoCs prove/​refute the *deviations I found*, not necessarily an awarded mechanism. The reveal
(Phase 10) will determine match level. The recall harness's failure to surface any `KatanaGovernance` locus (BASE
freeze ⚠ note) is the leading risk that the actual awarded mechanisms lie outside the examined set.
