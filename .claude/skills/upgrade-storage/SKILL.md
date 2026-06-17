---
name: upgrade-storage
description: "Run the proxy/upgrade storage specialist agent. Only activates when a proxy pattern is detected. Pulls storage collision, uninitialized proxy front-run, UUPS auth gap, and storage layout drift patterns from Solodit and Immunefi. Activate on: /upgrade-storage, proxy, UUPS, storage collision, initialize front-run, selfdestruct implementation, upgradeable, storage gap."
---

# Proxy/Upgrade Storage Audit

Conditional audit — only runs when a proxy or upgradeable pattern is detected.

## Phase 1: Conditional Guard + Discovery

**CONDITIONAL:** Read `output/findings_protocol_context.json`. Check for any of these strings:
`ERC-1967`, `proxy`, `UUPS`, `TransparentProxy`, `BeaconProxy`, `upgradeable`

If NONE are found:
```
[/upgrade-storage] Skipped: no proxy or upgradeable pattern detected in output/findings_protocol_context.json.
Run /surface or /ite-audit first to classify the protocol, or pass --force to override.
```
Stop.

If detected: print which proxy type was identified (UUPS, Transparent, Beacon, or minimal proxy). Then grep:
```bash
grep -n "initialize\|_authorizeUpgrade\|__gap\|delegatecall\|StorageSlot\|ERC1967" <contract_path>
```
List all matches as priority targets.

## Phase 2: Pre-flight KB Recon

```bash
python tools/retriever.py proxy-upgrade "UUPS _authorizeUpgrade missing authorization empty override onlyOwner proxy" --top-k 5
python tools/retriever.py storage-collision "proxy implementation storage slot collision ERC-1967 variable layout drift" --top-k 5
python tools/immunefi_retriever.py --all "proxy upgrade uninitialized initialize front-run exploit storage collision" --top-k 5
```

Display summary:
```
Upgrade Storage KB Recon:
  Solodit proxy-upgrade: [top 3]
  Solodit storage-collision: [top 3]
  Immunefi: [top 3]

Top attack patterns:
  ITE-1 — Uninitialized proxy front-running
    Intent: take ownership of the contract before the legitimate deployer initializes it
    Technique: monitor mempool for proxy deployment → when deployed, immediately call initialize(attackerAddress) → attacker becomes owner/admin → drain or lock protocol
    Evasion: initialize() not called atomically with deployment; no factory that deploys+inits in one tx
  ITE-2 — UUPS _authorizeUpgrade empty or missing
    Intent: upgrade implementation to a malicious contract
    Technique: call upgradeTo(maliciousImpl) → _authorizeUpgrade() is empty override or not overridden → upgrade succeeds → attacker's code runs with proxy's storage → drain all funds
    Evasion: UUPS base has virtual _authorizeUpgrade() that does nothing; child must override with onlyOwner; omission compiles fine
  ITE-3 — Storage layout drift (gap shrink)
    Intent: corrupt all storage variables after the insertion point during an upgrade
    Technique: V1 uses uint256[50] __gap → V2 reduces to uint256[49] __gap to add variable before gap (instead of consuming gap slot) → all vars after the new one read from wrong slots → balances/roles/config corrupted
    Evasion: compiler does not detect storage layout changes; no automated layout comparison between versions
```

## Phase 3: Agent Dispatch

Spawn `agents/upgrade_storage.md` as a Task. Provide:
- Full contract source
- `output/static.json`
- `output/attack_surface.json`
- `output/findings_protocol_context.json`
- `output/findings_access_control.json` (if present — most proxy bugs are auth-related)
- `data/invariants/protocol_invariants.json`
- `data/threads/promising_threads.jsonl`
- `prompts/human_auditor_methodology.md`

After agent writes `output/findings_upgrade_storage.json`, validate:
```bash
python scripts/validate_agent_output.py output/findings_upgrade_storage.json
```

## Phase 4: KB Cross-Reference + Novelty Flagging

```bash
python tools/retriever.py proxy-upgrade "<finding_title> <description_excerpt>" --top-k 3
python tools/retriever.py storage-collision "<finding_title> <description_excerpt>" --top-k 3
python tools/immunefi_retriever.py --all "<finding_title>" --top-k 3
```

Take highest score across all queries. Flag `[NOVEL]` if < 0.4. Run:
```bash
python scripts/human_review_classifier.py
python scripts/generate_status.py
```

## Phase 5: Results Display + Next Actions

```
[/upgrade-storage] scan complete: N findings (proxy type: <type>)
  Critical: N  High: N  Medium: N  Low: N

Novel findings (KB similarity < 0.4):
  [UP-001] <title>

KB-matched findings:
  [UP-002] <title>   — matched: "Uninitialized UUPS proxy" (score: 0.90)

Next:
  /access-control    — upgrade auth issues often co-occur with access control findings
  /confirm UP-001    — multi-pass confirmation
  /human-queue       — human review queue
```
