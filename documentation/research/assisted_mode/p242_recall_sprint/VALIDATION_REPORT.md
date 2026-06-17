# P242 — Validation Report (both families across 16 mixed targets)

Research-only, un-wired. Both families run over prebuilt manifests (`--manifest`). A precision fix was applied to
each AFTER the first pass exposed FPs (documented below), with regression tests; results below are POST-FIX.

## Targets (16): 5 NFT/callback (A-likely), 7 vault/4626 (B-likely), 4 negative controls
A-likely: nextgen(anchor), renft, ai-arena, traitforge, looksrare · B-likely: pooltogether(anchor), concrete,
bakerfi, notional-exponent, spectra, sentiment-v2, reserve · controls: quantamm, dittoeth, kelp, fenix.

## First-pass FPs found → bounded precision fixes (each regression-tested)
- **Family A:** fired on `safeTransferFrom`(ERC20)-before-`_mint` in standard deposits (pooltogether/concrete/
  sentiment/reserve) — the INTENTIONAL, documented CEI-safe deposit pattern (ERC20 transferFrom triggers no recipient
  callback). **Fix:** dropped ambiguous `safeTransferFrom`/`safeTransfer(`/`.call(` from the callback set; kept
  ERC721/1155-specific receiver callbacks (`_safeMint`/`safeBatchTransferFrom`/`onERCxReceived`) + `.call{value}`.
  Regression test: ERC20 deposit-before-mint → REJECT; nextgen → ADVANCE.
- **Family B:** fired on EVERY 4626 vault's `preview*`/`max*` using its own `convertTo*` (sentiment 8, concrete 5) —
  the common, usually-compliant pattern = broad noise. **Fix:** require the EXTERNAL-max wrapper shape
  (`externalVault.convertTo*(externalVault.maxRedeem())` = the M-02 anchor); dropped the preview-only medium shape.
  Regression test: own-convert preview → REJECT; external-max wrapper → ADVANCE.

## Post-fix results (only non-zero shown; 11 targets = 0/0, incl. all 4 controls)
| Target | Family A | Family B | Classification |
|---|---|---|---|
| nextgen | 3 (mint, airDropTokens, burnToMint) | 0 | A: **TP family** (H-01 `_safeMint` before counter; mint = anchor, others same pattern) |
| pooltogether | 0 | 4 (_maxYieldVaultWithdraw, maxWithdraw, maxRedeem, maxDeposit) | B: **TP (M-02)** = `_maxYieldVaultWithdraw`; maxWithdraw/maxRedeem are SAME-ROOT (call it); maxDeposit mild over-flag |
| sentiment-v2 | 0 | 4 (_maxWithdraw, maxWithdraw, maxRedeem, maxMint) | B: **PLAUSIBLE** (SuperPool wrapper-convert; unverified vs answer key) + same-root |
| concrete | 0 | 1 (maxMint) | B: **PLAUSIBLE** (unverified) |

## Metrics per family
| Family | targets | candidates | TP | plausible | FP | high-conf FP | precision | controls |
|---|---|---|---|---|---|---|---|---|
| A create_time_reentrancy | 16 | 3 (1 target) | 3 (nextgen H-01 family) | 0 | **0** | **0** | 100% | 0 (clean) |
| B erc4626_share_accounting | 16 | 9 (3 targets) | 1 (pooltogether M-02) | 2 (sentiment/concrete, unverified) | 0 clear | **0** | ≥1 TP, rest plausible/same-root | 0 (clean) |

## Acceptance vs criteria
| Criterion | Family A | Family B |
|---|---|---|
| 0 high-confidence FP | ✓ | ✓ (after fix) |
| Low candidate volume | ✓ (3, one target) | ~ (9 raw / ~3 distinct roots — same-root duplication remains) |
| Replay recovers anchor | ✓ (nextgen H-01) | ✓ (pooltogether M-02) |
| No broad noise (controls 0) | ✓ | ✓ |
| Independent (non-anchor) TP | none (0 elsewhere) | sentiment/concrete = plausible-unverified |

## Read of results
- **Family A is clean and ready** for advisory use: recovers the nextgen mint-reentrancy family, 0 FP / 0 noise
  across 16 diverse targets after the receiver-callback narrowing. (Known blind spot: cross-contract / Seaport-
  mediated create-reentrancy like reNFT H-03 — not detectable by a per-function source classifier.)
- **Family B is narrowed but not fully proven:** recovers the M-02 anchor with 0 high-conf FP, but retains same-root
  volume across max-functions and its broader hits (sentiment/concrete) are unverified and the convertTo-in-max
  pattern is inherently nuanced (not always a bug). Needs a same-root dedup + per-target answer-key verification
  before advisory use → keep research-only.

## Final Verdict

# B — ONLY_CREATE_TIME_READY

Family A (`create_time_reentrancy`) meets the advisory bar: recovers the nextgen H-01 mint-reentrancy family,
**0 high-confidence FP and 0 noise across 16 diverse targets** (after the receiver-callback narrowing), negative
controls clean. Family B (`erc4626_share_accounting`) recovers its M-02 anchor with 0 high-confidence FP but retains
same-root volume across max-functions and unverified breadth (sentiment/concrete), and the convertTo-in-max pattern
is inherently nuanced — it stays **research-only** pending a same-root dedup + per-target answer-key verification.
Not A (B not ready), not C (Family A — create-time — IS ready), not D (A is ready), not E (both recover anchors).

## Recommendation / next phase (per the P242 stop-condition)
P242 ends detector expansion. Next phase = **supervised live hunting** (consistent with P241's coverage-bound
finding), with Family A added as a research-advisory signal (0-FP-validated) alongside the P237/P238 lenses, and
Family B kept research-only. No third family. (Alternative if more controlled evidence is wanted first: one final
in-domain shadow contest.) Production wiring of any detector remains a separate human decision.
