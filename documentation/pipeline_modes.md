# Audit-Watch Pipeline Modes

Audit-Watch is **recall first, precision second**: examine the whole denominator, surface candidates with the
lens suite, then (for real reports) confirm reachability. The mode you run determines which gates apply and
what blocks.

## The three gates — separation of responsibility

| Gate | Question it answers | Script | Blocks where |
|---|---|---|---|
| **coverage_gate** | *Did we examine the denominator?* — every in-scope manifest item has an evidence-anchored disposition | `coverage_completeness_gate.py` | Step 3.9 (full / review-gate) |
| **min_confirm_gate** | *Does the finding carry the required fields?* — entrypoint, manifest_refs, preconditions, impact, guards, PoC plan, severity, confidence | `min_confirm_gate.py` | Step 3.9 (full / review-gate) + submission-confirm |
| **confirm_gate** | *Is it reachable / submission-safe?* — can an unprivileged attacker drive the claimed path to the claimed impact in the deployed lifecycle state | `confirm_gate.py` | submission-confirm only (advisory in eval) |

`coverage_gate` and `min_confirm_gate` answer *completeness* and *form*; `confirm_gate` answers *reachability
truth*. The first two run inside `coverage_review_gate()` (Step 3.9). **`confirm_gate` is NOT wired into the
eval/full path** — it is invoked only via the two manual commands below, so eval recall is never blocked.

---

## 1. Fast point-and-shoot mode
- **Purpose:** quick look at a single contract; surface obvious issues fast.
- **Commands:** `./run_pipeline.sh analyze <contract>` → `/ite-audit` specialists → `./run_pipeline.sh triage`.
- **Gates used:** none hard. `coverage-manifest` optional.
- **Blocks:** nothing.
- **Does not block:** everything — this is exploratory.
- **Artifacts:** `output/findings_*.json`, `output/tool_summary.md`.
- **When:** triage / first pass / time-boxed look.

## 2. Full audit mode
- **Purpose:** complete, coverage-enforced audit of a scope.
- **Commands:** `./run_pipeline.sh analyze <contract>` → `/deep-analysis` → `./run_pipeline.sh analyze-resume <contract>` → `/ite-audit` → `/coverage-sweep` → `./run_pipeline.sh full`.
- **Gates used:** Step 3.9 `coverage_review_gate()` = **coverage_completeness_gate + min_confirm_gate**.
- **Blocks:** the review gate is HARD-BLOCKED until every in-scope manifest item is examined/cleared/finding/
  deferred with evidence AND every submission candidate carries its confirmation skeleton.
- **Does not block:** confirm_gate is not in this path.
- **Artifacts:** `output/review_gate.md`, `coverage_manifest.json`, `coverage_dispositions.json`,
  `merged_findings.json`, `coverage_gate.json`, `min_confirm_gate.json`.
- **When:** the real audit. Pause at `review_gate.md`, then pick PoC IDs.

## 3. Eval mode (recall measurement)
- **Purpose:** measure recall honestly against a sealed answer key without precision penalties.
- **Commands:** coverage-enforced run → root-cause dedup (`build_eval_inventory.py` → `eval_findings.json`)
  → optional `./run_pipeline.sh confirm-advisory`.
- **Gates used:** coverage_gate (PASS at 91.9%); `confirm-advisory` = `confirm_gate.py --mode eval`.
- **Blocks:** **nothing.** confirm-advisory is advisory only — it classifies (likely_reachable /
  uncertain+needs_runtime_poc / lifecycle_only / duplicate / …) and **always exits 0**.
- **Does not block:** uncertainty, needs_runtime_poc, lifecycle_only, partial_eval_finding — all preserved so
  recall is measured fairly.
- **Artifacts:** `output/eval_ready/*` (frozen scoring set + scorecard), `output/confirm/confirm_gate.json`
  (advisory).
- **When:** benchmarking the pipeline. Never use the confirm gate to drop eval candidates.

## 4. Submission mode (real-report precision)
- **Purpose:** protect real reports from bad/unreachable/duplicate High-Critical claims.
- **Commands:** `./run_pipeline.sh submission-confirm` (or `submission-confirm --strict`), then
  `./run_pipeline.sh submit` for PoC → QC → pack.
- **Gates used:** `min_confirm_gate` (field presence) + `confirm_gate --mode submission` (reachability truth).
- **Blocks (exit 1):** any **confirmed** High/Critical claim (merged finding or `confirmed_eval_finding`) that
  is `external_entrypoint_missing` / `privileged_only` / `dead_path` / `insufficient_evidence`, or an unmerged
  `duplicate_root_cause`. With `--strict`, also `lifecycle_only` + `uncertain`.
- **Does not block:** `partial_eval_finding` / `real_world_poc_later` (self-declared non-confirmed → warn);
  `lifecycle_only` in non-strict mode (→ manual-review warning — a reseed/migration protocol's real bugs live
  in init files, so this is never an auto-kill).
- **Override:** `AUDITWATCH_CONFIRM_OVERRIDE=1` forces PASS (document the reason).
- **Artifacts:** `output/confirm/{confirm_inventory,reachability_analysis,confirm_gate}.json`,
  `output/min_confirm_gate.json`.
- **When:** before filing a real-world report. **High/Critical real-world submissions also require a PoC**
  (L1/L2/L3) — see CLAUDE.md non-negotiables. (PoCs are NOT required for eval classification.)

---

## Quick reference
- Measuring recall? → eval mode + `confirm-advisory` (never blocks).
- Filing a report? → `submission-confirm` (blocks bad High claims) → PoC → `submit`.
- Coverage question → `coverage-gate`; form question → inside it (`min_confirm_gate`); reachability question →
  `submission-confirm`.
