# P222 — Dashboard priority verification

## Detail card top-line (read-only), ZETA-04
`finding_detail.load_unified_detail("funnel:ZETA-04")` → `top_line_status`:

```
banner: CLEAN_HIT · L3_PASS · TRUSTED_SYSTEM_ACTOR_REACHABLE · HIGH_PRIORITY_HUMAN_REVIEW
display_lines:
  - Not submission-ready
  - Human review priority: High
  - Reason: program threat-model decision required
  - External route/submission disabled
submission_ready: False
routing_allowed: False
```

This is exactly the desired top-line. The banner is composed from recorded fields (conversion outcome, L3
status, reachability class, human-review priority) and never computes severity or flips a flag.

## Read-only, no submit/promote controls
- The card echoes `submission_ready=False` / `routing_allowed=False` and adds **no** action controls.
- `dashboard.py` adds only GET filters; there is no new POST and no submit/promote endpoint.
- `dashboard_sync.py` (the synced-record contract incl. the `browser_computes_severity:false` /
  `submission_ready:false` constants) is **byte-identical** — the priority fields ride via `CARD_INJECT`.

## Severity never browser-computed
`browser_computes_severity` stays `False` on every record; `_sev_or_status` (which rejects conversion/decision
tokens) is untouched; the banner shows the *priority label*, never a severity.
