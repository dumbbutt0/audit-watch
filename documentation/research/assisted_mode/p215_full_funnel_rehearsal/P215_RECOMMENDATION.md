# P215 — RECOMMENDATION

## DECISION: `FULL_FUNNEL_REHEARSAL_PARTIAL`

### Why PARTIAL (not READY_FOR_REAL_HUNT, not FAILED_*)
- **Routing works & is safe (the phase's core claim is proven):** real candidates flowed through the *actual* funnel —
  workspace → coverage manifest → blind discovery → merge → triage → min_confirm → confirm (eval+submission) →
  pre-submission gate → packages → L3 readiness → dry-run queue → dashboard → freeze → score. No side page, no stage
  bypassed, **0 route/submit side effects**, production hashes byte-identical, quantamm restored, key sealed until
  post-freeze. So **not** FAILED_ROUTING / FAILED_PACKAGE / ABORTED.
- **L3 precision is strong:** 0 false-Highs; the one fully-ready item (ZETA-07) is a genuine low; privileged/centralization
  correctly not promoted (matches official QA[09]). So **not** FAILED_L3.
- **But two real shortfalls keep it short of "ready":**
  1. **Recall/scope:** discovery was Solidity-only; the contest is **Go-node-heavy** (~40 of 48 findings off-chain) →
     most Highs unreachable by construction.
  2. **DoS under-rating recurs:** both in-scope Solidity Highs were **found** (H-13 exactly = ZETA-04; H-10 same
     location = ZETA-11) but **rated Medium** and left `needs_harness`. Same direction as P212.

### What this validates
- The end-to-end funnel is **operationally real and safe** for a guided hunt.
- The over-rating guard holds on a **second** live target (P212 SOPH + P215 ZetaChain → 0 false-Highs both times).

### What to fix before a real hunt (human decisions / next phases)
1. **Scope the off-chain node code** (Go) when a contest includes it — the single biggest recall lever here.
2. **Harness the `needs_harness` High-ceiling DoS candidates.** L3 fail-closes them (correct) but recall needs executed
   PoCs. For H-13/H-10 a harness + the P214 carve-out (for the permissionless, admin-free, deterministic core-path DoS
   shape — H-10 fits; H-13 has an admin pause prereq so it would need the non-carve-out High path) is the route to a
   correctly-rated High.
3. **Raise the triage DoS severity floor** or add a DoS-availability lens so pause/permanent-revert findings aren't
   defaulted to Medium pre-harness.
4. **confirm_gate privilege gap:** consider teaching the reachability classifier about TSS/module gating so privileged
   Highs are demoted at confirm_gate, not only at L3.
5. **Dashboard depends on Step-3 `populate_finding_metadata`** — ensure the funnel always runs it.

### Safety posture
Default-off preserved (`AUDITWATCH_L3_READINESS` unset at END); research-only; nothing routes/submits/promotes; human
review mandatory. The dry-run queue is a safe local stand-in for submission and behaved correctly (0 Highs without L3
PASS).

## ARC
over-HIGH measured(P199) → L3 principle(P204) → 2-corpora(P205/P207) → dry-run(P208) → design(P209) → dark impl(P210)
→ E2E rehearsal(P211) → pseudo-live hunt, under-rated High(P212) → DoS carve-out validated(P213) → carve-out wired
(P214) → **first FULL-FUNNEL rehearsal on a fresh contest: routes end-to-end & safe, 0 false-Highs, but Solidity-scope
recall gap + DoS under-rating recur (P215)**.
