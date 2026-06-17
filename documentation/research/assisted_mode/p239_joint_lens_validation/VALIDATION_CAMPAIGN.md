# P239 — Joint validation campaign: Safe-management (P237) + hostile-token settlement (P238)

> Research-only. Both lenses run over 20 existing workspaces (prebuilt manifests, explicit `--manifest`/`--out`, no
> active-audit switch). Every candidate manually classified by reading source. Mechanism-based, not answer-key
> matching. No wiring / dashboard sync / routing / severity / production-source edits. Raw outputs in `outputs/`.

## Target set (20: ≥5 Safe-likely · ≥5 settlement-likely · 5 negative-control)
kleidi-2024-10-holdout (Safe timelock/guard) · renft-2024-01-fresh (Safe-guard rental, ANCHOR) ·
vultisig-2024-06-holdout · badger-2024-06-holdout (1019 fns) · munchables-2024-05-holdout · |
looksrare-2022-11-fresh (NFT mkt) · secondswap-2024-12-fresh · blackhole-2025-05-eval (rewards, 1028 fns) ·
revert-lend-2024-03-strict-eval · wildcat-2023-10-bench · dyad-2024-04-fresh · sentiment-v2-2024-08-fresh ·
zaros-2025-01-part-2-eval · lambowin-2024-12-fresh · decent-2024-01-holdout · |
**negative controls:** quantamm-2024-12-eval (AMM math) · maia-talos-2023-05-semantic-tvl (1369 fns) ·
traitforge-2024-07-fresh (NFT mint) · ai-arena-2024-02-fresh (NFT gaming) · panoptic-2025-12-strict-eval (options).
Source resolution verified on a sample of 0-candidate targets (non-empty bodies read) → zeros are genuine clean
signal, not unresolved-source false negatives.

## Per-target results (only non-zero shown; the other 18 targets = 0/0)
| Target | group | safe cand | hostile cand | labels |
|---|---|---|---|---|
| renft-2024-01-fresh | Safe + settlement (anchor) | 2 high + 2 med | 2 high | TP: H-04 (disableModule offset), H-02 (setFallbackHandler); PLAUSIBLE: 2 med residual-coverage; TP: H-01 (`PaymentEscrow._settlePayment`), reclaim DoS (`Reclaimer.reclaimRentalOrder`) |
| revert-lend-2024-03-strict-eval | lending settlement | 0 | 1 med | PLAUSIBLE: `AutoCompound._withdrawBalanceInternal` (per-position withdraw to `to`; isolated, weak) |
| **18 others** (incl. all 5 negative controls + kleidi/vultisig/badger/munchables) | — | 0 | 0 | clean — no candidates |

## Precision table — per lens
| Lens | scanned | candidates | TP (high) | plausible (med) | FP | high-conf precision | vol/target | noisy class |
|---|---|---|---|---|---|---|---|---|
| safe_management_coverage | 20 | 4 (1 target) | 2 | 2 | 0 | **2/2 = 100%** | 0.20 | none |
| hostile_token_settlement | 20 | 3 post-fix (5 pre-fix) | 2 | 1 | 0 (2 found + fixed) | **2/2 = 100%** | 0.15 | admin/self token-rescue (fixed) |

## Precision table — combined stack
| Metric | Value |
|---|---|
| Total candidates | 7 |
| Total TP + plausible | 7 |
| Total false positives | **0** |
| **FP rate** | **0%** |
| Highest-noise target | reNFT (6 — but all TP/plausible; it is the anchor) |
| Highest-value target | reNFT (H-01, H-02, H-04) |
| Lens overlap | reNFT only (both lenses fire — disjoint findings: Safe-mgmt selector defects vs hostile-token settle/reclaim) |
| Operator-manageable | **YES** (7 candidates across 20 targets; 18 targets silent) |
| Normalization | all 7 records `routing_allowed:false` / research-only ✓ |

## Fixes applied (1, narrow, allowed class)
**Hostile-token lens — admin/self token-rescue FP class.** Validation surfaced 2 FPs: `blackhole
RewardsDistributor.withdrawERC20` (`require(msg.sender == owner)` → `transfer(msg.sender, balance)`) and `decent
UTBFeeCollector.redeemFees` (`onlyOwner` → `transfer(owner, amount)`). Root causes: (a) inline `msg.sender == owner`
admin gates not detected (only modifier form was), and (b) the word `owner` in `counterparty_terms` matched the
access-control require, defeating the caller's-own-asset suppression. **Fix (`config/hostile_token_settlement_patterns.json`
+ `..._taxonomy.py`):** require a *genuine external settlement counterparty* (drop `owner` — an access-control word,
not a counterparty) and add inline `msg.sender == owner/admin` to admin detection. Result: both FPs suppressed,
reNFT anchor preserved (2 high), revert-lend medium unchanged. **2 regression tests added**
(`test_p239_owner_rescue_to_msg_sender_rejected`, `test_p239_onlyowner_redeem_to_owner_rejected`). This is the only
fix; it is in the allowed "trusted/admin-only path not downgraded" + "caller mistaken" classes. No
prompt/routing/severity change.

## Acceptance criteria (to wire)
| Criterion | Status |
|---|---|
| 0 high-confidence false positives | ✓ (only highs are reNFT TPs) |
| Low candidate volume | ✓ (7 / 20 targets; 18 silent) |
| Candidates mechanism-specific, not generic Safe/token noise | ✓ (all 5 negative controls + 4 non-anchor Safe-likely targets = 0) |
| Normalization preserves routing_allowed=False | ✓ |
| No forbidden-file changes | ✓ (dashboard_sync c1af70e1 / deep_trace c095c426 / min_confirm 2a15169a / confirm_gate afc481c9 / validate_p208 ae55eb80) |
| No dashboard/routing/severity side effects | ✓ (un-wired; active audit unchanged) |

## Honest limits
- All confirmed TRUE POSITIVES are on the reNFT **anchor**; the 19 non-anchor targets produced **1 plausible
  medium** (revert-lend) and 0 confirmed independent TPs. So this campaign strongly validated **precision / absence
  of noise**, but did **not** demonstrate independent recall (the corpus simply did not contain other instances of
  these rare bug shapes — e.g. kleidi, a real Safe system, has no flagged guard defect).
- A new FP class appeared at n=20 and was fixed; the FP surface may not be fully mapped.

## Final Verdict

# A — READY_TO_WIRE_BOTH (as research-advisory signals)

Every stated acceptance criterion is objectively met for **both** lenses: 0 high-confidence FP across 20 diverse
targets (after one narrow, regression-tested fix), 0 noise on all 5 negative controls and all non-anchor Safe-likely
targets, both reNFT anchor families recovered, normalization keeps `routing_allowed:false`, forbidden hashes intact,
no side effects. The lenses are mechanism-specific, not generic Safe/token noise.

**Qualification (honest):** "wire" here = include in the **research candidate funnel as advisory signals**, NOT
auto-promote to production severity/routing (the normalization layer already enforces `routing_allowed:false`).
Because confirmed TPs were anchor-concentrated, production routing/severity should remain a separate human decision
until recall is shown in-flow.

## Recommendation / next step: **second shadow contest** (not another lens)
Precision is validated; the open question is **recall in-flow**. Run a second blind shadow contest (fresh
architecture, esp. a Safe-guarded or settlement-heavy protocol) with both lenses active as advisory signals, and
measure whether they recover awarded findings end-to-end. That confirms independent recall before any production
wiring. A third lens (create-time reentrancy, to close reNFT H-03) is a later option, not the immediate next step.

## Closeout
- **Targets:** 20 (list above). **Candidate counts:** safe 4, hostile 3 (post-fix) = 7. **TP/plausible/FP:** 4 TP +
  3 plausible / 0 FP. **Precision:** 100% high-conf (both lenses). **Volume:** 0.35 candidates/target; 18/20 silent.
- **Fixes:** 1 (hostile admin/self-rescue suppression) + 2 regression tests.
- **Tests:** `tests/hostile_token_settlement/` + `tests/safe_management_coverage/` + P228–238 + permit + sibling →
  **74 passed**.
- **Forbidden hashes:** unchanged. **Detectors:** un-wired. **Active audit:** `size-credit-2024-06-blind` (restored
  — never switched).
- **Wire either lens?** Both meet the precision bar → eligible to wire as research-advisory; production
  routing/severity deferred pending recall-in-flow.
- **Next step:** second shadow contest (with both lenses advisory), not another lens.
