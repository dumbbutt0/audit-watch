# Architecture

## System Components

```mermaid
graph TD
    subgraph Input
        SRC[Contract Source .sol]
        SPEC[Spec / README]
    end

    subgraph Zero-Trust Layer
        SBC[sandbox_check.py<br/>prompt injection scan]
    end

    subgraph Step 0 — Deep Analysis
        INV[extract_invariants.py]
        MAP[map_interactions.py]
        DT[deep_trace.py]
        BT[backward_trace.py]
        MT[multi_tx_trace.py]
        SMT[smt_check_invariants.py]
        ET[escalate_threads.py]
    end

    subgraph Step 1 — Static Analysis
        SA[static_analysis.py<br/>slither + AST]
        SC[supply_chain_check agent]
        DM[defense_mapper.py]
    end

    subgraph Step 2 — Specialist Agents — parallel
        RE[reentrancy.md]
        AC[access_control.md]
        AR[arithmetic.md]
        OR[oracle.md]
        FL[flash_loan.md]
        LG[logic.md]
        DS[dos.md]
        SN[snapshot.md]
        EA[economic_attack.md]
        TI[token_integration.md]
        CC[cross_chain.md]
        UP[upgrade_storage.md]
        BS[behavioral_state_analysis.md]
        SG[semantic_guard.md]
        E4[erc4626.md]
        TS[transient_storage.md]
        PC[protocol_context.md]
    end

    subgraph Step 2.5 — Connector
        CAC[cross_agent_connector.py]
    end

    subgraph Step 3 — Synthesis
        CS[synthesize_compound_findings.py]
        RG[report_generator.py]
        MPC[multi_pass_confirm.py]
        FP[fp_pattern_check.py]
        PSG[pre_submission_gate.py]
        ICE[run_impact_chain_escalation.py]
    end

    subgraph Step 4 — Triage
        TF[triage_findings.py]
        HRC[human_review_classifier.py]
    end

    subgraph Step 5–8 — Review and PoC
        SR[run_specialist_review.py]
        POC[generate_poc_test.py]
        QC[run_quality_checklist.py]
        PCG[analyze_poc_completeness.py]
    end

    subgraph Output
        REPORT[audit_report.md]
        SUBMIT[submission_pack.md]
        HUMAN[human_review_queue.jsonl]
    end

    subgraph Knowledge Base
        CHROMA[Chroma DB<br/>Solodit / C4 / Sherlock / Immunefi]
        KB_MCP[kb_mcp_server.py]
    end

    subgraph On-Chain Context
        QN[quicknode_mcp.py]
        DUNE[dune_mcp.py]
        GRAPH[graph_mcp.py]
    end

    subgraph Visualization
        VIZ[viz/server.py — port 8766]
        DASH[dashboard.py — port 8765]
    end

    SRC --> SBC
    SBC --> INV
    INV --> MAP --> DT
    DT --> ET
    BT --> ET
    MT --> ET
    SMT --> ET

    ET --> SA
    SA --> DM
    DM --> RE & AC & AR & OR & FL & LG & DS & SN & EA & TI & CC & UP & BS & SG & E4 & TS & PC

    RE & AC & AR & OR & FL & LG & DS & SN & EA & TI & CC & UP & BS & SG & E4 & TS & PC --> CAC
    CAC --> CS --> RG
    RG --> ICE --> MPC --> FP --> PSG
    PSG --> TF --> HRC

    HRC --> HUMAN
    TF --> SR
    SR --> POC --> QC --> PCG --> SUBMIT

    CHROMA --> KB_MCP
    KB_MCP -.->|retrieval| RE & AC & AR & OR & FL & LG
    QN & DUNE & GRAPH -.->|on-chain context| OR & FL & EA

    ET --> VIZ
    CAC --> VIZ
    TF --> DASH
```

---

## Data Flow: Contract Source to Submission Package

1. **Contract source** enters the pipeline as file paths or directory
2. **Sandbox check** scans for prompt injection patterns in comments and NatSpec
3. **Deep analysis** (Step 0) extracts invariants, maps the call graph, and traces dangerous chains before any pattern-matching runs
4. **Static analysis** (Step 1) produces `output/static.json` with AST, CFG edges, external calls, modifier lists, and taint sinks
5. **Specialist agents** (Step 2) each receive the contract source and `static.json`, consult the KB, and write `output/findings_<name>.json`
6. **Cross-agent connector** (Step 2.5) makes one holistic pass over all findings to find compound exploit chains
7. **Synthesis and gating** (Steps 3–3.7) merge findings, run multi-pass confirmation, check for known FP patterns, and apply 8 pre-submission gates
8. **Triage** (Step 4) calls the Claude triage agent and routes findings to submit/poc_required/downgraded/rejected
9. **Human review classifier** (Step 4.5) routes findings requiring expert judgment to `human_review_queue.jsonl`
10. **Specialist review and PoC** (Steps 5–8) model exploitability, estimate duplicate risk, calibrate severity, run PoC tests, and verify completeness
11. `final_submission_pack.py` produces the contest-ready `submission_pack.md`

---

## Agent Orchestration Model

Specialist agents are spawned as parallel Claude Code Tasks (via the Task tool). Each agent:
- Receives contract source as file content
- Reads `output/static.json` for pre-parsed data
- Reads `output/attack_surface.json` to prioritize high-scoring functions
- Calls `tools/retriever.py` and `tools/immunefi_retriever.py` for KB precedent
- Writes exactly one output file: `output/findings_<agent_name>.json`
- Conforms to `schema/findings_schema.json`

Conditional agents are only spawned when their trigger condition is met in `output/static.json` or `output/findings_protocol_context.json` (see [agents.md](agents.md) for trigger conditions).

---

## Storage Model

### Per-audit paths (isolated per contest)

```
audits/<audit_id>/
  meta.json             — contest metadata, scope, deadline
  output/               — all findings_*.json, merged_findings.json, reports
  data/triage/          — submit.jsonl, poc_required.jsonl, rejected.jsonl, gate_results.jsonl
  data/findings/        — <ID>.json per finding (for pipeline cross-referencing)
  data/exploitability/  — models.jsonl
  data/duplicates/      — risk.jsonl, clusters.jsonl
  data/severity/        — calibrated.jsonl
  data/runtime_poc/     — results.jsonl
  data/judge_simulation/— results.jsonl
  data/threads/         — promising_threads.jsonl, dead_ends.jsonl
  data/invariants/      — protocol_invariants.json, high_suspicion.json
  data/interactions/    — call_graph.json, dangerous_chains.json
  data/fp_autopsies/    — rejection_rules.jsonl (per-audit)
  data/evaluation/      — ground_truth.jsonl (human-only write)
  pocs/                 — generated PoC test files
  reports/              — poc_evidence.md
```

### Project-level paths (shared across all audits)

```
agents/       — agent specifications (read-only from agent perspective)
prompts/      — prompt templates
schemas/      — JSON schemas
templates/    — proof requirement templates
kb/           — Chroma vector DB
config/       — policy files, active_audit.json
data/fp_autopsies/rejection_rules.jsonl  — accumulated FP rules (all audits)
data/sessions/ — viz reasoning graph sessions
```

All pipeline scripts resolve paths through `scripts/audit_context.py`. The active audit is tracked in `config/active_audit.json`.

---

## Human Review Integration Points

| Stage | Where humans intervene |
|-------|----------------------|
| Step 0.5 | Sandbox check raises flags — human decides whether to proceed |
| Step 3.5 | `confirmation_score < 0.6` → `human_review_required = true` |
| Step 3.6 | FP pattern similarity warning → human reviews before reject |
| Step 3.7 | Gate WARN (3+ warnings) → routes to human review |
| Step 4.5 | 2+ human routing criteria → `human_review_queue.jsonl` |
| ICE | `ice.hold == true` → human consumer tracing before severity assignment |
| PoC | Critical claims without Level 2 PoC → manual exploit verification |
| Submission | Human auditor reads full exploit path before any submission |

---

## Two-Dashboard Architecture

### Audit Dashboard — port 8765

```bash
python scripts/dashboard.py
```

Tracks overall pipeline progress: finding counts by severity, triage bucket distribution, PoC status, judge simulation verdicts, duplicate risk. Auto-refreshes every 10 seconds via SSE. Reads JSONL pipeline files live — no rebuild needed.

### Reasoning Graph — port 8766

```bash
python viz/server.py
```

Live cognitive debugger showing the evolution of hypotheses, branches, and evidence across one audit session. Visualizes which hypotheses were born, which converged to findings, and which were invalidated — and why. Useful for reviewing agent reasoning and identifying where the pipeline diverged from expected paths.

See [reasoning-graph-dashboard.md](reasoning-graph-dashboard.md) for details.
