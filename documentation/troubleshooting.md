# Troubleshooting

---

## Claude Rate Limits / Context Window Exhaustion

**Symptom:** Agent returns an error mid-run; triage script fails with API error; `confirmation_score = 0.0` with error in `human_review_reason`.

**Diagnosis:**
- Rate limit: check for `429` or `rate_limit` in the error message
- Context window: check for `context_length_exceeded` or `max_tokens` in the error

**Fix:**
- Rate limit: wait 60 seconds and re-run the affected step with `--finding-id` to process one at a time
- Context window: split the contract directory into smaller subsets; run agents on individual files rather than the full directory
- Long contracts: ensure `output/static.json` is pre-generated before spawning agents — static.json is a compact summary that fits in context much better than raw source

**Multi-pass confirm API error:** When `multi_pass_confirm.py` hits an API error on a confirmation pass, it records `confirmation_score = 0.0` and sets `human_review_required = true`. Check `human_review_reason` — it will say "API error during pass N". Re-run: `python scripts/multi_pass_confirm.py --finding-id <ID> --force`

---

## Broken Python Dependencies

**Symptom:** `ImportError`, `ModuleNotFoundError`, or version conflict errors on startup.

**Common causes and fixes:**

| Error | Fix |
|-------|-----|
| `slither.exceptions.SlitherError` | `pip install --upgrade slither-analyzer` |
| `z3.Z3Exception` | `pip install z3-solver==4.12.4.0` (specific version for ARM compatibility) |
| `chromadb` import error | `pip install "chromadb>=0.4.22"` |
| `anthropic` version mismatch | `pip install "anthropic>=0.25.0"` |
| `fastapi` / `uvicorn` error | `pip install "fastapi>=0.110.0" "uvicorn>=0.29.0"` |

Always run inside the virtual environment:
```bash
source .venv/bin/activate
```

---

## Missing RPC/API Keys

**Symptom:** `Warning: QUICKNODE_ENDPOINT_ETHEREUM not set — skipping on-chain query` in stderr.

**Behavior:** All on-chain MCP tools degrade gracefully when keys are absent. The pipeline continues without on-chain data. This is expected behavior — on-chain tools are optional context providers.

**Fix:** Add the key to `.env`:
```bash
echo 'QUICKNODE_ENDPOINT_ETHEREUM=https://your-endpoint.quicknode.com/abc123' >> .env
```

**Immunefi MCP unreachable:** `tools/immunefi_retriever.py` returns `[]` if `https://reports.immunefi.com/~gitbook/mcp` is down. This is non-fatal. The agent continues with Solodit KB results only.

---

## Hardhat / Foundry Compile Errors

**Symptom:** `generate_poc_test.py` generates test code that fails to compile.

**Common fixes:**

| Error | Fix |
|-------|-----|
| `Stack too deep` | Add `viaIR: true` to `foundry.toml` under `[profile.default]` |
| `CompilerError: Stack too deep` (Hardhat) | Add `viaIR: true` in `hardhat.config.js` `solidity.settings.viaIR` |
| Missing import | Check that all contract imports resolve relative to the project root |
| Version mismatch | `solc-select use <version>` to match the contract's pragma |
| Foundry `forge test` not found | `curl -L https://foundry.paradigm.xyz | bash && foundryup` |

The PoC generator allows up to `max-repair-attempts` (default 3) repair cycles. If all repair attempts fail, the result is `compile_error` and the finding moves to `poc_required` for manual PoC work.

---

## Wrong Working Directory

**Symptom:** `FileNotFoundError` for files that should exist; paths resolve to wrong locations.

**Fix:** Always run pipeline scripts from the project root:
```bash
cd /path/to/smart-contract-auditor
source .venv/bin/activate
python scripts/generate_status.py
```

Do not `cd` into `scripts/` or `tools/` before running. All scripts use `Path(__file__).resolve().parent.parent` to locate the project root — this breaks if you run them from unexpected directories.

---

## Stale merged_findings.json

**Symptom:** Triage results don't include new findings added by agents that ran after the last report generation.

**Fix:** Re-run report_generator.py to regenerate the merged file:
```bash
python tools/report_generator.py
```

Then re-run the ICE and confirmation steps:
```bash
python scripts/run_impact_chain_escalation.py
python scripts/multi_pass_confirm.py
python scripts/generate_status.py
```

---

## Dashboard Not Updating

**Symptom:** Browser shows stale data; new findings not appearing.

**Causes and fixes:**

| Symptom | Fix |
|---------|-----|
| Dashboard not refreshing | Check `watchfiles` is installed: `pip install watchfiles>=0.21.0` |
| Port 8765 already in use | Kill existing process: `lsof -ti:8765 | xargs kill` |
| Port 8766 (viz) conflict | Kill: `lsof -ti:8766 | xargs kill` |
| JSON parse error in JSONL | Run `python scripts/validate_agent_output.py output/` to find the offending line |
| Old data showing | Hard-refresh browser (Ctrl+Shift+R); check that `generate_status.py` ran recently |

---

## False High Confidence Scores

**Symptom:** `confirmation_score` is high (> 0.9) for a finding that later gets rejected by judges.

**Root cause:** The confirmation passes all agreed because they shared the same flawed reasoning. High confirmation_score does not mean the finding is correct — it means the LLM was consistent.

**Fix:** Check `human_review_queue.jsonl`. Findings with novel patterns (low KB similarity < 0.4) should be in the human queue regardless of confirmation score. If a high-confidence finding is later rejected, record an FP autopsy:
```bash
python scripts/record_fp_autopsy.py \
  --finding-id <ID> \
  --judge-outcome rejected \
  --rejection-reason "<exact judge reason>"
```

---

## Duplicate Report Risk

**Symptom:** Unsure whether a finding overlaps with other known findings or previous submissions.

**Fix:**
```bash
python scripts/estimate_duplicate_risk.py --finding-id <ID>
```

Also search the Solodit KB directly:
```bash
python tools/retriever.py <vuln_type> "<description of the finding>"
```

If `duplicate_risk == "high"`, strongly consider merging with or dropping the finding. Check the `overlap_reason` and `unique_angle` fields for guidance.

---

## Missing VIZ_SESSION_ID

**Symptom:** Reasoning graph dashboard shows no events; `viz/server.py` displays empty graph.

**Cause:** Pipeline scripts emit events to `data/sessions/{session_id}/events.jsonl`. If `VIZ_SESSION_ID` is not set, events are silently skipped.

**Fix:**
```bash
# Create a session and export the ID
export VIZ_SESSION_ID=$(python -c "from viz.session import create_session; print(create_session())")
# Then run pipeline steps with this env var set
```

Alternatively, `viz/server.py` will load the most recent session from disk on startup if `VIZ_SESSION_ID` is not set.

---

## triage_findings.py Overwrites submit.jsonl

**Symptom:** Running `python scripts/triage_findings.py` without `--finding-id` overwrites existing triage decisions.

**Fix:** Never run `triage_findings.py` without `--finding-id` on an existing audit with known-good triage decisions. Use:
```bash
python scripts/triage_findings.py --finding-id NEW-001
```

For multiple new findings:
```bash
for id in NEW-001 NEW-002 NEW-003; do
  python scripts/triage_findings.py --finding-id $id
done
```

See the memory note: [feedback_triage_reruns.md](../audits/xterio-2026-05/memory/).
