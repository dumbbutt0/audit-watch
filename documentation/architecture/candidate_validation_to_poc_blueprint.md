# Blueprint — Candidate Validation → PoC Pipeline

> **Status: DESIGN ONLY. No code in this document.** It blueprints a strict, per-candidate validation pipeline
> that pushes a research detector candidate through 10 kill-gates until — and only until — a Proof-of-Concept task
> is justified. Nothing here is implemented; no PoC, report, script, config, or schema is created by this document.
>
> **Track: research-only / `routing_allowed:false`.** This layer is a continuation of the research detector
> platform (see `platform_overview.md`, `platform_invariants.md`, `investigation_workspace.md`). It is **separate
> from the production pipeline** (`triage_findings.py` → `model_exploitability.py` → `judge_simulate.py` →
> `confirm_gate.py` → `pre_submission_gate.py` → `submission/`) and does not route into it.

## What `POC_READY` means (and does not mean)
```
POC_READY is ONLY permission to create a LOCAL PoC task.
POC_READY is NOT a severity verdict.
POC_READY is NOT a submission/bounty verdict.
POC_READY is NOT permission to draft a report.
REPORT_READY is a separate, later, human-gated state and is NOT implied by POC_READY.
```
A candidate is **not a bug**. The pipeline never asserts validity, severity, or exploitability as fact; it produces
*hypotheses + evidence + pass/fail gate results*, and a `poc_ready.lock.json` that authorizes **only** the creation
of a local PoC task (which itself remains human-in-the-loop and runs through the existing PoC engine + L3 standard).

---

## 1. Architecture Overview

### Position in the platform
```
detector (*_audit.json)
  → normalize_research_findings.py  → research_findings_normalized.json
  → evidence_bundle_gate.py         → evidence_bundles.json   (READY_FOR_REVIEW)
  → [CANDIDATE VALIDATION PIPELINE]  ← this blueprint           (10 gates, per-candidate artifacts)
        → POC_READY (poc_ready.lock.json)  → make_poc_task.py → (existing) build_poc_queue.py → PoC engine
        → REPORT_READY (report_ready.lock.json)  → (human) report drafting
```
The pipeline **consumes** existing research-track output and **reuses** existing primitives rather than
re-implementing them. It writes only to a new research area; it never writes to `audits/<id>/output/` (the wired
production substrate) and never calls a production gate.

### Reuse map (every item below already exists in the workspace)
| Pipeline concept | Reuses |
|---|---|
| Candidate input + IDs | `evidence_bundles.json` / `research_findings_normalized.json` (candidate_id `<detector>:<lens_id>:<hash8>`), raw `scripts/multicall_invariant_audit.py` output |
| Forbidden-field guard | `human_validation.FORBIDDEN_KEYS` + `assert_no_forbidden_fields` (and `investigation_workspace.assert_no_forbidden_fields_deep`) |
| Append-only + four flags discipline | `investigation_workspace.py` row pattern (`routing_allowed:false`, `research_only:true`) |
| source_resolve | `human_validation.abs_source(file_rel, roots)` + evidence-bundle `location`/`code_snippet` (brace-aware) |
| reachability / scope (as research analogues, NOT wired) | the *contracts* of `confirm_gate.py` and `submission/gates/gate_scope.py`, `gate_reachability.py` |
| context_map / defense_map / invariant / sequence | `investigation_workspace` `PROMOTION_CATEGORIES` + the 13 `CHAIN_SECTIONS` (Attacker Preconditions, Entry Point, Broken Check, Exploit Path, State Change, Impact Hypothesis, Counter Signals) |
| negative_validation | design analogue of `judge_simulate.py` persona objections + `pre_submission_gate.py` kill tags |
| certainty_score | strict all-required-true variant of the 12-category promotion checklist (`human_vuln_promotion_checklist.md`) |
| poc_readiness handoff | the lock that a new `make_poc_task.py` checks before handing to `build_poc_queue.py` → `generate_poc_plan.py` → `generate_poc_test.py` → `run_poc_tests.py` → `poc_validation_gate.py` (L3 standard in `documentation/poc-development.md` / CLAUDE.md) |
| path resolution | `scripts/audit_context.py` (`get_active_audit`, ROOT) — but artifacts land under `documentation/research/candidates/` |

### Hard rule (restated, enforced at the lock)
> Never create a PoC file, exploit script, or submission report from a detector candidate unless a
> `poc_ready.lock.json` exists for that candidate **and** every hard gate passed. `make_poc_task.py --require-lock`
> refuses to run otherwise.

---

## 2. Candidate Lifecycle State Machine

```
RAW_CANDIDATE
   │ source_resolve_gate
   ├─ fail→ KILLED (mismatch) / NEEDS_CONTEXT (unresolved)
   ▼
RESOLVED_SOURCE
   │ reachability_gate
   ├─ fail→ KILLED (no attacker path) / NEEDS_CONTEXT (callgraph unknown)
   ▼
REACHABLE ──scope_gate──► (fail→ KILLED/NEEDS_CONTEXT)
   ▼
CONTEXT_MAPPED        ◀── HUMAN REVIEW POINT #1
   │ defense_map_gate
   ▼
DEFENSE_MAPPED
   │ invariant_gate (fail→ KILLED: no invariant)
   ▼
INVARIANT_ANALYZED
   │ sequence_gate (no sequence→ PARTIAL; all blocked→ KILLED)
   ▼
SEQUENCE_CANDIDATE    ◀── HUMAN REVIEW POINT #2
   │ negative_validation_gate (survives kill checks?)
   ▼
NEGATIVE_TESTED
   │ certainty_score_gate (all required true?)
   ▼
VALIDATION_READY      ◀── HUMAN REVIEW POINT #3 (before POC_READY)
   │ poc_readiness_gate → writes poc_ready.lock.json
   ▼
POC_READY ───(make_poc_task)──► local PoC task (existing engine)
   ⋮ (after PoC proves impact, human)
   ▼
REPORT_READY          ◀── HUMAN REVIEW POINT #4 (before REPORT_READY)

terminal off-ramps from any state: KILLED, NEEDS_CONTEXT, PARTIAL
```

Per-state contract (entry / required artifact / pass / fail / next / advanced-by):

| State | Entry condition | Required artifact | Pass criteria | Fail → | Advanced by |
|---|---|---|---|---|---|
| **RAW_CANDIDATE** | a bundle/normalized record exists | `candidate_manifest.json` | manifest written w/ candidate_id+audit_id+source ref | — | script (ingest) |
| **RESOLVED_SOURCE** | manifest exists | `source_resolution.json` | file+function located, snippet/signature matches, line range + source hash recorded | KILLED if mismatch; NEEDS_CONTEXT if unresolved | script |
| **REACHABLE** | source resolved | `reachability_map.json`, `callable_surface.json` | external/public entry → candidate path; no privileged-only blocker the attacker can't satisfy | KILLED if no path; NEEDS_CONTEXT if callgraph unresolved | script |
| **CONTEXT_MAPPED** | reachable + in-scope | `state_mutation_map.json` (+ scope check in manifest) | all related state/fns/contracts mapped (detector-specific) | NEEDS_CONTEXT | script → **human review #1** |
| **DEFENSE_MAPPED** | context mapped | `defense_map.json` | guards/modifiers/checks enumerated incl. checks skipped in batch | NEEDS_CONTEXT | script |
| **INVARIANT_ANALYZED** | defenses mapped | `invariant_analysis.json` | exactly one invariant statement + pre/post vars + mutating fns + why final check suffices/fails | KILLED if no meaningful invariant | script |
| **SEQUENCE_CANDIDATE** | invariant stated | `sequence_candidates.json` | ≥1 attacker-controlled, encodable sequence w/ preconditions + expected violation + impact | PARTIAL if suspicious-no-sequence; KILLED if all blocked | script → **human review #2** |
| **NEGATIVE_TESTED** | ≥1 sequence | `negative_tests.json` | survives all kill checks (guards/final-invariant/state/perm/impact/caller-local/intended/duplicate) | KILLED if any kill check refutes every sequence | script |
| **VALIDATION_READY** | survived kills | `validation_scorecard.json`, `promotion_decision.json` | all required certainty fields true | PARTIAL / NEEDS_CONTEXT | script → **human review #3** |
| **POC_READY** | scorecard all-true + human ok | `poc_ready.lock.json` | lock written (see §10) | — | **human** confirms; script writes lock |
| **REPORT_READY** | PoC proved impact (L3) + human ok | `report_ready.lock.json` | separate human gate (not implied by POC_READY) | — | **human** |
| **KILLED** | any gate refutation | `verdict.md` | terminal | — | script (no human needed) |
| **NEEDS_CONTEXT** | unresolved input | `verdict.md` | terminal-pending | — | script |
| **PARTIAL** | suspicious, incomplete | `verdict.md` | parked | — | script |

**Who may advance:** deterministic scripts advance and may **KILL** without human review (cheap leads die fast).
Promotion *past* CONTEXT_MAPPED, *past* SEQUENCE_CANDIDATE, *to* POC_READY, and *to* REPORT_READY each require an
explicit human review (§9).

---

## 3. Validation Gates

Each gate is a separate module under `scripts/candidates/gates/`. All read prior artifacts + source (read-only) and
write one artifact with the common header (§4). All emit a status in {PASS, NEEDS_CONTEXT, PARTIAL, KILLED}.

**A. source_resolve_gate** — *reuses `hv.abs_source`, evidence-bundle `location`/`code_snippet`.*
Pass: file exists; function located; snippet/AST signature matches; line range captured; **source hash recorded**.
Fail: NEEDS_CONTEXT (unresolved) / KILLED (nonexistent or mismatched code). → `source_resolution.json`.

**B. reachability_gate** — *reuses the contract of `confirm_gate.py` (reachability_status), as a research artifact.*
Pass: external/public entrypoint found; call path entry→candidate; no privileged-only blocker unless attacker can
satisfy it; no owner/admin/governance assumption. Fail: KILLED (no attacker-reachable path) / NEEDS_CONTEXT
(callgraph unresolvable). → `reachability_map.json`, `callable_surface.json`.

**C. scope_gate** — *reuses `submission/gates/gate_scope.py` contract + coverage-manifest `in_scope`.*
Pass: source path in target repo; asset in scope or impact has primacy; no excluded assumption. Fail:
KILLED / NEEDS_CONTEXT. (Records the manifest `in_scope` flag.) → recorded in `candidate_manifest.json`.

**D. context_map_gate** — *reuses `investigation_workspace` context fields.*
For multicall candidates require: all `isMulticall` references; all external/public functions callable through
multicall; all delegatecall/self-call paths; all functions mutating the compared accounting variables; all
validation functions related to the invariant. → `state_mutation_map.json`.

**E. defense_map_gate** — *reuses `submission/gates/gate_defense.py` contract.*
Map: modifiers; access control; reentrancy guards; pause checks; slippage/minimum checks; solvency/invariant
checks; multicall restrictions; **validations skipped during multicall**; token-transfer restrictions. →
`defense_map.json`.

**F. invariant_gate** — *reuses the "Broken Check"/"State Change" chain sections + promotion `state_or_invariant`.*
Pass: exactly one invariant statement; pre-state vars; post-state vars; mutating fns; reason the final validation is
sufficient or incomplete; exact security property at risk. Fail: KILLED if no meaningful invariant. →
`invariant_analysis.json`.

**G. sequence_gate** — *reuses chain sections Attacker Preconditions / Entry Point / Exploit Path / Impact
Hypothesis; analogue of `model_exploitability.py execution_sequence`.* Pass: ≥1 attacker-controlled sequence;
encoded/encodable calls; preconditions; expected state transitions; expected violated invariant; expected impact;
defenses considered. Fail: PARTIAL (no full sequence) / KILLED (every sequence blocked). **Does not write a PoC.**
→ `sequence_candidates.json`.

**H. negative_validation_gate** — *analogue of `judge_simulate` objections + `pre_submission_gate` kill tags.*
Try to kill before PoC: known guards block sequence; final invariant catches sequence; required state unreachable;
attacker lacks permissions; no value/protocol impact; caller-local only; intended behavior; duplicate/known accepted
risk (if local data exists). Advance only if a sequence **survives**. → `negative_tests.json`.

**I. certainty_score_gate** — *strict variant of the 12-category promotion checklist.*
Required booleans (ALL must be true to reach POC_READY): `source_resolved`, `attacker_reachable`, `in_scope`,
`invariant_defined`, `defense_bypassed_or_missing`, `concrete_sequence`, `measurable_impact`, `testable_locally`,
`no_kill_condition_found`. **A weighted average alone may never promote.** → `validation_scorecard.json`,
`promotion_decision.json`.

**J. poc_readiness_gate** — writes `poc_ready.lock.json` **only** when all hard requirements pass (see §10). Records:
candidate_id; exact sequence to test; target test-file suggestion; setup requirements; expected assertion; impact
claim (hypothesis); gates passed; unresolved risks; and the explicit statement that **no report generation is
authorized**.

---

## 4. Gate Artifact Schema

**Common header (every artifact):**
```json
{
  "candidate_id": "multicall_invariant:Multicall:multicall:pre_post_supply_invariant:5100f196",
  "audit_id": "size-credit-2024-06",
  "contract_path": "audits/size-credit-2024-06/contracts/2024-06-size/contracts/libraries/Multicall.sol",
  "source_hash": "md5:cecf083ad025a572e8e8766a6e86c1c4",
  "git_commit": null,
  "generated_at": "<UTC ISO>",
  "tool": "scripts/candidates/gates/<gate>.py",
  "evidence_refs": ["<file>:<line>", "..."],
  "status": "PASS|NEEDS_CONTEXT|PARTIAL|KILLED",
  "reasons": ["..."],
  "unresolved_assumptions": ["..."],
  "routing_allowed": false,
  "research_only": true
}
```
*(`git_commit` is `null` when the source tree is not a git repo — verified: `audits/size-credit-2024-06` is not a
git repo, so `source_hash` carries the md5 instead.)*

**Per-artifact bodies (added under the header):**
- `candidate_manifest.json` — detector, detector_version, candidate_surface, location, **detector_confidence**
  (verbatim from bundle), declared_severity_potential, in_scope+reason, lifecycle_state.
- `source_resolution.json` — resolved_abs_path, function_signature, line_range, snippet_match (bool), source_hash.
- `reachability_map.json` — entrypoints[], call_path[], privileged_blockers[], attacker_can_satisfy (bool).
- `callable_surface.json` — externally callable fns reaching the candidate (for multicall: callable sub-calls).
- `state_mutation_map.json` — variables, mutating_functions[], related_validations[], flag_behavior (isMulticall).
- `defense_map.json` — guards[] {type, location, blocks_sequence?}, skipped_in_batch[].
- `invariant_analysis.json` — invariant_statement, pre_state[], post_state[], mutators[], final_check_sufficient
  (bool + why), security_property.
- `sequence_candidates.json` — sequences[] {steps[], preconditions[], expected_transition, expected_violation,
  expected_impact, defenses_considered[]}.
- `negative_tests.json` — kill_checks[] {name, result (refuted|survived), evidence}, survived (bool).
- `validation_scorecard.json` — the 9 required booleans + the four confidences (§8) + overall.
- `promotion_decision.json` — from_state, to_state, decided_by (script|human), rationale, human_review_ref.
- `poc_ready.lock.json` / `report_ready.lock.json` — see §10.

---

## 5. Command Interface

```bash
python scripts/candidates/validate_candidate.py \
  --candidate-id "multicall_invariant:Multicall:multicall:pre_post_supply_invariant:5100f196" \
  --audit-id "size-credit-2024-06" \
  --candidate-json "documentation/evals/judge_corpus/_runs/size-credit-2024-06/output/multicall_invariant_audit.json" \
  --target-root "audits/size-credit-2024-06/contracts/2024-06-size" \
  --mode strict        # runs gates A→I in order, stops at first KILLED/NEEDS_CONTEXT/PARTIAL or human-review pause

python scripts/candidates/promote_candidate.py --candidate-id "<id>" --to POC_READY --strict
python scripts/candidates/candidate_status.py  --candidate-id "<id>"     # prints state + per-gate status
python scripts/candidates/list_poc_ready.py                              # all candidates holding a valid lock
python scripts/candidates/make_poc_task.py --candidate-id "<id>" --require-lock
#   ^ REFUSES unless poc_ready.lock.json exists AND all hard gates passed; then enqueues into the existing
#     build_poc_queue.py flow. It does NOT itself generate a PoC, a report, or a submission.
```

---

## 6. Directory Layout
```
documentation/research/candidates/<audit_id>/<candidate_hash>/
  candidate_manifest.json   source_resolution.json   reachability_map.json   callable_surface.json
  state_mutation_map.json   defense_map.json         invariant_analysis.json sequence_candidates.json
  negative_tests.json       validation_scorecard.json promotion_decision.json
  poc_ready.lock.json       report_ready.lock.json    notes.md                verdict.md

scripts/candidates/
  validate_candidate.py  promote_candidate.py  candidate_status.py  list_poc_ready.py  make_poc_task.py
  gates/
    source_resolve_gate.py  reachability_gate.py  scope_gate.py  context_map_gate.py  defense_map_gate.py
    invariant_gate.py       sequence_gate.py      negative_validation_gate.py  certainty_score_gate.py
    poc_readiness_gate.py

config/candidate_validation_policy.json
tests/candidates/            # pure-function gate tests (mirrors tests/<lens>/ convention)
```
`<candidate_hash>` = the 8-char suffix of candidate_id (e.g. `5100f196`). Artifacts live under
`documentation/research/` (research-only); **never** under `audits/<id>/output/`.

---

## 7. Policy Design — `config/candidate_validation_policy.json`
```json
{
  "schema_version": 1,
  "required_gates_by_detector": {
    "default": ["source_resolve","reachability","scope","context_map","defense_map",
                "invariant","sequence","negative_validation","certainty_score","poc_readiness"],
    "multicall_invariant": ["source_resolve","reachability","scope","context_map","defense_map",
                            "invariant","sequence","negative_validation","certainty_score","poc_readiness"]
  },
  "hard_blockers": ["source_mismatch","no_attacker_path","out_of_scope","no_invariant","all_sequences_blocked"],
  "detector_requirements": {
    "multicall_invariant": {
      "must_map": ["self_delegatecall_paths","isMulticall_flag_behavior",
                   "before_after_accounting_variables","final_invariant_function_explanation",
                   "callable_subcall_list"],
      "must_produce": ["sequence_candidates","negative_tests_against_final_invariant"],
      "poc_ready_requires": "at_least_one_harmful_sequence_survives_negative_tests"
    }
  },
  "certainty_required_true": ["source_resolved","attacker_reachable","in_scope","invariant_defined",
    "defense_bypassed_or_missing","concrete_sequence","measurable_impact","testable_locally","no_kill_condition_found"],
  "poc_readiness_requirements": { "all_certainty_required_true": true, "human_review_3_signed": true },
  "report_readiness_requirements": { "poc_proved_at_level": "L3", "human_review_4_signed": true,
    "note": "REPORT_READY is independent of POC_READY and never auto-granted" }
}
```

---

## 8. Confidence Language (four separate fields — never conflated)
| Field | Source of truth | May it promote to PoC? |
|---|---|---|
| `detector_confidence` | carried **verbatim** from the bundle (e.g. `high`) | **No** — never promotes directly |
| `validation_confidence` | requires the gate artifacts to exist + pass | contributes only |
| `exploit_confidence` | requires a concrete surviving sequence (`sequence_candidates.json` + `negative_tests.json`) | required for POC_READY |
| `impact_confidence` | requires measurable protocol harm stated as a testable assertion | required for POC_READY |
Rule: `detector_confidence` is an input signal, not a verdict. Only the certainty scorecard (all required booleans
true) + human review #3 yields POC_READY.

---

## 9. Human Review Points
Pause for human review **after CONTEXT_MAPPED**, **after SEQUENCE_CANDIDATE**, **before POC_READY**, and **before
REPORT_READY**. Killing weak candidates (any gate refutation) requires **no** human review — the system fails fast.
Human decisions are recorded in `promotion_decision.json` (`decided_by:"human"`, `human_review_ref`) and may reuse
the existing `/validation` investigation-workspace review surface (same candidate_id).

---

## 10. Example Outputs — Size multicall (values verified from source this task)

> **Provenance.** The following were directly verified against the working tree on 2026-06-01:
> `Multicall.sol:26` function + self-delegatecall loop + before/after capture + `validateBorrowATokenIncreaseLte
> DebtTokenDecrease`; `isMulticall` set/unset at `Multicall.sol:27/44`, declared at `SizeStorage.sol:94`, read at
> `Deposit.sol:80` gating `state.validateBorrowATokenCap()` at `Deposit.sol:81`; external entry
> `Size.sol:142 multicall(bytes[] calldata _data)`; md5 `cecf083ad025a572e8e8766a6e86c1c4`; detector candidate
> (`finding_shape:pre_post_supply_invariant`, `confidence:high`, `manifest_id:function:Multicall:multicall#abbe5b7b`,
> `visibility:internal`); corpus `candidate_id ...:5100f196` (`declared_severity_potential:medium`). Any value NOT in
> this list is an **illustrative placeholder** and is tagged `"_illustrative": true`.

### 10a. candidate_manifest.json (verified inputs)
```json
{
  "candidate_id": "multicall_invariant:Multicall:multicall:pre_post_supply_invariant:5100f196",
  "audit_id": "size-credit-2024-06",
  "contract_path": "audits/size-credit-2024-06/contracts/2024-06-size/contracts/libraries/Multicall.sol",
  "source_hash": "md5:cecf083ad025a572e8e8766a6e86c1c4",
  "git_commit": null,
  "generated_at": "<UTC ISO>",
  "tool": "scripts/candidates/validate_candidate.py",
  "detector": "multicall_invariant",
  "detector_confidence": "high",
  "declared_severity_potential": "medium",
  "candidate_surface": "Multicall.multicall",
  "location": {"file": ".../libraries/Multicall.sol", "start_line": 26},
  "manifest_id": "function:Multicall:multicall#abbe5b7b",
  "visibility": "internal",
  "in_scope": true,
  "lifecycle_state": "RAW_CANDIDATE",
  "routing_allowed": false, "research_only": true
}
```

### 10b. validation_scorecard.json — SUCCESS path (booleans illustrative pending real gate runs)
```json
{
  "candidate_id": "multicall_invariant:Multicall:multicall:pre_post_supply_invariant:5100f196",
  "audit_id": "size-credit-2024-06", "source_hash": "md5:cecf083ad025a572e8e8766a6e86c1c4",
  "_illustrative": true,
  "required": {
    "source_resolved": true, "attacker_reachable": true, "in_scope": true, "invariant_defined": true,
    "defense_bypassed_or_missing": true, "concrete_sequence": true, "measurable_impact": true,
    "testable_locally": true, "no_kill_condition_found": true
  },
  "confidences": {"detector_confidence":"high","validation_confidence":"high",
                  "exploit_confidence":"medium","impact_confidence":"medium"},
  "all_required_true": true,
  "reasons": ["external entry Size.sol:142 → internal Multicall.multicall (verified path exists)",
              "isMulticall skips validateBorrowATokenCap at Deposit.sol:80 (verified) — per-call cap deferred",
              "final invariant validateBorrowATokenIncreaseLteDebtTokenDecrease may be incomplete across interleavings (HYPOTHESIS)"],
  "unresolved_assumptions": ["a concrete sub-call interleaving that the final invariant fails to catch (to be proven by PoC)"],
  "routing_allowed": false, "research_only": true
}
```

### 10c. promotion_decision.json
```json
{
  "candidate_id": "...:5100f196", "from_state": "VALIDATION_READY", "to_state": "POC_READY",
  "decided_by": "human", "human_review_ref": "review#3:<alias>:<UTC>",
  "rationale": "all 9 required booleans true; ≥1 harmful sequence survived negative tests (illustrative)",
  "_illustrative": true, "routing_allowed": false, "research_only": true
}
```

### 10d. poc_ready.lock.json (the authorization — local PoC task ONLY)
```json
{
  "candidate_id": "multicall_invariant:Multicall:multicall:pre_post_supply_invariant:5100f196",
  "audit_id": "size-credit-2024-06", "source_hash": "md5:cecf083ad025a572e8e8766a6e86c1c4",
  "_illustrative": true,
  "authorizes": "local_poc_task_only",
  "not_authorized": ["severity_verdict","submission","report_generation"],
  "exact_sequence_to_test": ["call Size.multicall([...]) batching deposit/withdraw sub-calls",
                             "interleave so per-call validateBorrowATokenCap is skipped (isMulticall=true)",
                             "observe final validateBorrowATokenIncreaseLteDebtTokenDecrease passes while a cap/accounting invariant is breached (HYPOTHESIS — to prove)"],
  "target_test_file_suggestion": "pocs/<runner>/size-credit-2024-06/multicall_invariant_5100f196/...",
  "setup_requirements": ["deploy Size with a market","attacker EOA with deposit funds (illustrative)"],
  "expected_assertion": "post-batch accounting/cap invariant violated despite final check passing",
  "impact_claim": "HYPOTHESIS: accounting/cap bypass via multicall interleaving (severity TBD by PoC, not here)",
  "gates_passed": ["source_resolve","reachability","scope","context_map","defense_map","invariant","sequence","negative_validation","certainty_score"],
  "unresolved_risks": ["final invariant may in fact catch all interleavings → would flip to KILLED on PoC"],
  "report_generation_allowed": false,
  "routing_allowed": false, "research_only": true
}
```

### 10e. KILLED example (verdict.md + scorecard excerpt)
A plausible KILLED outcome for this same candidate if negative tests refute it:
```json
{
  "candidate_id": "...:5100f196", "status": "KILLED", "_illustrative": true,
  "killed_by": "negative_validation_gate",
  "reasons": ["final validateBorrowATokenIncreaseLteDebtTokenDecrease provably catches every constructed interleaving",
              "OR Multicall.multicall is internal and no external entry reaches it (would KILL at reachability)"],
  "no_poc_task_created": true, "routing_allowed": false, "research_only": true
}
```
*(Reachability note: `Multicall.multicall` is `internal` — verified — so reachability depends on the external
facade `Size.sol:142 multicall(bytes[])`; if that path were absent the candidate would be KILLED at the
reachability gate. This is exactly the kind of fast kill the pipeline exists to do.)*

---

## 11. Backward Compatibility & Dashboard Integration
- **Consumes, never mutates:** reads `evidence_bundles.json` / `*_audit.json` / source; writes only new artifacts
  under `documentation/research/candidates/`. Detector outputs, normalized output, the frozen corpus, production
  gates, manifests, and `submission/` are untouched.
- **Dashboard:** the existing `/validation` investigation workspace already keys on `candidate_id`; it can render a
  per-candidate **lifecycle_state** badge + per-gate status (read-only) and link to the artifacts, or the
  promotion/chain tabs can be backed by these artifacts. No production dashboard (`_build_state`, severity/verdict
  UI) is touched. Cross-links: `investigation_workspace.md`, `human_vuln_promotion_checklist.md`.
- **Relationship to production:** if a human later decides to take a POC_READY candidate into the *production*
  pipeline, that is a separate, explicit, human bridging step (out of scope here) — the validation layer never
  auto-bridges.

---

## 12. Implementation Phases, Risks, Acceptance Criteria

### Phases
1. Artifacts + `candidate_validation_policy.json` + `candidate_manifest`/`source_resolution` (reuse `hv.abs_source`).
2. Deterministic gates A–C (source/reachability/scope) + `candidate_status.py` + `tests/candidates/`.
3. Gates D–F (context/defense/invariant) + human-review pause #1.
4. Gates G–H (sequence/negative) + human-review pause #2.
5. `certainty_score_gate` + `validation_scorecard`/`promotion_decision` + human-review #3.
6. `poc_readiness_gate` → `poc_ready.lock.json`; `make_poc_task.py --require-lock` handoff to `build_poc_queue.py`.
7. (Later, separate) REPORT_READY gate + human-review #4.

### Risks → mitigations
- *Scope creep / duplicating production gates* → reuse contracts, keep research-only, never wire into
  `confirm_gate`/`pre_submission_gate`/`submission/`.
- *False POC_READY* → all-required-true (no weighted-average promotion) + mandatory negative gate + human #3.
- *Source staleness* → `source_resolution` records md5/line-range; gate re-resolves and KILLs on mismatch.
- *Conflation with submission/severity* → explicit non-authorization fields in the lock; `make_poc_task` refuses
  without lock and never generates report/submission.
- *Path leakage* → artifacts confined to `documentation/research/candidates/`; reuse `audit_context` only for ROOT.

### Acceptance criteria (this blueprint)
Prevents detector candidates from becoming PoC/report tasks without proof (hard lock + all-true scorecard);
defines a clear candidate→POC_READY path; supports strict kill gates (fast, human-free kills); preserves
traceability (common artifact header w/ source_hash + evidence_refs); separates detector vs validation vs exploit
vs impact confidence; compatible with the current workspace (reuses real scripts/paths, writes only new research
artifacts); uses concrete file paths + script names; Size multicall worked through both POC_READY and KILLED.

---

### Verification note for this document
All Size-credit code facts cited above were directly read from the working tree during authoring (Multicall.sol,
SizeStorage.sol, Deposit.sol, Size.sol, md5sum, and the detector audit JSON). Items not so verified are tagged
`_illustrative` / "placeholder". This file is the sole artifact produced; no scripts, config, schemas, detector
outputs, PoC files, reports, manifests, or production gates were created or modified.
