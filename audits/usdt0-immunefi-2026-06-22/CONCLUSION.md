# USDT0 — Immunefi bug bounty — audit conclusion (SHORT: thin target)

**Target:** USDT0 (Immunefi $6M, omnichain USDT via LayerZero, KYC+PoC, deployed multi-chain).
**Scope:** 42 deployed assets across ~10 chains = three contract TYPES (verified source via Etherscan V2, incl. HyperEVM chainid 999):
- `OAdapterUpgradeable` (Ethereum lockbox, 0x6C96…1dee) — **15 lines**, pure wrapper over LayerZero `OFTAdapterUpgradeable`.
- `OUpgradeable` (the OFT, e.g. Arbitrum) — **84 lines**, canonical LayerZero mint/burn OFT (`_debit` burns, `_credit` mints, addr(0)→0xdead).
- `HyperLiquidComposer_V1_FeeToken` (HyperEVM, 0x8012…7585) — **42 lines** of glue inheriting **LayerZero-Labs-authored** `hyperliquid-composer` (FeeToken + RecoverableComposer + HyperLiquidComposer).

## Verdict: not a productive deep-audit target (thin LayerZero deployment)
USDT0 has **no meaningful custom protocol logic** — ~141 lines of standard wrappers over LayerZero's OFT/Adapter/Composer stack (massively audited, deployed across hundreds of protocols, OZ-audited deployment). The $6M custody is protected by LayerZero's core, not by USDT0-specific code. A real audit here = auditing LayerZero's OFT core (out of scope / astronomically picked-over). The thin wrappers are standard (initialize + `_disableInitializers`; canonical mint/burn). Nothing custom-exploitable.

**Nothing submitted. Pivoted to a target with real custom logic.** (Lesson: a $-headline + "custom extension" label can still resolve to thin LZ/OFT wrappers — confirm custom-code volume early before committing a fleet.)
