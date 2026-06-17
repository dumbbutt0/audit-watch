# P155 — Human-grade Review of H5 (abracadabra LockingMultiRewards post-expiry boost retention)

**Phase type:** reportability review gate (NOT a new bug hunt). Mechanism confirmation (P154) is taken as
given and kept strictly separate from severity, scope, and novelty.

**Candidate:** `H5-abracadabra-lockingrewards-boost` · audit `abracadabra-2024-03-holdout` (Code4rena
`2024-03-abracadabra-money`) · `LockingMultiRewards`.

**P154 established (not re-litigated here):** an unprivileged staker who locks keeps the boosted reward
weight (`bal.locked·mult`) after `unlockTime` because the only de-boost path (`processExpiredLocks`) is
`onlyOperators` and there is no user unlock; runtime PoC 4/4, zero-sum over-accrual A +175e18 == B −175e18.

## Gate results (detail in the companion tables)

| Gate | Result |
|---|---|
| 1 — Source intent | **intent_ambiguous** |
| 2 — Attacker model | **unprivileged_passive_benefit** |
| 3 — Operator/trusted-role scope | **trusted_operator_liveness_bounds_severity** |
| 4 — Impact / severity bound | **Medium candidate** (zero-sum staker loss; no protocol-fund loss; bounded by operator liveness) |
| 5 — Novelty / duplicate (local) | **duplicate_unknown** (+ public-known **cannot_assess** locally; Convex CvxLockerV2 lineage caveat) |
| 6 — Evidence completeness | **evidence_complete_for_human_review** |
| 7 — Final conversion decision | **remains_reportable_candidate_needs_human_review** (severity bounded to Medium) |

## Reasoning for Gate 7
Nothing in the review **refutes** the candidate or **confirms** a block:
- The attacker model is solid and unprivileged (Gate 2) — unlike P149, the intent ambiguity here does **not**
  collapse the attacker model; it only concerns whether the resulting loss is an accepted
  operator-maintenance tradeoff (a scope/severity question).
- The loss is **real and zero-sum among honest stakers** and is **not** retroactively corrected by later
  processing (past windows are finalized on claim/vesting) — so it is more than "delayed accounting"
  (Gate 4). But there is **no protocol-fund loss**, and with the documented operator cadence the per-lock
  window is small — so severity is **bounded to Medium**, not High (Gate 3/4).
- The two things that *could* block it — (a) a fully-trusted-operator / out-of-scope reading, and
  (b) a public-known duplicate from the 2024-03 contest — **cannot be confirmed from local resources**.
  Per the project rule, an unconfirmed block must not be asserted; unknowns stay unknown.

Therefore H5 **remains** a reportable candidate, now with a sharpened, bounded severity (Medium) and three
explicit caveats handed to the human: (1) confirm the program's operator trust/scope model — a
fully-trusted-operator reading would downgrade to Low/QA or place it out of scope; (2) run an external
public-known / duplicate check (the underlying lock-boost pattern is public via Convex/Curve, so a prior
report is plausible); (3) set the final Medium↔Low grade.

`submission_ready=false`, `routing_allowed=false`, `human_review_required=true`. The runtime fact
(`runtime_status=runtime_confirmed`) is unchanged.

## Alternative reading (documented, not adopted)
If the human determines the program treats `onlyOperators` as fully trusted and routine
`processExpiredLocks` maintenance as an assumed invariant, the honest reclassification is
`blocked_by_trusted_operator_scope` (→ Low/QA or out-of-scope). This review does not adopt that because the
scope/trust model is not determinable locally and honest third-party stakers bear the loss without any
self-remediation path.
