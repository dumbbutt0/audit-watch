# TipRun — submission packet (un-submitted findings)

Human-curated decision view for the findings not yet submitted. Each finding already has a platform-paste-ready
write-up at `<ID>/SUBMISSION.md` and a passing PoC under `<ID>/poc/` (run all: `cd ../harness && forge test
--match-path 'test/PoC_*.t.sol' -vv`). **Nothing here is submitted** — this is the operator's submit/hold call.

**Already submitted (not in this packet):** F-1 (Critical, `in_review`), M-1 (Medium, `in_review`, merged into
F-1), F-2 (High, **`out_of_scope`** — perp `Risk` margin engine not wired on the live profile).

**The F-2 lesson drives the ordering below:** F-2 was a *valid* bug rejected on **deployment reachability**, not bug
validity. So the packet is ordered by *submittability* = severity × how confident we are the path is live, and every
finding leads with its reachability/scope caveat — the single thing that decides whether it's worth submitting.

---

## Tier 1 — strong submit candidates (live path, attacker-reachable)

### N-1 — Privilege escalation to `ALLOW_ADMIN` → drain any account · **High**
- **Mechanism:** `PermissionsTransLib.processAdminSetSignerPermissions` trusts the caller-supplied `adminAccountId`
  (never bound to the canonical admin), and registration-time signer masks aren't delegation-gated. Any user
  self-mints `ALLOW_ADMIN` on their own account, then grants `ALLOW_WITHDRAW` on any victim and drains it.
- **Reachability:** permissionless from the attacker's side (register → escalate → withdraw). Residual bound is the
  trusted batcher relaying the txs — an *on-chain* authorization defect, not a trust assumption.
- **PoC:** `PoC_PermissionEscalation` (drains victim collateral 5000). Write-up: `N-1/SUBMISSION.md`.
- **Pre-submit:** ☐ confirm the live batcher relays user-supplied `REGISTER_ACCOUNT` / `ADMIN_SET_SIGNER_PERMISSIONS`
  / `WITHDRAWAL` txs (not filtered off-chain) ☐ novelty vs prior TipRun audits ☐ KYC.

### M-3 — Liquidate/Deleverage seize healthy accounts (no on-chain maintenance-margin precondition) · **Medium**
- **Mechanism:** `LiquidateTransLib` / `DeleverageTransLib` have no on-chain check that the target is actually below
  maintenance margin, so a (mis-)submitted liquidation can seize a perfectly healthy account.
- **Reachability:** operator/keeper-submitted, but the *missing on-chain guard* is the finding — a single bad input
  has unbounded effect with no contract-level backstop. State the trust dependency explicitly.
- **PoC:** `PoC_NoLiquidatablePrecondition`. Write-up: `M-3/SUBMISSION.md`.
- **Pre-submit:** ☐ frame as missing-invariant / trust-boundary ☐ confirm program treats liquidation-keeper actions
  as in-scope ☐ novelty.

---

## Tier 2 — submit only after confirming the deployment profile (same reachability axis that put F-2 OOS)

### N-2 — Capability registry fails open: no-op margin check when no `CAP_MARGIN_CHECK` provider · **High (perp only)**
- **Mechanism:** `PositionManager._marginCheck()` falls back to `NullMarginCheck` (no-op) when no provider is
  registered, and `TransactionProcessor.registerPlugin` never *requires* one — so a perp deployment can run with
  maintenance-margin enforcement silently disabled (fail-open). Insolvent positions accepted → bad debt.
- **Reachability (decisive):** impact exists only on a deployment that *should* run the perp margin engine but
  doesn't have it wired. On the live predict/spot profile the no-op is intended — **the exact not-wired condition
  that put F-2 out of scope.** Submit only if the perp margin profile is in scope; otherwise it's a fail-open
  design/hardening note.
- **PoC:** `PoC_CapabilityRegistryNoop` (insolvent short 5000 vs 1000 accepted). Write-up: `N-2/SUBMISSION.md`.
- **Pre-submit:** ☐ **confirm target runs the perp margin profile** ☐ identify how `CAP_MARGIN_CHECK` could be absent
  (deploy/upgrade window, operator error) ☐ novelty ☐ otherwise submit as design note only.

### M-2 — Oracle has no read-side staleness + monotonic-update guard commented out · **Low**
- **Mechanism:** `Oracle.updatePrice` monotonic guard is commented out and `Oracle.getPrice` has no max-age, so a
  stale/rolled-back price is trusted by margin/liquidation indefinitely. Defense-in-depth gap (privileged update
  path; feeder trusted).
- **Reachability (decisive):** the *only* consumer is `Risk.getAssetValueAndRisk` via the `CAP_MARGIN_CHECK` provider
  — i.e. it has value impact **only on the same perp profile N-2/F-2 require**; on a `NullMarginCheck` profile nothing
  reads the price and this reduces to a code-quality note.
- **PoC:** `PoC_OracleStaleness`. Write-up: `M-2/SUBMISSION.md`.
- **Pre-submit:** ☐ confirm perp margin profile in scope ☐ frame as defense-in-depth (no unprivileged primitive)
  ☐ novelty.

---

## Tier 3 — trust/design notes (Low; state the trust dependency, expect possible "accepted design")

### M-4 — `setSyntheticAssetsInfo` skips the `configVersion` bump · **Low/Medium**
- **Mechanism:** the mutator for the most security-relevant per-asset config (risk segments, oracle signer set,
  quorum) doesn't call `incrConfigVersionInternal()`, so the stale-config batch guard in
  `MultiTransactionProcessor` never triggers for in-flight user txs signed against the old config.
- **Reachability:** admin-triggered (`PRIVILEGED_ONLY_REACHABLE`), but **live on all profiles** (the guard isn't
  perp-only). Undermines a built-in safety mechanism.
- **PoC:** `PoC_ConfigVersionNotBumped`. Write-up: `M-4/SUBMISSION.md`.
- **Pre-submit:** ☐ frame as admin-config / safety-mechanism-defeat ☐ confirm program treats admin-config issues as
  in-scope ☐ novelty.

### N-4 — Settlement mints collateral at an unconstrained operator price · **Low**
- **Mechanism:** `SettlementTransLib.process` credits `collateral += syntheticBalance * settlementPrice` with the
  price a raw operator input (no oracle binding, no signed-outcome binding, no aggregate YES/NO conservation), so a
  mis-priced settlement mints unbacked, later-withdrawable collateral.
- **Reachability:** operator-driven — **no permissionless exploit**; reported as a missing on-chain invariant.
- **PoC:** `PoC_SettlementUnconstrained` (mints 5000 unbacked at operator price 50 vs oracle 1). Write-up:
  `N-4/SUBMISSION.md`.
- **Pre-submit:** ☐ frame as missing-invariant / defense-in-depth ☐ state operator-trust dependency (program may
  treat as accepted design) ☐ novelty.

---

## Submission order (recommended)
1. **N-1** (High, on-chain auth bypass — submit first)
2. **M-3** (Medium, missing on-chain liquidation precondition)
3. **N-2** (High *iff* perp profile confirmed in scope — else design note)
4. **M-4** (Low/Medium, admin-config safety defeat — live on all profiles)
5. **N-4** (Low, operator-trust missing invariant)
6. **M-2** (Low, defense-in-depth — bundle with the perp-profile decision for N-2)

> Every write-up already states its caveat in-line. Before submitting any finding, clear its ☐ boxes above — the
> recurring blockers are **deployment reachability** (is the path wired on the live profile?) and **novelty** (is it
> a duplicate of a prior TipRun audit / known issue?), which is where the previously-adjudicated TipRun findings were
> rejected — not on PoC validity.
