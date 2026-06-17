# P163 — Post-campaign retrospective & optimization design (H5–H9)

**Phase:** P163 · **Type:** retrospective + design, **documentation-only** (no hunting, no harness, no code
change). Every recommendation is `PROPOSED — NOT IMPLEMENTED`. research_only=true / routing_allowed=false /
submission_ready=false.

## Reading rules (applied throughout)
- Every claim is tagged **[DIRECT_EVIDENCE]** (observed in H5–H9 / B5 / H2), **[INFERENCE]** (generalized from
  ≤5 points), or **[SPECULATION]** (forward design, untested).
- **No recommendation is stated as established fact unless backed by DIRECT_EVIDENCE.**
- **Sample size is tiny (n=5 campaign + 2 cross-refs).** Any "rate" is descriptive of THIS campaign only;
  confidence intervals are wide. 1 confirmed reportable cannot establish precision/recall.
- **Do not assume the campaign succeeded.** 1/5 reportable + 0 submissions is *equally* consistent with
  "corpus depleted" and "selector over-tight" as with "selector working." Both readings are carried.

---

## Headline durable lesson (read this first)

**[DIRECT_EVIDENCE] The campaign's most durable, already-validated lesson is the source-grounded refutation
discipline — explicit, named-gate source refutation generated more value than additional harness
construction.** Evidence, observed directly in H5–H9: **4 candidates rejected without building a harness**
(H6/H7 source-refuted, H8/H9 gate-refuted), **0 fabricated confirmations**, and **1 real converter preserved**
(H5). This conclusion does not require extrapolation — it is what the campaign did.

**Distinguish this from the correction-layer selector, which remains a hypothesis (`INFERENCE`).** The
selector is the campaign's most *interesting* idea but its weakest-supported one (1 in-sample converter, 0
validated positive predictions). Ordering matters: **the validated discipline is the durable takeaway; the
selector is a candidate hypothesis to test next.** (Full justification in §1 "assumptions strengthened", §9,
and the Bottom line.)

---

## 1. Campaign retrospective

### What worked
- **Cheap source-refutation before harnessing.** [DIRECT_EVIDENCE] H6/H7 refuted from source; H8/H9 refuted at
  the strict gate; P160+P161 built **0 harnesses**. This is a real cost saving *measured on this campaign*.
- **No fabricated confirmations.** [DIRECT_EVIDENCE] Every non-converter carries source refs + a named
  blocker; nothing was upgraded to fit a desired outcome.
- **One genuine reportable with a real-contract PoC (H5).** [DIRECT_EVIDENCE] Mechanism + reachability +
  impact proven on unmodified production code.

### What failed / is unresolved
- **Only 1 reportable from 5, 0 submissions.** [DIRECT_EVIDENCE] The campaign produced no submitted finding.
- **H5 was never finished.** [DIRECT_EVIDENCE] Severity (bounded Low by keeper liveness) and novelty
  (`public_known_but_not_duplicate`, unresolved) remain human-pending; the "win" is a *candidate*, not a payout.
- **Cause of the 4 FPs is confounded.** [INFERENCE] We cannot separate "selector is good" from "remaining
  holdout corpus was depleted of converters." Both are live explanations; the data cannot distinguish them.
- **Selector may be over-tight.** [SPECULATION] A stricter gate that yields 0 harnesses for two phases could
  be discarding real bugs of other classes; we have no recall measurement to rule this out.

### Assumptions disproven
- **"claim + claim_many sibling pair ⇒ a bug."** [DIRECT_EVIDENCE] velodrome H2 and hybra H9 both have the
  pair and both refute — the pair alone predicts nothing.
- **"single-contract + permissionless + direct-value ⇒ attacker-reachable & beneficial."** [DIRECT_EVIDENCE]
  wildcat H7 is permissioned (isAuthorizedLender) and pays fixed parties; basin H8 is permissionless but
  self-funded/MEV. "value moves" ≠ "attacker profits."

### Assumptions strengthened
- **Attacker-is-recipient + real-contract PoC is the strongest converter.** [INFERENCE] Only H5 had it; it is
  the only converter — consistent but n=1.
- **Source-refute beats heavy harness when a guard/absence is decidable from source.** [DIRECT_EVIDENCE]
  H6/H7/H8/H9 all decided without a harness.

---

## 2. Conversion analysis

### Why H5 converted [DIRECT_EVIDENCE]
A de-boost **correction** exists in the operator-gated `processExpiredLocks`, but the ongoing reward-accrual
path **omits** it lazily → an expired locker keeps ~3× weight. The attacker **is** the recipient (the locker);
the loss is borne by honest stakers; a real Foundry PoC proved it on unmodified code. (Residual: severity
bounded Low by keeper liveness; novelty unresolved → reportable, not submission-ready.)

### Why H6–H9 did not [DIRECT_EVIDENCE, per candidate]
- **H6** — a source guard (`revert LossyDeposit` + debt-aware previews) makes the bad state unreachable/inert.
- **H7** — value path is permissioned (`isAuthorizedLender`) and permissionless fns pay fixed parties.
- **H8** — payout is a self-funded `balanceOf − reserves` surplus (donation/MEV), not an attacker-forced gain.
- **H9** — `claim`/`claim_many` are economically identical via the shared `_claim`; no correction layer to omit.

### Common FP characteristics [INFERENCE, n=4]
Value goes to a *fixed* party OR the attacker must *self-fund* the delta OR a *guard* neutralizes the state OR
there is *no correction comparand* a sibling could omit. Each FP fails on ≥1.

### Common converter characteristics [INFERENCE, n=1 + 1 cross-ref B5]
A recipient-correction/indirection layer exists; one economically-equivalent path applies it and another
omits it; an unprivileged caller reaches the omitting path; the caller (or a caller-controlled address) is the
recipient; the gain is not time/MEV/self-funded; a source comparand exists. **n is too small to call this a
law** — it is the working hypothesis.

---

## 3. Correction-layer taxonomy

Recipient-correction / ownership-indirection mechanisms. **Evidence column is the honest status**: only the
managed-NFT row is observed converting (B5); the rest are pattern-extrapolated.

| Layer | Mechanism | Source indicators (grep) | Common function names | Likely sibling-failure mode | Evidence |
|---|---|---|---|---|---|
| Managed-NFT original owner | a managed/auto-compounder NFT holds the veNFT; rewards must route to the *original* depositor, not the holder | `getOriginalOwner`, `managed`, `AVM`, `idToManaged`, `deposit_managed` | `claim`, `claim_many`, `getReward`, `_claim` | batch path uses `ownerOf` (the manager) instead of `getOriginalOwner` | **[DIRECT_EVIDENCE]** blackhole B5 confirmed |
| Original-owner lookup | a mapping records the canonical owner separate from current holder | `originalOwner`, `ownerOfAt`, `_owners[`, `beneficiaryOf` | `claim*`, `redeem*`, `withdraw*` | sibling reads live holder, not recorded owner | [INFERENCE] |
| Escrow beneficiary | funds escrowed for a named beneficiary; payout must read the beneficiary | `escrow`, `beneficiary`, `createEscrow`, `releaseEscrow` | `release*`, `claim*`, `execute*Withdrawal` | a parallel path pays `msg.sender`/holder, not the escrow beneficiary | [INFERENCE] (wildcat *has* escrow but is permissioned → not a converter here) |
| Delegate ownership | voting/reward power delegated; payout must resolve delegator vs delegate | `delegate`, `delegates(`, `_delegatee`, `moveDelegates` | `claim*`, `getVotes`, `getReward` | one path credits delegate, the equivalent credits delegator (or vice-versa) | [INFERENCE] |
| Wrapper ownership | a wrapper token holds an inner position; payout must map wrapper→underlying owner | `wrapper`, `unwrap`, `underlyingOwner`, `wrappedToken` | `claim*`, `redeem*`, `unwrap*` | sibling pays the wrapper contract or caller, not the underlying owner | [INFERENCE] |
| Staking-receipt ownership | receipt/share token represents a stake; rewards keyed to receipt holder | `receipt`, `shares`, `stakeOf`, `_shares[` | `getReward`, `claim*`, `harvest*` | batch/single disagree on receipt-holder vs staker | [INFERENCE] |
| Vault beneficiary | ERC4626-ish vault with a designated receiver distinct from caller/owner | `receiver`, `onBehalfOf`, `beneficiary` | `withdraw(…,receiver,owner)`, `redeem`, `claim*` | one path honors `receiver`, the equivalent silently pays `owner`/caller | [INFERENCE] |
| Account→beneficiary map | explicit `account => payTo` redirection | `payTo`, `rewardTo`, `beneficiaryOf`, `_redirect` | `claim*`, `distribute*` | a path ignores the redirection map | [INFERENCE] |
| Loop-carried recipient | a batch loop must carry the per-item recipient/state | `for (`, `recipients[i]`, `to = `, reused `recipient` | `batch*`, `multi*`, `*_many` | loop reuses the first/initial recipient or a stale var | [INFERENCE] |
| Per-recipient reward checkpoint | per-account `rewardDebt`/`index`/`paid` accounting | `rewardDebt`, `userRewardPerTokenPaid`, `checkpoint`, `index` | `getReward`, `_updateReward`, `claim*` | one path updates the checkpoint, the sibling omits/misorders it → double-claim | [INFERENCE] |

---

## 4. New pre-screen proposal (family-scoped, source-only) — PROPOSED, NOT IMPLEMENTED

**Order (gates to ADD / REORDER):**
1. `G0 correction_layer_exists` — **NEW, ordered FIRST** (scoped to distributor/parity/escrow/reward family).
2. `G1 path_divergence_opportunity` — two economically-equivalent paths treat the layer differently.
3. `G2 attacker_reachability` — arbitrary EOA reaches the omitting path (no role/KYC/keeper/victim).
4. `G3 attacker_is_recipient` — caller / caller-controlled address receives the value.
5. `G4 non_time_non_mev` — not interest/cooldown/oracle/MEV/donation/dust.
6. `G5 source_comparand` — sibling/reference/checkpoint exists.
7. → `HARNESS_ALLOWED` iff G0∧…∧G5; else `SOURCE_REFUTED_NO_HARNESS` with the first failed gate.

**Gates to REMOVE/DEMOTE:** raw "sibling pair exists" (disproven, §1), raw "direct value moves" (disproven),
file-count / light-deps — **demote from selection signals to harness-feasibility tie-breakers only**.

**Recall guard (critical, [SPECULATION] until measured):** G0 is a **family-scoped booster**, NOT a global
pre-filter. Candidates outside the distributor/parity/escrow/reward family must bypass G0 entirely and route
to the existing specialist pipeline — otherwise reentrancy/oracle/access-control/arithmetic bugs would be
silently dropped. **This is the single most important safeguard in the document.**

---

## 5. Dashboard improvements (read-only adapter additions) — PROPOSED, NOT IMPLEMENTED

Reuse existing surfaces: the verifier `conversion` block + `evidence_completeness` (added to
`scripts/finding_detail.py` in the prior phase) and `option_a_campaign.summary()`.

Mock fields per candidate row/detail:
- `correction_layer_present: bool|null` · `correction_layer_type: <taxonomy enum>|null`
- `path_divergence_present: bool|null` · `attacker_is_recipient: bool|null`
- `first_failed_gate: G0..G5|null` · `harness_recommended: bool` (= all gates pass)
- `conversion_likelihood: 0..1` — **heuristic, NOT a probability** [SPECULATION]: e.g.
  `0.2*G0 + 0.2*G1 + 0.2*G2 + 0.2*G3 + 0.1*G4 + 0.1*G5`, displayed with an explicit "heuristic" label and the
  gate breakdown, never used to auto-route.
Campaign-stats panel (from `summary()`): candidates, runtime_confirmed, reportable, harnesses_avoided,
source_refutations, gate_refutations, fabrication_rate. All additions are to the **read-only adapter**, not
detectors; none set severity/routing/submission.

---

## 6. Submission-pipeline implications

- **(a) Prioritize confirmed reportables over continued hunting?** **Recommend YES (soft).** [INFERENCE]
  Reasoning: H5 sat unfinished while four more candidates were screened; a reportable that is never triaged/
  submitted has zero value. Soft = "triage/handoff the open reportable before spending the next harness
  budget," not a hard stop. Required validation: `none` (process change).
- **(b) Pause campaigns when a reportable exists?** **Recommend NO hard pause; YES a checkpoint.**
  [INFERENCE] A hard pause risks losing momentum and assumes the reportable is submission-grade (H5 is not).
  A checkpoint = surface "open reportable: decide submit / hold / continue" to the human. Required validation:
  `none`.
- **(c) Require a retrospective before a new campaign?** **Recommend YES (lightweight).** [INFERENCE] A
  one-screen scorecard checkpoint (§8), not a heavy doc like this one. Required validation: `none`.
All three tie into the existing human-review / submission gates; **never auto-submit**.

---

## 7. Selection guidance — "How to identify correction-layer-bearing targets" (operator, ≤1 page)

1. **Grep for a correction/indirection layer first:** `getOriginalOwner|managed|AVM|originalOwner|escrow|
   beneficiary|delegate|wrapper|onBehalfOf|payTo|rewardDebt|idToOwner`.
2. **Find the correction call-site** (where the canonical recipient/owner is resolved).
3. **Find an economically-equivalent path that skips it** — the sibling/batch/alt entrypoint that uses
   `ownerOf`/`msg.sender`/current holder instead of the corrected recipient, or omits the checkpoint update.
4. **Confirm the omitting path is permissionless** and the **caller is the recipient** (or controls it).
5. **Confirm the gain is not time/MEV/self-funded** and a **source comparand** (the correct sibling) exists.
6. If all hold → `HARNESS_ALLOWED`; otherwise stop with the first failed gate. If **no correction layer
   exists, do not pursue the parity angle** — route to the normal specialist pipeline instead (recall guard).

---

## 8. Metrics & campaign scorecard

Metrics that matter more than raw finding count (computable from `option_a_campaign.summary()`):
- `harnesses_avoided` (source/gate refutations that skipped a harness) — **efficiency**, [DIRECT_EVIDENCE]=4.
- `source_refutations`, `gate_refutations` — **where** precision is enforced.
- `conversion_rate` = runtime_confirmed / candidates; `reportable_rate` = reportable / candidates.
- `precision_proxy` = reportable / harnessed (n is tiny → report as a fraction, not a %).
- `fabrication_rate` = fabricated confirms / candidates (**must be 0**; a hard invariant, not a target).
- `false_positive_reduction` vs a no-pre-screen baseline — **estimate only** [SPECULATION].

**H5–H9 scorecard (descriptive; n=5):** candidates 5 · runtime_confirmed 1 · reportable 1 · submission_ready 0
· harnesses_built 1 · harnesses_avoided 4 · source_refutations 2 · gate_refutations 2 · conversion_rate 1/5 ·
reportable_rate 1/5 · precision_proxy 1/1 · fabrication_rate 0. **Caveat: every rate here is a 5-sample point
estimate — not an operating point.**

---

## 9. Decision register (every proposed change; the acceptance-criteria table)

| # | Proposed change | Evidence | Status | Required validation | Justification |
|---|---|---|---|---|---|
| 1 | Source-refute before harness | DIRECT_EVIDENCE | **PROMOTE** | none | 4 harnesses avoided this campaign |
| 2 | Fabrication-rate = 0 invariant | DIRECT_EVIDENCE | **PROMOTE** | none | already held; codify as a hard rule |
| 3 | Demote file-count/light-deps to tie-breakers | DIRECT_EVIDENCE | **PROMOTE** | none | H7/H8 passed these yet refuted |
| 4 | Drop "sibling pair ⇒ bug" heuristic | DIRECT_EVIDENCE | **PROMOTE** (remove) | none | H2/H9 disprove it |
| 5 | Correction-layer **booster** (family-scoped) | INFERENCE | **KEEP_EXPERIMENTAL** | blind + runtime-confirmed | 1 converter + 1 cross-ref; positive predictions unvalidated |
| 6 | Correction-layer as **default global gate** | SPECULATION | **REJECT (for now)** | blind + runtime + submission | recall risk unquantified |
| 7 | Correction-layer taxonomy (managed-NFT row) | DIRECT_EVIDENCE | **PROMOTE** (that row) | none | B5 observed |
| 7b | Taxonomy (other 9 rows) | INFERENCE | **KEEP_EXPERIMENTAL** | runtime-confirmed | extrapolated, not observed |
| 8 | Dashboard correction-layer/gate flags | INFERENCE | **KEEP_EXPERIMENTAL** | none (display-only) | safe to show; don't auto-route |
| 9 | `conversion_likelihood` heuristic score | SPECULATION | **KEEP_EXPERIMENTAL** | blind campaign | weights untested; display-only |
| 10 | Campaign scorecard from summary() | DIRECT_EVIDENCE | **PROMOTE** | none | computable today |
| 11 | Soft "finish reportable before hunting" | INFERENCE | **PROMOTE** | none | H5 left unfinished |
| 12 | Hard pause on reportable | SPECULATION | **REJECT** | submission-outcome | over-rigid; H5 not submission-grade |
| 13 | Lightweight retrospective checkpoint pre-campaign | INFERENCE | **PROMOTE** | none | cheap; this phase shows its value |

**The three buckets, explicitly:** PROMOTE now = #1,2,3,4,7,10,11,13. KEEP_EXPERIMENTAL = #5,7b,8,9. REJECT =
#6,12.

### Final statuses (P163 review — locked)
These are the agreed, non-overclaiming statuses to carry forward. Consistent with the register above;
"observed row only" = the managed-NFT taxonomy row (B5); the 9 hypothesized rows stay KEEP_EXPERIMENTAL.

| Item | Status |
|---|---|
| Source-refute-first workflow | **PROMOTE** |
| Named-gate rejection recording (first-failed-gate + reason on every reject) | **PROMOTE** |
| Campaign scorecard | **PROMOTE** |
| Fabrication-rate invariant (=0) | **PROMOTE** |
| Lightweight retrospective checkpoint | **PROMOTE** |
| Correction-layer taxonomy (observed row only) | **PROMOTE** |
| Correction-layer selector | **KEEP_EXPERIMENTAL** |
| Conversion-likelihood scoring | **KEEP_EXPERIMENTAL** |
| Global correction-layer gate | **REJECT** |

"Named-gate rejection recording" is **[DIRECT_EVIDENCE]** — it is the mechanism behind the campaign's
`harnesses_avoided=4` (every rejection carried a first-failed-gate + source ref), so it is promoted in its own
right.

### Explicit decision on the correction-layer selector → **KEEP_EXPERIMENTAL** (not PROMOTE)
Evidence: `INFERENCE` — 1 confirmed converter (H5) + 1 cross-ref confirm (B5); 2 cross-ref refutes (H2, H9);
**0 of its positive predictions independently validated.**

- **What would let it become a DEFAULT campaign selector?** All of: (i) **≥10–15 independent blind-campaign
  candidates** where `correction_layer_present` predicts runtime_confirmed/reportable at a materially higher
  rate than the control selector (a real lift, not 1/1); (ii) **≥1 submission-outcome confirm** (a payout or
  accepted finding, not just runtime-confirmed); (iii) **a measured no-recall-collapse** on a mixed-bug-class
  control set (it must not drop reentrancy/oracle/access-control candidates).
- **What would cause us to ABANDON it?** Any of: correction-layer-present candidates that **consistently
  refute** downstream; correction-layer-**absent** candidates that **convert** (predictor has no signal); or a
  **measured recall drop** on non-parity classes when it is used as a gate.
- **Scope guard (holds even if promoted):** family-scoped **booster** for distributor/parity/escrow/reward,
  never a global pre-filter.

> **Preserved conclusion (carry verbatim into future documentation):** "The correction-layer selector may
> improve precision within the distributor/parity family, but current evidence is insufficient to justify
> promotion beyond an experimental, family-scoped booster."

#### Required control comparison — new selector vs the pre-P160 selector, on H5–H9
The new selector is the §4 gate stack; the **control** is the pre-P160 filter ("single-contract +
permissionless + direct-value + light-deps").

| Candidate | Pre-P160 control admits? | §4 selector admits? | Δ | Outcome (ground truth) | Confidence |
|---|---|---|---|---|---|
| H5 abracadabra | yes | **yes** (G0–G5 pass) | retained | reportable ✓ | DIRECT_EVIDENCE |
| H6 pooltogether | yes (then source-refuted) | **no** (guarded state) | newly rejected | FP avoided | DIRECT_EVIDENCE |
| H7 wildcat | yes (looked clean) | **no** (G2 permissioned) | newly rejected | FP avoided | DIRECT_EVIDENCE |
| H8 basin | yes (looked clean) | **no** (G3/G4 self-funded/MEV) | newly rejected | FP avoided | DIRECT_EVIDENCE |
| H9 hybra | yes (sibling pair) | **no** (G0 no correction layer) | newly rejected | FP avoided | DIRECT_EVIDENCE |

- **Cases newly promoted:** none beyond H5 (the new selector does not admit anything the control missed on
  this set). [DIRECT_EVIDENCE]
- **Cases newly rejected:** H6, H7, H8, H9 — the control would have harnessed (or wasted source time on) all
  four; the new selector cuts them earlier. [DIRECT_EVIDENCE on this set]
- **Expected precision impact:** on H5–H9, 4/4 FPs cut, 1/1 converter retained → apparent precision 1.0.
  **[INFERENCE]** — n=5; this is the campaign that *generated* the rule, so it is in-sample (overfit risk);
  out-of-sample precision is unknown.
- **Expected recall impact:** **the main risk.** On this set recall is 1/1 (no converter lost). But the set
  contains only parity/distributor/AMM/lending candidates; **the new selector would drop converters of other
  bug classes if used globally.** [SPECULATION] — unmeasured; this is exactly why status is KEEP_EXPERIMENTAL
  and scope is family-bounded.
- **Confidence overall:** the *refutations* are DIRECT_EVIDENCE; the *generalization to future precision/
  recall* is INFERENCE/SPECULATION. The rule was derived in-sample, so its on-set 1.0 precision must not be
  read as a validated operating point.

---

## 10. Prioritized action list

**Priority 1 — before another hunting campaign** (PROMOTE / `none`-validation / prerequisites):
- Wire the **campaign scorecard** from `option_a_campaign.summary()` (#10).
- Add the **read-only dashboard flags** + stats panel (#8) — display-only, no auto-routing.
- Adopt the **family-scoped pre-screen ordering** as documented operator guidance (#1,3,4) — guidance, not a
  code gate yet.
- Add a **lightweight retrospective/scorecard checkpoint** required before opening a new campaign (#13).
- Codify **fabrication_rate = 0** as a hard invariant (#2).

**Priority 2 — during the next campaign** (KEEP_EXPERIMENTAL; build the validation dataset):
- Apply the **correction-layer selector as a booster** (#5) and, for *every* candidate, **record its
  prediction vs the actual outcome** + first-failed-gate + harnesses_avoided — this is how we earn the
  evidence for a future PROMOTE decision.
- Trial the **conversion_likelihood heuristic** (#9) as a display-only sort key; do not auto-defer on it.
- Apply the **soft "finish the open reportable first"** rule (#11).

**Priority 3 — wait for multiple future campaigns** (need blind/runtime/submission validation):
- Make the correction-layer selector a **default gate** (#6) — only after the promotion thresholds above.
- Use conversion_likelihood to **auto-rank or auto-defer** candidates (#9 escalation).
- Promote the **hypothesized taxonomy rows** (#7b) once each is observed converting at runtime.

---

## Bottom line
The campaign's durable, evidence-backed gains are *process* (source-refute first; no fabrication; demote cheap
filters; a scorecard). The headline "correction-layer predictor" is a **promising hypothesis, not a proven
selector** — it was derived in-sample from 5 candidates, has 0 validated positive predictions, and **must stay
a family-scoped, experimental booster** until blind + runtime + submission evidence accrues. Promoting it to a
global default now would trade unmeasured recall for in-sample precision — the one move this retrospective
explicitly rejects.

> "The correction-layer selector may improve precision within the distributor/parity family, but current
> evidence is insufficient to justify promotion beyond an experimental, family-scoped booster."
