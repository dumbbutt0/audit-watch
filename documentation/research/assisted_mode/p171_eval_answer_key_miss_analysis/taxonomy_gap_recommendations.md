# P171 — Taxonomy gap recommendations (sections 4 + 7 detail)

Grounded in the quantamm Track-A misses (and the `failure_analysis.md` "fix directions"). Each family lists the
reject-first gates + the H10–H21 FP filters it must keep. Ranked at the end.

## F1 — Dynamic-weight lifecycle invariants  (PROMOTE)
- **Representative awarded:** H-04 (stale `lastUpdateIntervalTime`), M-04 (length-check DoS), M-08
  (maxTradeSizeRatio bypass), M-09 (post-init minWeight bypass), M-12 (computeBalance boundary revert), M-14
  (missing updateInterval). H-10 (epsilon) overlaps with F2.
- **Source signals:** `setWeights*` / `updateWeight*` / interpolation functions; a state var read for
  interpolation but not written on update; missing length/interval/bounds/epsilon checks in the setter body.
- **Reject-first gates:** must be a **permissionless** update path (M-08/M-09/L-04 are; an `onlyOwner` setter is
  not a finding); must have measurable victim impact (stale/incorrect weights → mispriced swaps).
- **Likely FPs / filters to keep:** permissioned (H7/H13/H16/H17 — check reachability of the setter);
  source-guard-present (verify the bound is actually *unchecked*, not enforced elsewhere — the symmetric
  quantamm over-clearance lesson).
- **Minimum viable selector:** flag dynamic-weight AMMs whose `setWeights`/update path lacks one of
  {sum==1, per-weight bounds, epsilon, updateInterval, interpolation-horizon, staleness}; **test next: YES**.

## F2 — Rule / estimator math-correctness lens  (PROMOTE — harness-feasible)
- **Representative awarded:** H-09 (int overflow in MathGuard), H-11 (EW-covariance), L-06 (negative weights),
  L-09 (single-asset variance underflow), M-07 (pack32 integer-division precision). H-10 (normalization).
- **Source signals:** `*MathGuard` / `*covariance` / `*gradient` / `*variance` / `pack*Array`;
  division-before-multiplication, signed `int128` math, normalization without re-clamp, single-asset/zero edges.
  (`units_invariant` already flags div-before-mul + decimals — it must be **escalated**, not cleared.)
- **Reject-first gates:** needs a **corrected-reference comparand** (the correct math) — strong runtime-confirm
  potential because the math is pure and deploy-light.
- **Likely FPs / filters to keep:** vendored/mock noise (H10 — protocol_src math only, not OZ Math libs);
  source-guard-present (do not flag if a proven in-scope clamp covers the output — but do not *clear* on an
  unproven in-scope guard either).
- **Minimum viable selector:** protocol_src math/estimator functions with an arithmetic edge + no proven clamp;
  **test next: YES** (best convertible-yield candidate — pure-math harness).

## F3 — Balancer-V3 hook lifecycle lens  (KEEP_EXPERIMENTAL)
- **Representative awarded:** H-07 (unauthorized remove-liquidity), M-11 (missing initialize), M-15
  (recovery-mode bypasses hooks → NFT not burned), M-03/M-10/M-18 (deposit-array / 100-cap griefing), M-05
  (withdraw-then-deposit fee avoidance).
- **Source signals:** `onAfterRemoveLiquidity` / `onRegister` / `onBefore*` router-auth; recovery-mode branch;
  FILO deposit array with a per-user cap.
- **Reject-first gates:** confirm the hook path is reachable by an unprivileged caller and harms a victim
  (griefing/DoS counts only at the right severity).
- **Likely FPs / filters to keep:** caller-claims-own (H11/H15/H21); design-intent (recovery mode may be
  intended admin-only); permissioned router.
- **Minimum viable selector:** Balancer-V3 hooks missing recovery/register/router-auth handling; integration-
  specific + higher FP → **test next: NO (experimental)**.

## F4 — Oracle-integration robustness checklist  (KEEP_EXPERIMENTAL)
- **Representative awarded:** M-06 (unhandled Chainlink revert locks all access), M-19 (staleness), L-07 (L2
  sequencer/deviation), L-12 (zero-staleness / updateInterval=0), L-02 (MultiHop precision), L-14 (decimals>18).
- **Source signals:** Chainlink `latestRoundData` without try/catch; no sequencer-uptime check; no deviation
  bound; `staleness==0`; decimals assumptions.
- **Reject-first gates:** mostly Low/Medium severity, DoS-flavored → lower reportable yield.
- **Filters to keep:** trusted-registry (H + oracle registration is often onlyOwner); design-intent.
- **Minimum viable selector:** extend the existing oracle lens (which caught one staleness mechanic) to the full
  checklist; **test next: NO (lower priority)**.

## Selection fix (Track B, cheap, PROMOTE)
- **Problem:** zaros H12 picked `CreditDelegationBranch._convertAssetsToUsdc` (internal swap plumbing) when the
  awarded bugs (H-01/H-05/H-06) live in the credit-delegation *accounting* functions of the same contract.
- **Fix:** within a flagged contract, rank candidate functions: prefer **external/public state-mutating
  accounting** functions over `internal`/swap/plumbing functions. Cheap, addresses a real adjacency miss.

## Ranking (section 7)
| Rank | Item | misses explained | source-detectability | reportable yield | FP risk | harness feasibility | decision |
|---|---|---|---|---|---|---|---|
| 1 | F1 dynamic-weight lifecycle | 6 | high (setWeights sigs) | medium-high | low | medium | **PROMOTE / test next** |
| 2 | F2 estimator-math lens | 6 | medium (math libs) | medium-high | medium | **high (pure math)** | **PROMOTE / test next** |
| 3 | Selection fix (fn ranking) | 1 (+ general) | high | n/a | low | n/a | **PROMOTE (cheap)** |
| 4 | F3 hook-lifecycle lens | 7 | medium | medium | higher | medium | KEEP_EXPERIMENTAL |
| 5 | F4 oracle robustness | 5 | high | low (DoS/Low) | low | low | KEEP_EXPERIMENTAL |

**Process fix that gates all of the above (highest leverage, 0 new lens):** forbid "guarded-downstream"
strong-clears when the guard/estimator is itself in scope and unproven → route to `needs_deep_pass`; and
escalate any recall-lens flag that overlaps a cleared item back to a candidate. This single sweep-policy change
explains the largest quantamm miss class.
