# Investigation Workspace

The dashboard's research-track investigation environment. It extends the Human Validation Console
(`human_validation_dashboard.md`) across the full human workflow:

```
Detector → Normalization → Evidence Bundle → Human Validation → Promotion Checklist
        → Chain Analysis Workspace → (future) PoC Investigation
```

Open it at **`http://localhost:8765/validation`** (`python scripts/dashboard.py`). It is a standalone, four-tab
console, fully isolated from the production pipeline dashboard at `/`.

> **Layer invariants (enforced by structure + a shared forbidden-field guard):**
> Human Validation = *review, don't route* · Promotion Checklist = *prioritize, don't verify* ·
> Chain Analysis = *explain, don't conclude* · Investigation Tracking = *organize, don't adjudicate*.
> Everything is `research_only:true` / `routing_allowed:false`. The workspace never surfaces or stores
> `is_bug`, `valid`, `severity`, `exploitability_score`, submission recommendation, bounty estimate, or routing —
> and shares no state with the production `_build_state`.

## Workflow
1. **① Review & Label** — browse/filter the 13 frozen bundles, inspect evidence, attach `hv-1` labels.
2. **② Promotion Checklist** — for the selected bundle, complete the 12 categories and choose an outcome.
3. **③ Chain Workspace** — for `PROMOTE_TO_CHAIN_ANALYSIS` bundles, build the 13-section bug chain, track status +
   Chain Confidence Evolution, export an investigation packet.
4. **④ Investigation Progress** — portfolio counts across promoted chains.

## Promotion lifecycle
A bundle starts `READY_FOR_REVIEW`. The promotion checklist records **12 categories** — evidence_coherence,
attacker_reachability, affected_asset_function, state_or_invariant, missing_validation, concrete_impact_hypothesis,
counter_signals_reviewed, poc_feasibility, scope_relevance, duplicate_known_issue_risk, next_step_confidence,
chain_completeness — each marked **met / partial / unmet / unknown** with an evidence reference. A live
**progress score** (met=1, partial=.5) and **completion status** are shown but **never auto-decide** the outcome.
The human chooses one of:
`PROMOTE_TO_CHAIN_ANALYSIS` · `NEEDS_MORE_EVIDENCE` · `HOLD_AS_WEAK_SIGNAL` · `ARCHIVE_AS_NOISE`.
(`chain_completeness`'s single-step vs multi-step nuance is captured in its evidence-ref/notes.)

## Chain-analysis lifecycle
Only `PROMOTE_TO_CHAIN_ANALYSIS` candidates open the Bug-Chain Builder (13 sections: Title/Finding Hypothesis,
System Context, Attacker Preconditions, Entry Point, Trust Assumption, Broken Check, Exploit Path, State Change,
Impact Hypothesis, PoC Plan, Counter Signals, Evidence Inventory, Open Questions). Each section carries notes,
code references, evidence references (with a **Source**: bundle / human_observation / external_note), an
**Evidence Attached? Yes/No** flag, and **⟦UNKNOWN⟧** / **⟦TO CONFIRM VIA PoC⟧** quick-insert tags. Impact stays a
*hypothesis*; nothing asserts severity or validity.

**Investigation status** (side panel) is one of: `not_started`, `researching`, `chain_mapping`, `poc_planning`,
`blocked`, `archived`.

### Chain Confidence Evolution
Three **manual, qualitative free-text** fields tracked alongside status: `initial_confidence`, `current_confidence`,
`reason_for_change` (e.g. initial "coherent hypothesis" → current "weaker after reviewing counter-signals" → reason
"invariant protected by secondary check"). It captures the reviewer's confidence in the *hypothesis* over time.
**It is not a verdict, not a severity, not a validity score.** Its later value: explaining *why* investigations
died or succeeded — without ever introducing severity/validity.

## File formats (new, append-only, under `documentation/evals/judge_corpus/`)
Each has a `.demo.jsonl` variant (header "demo files" toggle). All rows: `routing_allowed:false`,
`research_only:true`, and pass the forbidden-field guard. **Append-only** — saving never overwrites; the current
value is the newest row (per candidate, or per `(candidate, section_id)` for chain sections).

- **`promotion_labels.jsonl`** (`promo-1`): `timestamp, reviewer_alias, candidate_id, source_corpus_hash, detector,
  candidate_surface, categories{cat:{status,evidence_ref,notes}}, outcome, rationale, progress_score,
  completion_status, …flags`.
- **`chain_analysis.jsonl`** (`chain-1`): `timestamp, reviewer_alias, candidate_id, section_id (1..13),
  section_title, notes, code_references[], evidence_references[{source,ref}], evidence_attached, …flags`.
- **`investigation_status.jsonl`** (`status-1`): `timestamp, reviewer_alias, candidate_id, status, note,
  initial_confidence, current_confidence, reason_for_change, …flags`.

Bundles, detector outputs, normalization outputs, and `human_labels.jsonl` are **never modified**.

## Export format — Investigation Packet (Markdown)
`GET /api/validation/export/packet?candidate_id=…` (PROMOTE candidates only) returns Markdown that opens with the
mandatory banner:

```
⚠ Research Investigation — Not Validated — Not Severity Rated — Not Submission Ready
research_only:true · routing_allowed:false
```

then: Bundle → Human Labels → Promotion Checklist → Chain Sections → Chain Confidence Evolution → Open Questions.
Unauthored sections render as `⟦UNKNOWN⟧`. It is a research artifact, not a submission.

## API (additive; all read-only on the corpus)
`POST /api/validation/promotion` · `GET /api/validation/promotions` · `POST /api/validation/chain/section`
(409 unless the candidate's latest promotion is `PROMOTE_TO_CHAIN_ANALYSIS`) · `GET /api/validation/chain` ·
`POST /api/validation/status` · `GET /api/validation/investigation` · `GET /api/validation/export/packet`.

## Open in VS Code (jump to the vulnerable function)
The Bundle Detail (Tab ①) and the Chain Workspace header (Tab ③) show an **Open in VS Code** button that jumps
straight to the candidate function (`line` = the bundle's `location.start_line`). The backend computes the file's
absolute Linux path via `human_validation.abs_source(file_rel, ROOT)` — emitted **only** for files that resolve
under the repo root and exist (no traversal, no arbitrary-path leak); unresolvable sources show an "open manually"
note instead.

Because the dashboard runs in **WSL** while the browser is on **Windows**, the Linux path is mapped onto the
`\\wsl.localhost\<distro>\…` UNC path the Windows editor can open. A header **editor** selector (persisted locally)
chooses the link form:
- **VS Code (\\wsl.localhost)** *(default)* → `vscode://file//wsl.localhost/Ubuntu<linux-path>:<line>`
- **VS Code (WSL remote)** → `vscode://vscode-remote/wsl+Ubuntu<linux-path>:<line>`
- **Cursor (WSL remote)** → `cursor://vscode-remote/wsl+Ubuntu<linux-path>:<line>`
- **local path** → `vscode://file<linux-path>:<line>` (when the browser runs on the same host)

The displayed path and the **copy path** button use the Windows form
`\\wsl.localhost\Ubuntu\…\File.sol:<line>` (backslashes) so it can be pasted directly on Windows. The distro
defaults to `Ubuntu` (`WSL_DISTRO` in `dashboard/validation.js`).

## Snippet annotation (vulnerability hypothesis, at a glance)
The Bundle Detail code snippet is rendered with **display-only** inline comments explaining *why the detector
flagged it* — a header `// ── RESEARCH HYPOTHESIS — … (NOT a confirmed bug) ──` block (the detector's
`missing_binding_explanation`/`reason`/`rationale` + detector/signal + matched flags), inline ` // ⟵ flag: <token>`
markers on the first line containing each evidence token (e.g. `permittransferfrom`, `IERC20(asset)`, `balanceof`,
`delegatecall`), and one anchored `// ⚠ HYPOTHESIS: …` line. It is assembled in the browser from the bundle's own
evidence — the corpus and `code_snippet` are never modified — and is framed strictly as a hypothesis, never a
severity/validity verdict. An **explain (hypothesis)** checkbox (default on, persisted) toggles to the raw snippet
for diffing against the real file.

## Safety constraints
- Reads only the corpus + research JSONLs; touches no production state, no detector/normalization/gate/manifest/
  answer-key/submission/exploitability system.
- Every write passes `investigation_workspace.assert_no_forbidden_fields_deep` (shares
  `human_validation.FORBIDDEN_KEYS`) + a per-schema key allowlist — `is_bug`/`valid`/`severity`/`exploitability`/
  `submit`/`bounty`/routing cannot be stored, even nested inside a promotion category.
- Promotion outcome is human-chosen, never auto-derived. Impact is a hypothesis. Confidence is qualitative, not a
  verdict.
- Corpus opened read-only; corpus-hash bound into promotions, with a 409 drift guard + drift banner.

## Known limitations
- Small corpus (13 bundles); append-only history with no delete UI (by design); single local reviewer at a time
  (multi-reviewer agreement computed offline from the JSONLs). Un-wired: feeds only the (not-yet-built) judge
  evaluation; nothing routes to production. Distinct from the production `chains.md`/CHAIN-XXX and submission
  systems.

## Tests
`tests/investigation_workspace/test_investigation_workspace.py` — promotion (12 categories, enum/outcome
validation, scoring, forbidden-absent, no auto-outcome), chain sections (1..13, source enum, evidence_attached),
status + Chain Confidence Evolution, append-only + latest-wins, overview counts, export packet (banner + parts + no
forbidden tokens). Plus regression over `tests/human_validation`.
