# P240 — Setup & blind-state witness

**Phase:** P240 Second shadow contest with advisory lenses.
**Target:** PoolTogether V5 — Code4rena 2024-03 (`audits/pooltogether-2024-03-holdout`). Not reNFT; not a P239
true-positive source (unused substitute). In-scope: 6 files (PrizeVault, PrizeVaultFactory, TwabERC20,
abstract/Claimable, abstract/HookManager, interfaces/IVaultHooks), ~1,419 LOC — fully read.
**Mode:** in-place blind read of `contracts/src/` only (the answer key is isolated in `_sealed_answer_key/`; the
holdout's `findings/`/`data/`/`reports/` dirs were NOT read). No fork needed; holdout source untouched (read-only).
**Prior active audit (unchanged; explicit `--manifest` used):** `size-credit-2024-06-blind`.

## SEALED answer key (blind-state witness — NOT opened during the hunt)
The awarded findings are on disk at `_sealed_answer_key/report.md`; opened only at reveal (Phase 3).
| Sealed artifact | sha256 |
|---|---|
| `_sealed_answer_key/report.md` | `306ec8306d0f948eeb4219a1efa9d28ba02433ad770a89f59db942824dc9dead` |
| `_sealed_answer_key/README.md` | `e40c9532de446ddb4d015eec7d9301576d22cc1ee79fef2aff0fa87be2d3a15f` |
| `_sealed_answer_key/_FIREWALL_SEAL.txt` | `91cf9707316f7c96360aaf353e23d2be7b56032b967cb5d2ec7fefd422341e3f` |
Re-verified byte-identical at freeze = never opened during Phases 0–2.

## Build status
`contracts/` ships no foundry config / deps (`_sources` empty, `lib` empty) → a full L3 forge harness would require
vendoring PoolTogether V5 deps (OZ, pt-v5-twab-controller, pt-v5-prize-pool, solady). Harnessing is therefore
**BLOCKED_BY_BUILD** for this phase; the recall measurement (the phase's goal) does not require it. Candidate
reasoning is static/mechanism-based.

## Architecture note (determines lens applicability)
PoolTogether V5 PrizeVault is a **single-asset ERC4626** (immutable `_asset`) with a TWAB share token and a
prize-claim hook system. There is **no Gnosis-Safe guard** and **no order/array-selected settlement token**. Both
are OUTSIDE the lens domains (Safe-management needs a Safe guard; hostile-token-settlement needs an attacker/
order-selected token). Prediction (confirmed): both advisory lenses emit **0** candidates here.
