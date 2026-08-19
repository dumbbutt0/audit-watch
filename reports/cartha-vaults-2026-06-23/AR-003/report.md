# AR-003 — Parent _convertToShares/_convertToSharesRoundUp hardcode the 1e12 first-deposit offset instead of deriving it from asset decimals — diverges from the child for any asset != 6 decimals

- **Severity (recommended):** Low
- **Category (HackenProof VRT):** Business Logic Errors
- **Triage status:** downgraded
- **Confidence:** High
- **ICE:** Impact=Low · Confidence=High · Exploitability=Conditional (non-6-decimal asset; ADMIN/FACTORY deploy)
- **Location(s):** `src/CarthaParentVault.sol:129-142,340-365; src/CarthaVault.sol:916-919`
- **Vulnerable files (bundled in `sources/`):** `CarthaParentVault.sol`, `CarthaVault.sol`, `CarthaVaultFactory.sol`

## Description

CarthaParentVault._convertToShares and _convertToSharesRoundUp return amount * 1e12 on the first deposit (supply==0 || total==0) at CarthaParentVault.sol:133,140 — a HARDCODED offset, unlike the child which derives 10 ** (18 - assetDecimals) (CarthaVault.sol:918). For 6-decimal USDC both equal 1e12 and are consistent. For any other asset decimal count they DIVERGE: an 18-decimal asset gives parent offset 1e12 but child offset 1 (a 1e12 scale gap), an 8-decimal asset gives parent 1e12 but child 1e10. The factory binds a parent and child to the same asset ADDRESS (AssetMismatch check, CarthaVaultFactory.sol:155) so their decimals are necessarily equal, but the parent and child compute DIFFERENT first-deposit share scales from those same decimals. Since CarthaParentVault.totalAssets() values its child stake as parentShares * childTVL / childSupply (CarthaParentVault.sol:358-359), a scale mismatch between parent-minted shares and child-minted shares corrupts the rollup and parent sharePrice for non-6-decimal assets. Robustness/correctness; live-safe because the intended asset is 6-decimal USDC. Recommend deriving the offset as 10**(18 - asset.decimals()) in the parent too (matching the child), or constraining asset decimals to 6 at deploy.

## Impact

No impact with 6-decimal USDC. For any non-6-decimal asset the parent's first-deposit share scale diverges from the children's, corrupting totalAssets rollup and parent sharePrice (off by up to 1e12 for an 18-decimal asset).

## Attack path (Intent / Technique / Evasion)

- **Intent:** Corrupt parent/child share-scale consistency by hardcoding the parent offset to 1e12 regardless of asset decimals.
- **Technique:** Deploy parent+children with a non-6-decimal asset; parent first deposit mints amount*1e12 while children mint amount*10**(18-d); parent totalAssets (parentShares*childTVL/childSupply) mixes the two scales.
- **Evasion:** Parent offset hardcoded 1e12; child offset derived; factory matches asset by address (same decimals) but neither constrains decimals to 6.

## Reachability / follow-up

reachable: non-6-dec asset. no_privileged_keys: config. state_before_after: parent/child scale mismatch. why_guards_fail: hardcoded 1e12. scope_match: latent.

## Triage reasoning

CarthaParentVault._convertToShares/_convertToSharesRoundUp HARDCODE the 1e12 offset rather than deriving it (unlike the child), so parent/child share scales diverge for any non-6-dec asset. Factory AssetMismatch matches by address only, not decimals. Same latent root as AR-002; live-safe under 6-dec USDC.
