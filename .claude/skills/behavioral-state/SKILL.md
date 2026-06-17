---
name: behavioral-state
description: "Run the behavioral state analysis agent to find semantic divergence between NatSpec/comments and actual code behavior. Pulls documented-but-not-enforced patterns from KB. Activate on: /behavioral-state, BSA, NatSpec mismatch, comment says but code does, documented invariant, semantic divergence, doc lie, undocumented behavior."
---

# Behavioral State Analysis Audit

Targeted semantic divergence scan. Finds cases where NatSpec, comments, or protocol documentation make claims that the code does not enforce.

## Phase 1: Contract Discovery + Priority Targets

1. Find contract if not provided:
   ```bash
   find . -name "*.sol" -not -path "*/node_modules/*" -not -path "*/lib/*" -not -path "*/test/*" | head -20
   ```

2. Extract all NatSpec comments from the contract:
   ```bash
   grep -n "@notice\|@dev\|@param\|@return\|///\|/\*\*" <contract_path> | head -50
   ```

3. List functions that contain restrictive language in their NatSpec — these are the priority targets for divergence:
   ```bash
   grep -n "only\|must\|cannot\|should not\|invariant\|guarantee\|require" <contract_path> | grep -i "notice\|dev\|///\|/\*"
   ```

## Phase 2: Pre-flight KB Recon

```bash
python tools/retriever.py access-control "function documented admin only missing modifier guard NatSpec comment stated restriction not enforced" --top-k 5
python tools/retriever.py access-control "undocumented missing guard comment stated invariant fee cap restriction not in code" --top-k 5
python tools/immunefi_retriever.py access-control "undocumented missing guard access control exploit comment lie" --top-k 5
```

Display summary:
```
Behavioral State Analysis KB Recon:
  Solodit: [top 3]
  Immunefi: [top 3]

Top attack patterns:
  ITE-1 — NatSpec says onlyOwner, code has no modifier
    Intent: gain unauthorized admin privilege
    Technique: read NatSpec "@notice Only callable by the owner" → call function from non-owner address → function executes — no require(msg.sender == owner) check exists
    Evasion: modifier in parent contract but not inherited here; or developer removed modifier but forgot to update NatSpec
  ITE-2 — Comment-stated fee cap not enforced
    Intent: set fee to 100% and drain all protocol revenue
    Technique: find "@dev Fee cannot exceed 10%" in NatSpec → call setFee(10000) → no require(newFee <= 1000) exists → fee set to 100% → all subsequent txs pay full fee to attacker-controlled recipient
    Evasion: NatSpec states constraint as informational text only; no corresponding require in the setter
  ITE-3 — Admin-only event in permissionless path
    Intent: conceal an attack by emitting misleading admin events
    Technique: call permissionless function → function emits ConfigUpdated() or OwnershipTransferred() event → monitoring systems see event, interpret as admin action, do not alert → attacker's state change goes undetected
    Evasion: event name implies restricted access; monitoring relies on event name for alert classification
```

## Phase 3: Agent Dispatch

Spawn `agents/behavioral_state_analysis.md` as a Task. Provide:
- Full contract source
- `output/static.json`
- `output/attack_surface.json`
- `output/findings_protocol_context.json`
- `data/invariants/protocol_invariants.json`
- `data/threads/promising_threads.jsonl`
- `prompts/human_auditor_methodology.md`

After agent writes `output/findings_behavioral_state_analysis.json`, validate:
```bash
python scripts/validate_agent_output.py output/findings_behavioral_state_analysis.json
```
Note: BSA findings include a `bsa_metadata` field with `divergence_type` — report any findings missing this field.

## Phase 4: KB Cross-Reference + Novelty Flagging

```bash
python tools/retriever.py access-control "<finding_title> <description_excerpt>" --top-k 3
python tools/retriever.py logic-error "<finding_title> <description_excerpt>" --top-k 3
python tools/immunefi_retriever.py access-control "<finding_title>" --top-k 3
```

Note: BSA findings often have low KB similarity by design — they capture protocol-specific intent divergences not in generic KBs. Flag `[NOVEL]` if < 0.4. All BSA findings should be treated as requiring human review (BSA criterion in the classifier). Run:
```bash
python scripts/human_review_classifier.py
python scripts/generate_status.py
```

## Phase 5: Results Display + Next Actions

```
[/behavioral-state] scan complete: N findings
  (Note: BSA findings auto-route to human review — behavioral intent requires human judgment)
  Critical: N  High: N  Medium: N  Low: N

All BSA findings require human validation (bsa_metadata criterion):
  [BSA-001] <title>  divergence_type: <type>

KB-matched findings:
  [BSA-002] <title>   — matched: "Missing modifier despite NatSpec" (score: 0.78)

Next:
  /semantic-guard    — BSA modifier divergence often co-occurs with guard completeness issues
  /human-queue       — all BSA findings should be in human review queue
  /confirm BSA-001   — multi-pass confirmation
```
