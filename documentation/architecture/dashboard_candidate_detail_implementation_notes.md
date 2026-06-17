# Dashboard Candidate-Validation Detail View — Implementation Notes

Implements the read-only dashboard surface for the candidate→PoC validation pipeline blueprinted in
`candidate_validation_to_poc_blueprint.md`. A reviewer clicks a candidate and sees the full validation packet
(sections A–N) including the exploit path. **Read-only**: no PoC/report generation, no promotion, no mutation of
detector outputs, validation artifacts, production gates, or the frozen corpus.

## Phase 1 — current dashboard structure (inventory)
- **Backend:** `scripts/dashboard.py` — FastAPI on :8765. Routes via `@app.get/post("/api/...")`; pages via
  `FileResponse`; `app.mount("/static", StaticFiles(directory=dashboard/))`. Production state from `_build_state()`
  (severity/exploitability/judge/triage) — **left untouched**. The research-track `/validation` page + its
  `/api/validation/*` routes already exist (Human Validation / Investigation Workspace).
- **Frontend:** vanilla JS + HTML in `dashboard/` (`index.html`/`app.js` = production; `validation.html`/
  `validation.js` = research validation console). No build step; served from disk.
- **Candidate/vulnerability list model (before):** the only candidate list was the `/validation` evidence-bundle
  queue (frozen corpus). There was no per-candidate *validation packet* view.
- **Where rows render / click behavior added:** a **new** standalone page `/candidates` (not bolted onto
  `/validation`, which keeps that file untouched and gives the large A–N view its own room). Rows render in the left
  column grouped by lifecycle; clicking a row (or deep-linking `?candidate_id=`) renders the detail on the right.
- **Where data is loaded from:** `documentation/research/candidates/<audit_id>/<candidate_hash>/` artifacts; plus
  the frozen corpus (`documentation/evals/judge_corpus/frozen_corpus.json`) to back **RAW_CANDIDATE** rows for
  candidates that have no validation folder yet.

## Files changed
**New**
- `scripts/candidate_detail.py` — read-only adapter (loader + list + normalizer).
- `dashboard/candidates.html`, `dashboard/candidates.js` — the self-contained `/candidates` UI.
- `tests/candidate_detail/test_candidate_detail.py` — loader tests.
- `documentation/research/candidates/size-credit-2024-06/5100f196/` — **illustrative** fixture (15 artifacts;
  `report_ready.lock.json` intentionally omitted to demo a missing artifact). Every file is `"_illustrative": true`,
  `routing_allowed:false`, `research_only:true`.
- this notes doc.

**Edited (minimal, additive)**
- `scripts/dashboard.py` — `import candidate_detail as cd`; `CANDIDATES_HTML` path; 3 routes (`GET /candidates`,
  `GET /api/candidates`, `GET /api/candidate`). No other route / `_build_state` change.

**Must NOT touch (and did not)**
- detector scripts/outputs, `normalize_research_findings.py`, `evidence_bundle_gate.py`, `human_validation.py` /
  `investigation_workspace.py` *logic*, production gates, `submission/`, `frozen_corpus.json`, `validation.html/js`,
  `_build_state`, the production PoC/report engines.

## Data model added — `CandidateDetail`
`candidate_detail.load_candidate_detail(candidate_id)` returns a UI-safe dict: candidate_id, audit_id,
candidate_hash, detector, lifecycle_state, outcome, status_group, source{file,line,signature,snippet,source_hash,
abs_path,resolution_status}, **confidence{detector,validation,exploit,impact}** (always four distinct keys),
rationale (+evidence), reachability, callable_surface, state_mutation_map, defense_map, invariant_analysis,
exploit_sequences[], negative_tests, scorecard, promotion_decision, poc_ready{exists,authorizes,warning,data},
report_ready{exists,data}, evidence_timeline[], missing_artifacts[], hard_blockers[], next_action, illustrative,
sections{<artifact>:{status}}, raw{...}. `list_candidates()` merges candidate folders + frozen-corpus bundles
(as RAW) into list rows (Phase-2 fields). Reuses `human_validation.load_corpus` + `human_validation.abs_source`.

## Route / component & how to open a detail view
- Open `http://localhost:8765/candidates`.
- Click any candidate, **or** deep-link `http://localhost:8765/candidates?candidate_id=<candidate_id>` (URL updates
  on selection so a specific candidate is shareable/reopenable locally).
- Worked example: `/candidates?candidate_id=multicall_invariant:Multicall:multicall:pre_post_supply_invariant:5100f196`.

## Missing-artifact handling
Each artifact section reports `present | missing | failed`. Missing artifacts render "missing / not yet generated"
(never crash). A candidate with **no folder** that is a known corpus bundle returns a **RAW_CANDIDATE shell**
(source/rationale/detector_confidence from the bundle; all 16 artifacts `missing`; `next_action="resolve source"`).
A completely unknown candidate also returns safely (no folder, no crash).

## Exploit-path rendering
Section I renders each candidate sequence as a readable **Step 0..9 chain** (function, file:line, read/write,
effect, evidence ref, confidence, blockers) under a plain-English summary. If none exist: *"No complete exploit path
has survived validation yet"* + the list of missing artifacts needed to build one.

## Safe POC_READY display
- POC_READY is shown only as a status group label **"POC_READY — local PoC task allowed"** and the section-K banner
  carries the verbatim warning: *"POC_READY permits local PoC task creation only. It is not a severity verdict or
  submission approval."* The lock's `not_authorized` list (severity_verdict/submission/report_generation) is shown.
- The four confidences are four separate labeled cards (Detector / Validation / Exploit / Impact). Detector
  confidence is explicitly captioned "detector flagged it (NOT proof)" and is never merged with exploit confidence.
- Section L states report drafting is a separate human gate, never implied by POC_READY.

## Tests run
`pytest tests/candidate_detail tests/human_validation -q` → **38 passed**. `node --check dashboard/candidates.js` →
OK. Coverage: complete fixture loads full packet; four distinct confidence keys; POC_READY warning text; missing-
folder RAW shell; unknown candidate no-crash; KILLED tmp fixture surfaces kill reason; loader performs **no writes**
(mtime set unchanged); list grouping/counts.

## Update — Stage-1 generator now feeds real artifacts
`scripts/candidates/validate_candidate.py` (gates `source_resolve` → `reachability` → `context_map`, via
`scripts/candidates/gates/*` + `artifacts.py` + `policy.py` + `config/candidate_validation_policy.json`) now emits
**real** artifacts into `documentation/research/candidates/<audit_id>/<candidate_hash>/`, taking a candidate from
RAW_CANDIDATE → CONTEXT_MAPPED. The dashboard renders them with **no code change** (shapes match this doc).
Worked real example: `5d1136da` (`size-credit-2024-06`) — RESOLVED_SOURCE (md5 `cecf083…`), REACHABLE (Size.sol:142
facade), CONTEXT_MAPPED (isMulticall/Deposit.sol:80/final-invariant refs, 18-fn callable surface). It stops at
CONTEXT_MAPPED (`poc_allowed:false`, `report_allowed:false`, no poc/report locks). The generator refuses to
overwrite the illustrative `5100f196` fixture unless `--force`. See `candidate_validation_to_poc_blueprint.md`.

## Update — Stage-2 gates (defense_map + invariant) now feed real artifacts
`validate_candidate.py --max-stage invariant` adds `scripts/candidates/gates/{defense_map_gate,invariant_gate}.py`,
advancing a candidate CONTEXT_MAPPED → **INVARIANT_ANALYZED** and emitting **defense_map.json** + **invariant_analysis.json**
(plus updated scorecard/promotion/verdict). The dashboard renders them with **no code change** (artifacts carry the
alias keys `candidates.js` reads: `defenses[]`/`checks_skipped_when_isMulticall` and `invariant_statement`/`covers`/
`may_not_cover`/`sufficient_or_incomplete`; rich arrays in the raw accordion). Real example `5d1136da`: facade
`whenNotPaused`, isMulticall cap-skip at Deposit.sol:80 (`validateBorrowATokenCap`), final invariant
`validateBorrowATokenIncreaseLteDebtTokenDecrease` (CapsLibrary.sol:19) excerpted; coverage conclusion =
"partially covers / cannot determine" (hypothesis, not a bug). Stops at INVARIANT_ANALYZED:
`poc_allowed:false`/`report_allowed:false`, `next_required_gate:sequence_gate`, exploit/impact confidence `null`, no
sequence/negative/poc/report artifacts. `--max-stage` default stays `context` (Stage-1 behavior unchanged).

## Known limitations
- The validation pipeline (gates/scripts) is **not built yet** (blueprint is design-only), so all real candidates
  currently appear as **RAW_CANDIDATE** (sourced from the frozen corpus); the only fully-populated packet is the
  **illustrative** `5100f196` fixture, flagged with an ILLUSTRATIVE banner. Once `scripts/candidates/*` emit real
  artifacts, the same view renders them with no UI change.
- Single illustrative fixture; KILLED is exercised only in tests (tmp fixture).
- Read-only by design — no promote/kill/PoC actions from the dashboard.
- `WSL_DISTRO` is hardcoded to `Ubuntu` for the Open-in-VS-Code link (matches the workspace).
