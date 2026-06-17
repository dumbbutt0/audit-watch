# P215 — HUMAN REVIEW QUEUE

Human review is mandatory before any (non-existent) submission. Items a human must adjudicate, in priority order:

1. **ZETA-04 (=H-13) — RAISE SEVERITY.** Source-proven pause asymmetry (`onReceive` lacks `whenNotPaused`). P215 rated
   Medium; the mechanism causes **user fund loss during a paused CCTX** → should be **High**. Build the executed PoC,
   then it qualifies. **Highest-value item.**
2. **ZETA-11 (=H-10) — RE-MECHANISM + RAISE.** Trident `getZetaFromToken` is broken; P215 flagged pool-array validation
   but the real defect is the **wrong `exactInputSingle` router method** (always reverts). Confirm the precise mechanism;
   it is a High (core swap DoS).
3. **ZETA-10 — harness or drop.** Permissionless reentrancy claim; source analysis says no realized theft. Either build
   the executed refutation or drop to QA.
4. **ZETA-07 / ZETA-12 — downgrade to QA.** Executed-but-admin-misconfig (ZETA-07) and MEV/deadline (ZETA-12) — neither
   awarded; treat as QA hardening.
5. **ZETA-03/05/08 — centralization/QA.** Privileged trust-root items; document as centralization risk (matches
   official QA[09]).
6. **Recall gap to escalate:** the Go-node surface (observer/cctx/UTXO/TSS) was unscoped and holds most Highs — a real
   hunt must add it.

No item is submission-ready as-is on AI reasoning alone; all require human inspection (per Non-Negotiables).
