# P266 — DASHBOARD_CANDIDATE_SURFACE (Phase 2)

The smallest safe adapter: a **standalone advisory-only surface** generated from the frozen shadow output. It does
NOT modify `scripts/dashboard.py`, `scripts/dashboard_sync.py` (forbidden), `dashboard/*.html`, or any canonical
finding record. (`dashboard_sync.py` remains byte-identical — verified.)

## Generator
`p266_advisory_feed.py` (analysis-only, under the P266 dir) reads
`outputs/phi_shadow/recall_advisory_candidates.json` (frozen, `18f3d80f2b3c5dfa`) and emits two static artifacts:
- `outputs/advisory_recall_feed.json` (`62275f55f70bd675`)
- `outputs/p266_advisory.html` (`292a2b031d076436`)

The script imports nothing from the dashboard/finding stack; it only opens the frozen shadow JSON and writes its own
`outputs/`. The 8 textual matches for `dashboard*/confirm*/canonical` in the file are **safety comments + assertion
strings**, not imports or file operations.

## Fields shown per candidate
rank · recall class (RECALL_DELTA / NARROW_BASELINE) · locus (`contract.function`) · templates · inclusion reasons ·
status · severity. Each record also carries (machine-readable, in JSON) the B/C ranking handoff + generated-mechanism
count + promotion_label.

## Safety labels (every record + page banner)
Page banner: **ADVISORY ONLY · NOT CONFIRMED · NOT REPORTABLE · NOT SUBMISSION-READY · severity: HUMAN_PENDING**.
Every JSON record: `status=ADVISORY_RECALL_CANDIDATE`, `severity=null`, and
`reportable=submission_ready=concluded=emits_finding=production_routing=confirmed=canonical_record=False`. The
generator re-asserts this contract on every row and fails if any upstream record violated it.

## Controls
- **Present:** `select_for_p266_poc_queue` — advisory only; writes ONLY to the isolated P266 PoC queue (Phase 3),
  never to a canonical record. (On the static HTML the checkbox is disabled; selection is the manual Phase-3 step.)
- **Absent by design:** promote_to_finding · confirm · set_severity · mark_reportable · mark_submission_ready ·
  submit. It is structurally impossible for a candidate on this surface to be made to look confirmed/reportable.

## Operator selection flow
The operator reads the advisory feed, picks 2–4 candidates for PoC routing (Phase 3 TRIAGE_AND_POC_QUEUE.md writes
the isolated queue JSON). No selection mutates any canonical record or sets any authority field.

## Freeze
Feed + page hashed above; frozen before triage. `scripts/dashboard_sync.py` re-checked byte-identical (`c1af70e1`).
