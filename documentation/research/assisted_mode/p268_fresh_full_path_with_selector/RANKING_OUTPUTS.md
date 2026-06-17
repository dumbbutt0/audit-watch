# P268 — RANKING_OUTPUTS (Phase 5)

Profile B (messy-reconciliation weighting) + Profile C (runner-up challenge) top-2 per queued candidate, and — to
make the P267 effect measurable — the **RAW selection that the pre-P267 path (P266 behavior) would have made**.

| candidate | Profile B top-2 | Profile C top-2 | **RAW pre-P267 pick (P266-style)** | why raw picked it |
|---|---|---|---|---|
| C1 redeem | [M1 finishRedeem-accounting, M2 approval-revert] | [M1, M2] | **M2 (approval-revert)** | easier/cleaner to PoC (one-line revert), so the P266 PoC-feasibility bias selects it |
| C2 mint | [M1 inflation, M2 dust-rounding] | [M1, M2] | **M2 (dust-rounding)** | trivially demonstrable, so the bias selects it over the harder inflation |
| C-neg | [M1 slashing-accounting, M2 gated-no-path] | [M1, M2] | M2 / none | gated; nothing to do |

**The P266 failure reproduced in the raw column:** on both real pairs, the naive pre-P267 selection drops the
higher-impact mechanism (M1) for the easier rival (M2) — exactly the drop that gave P266 0 exact recovery.

Disagreements: B and C agree here (both surface M1 into top-2); the divergence is between the raw PoC-feasibility
pick (M2) and the impact-aware view (M1). Uncertainty: C1 M1 and C2 M1 both carry a real falsifier (virtual-share /
snapshot-rate dependency) to resolve in completion/PoC — that uncertainty is precisely why the raw path avoided them.

Frozen before running the selector.
