# P268 — PRE_REVEAL_GATE (Phase 10, frozen BEFORE reveal)

`PRE_REVEAL_REPORTABILITY_CANDIDATE` only if ALL hold: source-backed root cause · attacker control · value/invariant
delta · victim/gainer · terminal/amplifiable impact · selector preserved/selected it · five-op completion · PoC
support/strong runtime evidence · explicit FP refutation. Never sets severity/reportable/submission-ready/confirmed.

## C2-M1 — first-depositor share-inflation
| criterion | met? | evidence |
|---|---|---|
| source-backed root cause | ✅ | Karak `Vault` extends solady ERC4626, no `_decimalsOffset` override; `totalAssets`=balanceOf |
| attacker control | ✅ | permissionless `deposit` + direct donation |
| value/invariant delta | ✅ | victim 5000e18 → 0 shares (proportionality invariant broken) |
| victim/gainer | ✅ | victim loses deposit; existing share gains (partially) |
| terminal/amplifiable | ✅ | unconditional victim loss; repeatable per fresh vault/first-depositor |
| **selector preserved it** | ✅ | **KEEP_BOTH (anti-easy-PoC) — the raw pre-P267 path would have dropped it for C2-M2 dust-rounding** |
| five-op completion | ✅ | COMPLETED_CHAIN |
| PoC support | ✅ | `test_C2_first_depositor_inflation_zeros_victim` PASS |
| explicit FP refutation | ✅ | falsifier (virtual shares) tested → offset-0 insufficient → not an FP; attacker-profit caveat stated |
**Gate: `PRE_REVEAL_REPORTABILITY_CANDIDATE`** (victim-loss confirmed; attacker-profit PARTIAL noted). Not severity/
reportable/submission/confirmed.

## C1-M1 — finishRedeem
By-design (NO_CHAIN; quiet path safe; finisher gains 0). **Gate: NOT reportable.**

## C1-M2 — startRedeem approval revert
Low-impact UX/griefing (NO_CHAIN). **Gate: NOT reportable.**

## C-neg — slashing
Core-gated; REFUTED. **Gate: NOT reportable (negative control held).**

## Summary
| mechanism | gate |
|---|---|
| C2-M1 inflation | **PRE_REVEAL_REPORTABILITY_CANDIDATE** |
| C1-M1 finishRedeem | NOT reportable (by-design) |
| C1-M2 approval-revert | NOT reportable (UX) |
| C-neg slashing | NOT reportable (benign control) |

No severity/reportable/submission/confirmed assigned. **The reportable candidate (C2-M1) is exactly a mechanism the
P267 selector preserved that the pre-P267 path would have dropped.** Full pre-reveal set frozen; hashes in REVEAL.
