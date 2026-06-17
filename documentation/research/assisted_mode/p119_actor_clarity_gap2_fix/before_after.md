# P119 — Second actor_clarity gap: caller-equality admin-role gates

**Research-only / un-wired.** Affects candidate RANK ordering in the assisted research probe only — never
production routing, gates, severity, or submission. `actor_clarity` is a soft GATE in the ranking, not a scored
feature.

## The gap (recorded by P118)
P118 ran a runtime harness on the novel candidate `SecondSwap_Marketplace.unlistVesting` and reached
KILLED_RUNTIME — the function is in fact **seller/admin-gated**, yet the ranking had flagged it `permissionless`.
Root cause: the body role-guard regex (`_ROLE_GUARD_RE` = the `role_auth_modifier` primitive) only matches
`require(msg.sender == …` (**caller-first**) and `only*` modifiers. It misses the operand-reversed / OR-clause /
cast forms:

```solidity
// SecondSwap_Marketplace.unlistVesting
require(
    listing.seller == msg.sender || msg.sender == IMarketplaceSetting(marketplaceSetting).s2Admin(),
    "SS_Marketplace: Not the seller"
);
```

Both forms were invisible: `<role> == msg.sender` (reversed) and `msg.sender == s2Admin()` (after `||`, wrapped in
a cast). This is **distinct** from the P115 fix (which added signature-modifier detection like `onlyBorrower`).

## The fix (precision-first, role-targeted)
A new body regex `_CALLER_ROLE_EQ_RE` in `scripts/assisted/rank_signal_probe.py`, OR-ed into the `role_guarded`
computation in `_features_for`:

```python
_CALLER_EQ = r"(?:msg\.sender|_msgsender\(\))"
_ROLE_NAME = r"\b(?:owner|admin|s2admin|governor|governance|authority|manager|controller|guardian|operator|treasury|deployer|issuer)\b"
_CALLER_ROLE_EQ_RE = re.compile(_CALLER_EQ + r"\s*==\s*[^;\n]*?" + _ROLE_NAME
                                + r"|" + _ROLE_NAME + r"[^;\n]*?==\s*" + _CALLER_EQ, re.I)
```

### Why not a naïve "any `== msg.sender`" rule
`X == msg.sender` matches **two semantically different** patterns:
- **admin-role gate** — `msg.sender == owner()` / `== s2Admin()` / `== manager` → genuinely privileged → demote.
- **resource-ownership** — `nftContract.ownerOf(mergerTokenId) == msg.sender` → *not* access control; any token
  owner can call for their own resource, and the function is attacker-reachable.

A broad rule would falsely demote the **awarded** `EntityForging.forgeWithListed` (M-18), whose only
caller-equality is `require(ownerOf(mergerTokenId) == msg.sender)`. So the fix is **role-targeted**: the operand
must contain an admin-role word. The word boundary is the key — `\bowner\b` matches `owner()` but **not**
`ownerOf(` (no word boundary inside "ownerof"), so resource-ownership is preserved. Under-detection (e.g.
contract-address gates like `msg.sender == address(entityForgingContract)`) is accepted as **safer than false
demotion of attack surface**.

## Impact over the P105 corpus (computed in-memory; `p106/rank_signal_probe.json` NOT regenerated)

**Exactly 5 functions flip `permissionless → privileged`:**

| Function | Flip | Verdict |
|---|---|---|
| `secondswap :: SecondSwap_Marketplace.unlistVesting` | 1.0 → 0.0 | **TARGET** — seller/admin gate now detected ✓ |
| `secondswap :: SecondSwap_StepVesting.transferVesting` | 1.0 → 0.0 | awarded (H-01) — **correct demote** (see below) |
| `secondswap :: SecondSwap_StepVesting.createVesting` | 1.0 → 0.0 | role-gated (manager/issuer/deployer) |
| `secondswap :: SecondSwap_VestingManager.setSellable` | 1.0 → 0.0 | role-gated setter |
| `iq-ai :: AgentFactory.setAgentStage` | 1.0 → 0.0 | role-gated setter |

### Awarded-finding impact: only `transferVesting`, correctly
`transferVesting` is genuinely role-gated:
`require(msg.sender == tokenIssuer || msg.sender == manager || msg.sender == vestingDeployer)`. The H-01 exploit
**entrypoint** is the permissionless `spotPurchase` (which internally calls `transferVesting`), and `spotPurchase`
stays `permissionless` (1.0). Demoting the privileged callee does not hide the attack surface.

### Awarded-finding preservation: `forgeWithListed` (M-18) stays permissionless
Its only caller-equality is `ownerOf(mergerTokenId) == msg.sender` (resource-ownership) → not matched (`\bowner\b`
≠ "ownerof") → **1.0 → 1.0**.

### Other key functions preserved (1.0 → 1.0)
`ramses swap`, `phi distribute`, `secondswap spotPurchase`, all `claim`/`claimable`, `iq-ai moveLiquidity`,
`munchables burnNFTs`, `vultisig claim`, `phi PhiFactory.claim`.

## Test ripple = none
The 5 demoted functions all sit **below** the top-3 selection cutoffs, so every existing selection result is
identical to pre-fix (verified against the patched module):
- `assisted_fresh_run.select_candidate` global #1 = `ramses swap` (unchanged).
- `select_next_n(n=3, already_run=P116)` = `burnRemainingPurchasedNFTs, distribute, burnNFTs` — `distribute`
  still present, all permissionless.
- `select_next_n(n=3, no exclusions)` = `repayAndProcessUnpaidWithdrawalBatches, burnRemainingPurchasedNFTs,
  distribute` — `closeMarket`/`claimFromFactory` still excluded.

No existing test assertion changed. One test added: `test_p119_caller_equality_role_gate_detected` (incl. the
`forgeWithListed`-class resource-ownership preservation). `tests/assisted` → **197 passed**.

## Integrity
- Only `scripts/assisted/rank_signal_probe.py` changed (authorized; was `46381e52`). The `role_auth_modifier`
  primitive lives in `map_invariant_defenses.py` (PIPELINE-4, `e9b6bc1d`) and is **byte-identical**.
- FROZEN-5 + PIPELINE-4 unchanged; `terminal_distribution.py` (`c4aaa9a4`) / `assisted_fresh_run.py` (`129fc745`)
  unchanged; secondswap/phi `src/` unmutated.
- FLAGS unchanged (`is_gate:false`, `research_only:true`, `routes_in_production:false`). No severity / report /
  submission / READY produced. `p106/rank_signal_probe.json` untouched.
