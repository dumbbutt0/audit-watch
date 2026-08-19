# Aave V3 on Aptos — Cantina bug bounty — audit conclusion

**Target:** Avara / Aave V3 on Aptos (Cantina, **500,000 GHO**, PoC required). Full **Move rewrite** of Aave V3.3 (Aave's first non-EVM deployment). In-scope repo github.com/aave/aptos-aave-v3 @ main (919362b). ~25k LOC Move (aave-core 14.4k + config/data/oracle/acl/math).
**Audit baseline (in-repo, heavy):** Certora (Core V3.0.2 + V3.1-V3.3 + Periphery — incl. formal verification), Spearbit (Core V3.0.2 + V3.1-V3.3 + Periphery), Ottersec (V3.1-V3.3) + a Cantina CTF. Elite-audited.
**Post-audit delta:** commits since the V3.3 audits are almost entirely tooling (gas/npm/cli/MCP/agents); the ONLY logic change is a treasury-accrual-rounding precision tweak (pool_logic, PR #81, Dec-2025).
**Method:** focused Move-specific pass (not a full fleet on Certora-verified code) on the two residual classes EVM-focused audits can miss: (A) ported ray/wad math + consumers (the Cetus $220M class), (B) core lending logic + Move resource/auth/accounting model.

## Verdict: honest negative — faithful, hardened Move port

### Move math (Cetus class) — clean
- wad_ray_math: half-up rounding identical to Solidity; every mul has a pre-multiply overflow guard + div-by-zero asserts; no realistic intermediate overflow (worst products ~1e63 vs U256 ~1.16e77; FA amounts u64-bounded); u256→u128 index cast needs ~3.4e11x growth to truncate (rate-capped, impossible).
- Rounding matrix consistently favors the protocol: aToken mint=div_down/burn=div_up; vDebt mint=div_up/burn=div_down; HF collateral=ray_mul_down, debt=ray_mul_up+ceil_div; treasury=all round-down. Matches canonical Aave V3.3.
- **PR #81 treasury delta** (the only post-audit logic change): index-delta form `ray_mul_down(scaled_debt, nextIndex−currIndex)` is mathematically equivalent and *strictly more conservative* (single round-down); monotonic-index assert prevents underflow; benign, can't be gamed/dust-minted.
- Liquidation seize math rounds down + hard-capped at user balance (no over-seize); HF biased downward (can't fake-heal); compounded interest uses continuous e^(r·t) (over-charges borrowers ~4e-6, favors protocol). Decimals ≤18, symmetric normalization, no cross-decimal mis-scale.

### Core logic + Move resource/auth model — clean
- **Auth:** all entry points derive the actor from `signer::address_of` (never trust caller-supplied actor); state-mutating reserve/user setters are `public(friend)` (logic-modules-only); `internal_borrow` asserts `user==on_behalf_of` (no borrow against third party); ACL grant_role admin-gated.
- **Scaled-balance accounting:** mint/burn round in the protocol's favor every direction, scaled total supply in lockstep, assert nonzero — no free aTokens / debt erasure.
- **Token transfer:** a/debt token primary stores **force-frozen on credit** + FAs carry **no dispatch hooks** → closes both dispatchable-hook reentrancy and transfer-to-dodge-HF; debt tokens non-transferable; aTokens move only via pool transfer (post-move HF check) or friend-only liquidation.
- **Flashloan:** ability-less hot-potato receipts (no drop/store/key), consumable only by `pay_flash_loan_*` which enforce amount+premium or convert to a validated debt position — can't skip repayment / re-enter.
- **HF/liquidation:** `validate_liquidation_call` enforces HF<1e18; seizure clamped to collateral balance + 1-wei over-send guard + close-factor + dust guard. Isolation debt-ceiling + e-mode category re-validated on borrow.

## Submission
**Nothing submitted.** A faithful, hardened, elite-audited (Certora FV + Spearbit + Ottersec + CTF) Move port with no meaningful post-audit delta; the Move-specific residual (ray-math Cetus class + resource/auth model) held up. Honest negative. (Info-only nit: dead commented-out duplicate HF asserts in validation_logic.move:454-458 — the live assert at :472-475 enforces the same check.)
