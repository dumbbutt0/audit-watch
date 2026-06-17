# P197 — Recommendation: close the sub-arc, pivot to Centrifuge

## Closed hypotheses
- `production_coverage_gap_hypothesis` — closed P194 (0 artifact-confirmable coverage gaps).
- `selection_by_score_fix` — closed P195 (max gain 0 at 0% execution; axis-mismatch artifact).
- `execution_budget_fix` — closed P196 (auto-executor zero is api-free-by-design; deep runs via in-session skill).
- `generic_routing_bottleneck` — closed P190→P196 (decomposed into measurement noise + extraction defect + by-design deep-pass).

## Retained improvements (validated assets)
- **P183–P188 adjudication stack** (cross-corpus-general per P189) — the canonical production win.
- **P194 `eval_locus_resolver`** — eval-harness locus resolution, un-wired, tested.
- **P196 two-mechanism distinction** — `assigned_pass` (tier label) vs executed deep-pass.

## Next-corpus recommendation: **`centrifuge-2023-09-holdout`**
- **Architecture:** RWA tokenization — tranches, epoch close, NAV, escrow / InvestmentManager. **Maximally
  distinct** from the measured set (Balancer-AMM, perps, UniV3-NFT-lending, options, bridge).
- **Why it stresses adjudication, not matching:** the protocol is built on **conservation / epoch / escrow
  invariants** where a finding's worth turns on a *validity & severity judgment* ("is this accounting drift a real
  loss, under what preconditions?") — exactly the surface the P183–P188 stack (mechanism enumeration →
  carry-forward → non-responsive/severity-floor adjudication) is designed to exercise. Matching alone won't settle
  these; adjudication will.
- **Practical fit:** compact (21 files / 4.1k LOC) → a focused campaign; **sealed answer key** → ideal for the
  campaign's firewall/blind discipline (run blind, score at controlled unseal).
- **Alternates:** `badger-2024-06-holdout` (eBTC CDP/liquidation, richer/larger — **fallback if centrifuge's
  awarded set is thin**); `kleidi-2024-10-holdout` (Safe-module/timelock — compact authorization-stress alternate).
- **Caveat (explicit):** sealed answer-key finding count is `UNKNOWN` in P197; P198 must confirm the awarded count
  at controlled unseal and fall back to badger if thin.

## Why this is NOT more taxonomy / tooling work
The measurement & routing frontier is **empirically closed** — P190→P196 showed the remaining "loss" was
measurement noise and by-design architecture, with zero confirmed production defects. Building another detector /
normalizer / router / taxonomy layer would optimize a phantom bottleneck. The honest next move is a **science /
generalization step**: take the *already-validated* adjudication stack and test it on a **structurally different
protocol** (RWA/tranche accounting). That measures whether the validated win holds where the invariants are
genuinely new — which is where real, non-overfit recall improvement (or an honest failure mode) will surface.
It adds **no new production surface**; it stresses the surface we already trust.
