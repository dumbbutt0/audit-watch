# Audit-Watch Smart Contract Auditor

Audit-Watch is a multi-agent smart contract auditing framework built on Claude Code. It takes Solidity source files as input and produces a structured vulnerability report suitable for Immunefi, Code4rena, or Sherlock contest submission.

**Important:** All output requires human auditor review before submission. The framework automates systematic analysis; it does not replace expert judgment on novel patterns or Critical findings.

---

## Main Features

- **34 specialist agents** running in parallel — reentrancy, access control, arithmetic, oracle, flash loan, logic, DoS, snapshot, economic attack, token integration, cross-chain, proxy/upgrade, behavioral state analysis, semantic guard, ERC-4626, EIP-1153 transient storage, and more
- **Deep invariant analysis** (Step 0) — extracts protocol invariants, maps call graphs, and traces dangerous multi-hop chains before pattern-matching agents run
- **ITE attack surface mapping** (Step 0.25) — Intent/Technique/Evasion recon-first framework
- **Multi-pass confirmation** (Step 3.5) — runs High/Critical finding reasoning 3–5 times independently to handle LLM non-determinism
- **Impact Chain Escalation (ICE)** — never reports severity on a corrupted state that no trusted consumer ever reads
- **Pre-submission gate** — 8 structural validity gates with hard invalidation tags; filters false positives before triage API calls
- **PoC generation pipeline** — plans, writes, and runs Foundry/Hardhat/Rust proof-of-concept tests
- **Two live dashboards** — audit progress at port 8765, adversarial reasoning graph at port 8766
- **Per-audit workspaces** — isolated `audits/<id>/` directories; 10 real contest workspaces included
- **Knowledge base** — Chroma vector DB backed by Solodit, Code4rena, Sherlock, and Immunefi findings

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt
pip install slither-analyzer solc-select
solc-select install latest && solc-select use latest

# 2. Set API keys
echo 'ANTHROPIC_API_KEY=sk-ant-...' >> .env
echo 'SOLODIT_API_KEY=sk_...' >> .env

# 3. Build the knowledge base (~20 min)
python scripts/solodit_scraper.py

# 4. Verify setup
python tools/verify_setup.py

# 5. Create an audit workspace
python scripts/audit_manager.py new my-protocol-2026-06

# 6. Run an audit
# Tell Claude Code: "Audit this contract: contracts/MyProtocol.sol"
# Or run the pipeline script:
./run_pipeline.sh full
```

---

## Pipeline Overview

The pipeline runs in 8 numbered steps. Step 0 extracts protocol invariants and maps dangerous interaction chains. Steps 0.25 and 0.5 perform attacker mindset mapping and sandbox injection checks. Step 1 runs static analysis and supply chain checks. Step 2 spawns up to 16 specialist agents in parallel. Steps 3–3.7 synthesize compound findings, confirm high-severity findings through multiple passes, check against known false-positive patterns, and apply 8 pre-submission gates. Step 4 triages findings into submission buckets. Steps 5–8 handle specialist review, PoC generation, quality checklists, and completeness verification.

See [pipeline.md](pipeline.md) for the complete per-stage reference.

---

## Important Directories

| Directory | Purpose |
|-----------|---------|
| `agents/` | 34 specialist agent specifications |
| `prompts/` | 17 instruction templates used by agents |
| `.claude/skills/` | 23 Claude Code slash commands |
| `scripts/` | 58 Python pipeline scripts |
| `tools/` | Static analysis, KB retrieval, MCP tools, report generation |
| `schemas/` | 15 JSON schemas for pipeline data formats |
| `config/` | `agent_policy.json`, `zero_trust_policy.json`, mode settings |
| `viz/` | Reasoning graph visualization server (port 8766) |
| `dashboard/` | Audit progress dashboard frontend (port 8765) |
| `audits/` | Per-contest workspaces (isolated output, data, pocs) |
| `kb/` | Chroma vector database (Solodit/Immunefi/C4 findings) |

---

## Warning

The framework's output — including severity assessments, PoC tests, and triage decisions — is AI-generated and subject to both false positives and false negatives. Before submitting any finding to a live bounty program or contest:

1. Read the full exploit path personally
2. Confirm every precondition is achievable on-chain
3. Verify PoC tests run cleanly in a local or fork environment
4. Check the human review queue (`data/triage/human_review_queue.jsonl`) — these findings require expert review before submission

See [troubleshooting.md](troubleshooting.md) for common issues.
