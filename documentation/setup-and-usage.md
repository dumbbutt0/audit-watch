# Setup and Usage

---

## Requirements

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.11+ | All pipeline scripts |
| slither-analyzer | >= 0.10.0 | Static analysis (Step 1) |
| solc / solc-select | latest | Solidity compilation |
| Node.js / npm | LTS | Hardhat test execution (optional) |
| cargo / rustup | stable | Rust PoC tests (optional, for Soroban/Starknet) |
| z3-solver | >= 4.12.0 | SMT invariant falsification (Step 0e) |

---

## Installation

```bash
# 1. System prerequisites (Ubuntu/Debian)
sudo apt install python3.12-venv python3-full -y

# 2. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Python dependencies
pip install -r requirements.txt

# 4. Smart contract tools
pip install slither-analyzer solc-select
solc-select install latest
solc-select use latest
```

---

## Environment Variables

Set in `.env` at the project root (created automatically on first audit setup).

| Variable | Required | Purpose |
|----------|----------|---------|
| `ANTHROPIC_API_KEY` | Yes | Claude API for triage, agents, PoC generation |
| `SOLODIT_API_KEY` | Yes | Solodit API for knowledge base building |
| `QUICKNODE_ENDPOINT_ETHEREUM` | No | Live bytecode verification (ethereum) |
| `QUICKNODE_ENDPOINT_ARBITRUM` | No | Live bytecode verification (arbitrum) |
| `QUICKNODE_ENDPOINT_BASE` | No | Live bytecode verification (base) |
| `QUICKNODE_ENDPOINT_POLYGON` | No | Live bytecode verification (polygon) |
| `ETHERSCAN_API_KEY` | No | Contract verification via Etherscan |
| `DUNE_API_KEY` | No | Protocol TVL and volume from Dune Analytics |
| `GRAPH_API_KEY` | No | Historical on-chain state from The Graph |
| `GLIDER_API_KEY` | No | Cross-repo variant analysis via Glider |

All on-chain tools degrade gracefully if their key is absent — they return `{}` or `[]` and the pipeline continues.

---

## Building the Knowledge Base

```bash
# Full initial scrape (~1000 findings, ~20 minutes)
python scripts/solodit_scraper.py

# Test first (50 findings, ~3 minutes)
python scripts/solodit_scraper.py --limit 50

# Continuous background mode (fetches new findings every 30 minutes)
nohup python scripts/solodit_scraper.py --continuous > kb/scraper.log 2>&1 &

# Ingest Code4rena / Sherlock reports
python scripts/ingest_c4_reports.py
```

---

## Pre-Flight Check

```bash
python tools/verify_setup.py
```

Expected output:
```
✓ Chroma DB: N findings indexed
✓ slither available
✓ solc available
✓ Embeddings model loaded
```

---

## Audit Management

```bash
# Create a new workspace
python scripts/audit_manager.py new my-protocol-2026-06

# List all audits + status
python scripts/audit_manager.py list

# Show current audit details
python scripts/audit_manager.py info

# Switch active audit
python scripts/audit_manager.py switch my-protocol-2026-06

# Update status
python scripts/audit_manager.py status active|submitting|archived
```

The active audit ID is stored in `config/active_audit.json`. All pipeline scripts resolve paths through `scripts/audit_context.py` based on this value.

---

## Running the Full Pipeline

### Option A: Via Claude Code (recommended)

Open Claude Code in the project directory and say:
```
Audit this contract: contracts/MyProtocol.sol
```
Claude Code reads `CLAUDE.md` and executes the full workflow automatically, prompting for human decisions at the appropriate points.

### Option B: Via run_pipeline.sh

```bash
# Full pipeline
./run_pipeline.sh full

# Individual stages
./run_pipeline.sh status
./run_pipeline.sh triage
./run_pipeline.sh specialist
./run_pipeline.sh poc RE-001
./run_pipeline.sh poc-all
./run_pipeline.sh package
./run_pipeline.sh checklist
./run_pipeline.sh gate
```

### Option C: Step-by-step

Follow the steps in [pipeline.md](pipeline.md) in order.

---

## Launching Dashboards

```bash
# Audit progress dashboard (port 8765)
python scripts/dashboard.py
# Opens http://localhost:8765 in browser

# Reasoning graph dashboard (port 8766)
python viz/server.py
# Opens http://localhost:8766
```

---

## Mode Control

```bash
# Check current mode
cat config/agent_policy.json | grep active_mode

# Change mode
# fast: triage only, no scanning or PoC
# normal: specialists + PoC for top 3 findings (default)
# deep: full pass, all PoCs, requires approval prompt
```

Or in Claude Code:
```
/mode fast
/mode normal
/mode deep
```

---

## Common Commands Reference

These map to the phone control commands in `config/phone_commands.md`:

| Command | Action |
|---------|--------|
| `/status` | `python scripts/generate_status.py` → print summary |
| `/top` | Show top 5 findings ranked by exploitability × severity ÷ duplicate_risk |
| `/poc` | Summarize all PoC results |
| `/submit-ready` | Filter findings: submit + proved + checklist passed |
| `/risks` | Top 2 rejection risks per submit-ready finding |
| `/novel` | 5 findings with lowest KB similarity (most novel) |
| `/continue` | Run the next safe pipeline step |
| `/stop` | Stop and summarize state + next recommended action |
| `/package [id]` | Build submission pack |
| `/human-queue` | Show findings requiring human review |
| `/confirm [id]` | Run multi-pass confirmation |
| `/surface` | Show attack surface map |

---

## Migrating Existing Audit Data

If you have data from the legacy flat `output/` structure:

```bash
# Preview what will be migrated
python scripts/migrate_to_audit.py --dry-run

# Migrate K2 data to audits/k2-kinetic-2026-04/
python scripts/migrate_to_audit.py
```

---

## Auto-Activate Virtual Environment

Add to `~/.bashrc` to automatically activate the venv when entering the project directory:

```bash
cd() { builtin cd "$@" && [ -f .venv/bin/activate ] && source .venv/bin/activate; }
```

---

## Switching Audits While Dashboard Runs

Either:
```bash
python scripts/audit_manager.py switch my-protocol-2026-06
```

Or POST to the running dashboard:
```bash
curl -X POST http://localhost:8765/api/audits/switch \
  -H 'Content-Type: application/json' \
  -d '{"audit_id": "my-protocol-2026-06"}'
```

The server picks up the new active audit on the next `/api/state` poll — no restart needed.
