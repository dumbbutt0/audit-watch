# P242 Family B — `erc4626_share_accounting` (RESEARCH-ONLY, un-wired, NARROW)

is_gate:false · research_only:true · routes_in_production:false · routed_manifest_ids:[].

## Research / motivation
P240/P241 recurring vault/share-accounting miss. EIP-4626 share-accounting defects generalize across vaults/
wrappers/lending shares/yield routers. This detector targets the most mechanism-clear sub-shape only (precision over
recall — the family is inherently FP-prone).

## Taxonomy / two-signal gate (per-function; is-4626 computed per contract by the runner)
S1 is-4626 context (IERC4626 / convertToShares+convertToAssets / previewDeposit+previewRedeem) · S2 a max/limit/
preview function using the EXTERNAL-max WRAPPER shape: `externalVault.convertToAssets(externalVault.maxRedeem())`
(approximate convertTo* where EIP-4626 mandates exact preview*). ADVANCE high.

## Anchor + scope
**In-repo anchor (recovered):** PoolTogether `PrizeVault._maxYieldVaultWithdraw` = `yieldVault.convertToAssets(
yieldVault.maxRedeem())` (= M-02; should use `previewRedeem`).
**Precision fix (P242):** require the external-max wrapper (dropped the preview-only medium shape that fired on
EVERY 4626 vault's preview*/max* — sentiment 8 / concrete 5 broad noise). Now 0 high-conf FP across 16 targets.
**Residual limits:** same-root volume across public max-functions (maxWithdraw/maxRedeem call the inner _max*); and
broader hits (sentiment SuperPool, concrete) are PLAUSIBLE-unverified (convertTo-in-max is nuanced, not always a
bug). Needs same-root dedup + per-target answer-key verification before advisory use.

## Files
scripts/erc4626_share_accounting_{taxonomy,audit}.py · config/erc4626_share_accounting_patterns.json ·
tests/erc4626_share_accounting/ (8 tests, incl. PrizeVault._maxYieldVaultWithdraw replay + own-convert regression) ·
research_finding_normalization.json entry.

## Stability classification
**PROMISING-BUT-NEEDS-REFINEMENT** — recovers the M-02 anchor with 0 high-conf FP, but same-root volume +
unverified breadth + inherent nuance keep it below the advisory bar. **Keep research-only.**
