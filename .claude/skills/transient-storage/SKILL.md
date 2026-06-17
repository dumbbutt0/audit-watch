---
name: transient-storage
description: "Run the EIP-1153 transient storage specialist agent. Only activates when TSTORE/TLOAD opcodes are detected. Pulls cross-function reentrancy bypass, delegatecall namespace collision, and flash loan unlock patterns from Solodit and Immunefi. Activate on: /transient-storage, transient storage, TSTORE, TLOAD, EIP-1153, ReentrancyGuardTransient, transient reentrancy."
---

# EIP-1153 Transient Storage Audit

Conditional audit — only runs when TSTORE/TLOAD opcodes are detected in the contract.

## Phase 1: Conditional Guard + Discovery

**CONDITIONAL:** Two checks:
1. Read `output/static.json` for `"has_transient_storage": true`
2. Grep the contract:
   ```bash
   grep -in "tstore\|tload\|ReentrancyGuardTransient" <contract_path>
   ```

If both checks return negative:
```
[/transient-storage] Skipped: no TSTORE/TLOAD/ReentrancyGuardTransient detected.
This agent only applies to contracts using EIP-1153 transient storage (post-Cancun).
```
Stop.

If detected: "Transient storage detected. Checking for reentrancy bypass, delegatecall namespace collision, and flash-loan unlock." Print the grep results as the pre-scan list (N uses at: [locations]).

## Phase 2: Pre-flight KB Recon

```bash
python tools/retriever.py reentrancy "transient storage TSTORE TLOAD reentrancy guard bypass cross-function sibling unguarded" --top-k 5
python tools/retriever.py --all reentrancy "EIP-1153 transient storage slot aliasing delegatecall namespace collision proxy" --top-k 5
python tools/immunefi_retriever.py reentrancy "EIP-1153 transient storage reentrancy exploit bypass" --top-k 5
```

Display summary:
```
Transient Storage KB Recon:
  Solodit reentrancy: [top 3]
  Solodit general: [top 3]
  Immunefi: [top 3]

  Note: transient storage is a newer attack surface — expect many findings to have low KB similarity.
  Low similarity does NOT mean false positive here; it likely means novel pattern.

Top attack patterns:
  ITE-1 — Cross-function reentrancy via unguarded sibling
    Intent: read/modify shared state with a half-updated sibling function
    Technique: call guarded functionA() → ReentrancyGuardTransient sets transient slot → external call → in callback, call unguarded functionB() (same group, no guard) → functionB reads/writes same state half-updated by functionA
    Evasion: guard applied to functionA only; functionB not identified as requiring same guard; transient guard does not protect sibling functions
  ITE-2 — Delegatecall transient namespace collision
    Intent: corrupt transient state of proxy by triggering implementation's TSTORE
    Technique: proxy uses transient slot 0 as reentrancy lock → proxy delegates to implementation → implementation uses transient slot 0 as flash-active flag → implementation's TSTORE writes to proxy's transient namespace (same slot 0) → proxy reads wrong semantic value
    Evasion: TSTORE in DELEGATECALL context writes to caller's transient namespace; developer tested implementation standalone; slot 0 chosen without audit of proxy's own transient usage
  ITE-3 — Flash loan callback unlocks transient-gated function
    Intent: call a function that should only be callable during a specific internal operation
    Technique: flash loan provider sets transient slot FLASH_ACTIVE=1 during callback → target has require(tload(FLASH_ACTIVE)==1) as only guard → attacker initiates flash loan → in callback (when FLASH_ACTIVE==1) calls gated function
    Evasion: transient gate set by EXTERNAL contract (flash provider); any flash loan initiator can trigger gate; gate not restricted to internal callers
```

## Phase 3: Agent Dispatch

Spawn `agents/transient_storage.md` as a Task. Provide:
- Full contract source
- `output/static.json`
- `output/attack_surface.json`
- `output/findings_protocol_context.json`
- `data/invariants/protocol_invariants.json`
- `data/threads/promising_threads.jsonl`
- `prompts/human_auditor_methodology.md`

After agent writes `output/findings_transient_storage.json`, validate:
```bash
python scripts/validate_agent_output.py output/findings_transient_storage.json
```

## Phase 4: KB Cross-Reference + Novelty Flagging

```bash
python tools/retriever.py reentrancy "<finding_title> <description_excerpt>" --top-k 3
python tools/immunefi_retriever.py reentrancy "<finding_title>" --top-k 3
```

Note: expect low similarity scores. Transient storage is a post-Cancun feature. A low score here is expected and should NOT automatically suppress the finding — it IS likely novel. Flag `[NOVEL]` if < 0.4. Run:
```bash
python scripts/human_review_classifier.py
python scripts/generate_status.py
```

## Phase 5: Results Display + Next Actions

```
[/transient-storage] scan complete: N findings (EIP-1153 transient storage)
  Critical: N  High: N  Medium: N  Low: N

Novel findings (low KB similarity expected for EIP-1153 — novel does not mean false positive):
  [TS-001] <title>

KB-matched findings:
  [TS-002] <title>   — matched: "Reentrancy guard bypass" (score: 0.72)

Next:
  /reentrancy        — transient-storage findings often co-occur with classic reentrancy
  /confirm TS-001    — multi-pass confirmation essential for novel transient-storage findings
  /human-queue       — all transient-storage novel findings should be human-reviewed
```
