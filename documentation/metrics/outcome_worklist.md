# Calibration outcome worklist (human-only)

_generated 2026-06-17T18:14:29.498479+00:00 · 7 accepted finding(s) awaiting an outcome_

Recording any of these moves FP/recall off **unmeasured**. AI must not fill the verdict — you supply `--outcome`, `--severity`, and provenance (`--evidence-class/--source-file/--evidence`). A record without provenance is routed to `needs_human_review.jsonl`, never ground truth.

## k2-kinetic-2026-04 — 7 pending

- **AC-002** (medium) — verifyValidator() is callable by anyone — no access control — allows unauthorized state transitions
  ```bash
  python scripts/audit_manager.py switch k2-kinetic-2026-04
  python scripts/record_outcome.py --finding-id AC-002 \
      --outcome <accepted|invalid|duplicate|downgraded|paid> \
      --severity <critical|high|medium|low|invalid> --claimed-severity medium \
      --evidence-class <fork_confirmed|report_response|...> \
      --source-file audits/k2-kinetic-2026-04/data/runtime_poc/results.jsonl \
      --evidence "<one-line evidence>"
  ```
- **AC-003** (medium) — verifyDeposit() is callable by anyone — no access control — unsafe beacon proof state mutation
  ```bash
  python scripts/audit_manager.py switch k2-kinetic-2026-04
  python scripts/record_outcome.py --finding-id AC-003 \
      --outcome <accepted|invalid|duplicate|downgraded|paid> \
      --severity <critical|high|medium|low|invalid> --claimed-severity medium \
      --evidence-class <fork_confirmed|report_response|...> \
      --source-file audits/k2-kinetic-2026-04/data/runtime_poc/results.jsonl \
      --evidence "<one-line evidence>"
  ```
- **DS-001** (high) — AerodromeAMO: strict equality on rounding-sensitive token amount permanently DoSes strategy
  ```bash
  python scripts/audit_manager.py switch k2-kinetic-2026-04
  python scripts/record_outcome.py --finding-id DS-001 \
      --outcome <accepted|invalid|duplicate|downgraded|paid> \
      --severity <critical|high|medium|low|invalid> --claimed-severity high \
      --evidence-class <fork_confirmed|report_response|...> \
      --source-file audits/k2-kinetic-2026-04/data/runtime_poc/results.jsonl \
      --evidence "<one-line evidence>"
  ```
- **FL-005** (medium) — BaseCurveAMOStrategy zero-slippage withdrawal in withdrawAll() exposed to MEV sandwich
  ```bash
  python scripts/audit_manager.py switch k2-kinetic-2026-04
  python scripts/record_outcome.py --finding-id FL-005 \
      --outcome <accepted|invalid|duplicate|downgraded|paid> \
      --severity <critical|high|medium|low|invalid> --claimed-severity medium \
      --evidence-class <fork_confirmed|report_response|...> \
      --source-file audits/k2-kinetic-2026-04/data/runtime_poc/results.jsonl \
      --evidence "<one-line evidence>"
  ```
- **FL-006** (medium) — AerodromeAMO _removeLiquidity uses amount0Min/amount1Min = 0 enabling sandwich attacks
  ```bash
  python scripts/audit_manager.py switch k2-kinetic-2026-04
  python scripts/record_outcome.py --finding-id FL-006 \
      --outcome <accepted|invalid|duplicate|downgraded|paid> \
      --severity <critical|high|medium|low|invalid> --claimed-severity medium \
      --evidence-class <fork_confirmed|report_response|...> \
      --source-file audits/k2-kinetic-2026-04/data/runtime_poc/results.jsonl \
      --evidence "<one-line evidence>"
  ```
- **LG-001** (high) — AerodromeAMOStrategy: strict == 0 equality in _updateUnderlyingAssets causes DoS
  ```bash
  python scripts/audit_manager.py switch k2-kinetic-2026-04
  python scripts/record_outcome.py --finding-id LG-001 \
      --outcome <accepted|invalid|duplicate|downgraded|paid> \
      --severity <critical|high|medium|low|invalid> --claimed-severity high \
      --evidence-class <fork_confirmed|report_response|...> \
      --source-file audits/k2-kinetic-2026-04/data/runtime_poc/results.jsonl \
      --evidence "<one-line evidence>"
  ```
- **LG-002** (medium) — BaseCurveAMOStrategy: improvePoolBalance reverts when pool is perfectly balanced
  ```bash
  python scripts/audit_manager.py switch k2-kinetic-2026-04
  python scripts/record_outcome.py --finding-id LG-002 \
      --outcome <accepted|invalid|duplicate|downgraded|paid> \
      --severity <critical|high|medium|low|invalid> --claimed-severity medium \
      --evidence-class <fork_confirmed|report_response|...> \
      --source-file audits/k2-kinetic-2026-04/data/runtime_poc/results.jsonl \
      --evidence "<one-line evidence>"
  ```

