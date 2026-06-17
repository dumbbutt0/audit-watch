# P160 — Option-A candidate #4 · STRICT 4-gate pre-screen · precision experiment

**Phase:** P160 · **Candidate:** `H8-basin-well-shift-skim-sync` (audit `basin-2024-07-holdout`, arch
`basin` — NEW) · **Decision:** `SOURCE_REFUTED_NO_HARNESS` · **Outcome:** `STATIC_FALSE_POSITIVE` ·
**Duplicate:** `duplicate_unknown` (holdout; `_sealed_answer_key` not opened) ·
research_only=true / routing_allowed=false / submission_ready=false.

**Purpose:** not to force a finding — to test whether moving the strict converting-profile filter to a
**pre-harness gate** prevents another P159/Wildcat-style false positive. It did: **0 harnesses built**, all
remaining shortlist candidates rejected from source evidence at the gate.

---

## 1. Candidate selected
Best remaining shortlist candidate = **basin Well** (`audits/basin-2024-07-holdout/contracts/src/Well.sol`).
Chosen because it is the only remaining shortlist item with *both* a permissionless entrypoint **and** a
caller-chosen recipient — i.e. the only one that even reaches gates 3–4.

## 2. Pre-screen table (basin Well — real source evidence)

| Gate | Verdict | Source refs |
|---|---|---|
| 1 · permissionless value entrypoint | **PASS** | `swapFrom` :207, `swapTo` :289, `shift` :381, `addLiquidity` :425, `removeLiquidityOneToken` :545, `removeLiquidityImbalanced` :596, `sync` :644, `skim` :686 — all `external nonReentrant`, no auth modifier |
| 2 · attacker-is-recipient | **PASS** | caller-supplied `recipient`: `swapFrom` :212, `shift` :384, `removeLiquidityOneToken` :549, `removeLiquidityImbalanced` :599, `sync` :644, `skim` :686 |
| 3 · non-time/non-keeper mechanism | **FAIL** | the recipient-controlled "excess" functions only pay out a surplus the caller must first create themselves: `skim` :691-695 transfers `balanceOf(this) - reserves`; `shift` :399 pays `reserves[j] - _calcReserve(...)`; `sync` :654-657 mints LP for `calcLpTokenSupply(balances) - totalSupply()`. All are **balance-vs-stored-reserve (donation/MEV) deltas**, not an attacker-forced net gain; swaps (:253, :307) are slippage-protected arithmetic. → rejected as MEV-only / self-funded surplus |
| 4 · logic-omission/parity/comparand | **FAIL** | every mutating fn has a consistent view-twin (`getSwapOut` :266, `getSwapIn` :336, `getShiftOut` :411, `getAddLiquidityOut` :487, `getRemoveLiquidityOneTokenOut` :569, `getSyncOut` :667) and `_setReserves` :714-719 guards `reserves[i] > balanceOf` (`InvalidReserves`). No sibling mismatch / missing recipient correction / missing accounting update — only AMM arithmetic with no source-backed comparand |

## 3. Decision
**`SOURCE_REFUTED_NO_HARNESS`** — basin Well fails gates 3 and 4. No harness built.

## 4. / 5. Harness
Not allowed → **not built**. No PoC directory, no mocks, no production-source modification, no sidecar row.

## 6. Shortlist gate-scan (cheap, source-only — the precision measurement)

| Candidate | G1 perm. | G2 recipient | G3 non-time | G4 comparand | Result | Killing evidence |
|---|---|---|---|---|---|---|
| **basin Well** (selected) | ✅ | ✅ | ❌ | ❌ | SOURCE_REFUTED | MEV/donation + no comparand (refs above) |
| looksrare aggregator | ✅ | ❌ | — | — | rejected G2 | `execute` moves the **caller's own** funds; leftovers returned to `originator` — LooksRareAggregator.sol:108-109, :64 |
| salty | ✅ | ✅ | ❌ | — | rejected G3 | `cooldownExpiration` — IStakingRewards.sol:15; staking time-gated |
| munchables | ✅ | — | ❌ | — | rejected G3 | time-gated pet/lock — SnuggeryManager.sol:220-242 |
| spectra | ✅ | ✅ | ~ | ❌ | rejected G4 | PrincipalToken rate/arithmetic (no comparand); rate-mismatch class already covered (H4/H6) |

**No remaining shortlist candidate passes all four gates.** Phase stops cleanly with the basin FP recorded.

## 7. Precision finding (the experiment's result)
- **The strict pre-screen prevented a harness on every remaining candidate** (0 built this phase) — including
  basin, which the P159-era selection rules (file-count/direct-value/light-deps) would have advanced to a
  harness (it passes gates 1–2 and looks like a clean AMM target).
- **It would also have caught P159's Wildcat at gate 1** (`deposit`/`queueWithdrawal` gated by
  `controller.isAuthorizedLender`) — i.e. the FP that cost a full post-hoc precheck in P159 is now a one-line
  gate-1 rejection.
- **Net:** the filter improves precision exactly as intended — it converts "harness then discover non-
  conversion" into "reject from source at a named gate, with refs." The cost is that, with the converting
  profile (single-contract · permissionless · attacker-is-recipient · non-time · logic-omission) now scarce in
  the remaining holdout corpus, the honest steady-state output is **gated rejections, not reportables**.

## Campaign funnel (H5 → H6 → H7 → H8)
4 candidates · 1 runtime_confirmed (H5) · 1 reportable_candidate (H5) · 3 static_false_positive
(H6 source-refuted, H7 source-refuted, H8 gate-refuted) · **0 submission_ready**. H8 is the first FP killed
*at the pre-screen gate* rather than after selection — the intended precision improvement.

**Boundaries:** no production/harness/prompt/detector/taxonomy/dashboard/routing/severity/submission/corpus/
SIDECAR/symlink change; runtime sidecar byte-identical (H8 not_run → no row); ledger append-only; all flags
research_only/routing_allowed/submission_ready = false.
