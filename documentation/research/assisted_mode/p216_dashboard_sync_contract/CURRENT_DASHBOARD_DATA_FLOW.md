# P216 — CURRENT DASHBOARD DATA FLOW

Two data worlds explain why P215 showed on root but not on /findings, /candidates, /funnel.

## World 1 — active audit workspace (root)
- **Routes:** `/` (index) → `/api/state` → `dashboard._build_state()`.
- **Reads:** the **active** audit (`config/active_audit.json`) workspace: `output/merged_findings.json`,
  `data/triage/*.jsonl`, `data/findings/<id>.json` (the Step-3 `populate_finding_metadata` substrate).
- **Renders:** severity distribution + triage funnel counts for the active audit.
- P215 populated this substrate on the zetachain audit → root shows the 12 ZETA candidates.

## World 2 — global research tracks (the three target pages)
- **Routes & readers:**
  - `/funnel` → `/api/funnel` → `funnel.load_records()` → `documentation/research/funnel/funnel_records.json`
    (+ `funnel/outcomes/*.json`).
  - `/findings` → `/api/findings` → `findings_overview.load_overview()` which aggregates **3 tracks**:
    runtime (`output_research/value_provenance_eval/runtime_status.jsonl`), **funnel** (`funnel.load_records()`),
    detector (`human_validation.load_corpus()`); + campaign (`output_research/option_a_campaign/ledger.jsonl`).
  - `/candidates` → `/api/candidates` → iterates `findings_overview.load_overview()["rows"]` (+ detector
    `candidate_detail.list_candidates()`).
- **Detail card** (the synced verifier card): `/api/candidate?candidate_id=<key>` →
  `finding_detail.load_unified_detail(key)` dispatched by key prefix (`funnel:`/`runtime:`/`detector`/`campaign:`).
  For every track it calls **`build_verifier_evidence(detail, raw, documents, track)`** → the full checklist:
  `report_summary`, `evidence_completeness`, `function_map`, attacker, `defense_map`, exploit steps, severity args,
  impact, `red_flags`, conversion, blocker. **Severity is never derived** (`_sev_or_status` rejects conversion tokens →
  `HUMAN_PENDING`); `submission_ready`/`routing_allowed` forced false.

## The funnel chokepoint
`funnel.load_records()` is the **single** reader feeding all three target pages (directly for `/funnel`, via
`findings_overview._load_funnel` for `/findings` and `/candidates`). `normalize_record()` validates enums
(`conversion` ∈ {CLEAN_HIT,STRONG_PARTIAL,ADJACENT,REJECTED,ABSTAINED,NONE}; `poc.poc_status` ∈
{NOT_STARTED,IN_PROGRESS,REPRODUCED,PARTIAL_REPRO,NOT_REPRODUCED}; `submission_status`; duplicate/scope/severity_check).

## Required fields the card consumes (so the adapter can fill the synced card)
`mechanism_correctness` → mech_confirmed · `severity_gate` → sev_bearing · `impact`/`suspected_mechanism`/`finding_title`
→ mechanism/attacker · `surface_function` + `contract_function`/`target` → function_map · `claimed_severity`/
`severity_recommendation`/`final_severity_recommendation` → severity (via `_sev_or_status`) · `novelty_status` ·
`reachability_verdict` · `p155_gate1_source_intent`/`p155_gate2_attacker_model` → red flags + intent · `vulnerable_output`
→ impact · `blocker_reason`/`primary_blocker_if_not_reportable` → blocker · `artifact_links`/source_refs → documents &
evidence. Sections derived from markdown docs (exploit steps ← `harness_design.md`, defense_map ← `defense_map.md`,
severity args ← `severity_finalization_memo.md`) — P216's renderer edit additionally honors **inline** versions of
these on the record.

## Why P215 split
P215 candidates were written to World 1 (audit workspace) — and then (prior turn) hand-appended to World 2's
`funnel_records.json`. P216 makes World 2 the canonical sync target for **all** sources via a generated mirror +
adapter, so future candidates never depend on which world they happened to land in.
