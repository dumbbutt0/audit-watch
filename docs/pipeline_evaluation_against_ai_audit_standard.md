# Audit-Watch — Evaluation Against the AI-Audit Standard

_Reviewer stance: judge whether this behaves like a serious AI-assisted security researcher that
produces valid, triage-ready, externally exploitable findings with **low false positives** — not a
scanner. Evidence-cited, no hype, deliberately harsh. Date: 2026-05-29 (refresh)._

> **What changed since the prior (38/50) pass.** That review's single biggest weakness and #1
> recommended fix were the same thing: *"the feedback loop is open; the system can't measure its own
> FP/recall."* Since then the loop has been **built** — `scripts/record_outcome.py`,
> `derive_learning.py`, `promote_learning.py`, `compute_metrics.py` all exist, and
> `documentation/metrics/metrics.json` is populated and surfaced live each session
> (`FP=0.5 n=4 · recall=1.0 n=2 · PoC=0.824 n=74`). That is a real upgrade and it is credited below.
> **But the plumbing was built and there is no water in it.** The loop is fed **6 outcome records
> across 12 audits**; `metrics.json` itself admits *"Low ground_truth_records ⇒ metrics are
> directional, not yet robust."* A 50% false-positive rate computed on **n=4** is statistical noise,
> not a measurement. So the score barely moves: the bottleneck **shifted** from "no loop" to "loop
> starved of data" — it did not close. A closer pass also docks the context graph the prior review
> over-credited. **Net: ~37/50.**

> Evidence scope: `scripts/`, `tools/`, `agents/`, `prompts/`, `schema/`, `templates/`, `kb/`,
> `documentation/`, `config/`, and live artifacts under `audits/<id>/` (13 workspaces). Two internal
> studies are folded in: the Beanstalk benchmark (`documentation/evals/beanstalk-finale/`) and the
> 2026-05-29 refinement (`documentation/refinement/`). All counts below were re-verified against the
> tree on the review date.

---

## Category 1 — Codebase Context Graph — **3 / 5**

**What exists.** A genuine pre-specialist context build, not file summaries:
- `scripts/extract_invariants.py` → `data/invariants/{ACCOUNTING,SOLVENCY,STATE_MACHINE,ARITHMETIC}.jsonl`
  (protocol invariants + the functions that mutate them).
- `scripts/map_interactions.py` → function-interaction graph + dangerous call chains;
  `scripts/backward_trace.py` (sink→source); `scripts/multi_tx_trace.py` (multi-tx state machine);
  `scripts/deep_trace.py` pairs high-suspicion invariants with dangerous interactions into
  `data/threads/promising_threads.jsonl`.
- `tools/static_analysis.py` → `output/static.json`: functions, state vars, external calls,
  modifiers, plus `is_proxy` / `is_erc4626` / `has_transient_storage` flags that gate conditional
  specialists.
- `agents/attacker_mindset.md` → `output/attack_surface.json` (every function scored 1–5 with
  per-specialist `agent_hints`); `agents/protocol_context.md` classifies protocol type / standards /
  inheritance. `scripts/generate_contract_context.py` → `notes/contract_context.md` (deterministic,
  no-API: attacker-reachable vs privileged entrypoints, oracle reads, delegatecalls, initializers).

**What's missing — and why this is a 3, not a 4.**
- **No materialized graph object.** There is no single queryable `relational_graph.json`
  (contracts↔functions↔state↔roles↔external-calls). The "graph" is scattered across JSONL files,
  some of which downstream stages don't reliably read.
- **Cross-contract chaining is a regex heuristic.** `scripts/run_impact_chain_escalation.py` finds
  "consumers" of corrupted state with **ripgrep patterns** and its own docstring concedes it
  *"misses indirect reads, interface calls, inheritance, delegatecall, and generated accessors."*
  That is the exact surface where real exploit chains live. A finding's `severity_ceiling` can hinge
  on a `search_method: static_search` that is structurally blind to inheritance.
- **Context produced but inconsistently consumed.** The refinement docs themselves note specialists
  don't reliably re-read `data/invariants/`. Producing a graph nobody is forced to use is not the
  same as reasoning over one.
- Role/permission and asset-flow maps are *implicit* in `attack_surface.json` + specialist outputs,
  not first-class. Proxy/upgrade mapping is flags + an agent, not a rendered storage-slot diagram.

**Improve.** Emit one consolidated `relational_graph.json`; replace (or back-stop) the ripgrep
consumer search with Slither/AST-level reachability including inheritance and delegatecall; add a
coverage gate that fails Stage 2 if a specialist ignored a high-suspicion invariant in its category.

---

## Category 2 — Exploitability Validation — **4 / 5**

**What exists.** Exploitability is a first-class gate, and this is the pipeline's strongest claim to
"not a scanner."
- **ICE** (Impact / Confidence / Exploitability) re-derived from raw source at each stage; a finding
  advances only if I≥Medium AND C≥High AND the path is traced end-to-end
  (`CLAUDE.md`, `documentation/refinement/zero_trust_triage_policy.md`).
- **Impact-chain escalation** (`prompts/impact_chain_escalation.md`): `ice_chain` requires
  `corrupted_state`, `consumer_found`, `consumer_function`, `exploit_path`, `severity_ceiling`.
  No consumer ⇒ routed to PoC-required, not auto-accepted.
- **8 hard-reject gates** (`scripts/pre_submission_gate.py`): reachability, state realism, privilege,
  defense, economics, PoC, severity, duplicate — emitting permanent `invalidation_tags`
  (`admin_only`, `impossible_state`, `no_profitability`, `requires_compromised_key`,
  `non_exploitable`, …). The admin/impossible-state keyword lists are concrete and enforced.
- **ITE decomposition** (Intent/Technique/Evasion) per finding, including the evasion/defense gap.
- **No-silent-clear rule**: clearing safety-net code (solvency modifiers, oracle aggregators, bridge
  checks, init/migration) requires a written attacker-path `disproof`, enforced by
  `scripts/validate_agent_output.py`; failures route to human review rather than silently passing.

The rejection examples that fire here are real and correct: `data/triage/rejected.jsonl` AC-001 is
turned down because the path *"requires a compromised validatorRegistrator key … a trusted hot key,
not an unprivileged attacker"* and *"the `_recipient == vaultAddress` guard … means funds go to the
vault, not the attacker."* That is the right instinct.

**What's missing.** The "who is the attacker / what capital / what precondition-state / what blocking
guard" packet is enforced by **prose discipline** in `prompts/human_auditor_methodology.md`, not as
validated structured fields a finding cannot reach `submit` without. Mainnet-state preconditions are
reasoned, not always fork-verified before triage. And the consumer search feeding ICE is the same
heuristic flagged in Category 1 — so an "end-to-end traced path" can rest on a blind regex.

**Improve.** Promote the exploitability packet to required, schema-validated fields (like ICE);
require a fork check for any finding whose severity depends on a specific mainnet precondition.

---

## Category 3 — False-Positive Control — **4 / 5**

**What exists.** A real "rejection brain" that does not reward volume — the system's best-developed
muscle.
- `data/fp_autopsies/rejection_rules.jsonl` = **178 structured rules** (verified), each with
  `pattern_type`, `trigger_conditions`, `rejection_reason`, `invalidation_tag`,
  `confidence_threshold`, `trust_level`, `judge_outcome`. Classes include `requires_compromised_key`,
  `admin_attacker`, `bounded_impact`, `impossible_state`, `unrealistic_liquidity`, `out_of_scope`.
- `scripts/fp_pattern_check.py` matches new findings against these rules by similarity (reject ≥0.85,
  warn ≥0.6).
- `scripts/judge_simulate.py` runs adversarial **skeptic personas** → `{verdict, simulated_severity,
  objections}` per finding (triage-downgrade simulation).
- `scripts/pre_submission_gate.py` (8 gates) + `pre_submission_dupe_screen.py` +
  `data/duplicate_registry.jsonl` (**2 confirmed cross-audit real duplicates**: CC-001→Immunefi
  #3329553, GAC-001→#76929).
- Of ~505 merged findings, only **7** reached `submit` and **39** are in `rejected.jsonl` with
  per-finding reasoning. The funnel is genuinely tight.

**What's missing — read this honestly.**
- The system now *measures* its FP rate and it reads **0.5 (n=4)** with `access_control` reliability
  **0.5 (n=4)** (`metrics.json`). On its face that says half of recorded findings were false
  positives. It is almost certainly noise at n=4 — but that is precisely the problem: **the FP brain
  is unfalsifiable right now.** You cannot claim "low false positives" as a property; you can only
  claim the machinery to suppress them exists.
- The *opposite* failure — false **negatives** — is the documented real one: Beanstalk cleared
  **5 real bugs**. The no-silent-clear gate targets this but is new and unproven live.

**Improve.** Feed the loop (Category 8) until the FP rate is computed on n in the dozens-plus;
auto-promote recurring FP shapes into rules; report FP/recall **per agent and per bug class** so
"low FP" becomes a measured claim instead of an aspiration.

---

## Category 4 — PoC Generation & Proof Quality — **4 / 5**

**What exists.** Reaches **Level 3–4 routinely** and is honest about partials.
- L1/L2/L3 standard (`CLAUDE.md`): L1 entry from EOA, L2 named storage/balance assertions
  (`vm.load`), L3 economic/security outcome proven in output.
- `templates/proof_requirements/*.json` (**10** bug-class templates: oracle slot0, read-only
  reentrancy, zero-slippage sandwich, allowance theft, liquidation DoS, …) with `proof_signatures`
  and L3A/B/C descriptors and explicit Medium-vs-High severity rationale.
- Generator chain: `generate_poc_plan.py` → `generate_poc_test.py` (compile-repair loop) →
  `run_poc_tests.py` / `run_integrated_poc.py`; `analyze_poc_completeness.py` caps severity if L3 is
  unproven.
- **Real deployed-behavior fork PoCs** in `audits/*/pocs/foundry/test/*.t.sol`
  (`FL006_ZeroSlippage.t.sol`, `RFI004_FeeOnTransfer_fork.t.sol` forks Optimism mainnet,
  `AC004_AlreadyInitialized.t.sol`, `CHAIN001_IntegratedPoC.t.sol`). RFI-004 includes a **USDC
  negative control** proving the fee token is the root cause — a genuinely strong signal.
- `data/runtime_poc/results.jsonl` (14 records) logs `status` + `runtime_level` +
  `real_function_called` + `public_entrypoint_called` + `assertion` + `stdout_excerpt`. Aggregate
  PoC success = **61/74 = 82.4%**, with partials honestly labelled (origin: 9 at L0/inconclusive).

**Classification: Level 4 reached** (fork PoCs of real deployed behavior); **Level 5** (full
loss/insolvency) for a subset (e.g. CHAIN-001).

**What's missing.** PoC generation is API-dependent (the reasoning core). Non-EVM (Solana/Anchor,
Vyper) harnesses are thin. There is **no automated deployed-address verification or fork-block
pinning** required on an "L4" claim, so "fork PoC of the in-scope deployment" is asserted by the
test author, not enforced. RFI-004's headline assertion is a *mock* integration ("proved at Level 2 —
mock pool, not mainnet fork") even though the file forks mainnet elsewhere — exactly the ambiguity a
required address/block field would remove.

**Improve.** Make `deployed_address` + `fork_block` required, validated fields on any L4 claim;
expand non-EVM PoC harnesses.

---

## Category 5 — Report Quality & Triage Resistance — **4 / 5**

**What exists.** Sample reports are submission-grade.
`audits/origin-protocol-2026-05/reports/AR-001-submission.md` (oracle unit mismatch in a liquidation
close-factor) has: precise title, brief, root cause to the **exact line** (`calculation.rs:68`),
dimensional analysis (missing `oracle_to_wad × 10^decimals`; 14-dec oracle + 6-dec USDC ⇒ ~100× off
⇒ excess seizure), affected functions, scope-tied impact, and **companion `*_rebuttal.md` /
`*_triage_notes.md` that pre-empt project pushback.** Format is enforced by
`prompts/submission_writer.md` (an 8-question pre-write gate that blocks the report if the
state-consumer questions Q2/Q3 are unanswered) and packaged by `scripts/final_submission_pack.py`.
The flare AC-004 finding shows the full ITE + `ice_chain` + cross-agent-ref structure end to end.

Against the triage tests: a triager **can** reproduce (fork PoC + exact line); the protocol **cannot**
trivially dismiss (defenses-considered + why-not-invalid addressed); severity is calibrated, not
asserted; impact is scope-tied.

**What's missing.** The "defenses considered / why-not-invalid / why-not-merely-best-practice" triad
is present **unevenly** across older reports — it's prose convention, not a validated required
section. No automated reproduction-instruction linter. (Per user preference, a "Quality Checklist"
section is correctly excluded from final reports.)

**Improve.** Make the defenses-considered + why-not-invalid + scope-mapping triad a required,
validated section for every High/Critical report.

---

## Category 6 — Memory & Learning — **3 / 5**

**What exists — including the new machinery.**
- Long-term: 691MB Chroma KB (`kb/chroma/`), `kb/attack_primitives.json`, `kb/patterns/*.json`,
  `kb/reference_implementations/`; retrieval via the `kb-search` MCP (`search_findings`,
  `search_immunefi`, `get_primitives`).
- Rejection memory: the 178-rule `rejection_rules.jsonl` + `record_fp_autopsy.py`.
- Cross-audit duplicate memory: `data/duplicate_registry.jsonl`.
- Severity learning: `data/learning/severity_rules.yaml`, `data/severity/calibrated.jsonl`.
- **NEW closed-loop machinery**: `scripts/record_outcome.py` (provenance-gated outcome capture) →
  `scripts/derive_learning.py` (deterministic, no-API; stages candidate rules to
  `data/learning/_proposed/`) → `scripts/promote_learning.py` (human gate into shared rules). This is
  exactly the architecture the prior review asked for, and it is real.

**What's missing — why this stays a 3 despite the upgrade.** *The loop has never actually fired.*
- `ground_truth.jsonl` totals **6 records across 12 audits** (verified: 1 flare + 1 tools-for-humanity
  + 2 xterio + 2 gearbox). `ground_truth.jsonl` is human-write-only and almost empty.
- The session calibration banner reports `unpromoted_learning=0` — i.e., `derive_learning.py` has
  proposed nothing that's been promoted. No rule in the corpus demonstrably came from *this
  pipeline's own* accepted/rejected outcomes (vs. imported corpora).
- The standard's criterion is "improve over time." The pipeline now *can* learn; there is **no
  evidence it has.** Capability ≠ demonstrated improvement. The Beanstalk economic-invariant miss
  still has no learned guard.

**Improve.** Force outcome capture (wire `final_submission_pack.py` to require a verdict →
`record_outcome.py`); backfill the known outcomes already in project memory (CC-001/GAC-001
duplicates, GL-001 fork-confirmed FP); then run `promote_learning.py` and show a rule that was
*born* from this loop. Until then this is infrastructure, not learning.

---

## Category 7 — Agent Design & Workflow — **4 / 5**

**What exists.** 34 agents (verified) with distinct, non-redundant roles and a real
skeptic/builder/checker split:
- Specialists (reentrancy, access_control, arithmetic, oracle, flash_loan, logic, dos, snapshot,
  economic_attack, token_integration, behavioral_state_analysis, semantic_guard) + conditional
  (cross_chain / upgrade_storage / erc4626 / transient_storage) each emit schema-conformant
  `findings_<agent>.json`. Roles are genuinely distinct (access_control ≠ semantic_guard ≠
  behavioral_state).
- **Skeptic** is explicit: `judge_simulate.py` (adversarial personas with objections) +
  `pre_submission_gate.py` (8 gates) + `multi_pass_confirm.py` (3–5 independent re-confirmations with
  KB tool-use). **Scope/severity checkers**: `calibrate_severity.py`, `estimate_duplicate_risk.py`,
  `model_exploitability.py`.
- Clean merge: `tools/report_generator.py` (five-axis dedup that **links** rather than collapses) →
  `merged_findings.json`. Orchestration via `/ite-audit` (parallel specialists) + `run_pipeline.sh`,
  output validated by `validate_agent_output.py`.

**What's missing.**
- **Agents agree more than they adversarially validate.** Beyond merge + judge-sim there is **no
  disagreement arbiter**: when two stages reach different conclusions there's no explicit "escalate
  the conflict to the human queue" step. There is **no dedicated exploit-builder agent** — PoCs come
  from templates + the generator chain, so attack construction is the least agentic part.
- **API fragility / cost.** ~21 of 24 reasoning steps are still separate Anthropic API calls (only
  `/triage` is skill-in-session). Production artifacts show `confirmation_api_error →
  human_review_required` with **no retry/fallback** — a missing key historically stalled a run
  mid-pipeline. `multi_pass_confirm` consistency *is* the confirmation signal, so model nondeterminism
  is load-bearing.

**Improve.** Finish skill-in-session conversions (recipe in
`documentation/refinement/api_dependency_audit.md`); add a disagreement-arbiter; add retry/fallback
on confirmation calls.

---

## Category 8 — Data, Metrics & Feedback Loops — **3 / 5**

**What changed — the kind, not the score.** The prior review said these metrics "can be computed but
aren't fed." Now they **are** computed and surfaced: `scripts/compute_metrics.py` →
`documentation/metrics/metrics.json` (regenerated today) reports `false_positive_rate`,
`recall_on_valid`, `valid_finding_rate`, `duplicate_rate`, `severity_downgrade_rate`,
`poc_success_rate`, and `per_agent_reliability`; a SessionStart hook prints live calibration. There
is also a real worked accuracy study (`documentation/evals/beanstalk-finale/`, HIT/PARTIAL/MISS) and
`scripts/evaluate_pipeline_accuracy.py`.

**Why it's still a 3 — the bottleneck moved, it didn't close.** Every rate except PoC is computed on
a corpus of **6 ground-truth records**:
- `false_positive_rate = 0.5 (n=4)` · `recall_on_valid = 1.0 (n=2)` · `valid_finding_rate = 0.333
  (n=6)` · `duplicate_rate = 0.333 (n=6)` · `per_agent access_control = 0.5 (n=4)`.
- `metrics.json` is honest about it: *"Low ground_truth_records ⇒ metrics are directional, not yet
  robust."* These are not measurements; a single new outcome swings the FP rate by 10–25 points.
- Only `poc_success_rate = 0.824 (n=74)` rests on enough data to mean anything — and that measures
  PoC *construction*, not finding *validity*.

So: the dashboard exists, the wiring exists, but the numbers that matter (FP rate, acceptance rate,
downgrade rate, per-agent reliability, time-per-valid-finding) are **effectively unknown** because
they're starved. A pipeline that can't yet trust its own FP/recall still can't tune itself.

**Improve.** Treat outcome capture as a first-class, *enforced* pipeline step; backfill historical
verdicts; set a "metrics are trustworthy at n≥30 per rate" threshold and surface n alongside every
number (it already stores n — now gate decisions on it).

---

## Category 9 — Manual Research Integration — **4 / 5**

**What exists.** A strong human-augmentation surface:
- Navigation/attack-surface: `output/context_pack.md`, `output/attack_surface.json`,
  `output/step0_brief.md`, `notes/contract_context.md`, `notes/points_of_interest.jsonl`
  (attacker-reachable entrypoints to start from).
- Hypothesis queues: `data/threads/promising_threads.jsonl`, `output/coverage_gaps.json`.
- Human-in-the-loop: the pipeline **pauses** at `output/review_gate.md`; `human_review_queue.jsonl` +
  `/human-queue`; targeted skills `/surface`, `/confirm`, `/kb-patterns`, `/immunefi`; phone commands
  (`/top`, `/risks`, `/novel`, `/continue`) for one-screen control. Defense map
  (`output/defense_map.json`), PoC TODOs (`build_poc_queue.py`).

**What's missing.** No persistent, human-owned research journal (`notes/` is *generated*, not a
running human log that's never overwritten). Output can still be voluminous; there is no single
"researcher cockpit" that always answers "what do I look at next?"

**Improve.** Add a human-owned `notes/journal.md` (never overwritten) + `status/next_actions.md`.

---

## Category 10 — Bug-Bounty Practicality — **4 / 5**

**What exists.** Built for real bounty outcomes:
- Multi-audit isolation (`audits/<id>/`, `scripts/audit_manager.py`, `audit_context.py`), scope
  inventory (`generate_scope_inventory.py`), intake/association (`intake_contracts.py`, in-scope vs
  `_sources/`).
- Severity mapping to **Immunefi v2.2** (per project memory: MEV/insolvency = Critical, temp-freeze =
  High); duplicate-risk awareness with **confirmed real-world duplicates recorded**
  (`duplicate_registry.jsonl`).
- Submission packaging (`final_submission_pack.py`), evidence preservation (PoC files + stdout in
  `runtime_poc/results.jsonl`).
- Responsible testing: `sandbox_check.py` hard gate before any agent reads untrusted source;
  fork-only PoCs (no mainnet exploitation); privileged-compromise reliance is a rejection class;
  `config/zero_trust_policy.json` forbids dangerous ops in agent output.
- Track record: live submissions (origin 4 submit/7 PoC; tools-for-humanity 6; xterio 6; gearbox 4)
  and a **fork-confirmed false-positive rejection** (Gearbox GL-001) — evidence the gates catch their
  own side's mistakes.

**What's missing.** Program-payout-history and automated **scope-diff parsing** aren't first-class;
out-of-scope detection is manual/heuristic. No automated check that a finding's contract is on the
program's published in-scope list.

**Improve.** Add a scope-parser that ingests a program's in-scope asset list and auto-tags every
finding in/out of scope.

---

## Overall Score

| # | Category | Prior | **Now** |
|---|---|---|---|
| 1 | Codebase Context Graph | 4 | **3** |
| 2 | Exploitability Validation | 4 | **4** |
| 3 | False-Positive Control | 4 | **4** |
| 4 | PoC Generation & Proof Quality | 4 | **4** |
| 5 | Report Quality & Triage Resistance | 4 | **4** |
| 6 | Memory & Learning | 3 | **3** |
| 7 | Agent Design & Workflow | 4 | **4** |
| 8 | Data, Metrics & Feedback | 3 | **3** |
| 9 | Manual Research Integration | 4 | **4** |
| 10 | Bug-Bounty Practicality | 4 | **4** |
| | **Total** | 38 | **37 / 50** |

The score dropped one point despite a real feedback-loop build because (a) building the loop ≠
feeding it — the metrics it now produces are noise at n=4/n=6, so the underlying weakness persists in
a new form; and (b) a harder look at the context graph (regex consumer search, no materialized
graph, inconsistent consumption) corrects a prior over-grade. This is the honest read, not a
regression in the software.

## Biggest Strengths (top 5)

1. **Exploitability discipline.** ICE + impact-chain consumer tracing + 8 hard gates + no-silent-clear
   mean findings must reach a real consumer/impact, not "weird behavior." Static analysis is demoted
   to *context*, never a finding.
2. **A real rejection brain.** 178 structured FP rules + adversarial judge-simulation + cross-audit
   dupe registry; ~505 findings → 7 submit. Built to suppress invalids, not maximize count.
3. **Genuine fork PoCs with a negative control.** 82.4% PoC success on n=74, honest partials, and a
   USDC negative control. The clearest "not a scanner" signal in the repo.
4. **Submission-grade reports.** AR-001 (exact line, dimensional root cause, scope-tied impact,
   rebuttal notes) would survive triage.
5. **Operational + safety maturity.** Multi-audit isolation, sandbox gate, fork-only testing, human
   pause gate, Immunefi v2.2 mapping, and a fork-confirmed FP *rejection* of its own finding.

## Biggest Weaknesses (top 5)

1. **The loop is built but starved.** 6 ground-truth records ⇒ FP rate (0.5, n=4), recall (n=2), and
   per-agent reliability are statistically meaningless. The system still cannot *prove* its own
   accuracy — it can only display placeholders. `unpromoted_learning=0`: nothing has actually been
   learned from its own outcomes yet.
2. **Recall on economic/peg/solvency invariants.** Beanstalk: 56% meaningful recall, 5 real bugs
   *falsely cleared*. The no-silent-clear gate targets this but is new and unproven live.
3. **The context graph is heuristic where it matters most.** Cross-contract exploit-chain detection
   leans on a ripgrep search that admits it misses inheritance/delegatecall/indirect reads — and ICE
   severity can depend on it.
4. **API fragility / cost.** ~21 of 24 reasoning steps are separate API calls; confirmation has no
   retry/fallback (a missing key has stalled runs); multi-pass relies on model nondeterminism as
   signal.
5. **Context produced, inconsistently consumed; agents agree more than they adjudicate.** No coverage
   gate forcing specialists to use invariants; no disagreement arbiter; no dedicated exploit-builder.

## Highest-ROI Fixes (ranked)

1. **Feed the loop, don't just plumb it.** Enforce `record_outcome.py` at submission and **backfill
   the ~13 audits' known verdicts** (CC-001/GAC-001 dupes, GL-001 FP, all submitted/accepted). The
   loop already exists; data is the missing input. (Unlocks 6 + 8.)
2. **Gate metrics on sample size.** Surface `n` beside every rate and mark any rate with n<30 as
   "directional"; don't let tuning decisions read FP=0.5(n=4) as real.
3. **Economic-invariant / peg specialist agent** (reward/solvency/deltaB/gauge lifecycles) + a KB
   module — the worst-covered class in the benchmark.
4. **Coverage-enforcement gate**: fail Stage 2 if a specialist ignored a high-suspicion invariant in
   its category (kills silent false-negatives).
5. **Replace/back-stop the ripgrep consumer search** with Slither/AST reachability that follows
   inheritance + delegatecall; require it before any High/Critical `severity_ceiling`.
6. **Finish skill-in-session conversions** (`multi_pass_confirm`, `synthesize_compound`,
   `cross_agent_connector`, the Stage-5 quartet) + add confirmation retry/fallback.
7. **Structured exploitability packet** (attacker / capital / precondition-state / blocking-guards) as
   validated fields required before `submit`.
8. **Deployed-address verification + fork-block pinning** as required fields on any L4 PoC claim.
9. **Auto-promote recurring FP shapes** into `rejection_rules.jsonl` once the loop has data.
10. **Scope-diff parser** that ingests program in-scope lists and auto-tags in/out of scope; +
    disagreement-arbiter routing conflicting agent verdicts to the human queue.

## Missing Components

- **Trustworthy outcome corpus** — `record_outcome.py` exists but `ground_truth.jsonl` is ~empty
  (6 records). This is the keystone gap; everything in 6 + 8 is starved by it.
- A consolidated, queryable `relational_graph.json` (single context object).
- An AST/Slither-level consumer-reachability pass (vs. the current ripgrep heuristic).
- An `economic_invariant` / peg specialist agent + KB module for reward/solvency lifecycles.
- A coverage-enforcement gate; a disagreement-arbiter; a dedicated exploit-builder agent.
- A persistent human research journal (`notes/journal.md`) + `status/next_actions.md`.
- Scope-parser for program asset lists; deployed-address verifier + fork-block pinning for fork PoCs.
- Confirmation-call retry/fallback (API fragility).

## Recommended Target Architecture

```
audit-watch/
  scripts/
    intake/    intake_contracts · generate_contract_context · scope_parser.py (NEW)
    context/   extract_invariants · map_interactions · backward_trace · multi_tx_trace
               build_relational_graph.py (NEW) · ast_consumer_reachability.py (NEW, replaces rg)
    detect/    specialist orchestration (skill-in-session bundlers) · coverage_gate.py (NEW)
    triage/    triage_prepare/triage_write (+skill) · pre_submission_gate · judge_simulate
               disagreement_arbiter.py (NEW)
    poc/       generate_poc_* · run_integrated_poc · verify_deployed_address.py (NEW)
    learn/     record_outcome · derive_learning · promote_learning · record_fp_autopsy   [EXISTS — feed it]
    metrics/   compute_metrics (gate on n) · evaluate_pipeline_accuracy · dashboard
    llm_runtime.py · audit_context.py
  agents/      (+ economic_invariant.md NEW) (+ exploit_builder.md NEW)  prompts/  schema/
  templates/proof_requirements/
  kb/          chroma/ · patterns/ · attack_primitives.json · reference_implementations/
  audits/<id>/ contracts/ notes/(+journal.md) findings/{raw,validated} status/(+next_actions.md)
               output/ data/(evaluation/ground_truth.jsonl — MUST be fed) pocs/ reports/ meta.json
  documentation/ (policies · refinement · evals · metrics)   docs/ (this file · pipeline_reference)
```

## Immediate Implementation Plan

**Day 1**
- Wire `final_submission_pack.py` to require a verdict and append it via `record_outcome.py` to
  `ground_truth.jsonl`. **Backfill known outcomes** (CC-001/GAC-001 duplicates, GL-001 FP, all 7
  submits + their accepted/duplicate/invalid status from project memory).
- Re-run `compute_metrics.py`; record the first FP/recall numbers built on n>6 and label them
  "directional until n≥30."

**Week 1**
- Add the coverage-enforcement gate (fail Stage 2 on ignored high-suspicion invariants).
- Replace/back-stop the ripgrep consumer search with AST/Slither reachability.
- Add `notes/journal.md` + `status/next_actions.md`; gate every displayed metric on its `n`.
- Convert `multi_pass_confirm` / `synthesize_compound` / `cross_agent_connector` to skill-in-session;
  add confirmation retry/fallback.

**Month 1**
- Ship the `economic_invariant`/peg specialist + reward/solvency-lifecycle KB module; **re-run the
  Beanstalk benchmark and confirm recall moves off 56%.**
- Add `build_relational_graph.py`, the structured exploitability packet, the disagreement-arbiter,
  the scope-parser, and deployed-address verification; finish remaining skill conversions.

## Brutal Verdict

- **Is this a serious audit pipeline?** **Yes.** Fork PoCs with `status: proved` and a negative
  control, a 178-rule rejection brain, adversarial judge-simulation, ICE + consumer-chain gating, and
  AR-001-grade reports put it well past "scanner." It behaves like a disciplined AI-assisted
  researcher with real operational hygiene.
- **Is it a scanner wrapper?** **No.** Static analysis is explicitly demoted to *context*; nothing
  reaches `submit` without ICE + a traced consumer/impact chain. The funnel (505 → 7) proves it
  optimizes for validity, not volume.
- **Can it produce valid medium/high findings?** **Yes — and it has** (live submissions across
  origin/xterio/gearbox/tools-for-humanity, fork-confirmed PoCs, and at least one fork-confirmed FP
  *rejection*). Honest caveats: high-value findings still need human confirmation, and recall on
  economic/peg invariants is a documented blind spot (56% on Beanstalk).
- **Single biggest bottleneck:** **ground-truth data starvation.** The prior bottleneck — "no
  feedback loop" — was genuinely fixed: the loop is built. But it's fed **6 outcomes across 12
  audits**, so FP rate, recall, and per-agent reliability are noise, and learning has promoted
  nothing. The pipeline can now *see itself* in principle but is looking at an almost-empty dataset.
  Until that corpus fills, every downstream claim about accuracy — and every learned rule — rests on
  n≈4.
- **What to build next, before adding any tool or detector:** **fill the loop, then prove it.**
  Enforce outcome capture, backfill the known verdicts, and demonstrate one learned rule and one
  trustworthy (n≥30) FP/recall number. A pipeline that can't yet *trust* its own FP/recall cannot be
  tuned — and more detectors only add unmeasured noise until that corpus exists. The machinery is
  done; the discipline of feeding it is the work that remains.
```
