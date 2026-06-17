# P159 — Option-A candidate #3 (Wildcat market) — measured outcome

**Phase:** P159 · **Campaign:** Option-A conversion · **Status:** research_only, routing_allowed=false,
submission_ready=false · **Candidate:** `H7-wildcat-market-unprivileged-value-path` ·
**Outcome:** `static_false_positive` (source-refuted at precheck; no harness built) ·
**Duplicate:** `duplicate_unknown` (holdout; `_sealed_answer_key` not opened).

This phase executed the existing pipeline as-is. No prompts, detectors, taxonomy, dashboard, routing,
severity policy, submission policy, or corpus were changed. Production contract source is byte-identical.
The only data outputs are this write-up and one appended campaign-ledger row.

---

## 1. Shortlist (read-only pre-screen)

| Candidate (new arch) | Files / deps | Direct value + attacker field | Severity ceiling | Likely blocker |
|---|---|---|---|---|
| **Wildcat** `WildcatMarket{,Base,Config,Token,Withdrawals}` | 33 / 3 imports, no oracle | deposit / transfer / queue+executeWithdrawal; field=`amount` | High (lender funds) | **permissioned lenders + conservative scaled accounting** |
| basin **Well** (AMM) | 32 / 0 imports | swapFrom / shift / skim / removeLiquidity | High | permissionless but AMM-conditional/MEV/donation; ABDK + Aquifer-clone deploy |
| looksrare Aggregator | 33 / 4 | execute(orders) | Med–High | value needs victim approvals → victim-action / conditional |
| salty | 129 / 185 | swap / stake | High | heavy deploy graph; staking uses cooldowns → time/environmental |
| munchables | 70 / 39 | lock manipulation | Med | heavier deps; lock exploit is time/environmental |
| spectra | 48 / 106 | ERC4626 rate | Med | same class H4/H6 already covered (rate-mismatch) — avoid repeat |

## 2. Selection + rejection

**Selected:** Wildcat WildcatMarket family — it passed every P159 selection rule *on paper*: public
deposit/withdraw entrypoints, direct value movement, attacker-controlled `amount`, no keeper for the core
accounting, light self-contained deps (no oracle), and a feasible light real-contract harness
(`WildcatMarketBase` constructor pulls params from `IWildcatMarketController(msg.sender).getMarketParameters()`,
so the real market deploys from a ~20-line mock controller + mock ERC20 + mock sentinel — no clone, no RPC).

**Rejected (recorded):** basin Well held as fallback (permissionless reach but conditional/MEV bug classes +
heavier ABDK/Aquifer-clone deploy → lower *confirmable* conversion); looksrare = victim-action-dependent
value; salty = heavy graph + cooldown/time; munchables = heavy deps + time; spectra = rate-mismatch class
already exercised (H4/H6).

## 3. Source reachability map (the decisive precheck)

Entry points and who can actually reach the value path:

| Function | Visibility | Reachable by arbitrary EOA? | Value to caller |
|---|---|---|---|
| `deposit` / `depositUpTo` | external | **No** — `_getAccountWithRole(msg.sender, DepositAndWithdraw)` → reverts unless `controller.isAuthorizedLender(msg.sender)` (KYC-gated lenders) | n/a |
| `queueWithdrawal` | external | **No** — same role gate (`WithdrawOnly`) | n/a |
| `WildcatMarketToken.transfer` | external | sender needs a scaled balance (so a lender); recipient via `_getAccount` (no role) | recipient gets tokens it **cannot** withdraw (Null role fails `queueWithdrawal`) → griefing only |
| `executeWithdrawal(account, expiry)` | external | Yes (permissionless) | pays the **owed lender** `account`, not `msg.sender` → caller gains nothing |
| `collectFees` | external | Yes | pays the **immutable `feeRecipient`** → caller gains nothing |
| `nukeFromOrbit` / `stunningReversal` | external | Yes | **sanctions-gated** (`sentinel.isSanctioned`) → environmental, not attacker-forced |
| `processUnpaidWithdrawalBatch` / `updateState` | external | Yes | fair pro-rata / accrual bookkeeping → no caller value |

Call path to the accounting delta: `deposit → _getAccountWithRole (ROLE GATE) → scaleAmount → scaledBalance`.
The gate sits *before* any value movement, so an unprivileged attacker never reaches the mint/burn math.

## 4. Defense map

| Defense | Location | Covers the hypothesised bug? |
|---|---|---|
| Lender authorization gate | `WildcatMarketBase._getAccountWithRole` :197–213 (`controller.isAuthorizedLender`) | **Covers** — blocks arbitrary-EOA deposit/withdraw |
| Conservative scaled accounting | `MarketState.scaleAmount`/`normalizeAmount` (rayDiv/rayMul); dust comment `WildcatMarketWithdrawals` :60–61 | **Covers** — rounding leaves dust *in the protocol*, not to the caller |
| `scaleFactor` only moves via time | `_getUpdatedState`/`updateScaleFactorAndFees` (interest accrual on `block.timestamp`) | **Covers** the "attacker-forced, non-time" premise — any rounding divergence requires elapsed interest, and even then favors the protocol |
| Fixed-party payouts | `executeWithdrawal`→owed lender; `collectFees`→immutable `feeRecipient` | **Covers** — permissionless callers cannot redirect value |
| Sanctions gate | `sentinel.isSanctioned` on `nukeFromOrbit`/`stunningReversal` | **Covers** — those paths are environmental, not attacker-forced |

## 5. Runtime harness

**Not built.** The source precheck is decisive (the unprivileged-value premise is refuted before any math is
reached), so a harness would only re-confirm an absence. This is the H6 lesson applied: a cheap source-refute
beats a heavy harness. Deploy feasibility was confirmed (light, ~20-line mock controller) but spending it was
unwarranted — `runtime_status=not_run`, ledger-only (matching H6).

## 6. Conversion classification

```
mechanism_confirmed : false   (unprivileged direct-value path is absent / guarded)
attacker_reachable  : false   (deposit/withdraw gated by controller.isAuthorizedLender)
severity_bearing    : false   (permissionless fns pay fixed parties; rounding favors protocol)
novelty_clear       : not_assessed (source-refuted before novelty)
reportable          : false
outcome             : static_false_positive
primary_blocker     : unprivileged_value_path_absent_permissioned_or_value_neutral
reachability_verdict: permissioned_lender_gated_not_unprivileged
severity_class      : design_low_no_unprivileged_path
duplicate_status    : duplicate_unknown
```

## 7. What P159 taught the trainer

1. **Add a reachability pre-gate to selection, ordered FIRST.** Wildcat passed every existing selection rule
   (file-count, direct-value, attacker-controlled field, no-keeper, light-deps) yet failed on a dimension the
   rules don't check up front: *are the value-bearing entrypoints permissionless for an arbitrary EOA?*
   Permissioned lending / RWA / KYC arches sail through the paper filters and then die at reachability.
   **Proposed selection field (pre-screen, not a system change here): `value_entrypoints_permissionless ∈
   {yes, gated, victim_action}` — require `yes` before harnessing.**
2. **"Direct value" is necessary but not sufficient — the caller must be the value recipient.** Wildcat's
   permissionless functions move value, but always to a *fixed* party (owed lender, immutable feeRecipient),
   so a permissionless caller gains nothing. Selection should ask *"does `msg.sender` receive the value?"*
3. **"No keeper, non-time" excludes most lending-arch bugs.** In Wildcat every accounting divergence is gated
   behind time-based interest accrual *and* rounds dust to the protocol — so the attacker-forced/non-time rule
   structurally rules out the only arithmetic surface.
4. **The converting profile is narrow and largely harvested.** Across P147–P159 the profile that converts is
   *single-contract, permissionless, attacker-is-recipient, logic-omission/parity* (centrifuge escrow, decent
   fee-collector, abracadabra boost, blackhole distributor). Remaining fresh holdout arches are permissioned
   (wildcat), AMM-conditional (basin), time/keeper (salty/munchables), or victim-action (looksrare). The next
   candidate should be screened for the permissionless + attacker-is-recipient + logic-omission profile
   *before* the cheap filters, or the campaign should accept that honest non-conversions are the expected
   majority outcome at this stage.

## Campaign funnel (H5 → H6 → H7)

3 candidates · 1 runtime_confirmed (H5, prior) · 1 reportable_candidate (H5) · 1 source-refuted FP (H6) ·
1 source-refuted FP (H7) · **0 submission_ready**. H7 *downgraded at precheck* with a reason (permissioned
reachability) — a measured downgrade, not an engineered confirm.

**Boundaries:** no production/harness/prompt/detector/taxonomy/dashboard/routing/severity/submission/corpus/
sidecar/symlink change; runtime sidecar byte-identical (no row appended — H7 not_run); ledger append-only;
all flags research_only/routing_allowed/submission_ready = false.
