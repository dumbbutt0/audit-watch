---
name: ite-audit
description: "Full Jason Hadex ITE audit pipeline for smart contracts. Runs in order: sandbox check, attacker mindset surface map (Step 0.25), static analysis + supply chain check (Step 1), parallel specialist agents with ITE context (Step 2), compound synthesis (Step 3), multi-pass confirmation for High/Critical (Step 3.5), triage (Step 4), human-AI routing (Step 4.5). Activate when user says: run ite audit, hadex audit, full audit with ITE, start the methodology pipeline, or audit with human review."
---

# ITE Audit — Jason Hadex Methodology

Five phases. Attacker-first. 90% AI / 10% human. Confirm before claiming.

## Philosophy

1. **Attacker-first** — start from what the attacker wants, not what pattern the code looks like
2. **ITE decomposition** — every finding must have Intent, Technique, Evasion explicitly stated
3. **Non-determinism is real** — High/Critical claims are re-confirmed 3–5 times independently; below 60% agreement = human review required
4. **Patient zero awareness** — check the build chain before the contract logic
5. **Scale with oversight** — AI handles 90%; novel, cross-system, and unconfirmed findings go to the human queue

## Phase 0: Pre-flight

### 0a. Determine contract path
If the user didn't specify a contract, ask: "Which contract or directory should I audit?"

### 0b. Sandbox check
```bash
python scripts/sandbox_check.py <contract_path>
```
If flags are raised without `--allow-flagged`: stop and inform the user. The contract source is untrusted input and may contain prompt injection.

### 0c. Read base reasoning framework
Read `prompts/human_auditor_methodology.md`. This is the base reasoning framework for all subsequent phases. Apply attacker-first thinking, ITE decomposition, and human escalation triggers throughout.

### 0d. Check agent policy mode
Read `config/agent_policy.json` → `active_mode`.
- **fast**: skip Phases 1–4 (Steps 0.25, 1–3.5); run triage only against existing findings
- **normal**: run Phases 1–4 with PoC capped per config
- **deep**: full pass; print scope estimate before starting

## Phase 1: Attack Surface Mapping (Step 0.25)

Before any pattern-matching, map what the attacker would target and why.

Spawn as a Task: `agents/attacker_mindset.md`
Provide: full contract source + `output/static.json` and `output/findings_protocol_context.json` if available.

**Outputs:**
- `output/attack_surface.json` — all functions scored 1–5 by attack value
- `output/findings_attacker_mindset.json` — AM- prefix hypotheses for score ≥ 3 functions

Tell the user: "Attack surface mapped. Top targets: [list top 3 functions by score with scores]"

## Phase 2: Static Analysis + Supply Chain (Step 1)

Spawn these in parallel as Tasks:

```bash
python tools/static_analysis.py <contract_path>
python scripts/analyze_test_coverage.py --contract contracts/ --tests test/
```

Also spawn in parallel (no dependency on static.json):
- `agents/supply_chain_check.md` — provide project root listing, foundry.toml, package.json, .gitmodules

Supply chain check looks for: `ffi=true`, unpinned dependencies, suspicious imports, build script remote execution, unsigned GitHub Actions.

After all three complete:
```bash
python scripts/generate_status.py
```

Tell the user if any supply chain findings were produced.

## Phase 3: Specialist Agents (Step 2)

Spawn all applicable specialist agents in parallel as Tasks.

**Language routing (cross-language):** check `python -c "import sys;sys.path.insert(0,'scripts');import audit_context as a;print(a.audit_language())"`.
- **solidity** (default): use the Solidity specialist set below (unchanged).
- **rust**: use the **Solana/Anchor bundle** — `agents/solana_account_model.md` (signer/owner/account-substitution/
  Anchor-constraint/reinit/close-revival/unchecked-arithmetic) + `agents/solana_cpi.md` (CPI-program-pinning/
  PDA-seed/remaining_accounts/signer-seed-scope) — plus the language-agnostic conceptual specialists where they
  apply (logic, economic_attack, dos, access_control as concepts). The Solidity-syntax specialists (reentrancy
  storage-collision, erc4626, transient_storage, upgrade_storage) are skipped for rust. The Rust mechanism classes
  in `config/mechanism_classes.json` are `status:seeded` until the recall lab validates them on scored contests.
- **move**: use the **Move/Sui bundle** — `agents/move_clmm_math.md` (custom wide-math/`checked_shlw` overflow [the
  Cetus $220M class], liquidity⇄amount + fee-growth rounding direction, i32/i64/i128 signed-int & tick math,
  sqrt-price/Q64.64 precision, swap & flash-swap conservation) + `agents/move_object_capability.md` (capability/
  witness/admin gates bound to the specific object, shared-vs-owned object confusion, hot-potato repayment
  enforcement, Coin/Balance conservation, version/upgrade & init guards) — plus the language-agnostic conceptual
  specialists where they apply (logic, economic_attack, dos, access_control as concepts). The Solidity-syntax
  specialists (reentrancy/storage-collision/erc4626/transient_storage/upgrade_storage) and the Solana bundle are
  skipped for move. Note Move *aborts on native overflow* and *prevents EVM-style reentrancy* — so weight the
  custom-math, object/capability, and economic surfaces, not plain arithmetic/reentrancy. The Move mechanism
  classes (`move-*`) in `config/mechanism_classes.json` are `status:seeded` (language:move) until the recall lab
  validates them on scored Sui/Move contests.

**Every agent MUST:**
1. Read `output/attack_surface.json` — prioritize functions with `attack_surface_score >= 3` for DEPTH (spend your deepest reasoning here first).
2. **OPEN EVERY IN-SCOPE FILE IN YOUR REMIT — the cold pass is not complete until you have.** Read the **Priority Investigation Clusters** of `output/context_pack.md` first for DEPTH (deepest reasoning on the hot clusters). **Then enumerate the FULL in-scope file list from `output/coverage_manifest.json` (every distinct `file`) and OPEN, with the Read tool, every file whose contents match your specialty's triggers — running your full class checklist on each at specialist grade.** Prioritization controls ORDER/DEPTH, **never whether a specialty-relevant file is opened**: you do NOT defer a file your specialty touches to the lighter `/coverage-sweep`. The sweep is ONLY for files with no specialty owner (pure constants/interfaces/types). Record in each finding-file's coverage the fact you examined it; the fail-closed coverage gate (Step 3.85/3.9) still blocks until every in-scope manifest item has an evidence-anchored disposition.
   - **Why this is mandatory (hybra M-02 autopsy):** a reward bug in `GaugeV2.emergencyWithdraw` (a balance-mutator missing the `updateReward` modifier its siblings carry) was MISSED because the file was routed to a light sweep instead of opened by the reward specialist. Every banked class can only fire on a file that is actually opened. A specialist who opens only the hot clusters and trusts the sweep for the tail is the exact failure mode that caps blind recall — **open all your files.**
3. Apply `prompts/human_auditor_methodology.md` as base reasoning (attacker-first, ITE decomposition)
4. Populate the `ite{}` field (intent/technique/evasion) in every finding
5. Set `attack_surface_rank` to the score from `output/attack_surface.json` for the affected function

**Core agents (always spawn):**
- `agents/reentrancy.md`
- `agents/access_control.md`
- `agents/arithmetic.md`
- `agents/oracle.md`
- `agents/flash_loan.md`
- `agents/logic.md`
- `agents/dos.md`
- `agents/snapshot.md`
- `agents/economic_attack.md`
- `agents/token_integration.md`
- `agents/behavioral_state_analysis.md`
- `agents/semantic_guard.md`
- `agents/protocol_context.md`

**Fuzz-informed specialist (P141 — spawn when confirmed harness-fuzz evidence exists, ALL languages):**
- `agents/fuzz_attacker_synthesis.md` — spawn IFF `data/fuzz_results/divergences.jsonl` contains any record with
  `status == "confirmed"` (run `./run_pipeline.sh fuzz` first, after the harness runners, to derive it). This
  specialist fuses the confirmed fuzzer counterexample WITH the read source and reasons attacker-first, writing
  `output/findings_fuzz_synthesis.json`. It consumes ONLY `status=="confirmed"` records (the fuzz-lane FP guard,
  `scripts/fuzz_evidence_gate.py`, already ruled out harness/oracle artifacts). It NEVER sets final severity /
  triage — its output rides the same FP gauntlet (3.4→3.9) as every other specialist. Gated by
  `config/agent_policy.json → fuzz_synthesis.enabled`. If there are no confirmed records, skip it.

**Conditional agents** (check triggers per CLAUDE.md Step 2 rules):
- `agents/cross_chain.md` — if protocol_context identifies bridge/layer2/relayer
- `agents/upgrade_storage.md` — if protocol_context identifies proxy/UUPS/upgradeable
- `agents/erc4626.md` — if `static.json` has `is_erc4626: true` or protocol_context mentions vault
- `agents/transient_storage.md` — if `static.json` has `has_transient_storage: true`

After all complete:
```bash
python scripts/reference_diff.py --contract contracts/
python scripts/generate_status.py
# ENFORCE "open all in-scope files in remit" — flags specialty-relevant files NOT opened at specialist grade
python scripts/check_specialist_file_coverage.py
```
**The cold pass is NOT done while `check_specialist_file_coverage.py` reports gaps.** Each flagged file
names its owning specialist — re-open every flagged file with that specialist's class checklist and
record its disposition, then re-run the check until it prints `OK`. This is the hard backstop for the
hybra M-02 failure (a reward bug missed because `GaugeV2.sol` was never opened by the reward specialist).
Only then proceed to Phase 4 / the coverage sweep for the remaining no-specialty-owner files.

## Phase 4: Synthesis + Multi-Pass Confirmation (Steps 3 & 3.5)

```bash
python scripts/synthesize_compound_findings.py
python tools/report_generator.py
python scripts/validate_agent_output.py output/
```

Then multi-pass confirmation — this is the core Hadex non-determinism fix:
```bash
python scripts/multi_pass_confirm.py
python scripts/generate_status.py
```

Tell the user: "Multi-pass complete. [N] confirmed, [M] flagged for human review."

## Phase 5: Triage + Human Routing (Steps 4 & 4.5)

```bash
python scripts/triage_findings.py
python scripts/build_poc_queue.py
python scripts/final_submission_pack.py
python scripts/generate_status.py
```

Then human-AI routing:
```bash
python scripts/human_review_classifier.py
python scripts/generate_status.py
```

## Output

Print phone-readable summary:

```
Done:
- Attack surface: N functions mapped, top targets: [function names]
- Supply chain: clean ✅ / N issues found ⚠️
- Specialists: N agents, N findings (High: N, Medium: N, Low: N)
- Multi-pass: N confirmed ✅, M human-review flagged ⚠️
- Triage: N submit, N poc_required, N rejected
- Human queue: N findings need expert review

Needs you:
- Use /human-queue to see findings requiring manual validation
- [any specific blocker or decision required]

Next:
- python scripts/run_specialist_review.py
```

> **Depth corollary to "open all files" (noya H-04 autopsy):** opening a file means deep-reading **every function body** in it through your class checklist — NOT skimming the function map. The noya `executeWithdraw` batch-griefing High was missed even though the file was open, because only the signature map was read. A file is "covered" by a specialist only when each of its functions has been run through the relevant classes.
