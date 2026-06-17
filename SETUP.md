# Smart Contract Auditor — Setup Guide

## Prerequisites

```bash
sudo apt install python3.12-venv python3-full -y
```

## One-time setup (run once, in this exact order)

```bash
# 1. Navigate to the project
cd smart-contract-auditor

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install smart contract tools
pip install slither-analyzer solc-select
solc-select install latest
solc-select use latest

# 5. Set your API keys
export SOLODIT_API_KEY=sk_your_solodit_key_here
# Optional — enables Claude-powered pattern synthesis in agent files:
export ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here

# Save keys permanently so they survive terminal restarts:
echo 'SOLODIT_API_KEY=sk_your_solodit_key_here' >> .env
echo 'ANTHROPIC_API_KEY=sk-ant-your_key_here' >> .env   # optional

# 6. Verify all tools are ready
python tools/verify_setup.py
# Expected: 9/9 green except Chroma DB (not built yet)

# 7. Confirm API connection and tag counts
python scripts/solodit_scraper.py --show-tags

# 8. Test scrape (50 findings, takes ~3 minutes)
python scripts/solodit_scraper.py --limit 50

# 9. Test the retriever works
python tools/retriever.py reentrancy "withdraw function external call before state update"

# 10. Full initial scrape (~1000 findings, takes ~20 minutes)
python scripts/solodit_scraper.py

# 11. Final check — should be 10/10 green
python tools/verify_setup.py
```

## Every time you open a new terminal

```bash
cd smart-contract-auditor
source .venv/bin/activate
export SOLODIT_API_KEY=sk_your_key   # skip if you created .env
```

Auto-activate shortcut (add to ~/.bashrc):
```bash
cd() { builtin cd "$@" && [ -f .venv/bin/activate ] && source .venv/bin/activate; }
```

## Running the knowledge base updater

### Background — continuous mode (recommended)
Fetches new reports every 30 minutes and updates agent files with learned patterns:
```bash
# Run in background, log to file
nohup python scripts/solodit_scraper.py --continuous > kb/scraper.log 2>&1 &
echo $! > kb/scraper.pid   # save process ID to stop it later
tail -f kb/scraper.log     # watch live

# Stop it when you want
kill $(cat kb/scraper.pid)
```

### Interactive — watch it run
```bash
python scripts/solodit_scraper.py --continuous --interval 60
# Ctrl+C to stop cleanly
```

### Manual refresh
```bash
python scripts/solodit_scraper.py --refresh   # wipe and rebuild everything
```

## Running an audit

Open Claude Code in the project directory and say:
```
Audit this contract: path/to/YourContract.sol
```

Or for a directory:
```
Audit all contracts in: contracts/
```

Claude Code will read CLAUDE.md and execute the full 8-agent workflow automatically.

## What gets updated automatically (continuous mode)

Each cycle the scraper:
1. Fetches all new Solodit findings from the last 30 days
2. Adds them to the Chroma vector database
3. Analyses new findings by vulnerability category
4. Injects an "Auto-learned patterns" section at the bottom of each agent file
   - Uses Claude Haiku if ANTHROPIC_API_KEY is set (better insights)
   - Falls back to frequency-based extraction if not set

Agent files updated automatically:
  agents/reentrancy.md       ← reentrancy + read-only reentrancy patterns
  agents/access_control.md   ← access control + signature replay patterns
  agents/arithmetic.md       ← overflow, precision, rounding patterns
  agents/oracle.md           ← oracle, staleness, TWAP patterns
  agents/flash_loan.md       ← flash loan + sandwich + front-running patterns
  agents/logic.md            ← business logic + ERC4626 + liquidation patterns
  agents/dos.md              ← DOS + griefing + gas limit patterns
  agents/snapshot.md         ← governance + voting + snapshot patterns

Pattern history is stored in kb/patterns/<vuln_type>.json
