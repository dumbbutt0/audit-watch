# P266 — PRE_REVEAL_GATE (Phase 7, frozen BEFORE reveal)

Strict gate. A candidate becomes `PRE_REVEAL_REPORTABLE_CANDIDATE` only if ALL hold: PoC pass/strong runtime
evidence · exact source-backed root cause · attacker control · invariant/value delta · victim/gainer · terminal/
amplifiable impact · B/C survival · 5-op completion · explicit FP refutation · **no unresolved exploitability
assumption**. The gate never sets severity / submission-ready / confirmed.

## C1 — distribute royalty/dust → arbitrary caller
| criterion | met? | evidence |
|---|---|---|
| PoC pass | ✅ | C1 passes; attacker skims 1 ETH (1%) deterministically |
| exact source-backed root cause | ✅ | `CuratorRewardsDistributor.sol` L120 `_msgSender().safeTransferETH(...)`, no access control on `distribute` |
| attacker control | ✅ | permissionless; any EOA |
| invariant/value delta | ✅ | owner-set royalty + dust diverted to caller; conservation traced |
| victim / gainer | ✅ | gainer = arbitrary caller; victim = curator pool / protocol royalty |
| terminal / amplifiable | ✅ | every distribution skims 1% + dust; repeatable across creds/epochs |
| B/C survival | ✅ | m1a #1 under both B and C |
| 5-op completion | ✅ | COMPLETED_CHAIN |
| explicit FP refutation | ⚠️ | the benign reading "intended keeper incentive" is **not fully excludable from source** |
| no unresolved exploitability assumption | ⚠️ | **design-intent** (is the royalty meant to accrue to protocol?) is the one open assumption |
**Gate result: `PRE_REVEAL_REPORTABLE_CANDIDATE` — CONDITIONAL on design-intent.** All mechanical criteria pass;
the residual is whether paying the caller is intended. Flagged, not hidden. (Not severity/submission/confirmed.)

## C2 — just-in-time spot-share reward capture
| criterion | met? | evidence |
|---|---|---|
| PoC | ⚠️ PARTIAL | capture proven (49.5 ETH); profitability vs bonding-curve cost NOT modeled (Cred mocked) |
| source-backed root cause | ✅ | spot `getShareNumber` split in `distribute`; share acquirable via `buyShareCred` |
| attacker control | ✅ | permissionless buy + permissionless distribute |
| value delta | ✅ | attacker captures spot-share proportion of accrued rewards |
| terminal / amplifiable | ⚠️ | bounded by `SHARE_LOCK_PERIOD` (10m resale lock) + acquisition cost |
| no unresolved exploitability assumption | ❌ | **profitability is unresolved** (needs accrued-reward vs curve-cost economics) |
**Gate result: NOT reportable (held) — PARTIAL_CHAIN with an unresolved economic assumption.** Strong recall +
mechanism, insufficient for the strict gate this round.

## C-neg — withdrawWithSig
Refuted/benign (replay + forgery revert). **Gate result: NOT reportable (correct).** Negative control held.

## Summary
| candidate | gate result |
|---|---|
| C1 | PRE_REVEAL_REPORTABLE_CANDIDATE (conditional on design-intent) |
| C2 | NOT reportable — PARTIAL, economic assumption unresolved |
| C-neg | NOT reportable — benign (negative control held) |

No severity / submission-ready / confirmed assigned to any candidate. Frozen before reveal; hashes recorded in the
reveal doc. **No concluded/reportable canonical finding emitted** — all outputs remain advisory + human-review-gated.
