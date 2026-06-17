# P187 — Mechanism validity / severity adjudication rubric

**Status:** research-only calibration design. UN-WIRED. No selector / routing / severity / submission / prompt /
checker change this phase. The rubric is encoded read-only in `scripts/research/adjudication_rubric.py`
(`research_only:true / routes_in_production:false / is_gate:false`) and applied to frozen P186 evidence only.

## Why this exists
P186 (firewall-sealed fresh-model run) established that deep-pass mechanism **enumeration** is model-robust: a
different Claude model (Sonnet) independently selected 7/9 awarded mechanisms, matching Opus, with 6 selections
fully model-independent. It also showed that **adjudication** — deciding whether an *enumerated* mechanism is a
real, in-severity bug — is model-sensitive. Two awarded mechanisms flipped:

- **M-02** — Opus carried it; Sonnet **rejected** it.
- **M-06** — Opus selected it; Sonnet **rejected** it.

Both rejections were confident and source-backed (`leans_on_unproven_guard=false`, a concrete
`rejecting_source_fact`), so the P185 `demoted_unresolved_mechanism` checker — which fires only on *unproven*
demotions — stayed silent. The gap P187 addresses: **a confident but mis-targeted rejection of a real bug.**

The goal is **not to pick Opus over Sonnet.** It is to define objective checks that decide an enumerated
mechanism's status and, when models disagree, name the evidence that would settle it.

## The nine checks
Applied to one enumerated mechanism + its source evidence (and, if the model rejected it, its rejecting fact):

1. **Dimensional / unit consistency** — do the operands' units reconcile?
2. **Value-direction** — does the arithmetic move value in the alleged direction? Can the subtraction underflow,
   the division truncate to zero, the ratio exceed its bound? *Distinct from #1: a unit-consistent expression can
   still underflow or truncate.*
3. **Who gains / who loses** — a concrete beneficiary and a concrete victim are named.
4. **Exploit preconditions** — the chain/state required to trigger it, and whether it is reachable.
5. **Attacker controllability** — can an unprivileged actor drive the triggering input?
6. **Invariant violation** — the named protocol invariant that breaks.
7. **Severity boundary** — the **lowest** severity tier the mechanism *clears* (per the CLAUDE.md scale:
   Critical/High/Medium/Low). A DoS clears **Medium**. A mechanism is **not rejected** for failing a *higher* tier
   if it clears a lower one.
8. **Rejection responsiveness** *(only when a model rejected the mechanism)* — a rejection is **responsive** only
   if it (a) references the **alleged bug's locus** (the specific variable/expression), (b) addresses the
   **alleged failure-mode family**, and (c) rests on a **proven** fact (not an unproven downstream guard). A
   rebuttal aimed at a different expression, or a units-consistency answer to an underflow claim, is
   **non-responsive**.
9. **Settling evidence** — is a minimal **corrected-reference** or **differential check** feasible (recompute the
   expression the alleged-correct way and compare; assert the revert path; test the bound) that would objectively
   decide the disagreement?

## Decision tree → five outcomes
```
disposition == selected (carried as a primary mechanism, victim named)
        → SELECTED_VALID

disposition == unresolved (carried forward, open question, NOT rejected)
        → SELECTED_NEEDS_HARNESS      if a minimal check (#9) would confirm the open precondition/bound
        → UNRESOLVED_CARRY_FORWARD    otherwise (who-gains/who-loses genuinely open)

disposition == rejected
        → REJECTED_INCORRECTLY        if NOT responsive (#8): wrong locus, wrong failure-mode family,
                                      or leans on an unproven guard
        → REJECTED_INCORRECTLY        else if applies a too-high severity bar (#7): rebuts only a higher tier
                                      than the mechanism needs to clear (e.g. "not fund-loss" vs a DoS = Medium)
        → REJECTED_VALIDLY            else (responsive, proven, at the right tier)
```
`REJECTED_INCORRECTLY` is the cell the P186 checker misses. It splits into two objectively-distinct causes:
**non-responsive** (#8) and **severity-floor** (#7) — which, as the matrix shows, settle by *different* evidence.

## Worked examples (the two P186 flips)

### M-02 — non-responsive rejection (settled by execution)
- **Alleged failure mode / locus:** integer-division truncation/underflow of `lpTokenDepositValueChange` at
  `UpliftOnlyExample.onAfterRemoveLiquidity` lines 241–243:
  `lpTokenDepositValueChange = (int(now) - int(deposit)) / int(deposit)` — integer division, no 1e18 scaling.
- **Sonnet's rejecting fact:** *"feePerLP 1e18 units, feeAmount 1e18 units, mulDown cancels scale; floors favour
  LP."* This is a **units-consistency** argument about `feePerLP`/`feeAmount`/`mulDown` — a *different expression*
  (the later fee multiply, ~line 309), and a *different family* (UNITS, not DIRECTION/underflow). It **never
  references the alleged locus `lpTokenDepositValueChange`.**
- **Check #8:** `locus_referenced = false` → **non-responsive** → **REJECTED_INCORRECTLY**.
- **Settling evidence (#9):** a differential/corrected-reference test — recompute `lpTokenDepositValueChange`
  *with* 1e18 scaling and compare to the on-chain integer-division result on one concrete `(now, deposit)` input;
  assert the uplift fee is not silently zeroed. **Execution required.**

### M-06 — severity-floor rejection (settled statically)
- **Alleged failure mode / locus:** unhandled external-call revert locking all oracle access —
  `ChainlinkOracle._getData` line 201 `priceFeed.latestRoundData()` (no try/catch) and
  `UpdateWeightRunner._getData` line 157 `revert("No fresh oracle values available")` propagating. Awarded
  **Medium**.
- **Sonnet's rejecting fact:** *"revert propagates… view function… liveness/DoS not fund-loss; no inconsistent
  state."* This **is** responsive on locus and family (it correctly characterizes the revert DoS) — but it rejects
  on a **fund-loss / High** bar.
- **Check #7:** the mechanism is a DoS, which **clears Medium** per the severity scale; *"not fund-loss"* rebuts
  only the High tier → `applies_too_high_severity_bar = true` → **REJECTED_INCORRECTLY (severity_floor)**.
- **Settling evidence:** **static** — the severity scale already classifies a total-oracle-lockout DoS as Medium;
  no harness needed.

These two failing **different** checks (M-02 #8, M-06 #7) is the evidence the rubric discriminates rather than
rubber-stamping a model: it does not say "Opus was right," it says *what is wrong with each rejection and what
would settle it.*

## Anti-overfit note (read this before trusting the numbers)
This rubric was **designed against** the M-02 and M-06 disagreements, so its success on exactly those two cases is
**partly by construction** — it is a *demonstration that the checks express the disagreement objectively*, not an
independent recall result. Three guards keep it honest:

1. **In-phase control — the 6 stable selections.** H-07, M-03, M-10, L-01, L-02, H-03 are model-independent
   (selected/carried by both models). The rubric must classify **none** of them as `REJECTED_*`, **without any
   per-finding patch**. It does (test `test_anti_overfit_no_stable_selection_is_rejected`); only the 2 genuine
   flips are `REJECTED_INCORRECTLY` (`test_only_the_two_flips_are_rejected_incorrectly`).
2. **General logic, case-specific data.** The check functions (`rejection_is_responsive`,
   `applies_too_high_severity_bar`, `families_of`) are general; the per-finding rows supply only objective facts
   (answer-key locus/severity + frozen-model dispositions). The responsiveness verdict for M-02 is computed from
   Sonnet's *actual words* vs the alleged locus token, not asserted.
3. **No recall claim.** This is a calibration artifact, n=9, one corpus. **The genuine test is a future *blind*
   apply on a different corpus / fresh disagreements** — where the rubric has not seen the cases. That is deferred.

## Where this would go (recommendation only — not implemented)
See `DISAGREEMENT_REPORT.md` for the per-flip resolution and the staged recommendation. In short: the
severity-floor cause (M-06) is **static** and would extend the deep-pass checker/prompt; the non-responsive cause
(M-02) needs a **targeted harness-escalation** (`SELECTED_NEEDS_HARNESS` → emit a minimal differential test).
Both are future, separately-approved changes.
