# P162 — Option-A Campaign Study Guide (H5–H9)

**Phase:** P162 · **Type:** documentation-only (no hunting, no harness, no submission, no detector/prompt/
dashboard/taxonomy/routing/pipeline change) · research_only=true / routing_allowed=false /
submission_ready=false.

This guide turns the completed "run 5 more" Option-A campaign into a reusable, source-grounded selector for
future autonomous hunting. It is a training manual for the precision-AI selector, not a vuln report.

---

## 1. Executive summary

- The campaign ran **5 candidates** (H5–H9).
- **Results: 1 runtime_confirmed, 1 reportable (both H5), 4 static_false_positive (H6–H9), 0 submission_ready.**
- The **last two phases (P160 basin, P161 hybra) built 0 harnesses** — the strict 4-gate pre-screen refuted
  both candidates from source before any harness work, converting "harness-then-discover" into cheap,
  named-gate source rejections.
- The campaign **did not fabricate any confirms.** Every false positive is recorded with exact source refs
  and a named blocker; no candidate was upgraded to fit a desired outcome.
- After the single positive anchor (H5), the **honest steady-state was gated rejection, not repeated
  reportables** — the converting profile is genuinely scarce in the remaining holdout corpus. That is a
  correct precision result, not a failure: a selector that mostly rejects, with reasons, is doing its job.

## 2. Campaign outcome table

| ID | Protocol / contract | Target shape | Decision | Harness? | Primary blocker / confirmation reason | Trainer lesson |
|---|---|---|---|---|---|---|
| **H5** | abracadabra `LockingMultiRewards` | staking/locking reward weight retained after lock expiry | **RUNTIME_CONFIRMED → REPORTABLE_CANDIDATE** (severity bounded Low; human review) | **Yes** (real Foundry, 4/4) | de-boost correction exists only in operator-gated `processExpiredLocks`; reward accounting omits it lazily → expired locker keeps 3× weight at honest stakers' expense | **Positive anchor**: a correction (de-boost) exists but an economically-equivalent path omits it; attacker is the recipient |
| **H6** | pooltogether `PrizeVault` (ERC4626) | deposit/withdraw preview rate mismatch | STATIC_FALSE_POSITIVE (source-refuted) | No | `_depositAndMint` `revert LossyDeposit` + debt-aware `previewWithdraw/Redeem` make the bad state unreachable/inert | a suspicious state transition is not a bug if a guard makes it unreachable or economically inert |
| **H7** | wildcat `WildcatMarket{,Base,Config,Token,Withdrawals}` | lender deposit/withdraw accounting | STATIC_FALSE_POSITIVE (source-refuted) | No | deposit/withdraw gated by `controller.isAuthorizedLender`; permissionless fns pay fixed parties; scaled accounting rounds dust to protocol | "value moves" ≠ bug; the unprivileged caller must reach the path AND receive the benefit |
| **H8** | basin `Well` (AMM) | permissionless `shift`/`skim`/`sync` with caller-chosen recipient | STATIC_FALSE_POSITIVE (gate-refuted) | No | value is a `balanceOf − reserves` surplus the attacker must self-fund; swaps slippage-protected; view-twins + `_setReserves` guard | permissionless + recipient-controlled still fails if the delta is self-funded / MEV / donation-conditional |
| **H9** | hybra `RewardsDistributor` (ve(3,3)) | `claim` vs `claim_many` recipient parity | STATIC_FALSE_POSITIVE (gate-refuted) | No | `claim`≡`claim_many`; checkpoint in shared `_claim`; pays `ownerOf`; **no managed/original-owner correction layer** to omit | the bug is not the sibling pair — it's a correction layer applied in one path and omitted in the other |

Cross-campaign anchor for the predictor (claim/claim_many family): velodrome **H2** (sibling yes, layer **no**)
→ refuted; hybra **H9** (sibling yes, layer **no**) → refuted; blackhole **B5** (sibling yes, layer **yes** =
AVM `getOriginalOwner`) → confirmed.

## 3. Positive anchor: what converted (H5)

**Contract:** abracadabra `LockingMultiRewards` (staking + locked-boost rewards).

- **What made it pass selection:** single-contract, light deps (only ERC20 mocked), public unprivileged
  entrypoints, direct reward value, no oracle, deploy-light real-contract harness feasible.
- **Which gates mattered:** permissionless entrypoint (PASS), attacker-is-recipient (PASS), logic-omission
  comparand (PASS — a real de-boost correction exists elsewhere). Gate 3 (non-time) was the *bounding* axis,
  not a kill: the over-accrual grows with operator delay, which capped severity but did not refute the
  mechanism.
- **Why attacker reachability was real:** `stake`/`lock`/`getReward` are public (`whenNotPaused`); an
  arbitrary EOA locks, lets the lock expire, and keeps earning — no role/KYC/victim action.
- **Why the value path benefited the attacker:** the expired locker's boosted weight (`bal.locked * mult`)
  keeps counting in reward accounting, so the attacker (the locker) over-accrues ~3× an equal unlocked
  staker's share — value flows to the attacker at honest stakers' expense (zero-sum redistribution).
- **Source-backed omission:** the de-boost correction is implemented **only** in the operator-gated
  `processExpiredLocks`; it is **not** applied lazily when rewards are computed. So one path (operator
  maintenance) applies the correction and the economically-equivalent path (ongoing reward accrual) omits it.
- **Why it became reportable:** a real Foundry PoC on the unmodified contract proved mechanism + reachability
  + impact (window-by-window 3:1 unprocessed vs 1:1 processed; over-accrual == honest-staker loss).
- **Why it was NOT automatically submission_ready:** severity bounds to **Low** because de-boost is performed
  by an automated keeper (Gelato) — magnitude depends on operator-liveness delay; novelty is
  `public_known_but_not_duplicate` (a public C4 contest, not locally dup-checkable); operator-scope is a
  program-value call. Mechanism is settled; severity/scope/novelty are explicitly deferred to a human
  (P155/P156/P157 packaging).
- **What future selection should copy:** look for a **correction that exists in one place but is omitted on
  an equivalent, attacker-reachable path**, where the **attacker is the recipient** of the resulting excess.
  Prove the mechanism with a real-contract PoC; keep severity/novelty/scope as separate, human-owned axes.

## 4. False-positive classes: what did not convert

- **H6 — guard makes the bad state unreachable/inert.** A lossy-deposit / preview-rate-mismatch shape
  existed, but `_depositAndMint`'s `revert LossyDeposit` and debt-aware `previewWithdraw/Redeem` prevent the
  exploitable state. *Lesson:* a suspicious state transition is not enough — check whether a source-level
  guard makes the bad state unreachable or economically inert before believing the shape.
- **H7 — permissioned / value-neutral for an arbitrary caller.** An apparent deposit/withdraw value path
  existed, but it is gated by `controller.isAuthorizedLender` (KYC lenders) and the permissionless functions
  pay fixed parties (owed lender, immutable feeRecipient). *Lesson:* "value moves" is insufficient — the
  unprivileged caller must be able to **reach** the path and **receive** the benefit.
- **H8 — self-funded / MEV / donation-conditional.** `shift`/`skim`/`sync` are permissionless with a
  caller-chosen recipient, but the payout is a `balanceOf − reserves` surplus the attacker must first create
  (donation), and swaps are slippage-protected. *Lesson:* permissionless **plus** recipient-controlled still
  fails if the attacker must self-fund the delta or rely on conditional market positioning.
- **H9 — sibling pair without a correction layer.** The exact `claim`/`claim_many` shape existed, but the two
  are economically equivalent through the shared `_claim` (checkpoint included), both pay `ownerOf`, and there
  is no managed-NFT / original-owner / recipient-correction layer. *Lesson:* the bug is not the sibling pair;
  the bug is a **correction layer applied in one path and omitted in the other**.

## 5. Updated selection guidance — "Correction-layer-first selector"

Apply in order. **First** ask whether a correction/indirection layer exists; **then** whether two
economically-equivalent paths treat it differently; **then** apply the strict 4-gate pre-screen; **only then**
consider harnessing.

**A. Correction layer exists**
- managed / original owner · escrow / delegate / canonical recipient · account-to-beneficiary mapping ·
  loop-carried state · reward checkpoint / paid accounting · any other explicit source-level indirection.

**B. Path divergence exists**
- single path applies the correction, batch path omits it · withdraw path validates recipient, batch sibling
  skips it · one path updates accounting, sibling omits/misorders · loop should carry updated state but reuses
  the initial value.

**C. Attacker reachability exists**
- arbitrary EOA can call · no role / KYC / keeper / victim-action gate · no victim approval requirement.

**D. Attacker benefit exists**
- caller or caller-controlled address receives the excess value · value is **not** merely returned to the
  rightful owner · value is **not** fixed to protocol / fee recipient / lender / immutable recipient / victim.

**E. Mechanism is not time/MEV/self-funded**
- not primarily interest accrual · not cooldown timing · not oracle freshness · not donation/skim reserve
  delta · not dust-to-protocol · not pure slippage/MEV.

**F. Source-backed comparand exists**
- a sibling path · a corrected reference path · an existing guard/checkpoint/accounting update · a documented
  canonical recipient · an invariant enforced elsewhere.

## 6. Harness decision rule

**Do not build a harness unless ALL of these are true:**
- a correction / indirection layer exists,
- two economically-equivalent paths diverge on that layer,
- an unprivileged caller reaches the path,
- the caller or a caller-controlled address can benefit,
- the mechanism is not time / keeper / MEV / self-funded,
- a source-backed comparand exists.

If **any** condition fails → classify `SOURCE_REFUTED_NO_HARNESS` with the named blocker. (Equivalently: A∧B∧
C∧D∧E∧F ⇒ `HARNESS_ALLOWED`; otherwise no harness.)

## 7. Updated candidate labels (for future phases)

- `CORRECTION_LAYER_PRESENT` — an explicit correction/indirection layer exists in source.
- `CORRECTION_LAYER_ABSENT` — no correction/indirection layer (sibling pair alone is weak evidence).
- `PATH_DIVERGENCE_PRESENT` — two equivalent paths treat the correction layer differently.
- `PATH_DIVERGENCE_ABSENT` — equivalent paths share the corrected logic (no divergence).
- `ATTACKER_RECIPIENT_CONFIRMED` — caller / caller-controlled address receives the excess value.
- `ATTACKER_RECIPIENT_ABSENT` — value goes to owner / protocol / fee recipient / immutable / victim.
- `SELF_FUNDED_OR_MEV_CONDITIONAL` — gain depends on donation/reserve-delta/MEV/self-funded positioning.
- `PERMISSIONED_VALUE_PATH` — entrypoint requires role / KYC / controller / keeper / victim action.
- `SOURCE_GUARD_REFUTES` — a source-level guard makes the bad state unreachable or economically inert.
- `HARNESS_ALLOWED` — all six harness-rule conditions hold.
- `SOURCE_REFUTED_NO_HARNESS` — at least one condition fails; refuted from source, no harness built.

## 8. Prompt patch recommendation (RECOMMENDED — NOT APPLIED in P162)

> The following is a future recommendation only. P162 does not modify any prompt. Apply later as a separate,
> human-approved change to the candidate-selection prompt(s).

```
[candidate-selection prompt patch — proposed]
1. Screen for a correction/indirection layer (managed/original owner, escrow/delegate/canonical recipient,
   account-to-beneficiary map, loop-carried state, reward checkpoint) BEFORE looking for sibling-pair shape.
2. Treat claim/claim_many (and any single/batch pair) as WEAK evidence unless a recipient-correction layer
   exists that one path applies and the other omits.
3. Treat "direct value movement" as INSUFFICIENT unless the attacker (or a caller-controlled address) is the
   recipient of the excess.
4. Reject — before any harness — candidates that are permissioned, time-primary, MEV/donation/self-funded,
   or pure arithmetic without a comparand.
5. Require a concrete source-backed comparand (sibling path / corrected reference / existing checkpoint /
   documented canonical recipient / invariant enforced elsewhere) before HARNESS_ALLOWED.
```

## 9. Dashboard / triager implication (guidance only — not implemented in P162)

- Surface strict-gate failures as **successful precision outcomes**, not dead ends (a refuted-at-gate row is a
  saved harness, not a miss).
- Display the **first failed gate** prominently on the candidate row/detail.
- Display whether a **correction layer exists** and whether the **attacker is the recipient** as first-class
  fields.
- Display `HARNESS_ALLOWED` only when **all** gates pass.
- Keep `STATIC_FALSE_POSITIVE` visually and semantically **distinct from `NEEDS_CONTEXT`** (refuted vs.
  unresolved-needs-human).

## 10. Integrity

- **Documentation-only phase.** No production source changed. No harness built. No detector / taxonomy /
  dashboard code / routing / prompt / schema change. Existing frozen corpus unchanged. Runtime sidecar
  unchanged (read-only references only). Campaign ledger unchanged — **no ledger row** (P162 is not a
  candidate; the ledger schema is per-candidate). All edits are confined to this P162 documentation directory.
- Hash table is recorded in `integrity_checks.md` alongside this guide.

## 11. Final recommendation

- **Close the H5–H9 campaign.** Its measurement goal is met: one positive anchor and a validated precision
  filter.
- **Preserve H5 for human submission review** if desired — the P157 Low-severity human-review package is ready;
  mechanism is settled, severity/scope/novelty are the human's call.
- **Use the correction-layer-first selector (§5–§6) for the next corpus hunt.**
- **Do not continue grinding the depleted holdout shortlist** — its converting profile is exhausted; point the
  next hunt at a fresh corpus and screen for a correction-layer-bearing distributor/escrow first.
